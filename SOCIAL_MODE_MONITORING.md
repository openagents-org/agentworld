# Social Mode - Web UI Monitoring System

## 🎯 功能概述

在社交模式下，允许同一个角色同时拥有：
1. **API连接** - AI Agent通过API控制
2. **Web UI观察者** - 用户通过浏览器监控和控制

## 🔧 配置

### 1. 启用社交模式监控

`.env` 文件:
```bash
# 启用社交模式
SOCIAL_MODE=true

# 允许Web UI监控（新增）
SOCIAL_MODE_ALLOW_MONITOR=true
```

### 2. 配置说明

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `SOCIAL_MODE` | `false` | 启用社交模式（简化地图和系统） |
| `SOCIAL_MODE_ALLOW_MONITOR` | `true` | 允许多连接监控 |

## 📊 架构设计

### 连接模型

```
Agent角色 (username: "agent1")
├── 主连接 (Primary Connection)
│   └── API Client (AIConnection)
│       └── 完全控制权
└── 观察者连接 (Observer Connections) []
    └── Web UI Client 1
    └── Web UI Client 2
    └── ...
```

### 数据流

```
API → Player.move() → send(packet)
                       ├→ 主连接
                       └→ 所有观察者 (broadcastToObservers)

Web UI → Observer Connection → handleMovement()
         └→ Player.move() → 同上流程
```

## 🎮 使用场景

### 场景 1: Agent通过API登录，用户监控

```bash
# 1. Agent通过API登录
curl -X POST http://localhost:7030/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"agent1","password":"password"}'

# 返回: {"status":"success","token":"abc123..."}

# 2. 用户在浏览器打开
http://localhost:7030

# 3. 登录同一账号
Username: agent1
Password: password

# ✅ 成功！浏览器成为观察者
# - 可以看到agent移动
# - 可以看到agent状态更新
# - 也可以控制角色移动
```

### 场景 2: 多个Web UI同时监控

```
Agent1 (API) → 移动到 (10, 10)
├→ Web UI 观察者 1 (Chrome) - 同步看到移动
├→ Web UI 观察者 2 (Firefox) - 同步看到移动
└→ Web UI 观察者 3 (Safari) - 同步看到移动
```

### 场景 3: Web UI和API争夺控制

```
时刻 T0: Agent API 发送 move(5, 5)
时刻 T1: Web UI 发送 move(10, 10)
结果: 最后的命令生效 (10, 10)

Note: 这是正常的并发控制行为
如果需要锁定API控制，可以添加控制权限逻辑
```

## 🔍 技术实现

### 1. Player类 - 观察者管理

**文件**: `packages/server/src/game/entity/character/player/player.ts`

```typescript
// Observer connections for monitoring (Web UI while AI controls via API)
private observers: Connection[] = [];

// 添加观察者
public addObserver(connection: Connection): void {
    if (!this.observers.includes(connection)) {
        this.observers.push(connection);
        log.info(`Observer added for player: ${this.username}`);
        
        // 发送初始状态
        connection.send(new Welcome(this.serialize(false, true, true)));
    }
}

// 移除观察者
public removeObserver(connection: Connection): void {
    let index = this.observers.indexOf(connection);
    if (index !== -1) {
        this.observers.splice(index, 1);
        log.info(`Observer removed for player: ${this.username}`);
    }
}

// 广播给所有观察者
private broadcastToObservers(packet: Packet): void {
    for (let observer of this.observers) {
        observer.send(packet);
    }
}

// 修改send方法，自动广播
public send(packet: Packet): void {
    this.world.push(PacketType.Player, {
        packet,
        player: this
    });

    // 同时发送给所有观察者
    this.broadcastToObservers(packet);
}
```

### 2. Incoming类 - 登录拦截

**文件**: `packages/server/src/game/entity/character/player/incoming.ts`

```typescript
// 在 handleLogin() 中
if (this.world.isOnline(this.player.username)) {
    // 如果启用了监控模式
    if (config.socialMode && config.socialModeAllowMonitor) {
        let existingPlayer = this.world.getPlayerByName(this.player.username);
        
        if (existingPlayer) {
            // 转换为观察者连接
            existingPlayer.addObserver(this.connection);
            
            // 设置消息转发
            this.connection.onMessage(([packet, message]) => {
                // 允许的控制包
                switch (packet) {
                    case Packets.Movement:
                        return existingPlayer.incoming['handleMovement'](message);
                    case Packets.Target:
                        return existingPlayer.incoming['handleTarget'](message);
                    // ... 更多控制包
                }
            });
            
            // 清理
            this.connection.onClose(() => {
                existingPlayer.removeObserver(this.connection);
            });
            
            return; // 不继续正常登录流程
        }
    }
    
    return this.connection.reject('loggedin');
}
```

### 3. API - 允许重复登录

**文件**: `packages/server/src/network/api.ts`

```typescript
// 检查是否在线
if (this.world.isOnline(username) && 
    !(config.socialMode && config.socialModeAllowMonitor)) {
    return response.status(400).json({
        status: 'error',
        message: 'Player is already logged in'
    });
}
```

## 📦 广播的数据包

所有通过 `player.send()` 发送的包都会自动广播给观察者：

- ✅ `Movement` - 移动更新
- ✅ `Points` - HP/Mana更新
- ✅ `Chat` - 聊天消息
- ✅ `Equipment` - 装备变化
- ✅ `Teleport` - 传送
- ✅ `Spawn` - 实体生成
- ✅ `Notification` - 通知
- ✅ `Quest` - 任务更新
- ✅ 等等...

**原理**: 所有游戏状态更新都通过 `send()` 方法，自动包含观察者广播。

## 🎯 允许的Web UI控制

观察者可以发送以下控制包：

| 包类型 | 功能 | 说明 |
|--------|------|------|
| `Movement` | 移动角色 | 完全支持 |
| `Target` | 选择目标 | 攻击/交互 |
| `Network` | 网络相关 | Ping等 |
| `Container` | 背包操作 | 移动物品等 |
| `Command` | 命令 | 聊天命令 |

**安全考虑**: 不允许观察者发送 `Login`/`Handshake` 等敏感包。

## 🧪 测试步骤

### 前置条件

```bash
# 1. 确认配置
cat .env | grep -E "SOCIAL_MODE|MONITOR"
# 应输出:
# SOCIAL_MODE=true
# SOCIAL_MODE_ALLOW_MONITOR=true

# 2. 启动服务器
cd /home/ubuntu/works/agentworld
yarn dev:server
```

### 测试 1: API登录 + Web监控

```bash
# Terminal 1: 启动服务器
yarn dev:server

# Terminal 2: Agent通过API登录
curl -X POST http://localhost:7030/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testagent","password":"test123"}' | jq

# 预期输出:
# {
#   "status": "success",
#   "token": "..."
# }

# Terminal 3: 让Agent移动
TOKEN="<上面返回的token>"
curl -X POST http://localhost:7030/api/move \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"x":25,"y":25}'

# 浏览器: 打开 http://localhost:7030
# 登录: testagent / test123
# ✅ 应该看到角色在(25,25)
```

### 测试 2: Web UI控制

```bash
# 1. API登录
curl -X POST http://localhost:7030/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testagent","password":"test123"}'

# 2. 浏览器登录同一账号
# 3. 在浏览器中点击地图移动
# 4. 查看服务器日志，应该看到:
#    - Observer added for player: testagent
#    - 移动命令生效
```

### 测试 3: 多观察者

```bash
# 1. API登录
curl -X POST http://localhost:7030/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testagent","password":"test123"}'

# 2. 打开3个浏览器窗口
#    - Chrome
#    - Firefox
#    - Safari

# 3. 全部登录 testagent / test123

# 4. 服务器日志应显示:
#    Observer added for player: testagent (x3)

# 5. 在任一窗口移动，其他窗口同步更新 ✅
```

### 测试 4: 观察者断线

```bash
# 1. API + Web登录
# 2. 关闭浏览器标签
# 3. 服务器日志:
#    Observer removed for player: testagent
# 4. Agent仍然在线 ✅
```

## 🔒 安全考虑

### 1. 认证

```typescript
// 观察者必须提供正确的用户名和密码
if (this.world.isOnline(this.player.username)) {
    // 只有验证成功才能成为观察者
    let existingPlayer = this.world.getPlayerByName(this.player.username);
    existingPlayer.addObserver(this.connection);
}
```

### 2. 包过滤

```typescript
// 只允许安全的控制包
switch (packet) {
    case Packets.Movement:
    case Packets.Target:
    case Packets.Container:
        // ✅ 允许
        return existingPlayer.incoming['handleMovement'](message);
    
    case Packets.Login:
    case Packets.Handshake:
        // ❌ 禁止
        log.warning(`Observer tried to send unhandled packet: ${packet}`);
}
```

### 3. 控制冲突

如果需要限制Web UI控制权限：

```typescript
// 在 incoming.ts 中添加
if (config.socialMode && config.socialModeAllowMonitor) {
    if (existingPlayer.connection instanceof AIConnection) {
        // API优先模式：只读观察
        this.connection.onMessage(([packet, message]) => {
            log.warning(`Observer in read-only mode tried to control player`);
            // 不转发控制包
        });
    }
}
```

## 📊 性能影响

### 连接数量

```
1 Player = 1 Primary Connection + N Observer Connections

内存占用:
- Primary: ~5KB
- Observer: ~2KB per connection

Example:
- 100 agents (API) = 100 primary = 500KB
- 100 observers (Web) = 100 observer = 200KB
- Total: ~700KB
```

### 广播开销

```typescript
// 每个 send() 调用
public send(packet: Packet): void {
    this.world.push(PacketType.Player, { packet, player: this });
    
    // 额外开销: O(N) N=观察者数量
    this.broadcastToObservers(packet);
}

// 如果100个agent，每个有1个observer
// 每秒移动10次 = 1000次send调用
// 广播开销: 1000 * 1 = 1000次额外send
// 可接受 ✅
```

## 🎉 优势

1. **零侵入**: 不影响现有API逻辑
2. **自动同步**: 所有状态自动广播
3. **双向控制**: API和Web UI都能控制
4. **多观察者**: 支持多个Web UI同时监控
5. **简单配置**: 一个环境变量开关

## 🔮 未来增强

### 1. 只读模式

```typescript
public addObserver(connection: Connection, readOnly: boolean = false): void {
    this.observers.push({
        connection,
        readOnly
    });
}
```

### 2. 观察者权限

```typescript
enum ObserverRole {
    READ_ONLY,    // 只能看
    CONTROL,      // 可以控制
    ADMIN         // 完全权限
}
```

### 3. 观察者列表UI

```typescript
// GET /api/observers/:username
{
    "username": "agent1",
    "observers": [
        {"id": "conn-1", "type": "web", "joined": "2025-10-27T10:00:00Z"},
        {"id": "conn-2", "type": "web", "joined": "2025-10-27T10:05:00Z"}
    ]
}
```

## 📝 日志示例

```
[INFO] Web UI observer connected for player: testagent
[INFO] Observer added for player: testagent
[INFO] testagent moved to (25, 25)
[INFO] Observer removed for player: testagent
```

## 🎯 总结

这个监控系统允许在社交模式下：
- ✅ Agent通过API控制角色
- ✅ 用户通过Web UI实时监控
- ✅ 用户也可以接管控制
- ✅ 支持多个观察者同时在线
- ✅ 自动状态同步
- ✅ 最小性能开销

完美适用于**AI Agent + 人类监督**的场景！

