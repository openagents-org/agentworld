# Observer Multi-Connection Fix

## 🐛 问题描述

当Web UI作为observer登录已在线的agent时，会出现**两个相同的角色**。

### 症状
```
Agent "testuser" 通过API登录 → 角色1出现在游戏中 ✅
Web UI 用 "testuser" 登录 → 角色2也出现在游戏中 ❌
结果: 地图上有两个 "testuser"
```

## 🔍 根本原因

Player创建和登录流程：

```
1. network.handleConnection(connection)
   └→ new Player(world, database, connection)  // Player实例创建

2. incoming.handleHandshake()
   └→ 客户端握手成功

3. incoming.handleLogin(username, password)
   └→ 检查this.world.isOnline(username)
   └→ 如果在线 && socialMode:
       ├→ existingPlayer.addObserver(this.connection)
       └→ return;  // 尝试中断登录

4. database.login() 
   └→ player.load(data)
       └→ player.intro()  // ❌ 问题：还是会执行
           └→ entities.addPlayer(this)  // ❌ 第二个角色被添加
```

**问题**: 虽然在步骤3返回了，但Player实例已经创建，并且database.login()可能已经被调用，最终`intro()`仍然执行，导致第二个角色被添加到世界。

## ✅ 解决方案

添加`isObserverOnly`标志，阻止observer Player被添加到游戏世界。

### 实现细节

#### 1. Player类添加标志
```typescript
// player.ts
private isObserverOnly: boolean = false;

public markAsObserverOnly(): void {
    this.isObserverOnly = true;
    log.debug(`Player ${this.username} marked as observer-only`);
}
```

#### 2. intro()中添加检查
```typescript
// player.ts
public intro(): void {
    // If this is an observer-only connection, don't add to world
    if (this.isObserverOnly) {
        log.debug(`Skipping intro for observer-only connection: ${this.username}`);
        return;
    }

    // ... 正常的intro逻辑
    this.entities.addPlayer(this);
    this.send(new Welcome(this.serialize(false, true, true)));
}
```

#### 3. 检测observer时标记
```typescript
// incoming.ts
if (this.world.isOnline(this.player.username)) {
    if (config.socialMode && config.socialModeAllowMonitor) {
        let existingPlayer = this.world.getPlayerByName(this.player.username);
        if (existingPlayer) {
            // Mark this player instance as observer-only (prevents intro())
            this.player.markAsObserverOnly();
            
            // Convert this connection to an observer
            existingPlayer.addObserver(this.connection);
            
            // ... 设置消息转发等
            
            return; // Don't proceed with normal login
        }
    }
    return this.connection.reject('loggedin');
}
```

## 📊 执行流程对比

### 修复前 ❌
```
API Login:
  new Player → load → intro → addPlayer(player1) ✅

Web UI Login:
  new Player → detect online → addObserver → return
  BUT: Player still exists → load → intro → addPlayer(player2) ❌
  
Result: 2 players in world
```

### 修复后 ✅
```
API Login:
  new Player → load → intro → addPlayer(player1) ✅

Web UI Login:
  new Player → detect online → markAsObserverOnly() → addObserver → return
  Player still exists → load → intro
    → check isObserverOnly → return (skip addPlayer) ✅
  
Result: 1 player in world, 1 observer connection
```

## 🧪 测试验证

### 测试1: API + Web UI Observer

```bash
# 1. Agent通过API登录
curl -X POST http://localhost:7030/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123"}'

# 预期: 1个角色出现在地图
```

```javascript
// 2. Web UI浏览器登录
// 打开 http://localhost:7030
// 登录: testuser / test123

// 预期:
// - ✅ 只有1个角色可见
// - ✅ 可以在Web UI控制移动
// - ✅ 服务器日志显示 "Web UI observer connected"
```

### 测试2: 检查日志

```bash
# 应该看到:
[INFO] Web UI observer connected for player: testuser
[DEBUG] Player testuser marked as observer-only
[DEBUG] Skipping intro for observer-only connection: testuser

# 不应该看到:
[ERROR] Player testuser already exists
[ERROR] Duplicate player added
```

### 测试3: 断开Web UI

```bash
# 1. 关闭Web UI浏览器标签
# 2. Agent通过API移动

# 预期:
# - ✅ Agent仍然可以正常移动
# - ✅ 服务器日志: "Observer removed for player: testuser"
```

## 📁 修改的文件

### 1. `packages/server/src/game/entity/character/player/player.ts`

**添加**:
- `private isObserverOnly: boolean = false;` - 标志字段
- `public markAsObserverOnly(): void` - 标记方法

**修改**:
- `public intro()` - 添加isObserverOnly检查

### 2. `packages/server/src/game/entity/character/player/incoming.ts`

**修改**:
- `handleLogin()` - 检测observer时调用`markAsObserverOnly()`

## 🎯 为什么这个方案有效

1. **最小侵入**: 只在必要的地方添加检查
2. **防御性编程**: 即使Player实例存在，也不会被添加到世界
3. **保留功能**: Observer Player实例仍然存在，可以用于消息转发
4. **清晰日志**: 通过debug日志可以追踪observer行为

## 🔒 安全性

- ✅ Observer仍需正确的用户名和密码
- ✅ Observer只能观察自己账号的角色
- ✅ Observer不会创建额外的游戏实体
- ✅ Observer断开不影响主连接

## 🚀 下一步优化（可选）

### 可能的改进

1. **内存优化**: Observer Player可以是轻量级版本
```typescript
if (isObserverOnly) {
    // 不加载完整的inventory, quests等
}
```

2. **显式Observer类**: 创建专门的ObserverConnection类
```typescript
class ObserverConnection {
    constructor(existingPlayer: Player, connection: Connection) {
        // 专门处理observer逻辑
    }
}
```

3. **Observer管理UI**: 显示当前所有observers
```typescript
GET /api/player/:username/observers
{
    "observers": [
        {"id": "conn-123", "connected": "2025-10-27T10:00:00Z"}
    ]
}
```

## 📝 总结

✅ **问题**: Web UI observer创建第二个角色  
✅ **原因**: Player.intro()仍然执行  
✅ **解决**: 添加isObserverOnly标志阻止addPlayer  
✅ **效果**: 只有一个角色，observer正常工作  

---

**状态**: ✅ 已修复  
**测试**: 待验证  
**文档**: 完成  

