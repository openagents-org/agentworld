# Observer登录问题调试指南

## 🐛 问题: Web UI进不去

当Python API登录后，Web UI使用同一账号无法登录。

## 📋 调试步骤

### 步骤1: 确认配置

```bash
cd /home/ubuntu/works/agentworld
cat .env | grep SOCIAL
```

**预期输出**:
```
SOCIAL_MODE=true
SOCIAL_MODE_ALLOW_MONITOR=true
```

**如果没有**: 运行以下命令添加：
```bash
echo "" >> .env
echo "SOCIAL_MODE=true" >> .env
echo "SOCIAL_MODE_ALLOW_MONITOR=true" >> .env
```

### 步骤2: 重启服务器

```bash
# 停止现有服务器 (Ctrl+C)
# 重新启动
yarn dev:server
```

**预期看到**:
```
[INFO] ******************************************
[INFO] Map: 48x48 - divisions: 48
[INFO] Server is now listening on port: 7030
```

### 步骤3: Agent通过API登录

```bash
curl -X POST http://localhost:7030/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}'
```

**预期输出**:
```json
{
  "status": "success",
  "token": "..."
}
```

**服务器日志预期**:
```
[INFO] test has logged in!
```

### 步骤4: Web UI登录

1. 打开浏览器: `http://localhost:7030`
2. 输入账号: `test` / `test`
3. 点击登录

#### 预期服务器日志:
```
[INFO] Web UI observer connected for player: test
[DEBUG] Player test marked as observer-only
[DEBUG] Skipping intro for observer-only connection: test
[DEBUG] Observer fully initialized with map data for player: test
```

#### 预期浏览器表现:
- ✅ 成功进入游戏
- ✅ 看到一个角色
- ✅ 可以控制移动

## 🔍 常见问题

### 问题A: "Player is already logged in" 错误

**症状**: Web UI显示"already logged in"消息

**原因**: `SOCIAL_MODE_ALLOW_MONITOR` 未生效

**解决**:
1. 确认`.env`文件有该配置
2. 重启服务器（配置需要重启才能生效）
3. 清除浏览器缓存

### 问题B: 服务器无任何日志

**症状**: Web UI登录后，服务器没有任何"Observer connected"日志

**原因**: 
- WebSocket连接失败
- 客户端未发送Login包

**调试**:
```bash
# 1. 检查端口是否正确
netstat -an | grep 7030

# 2. 检查防火墙
sudo ufw status

# 3. 浏览器开发者工具 (F12)
# → Console标签
# → 查找错误消息
```

### 问题C: "Cannot read properties of undefined"

**症状**: 服务器报错 `Cannot read properties of undefined (reading 'addObserver')`

**原因**: `existingPlayer`为null

**调试**:
```javascript
// 在incoming.ts中添加调试:
let existingPlayer = this.world.getPlayerByName(this.player.username);
console.log('existingPlayer:', existingPlayer); // 添加这行
if (existingPlayer) {
    // ...
}
```

### 问题D: Web UI卡在加载中

**症状**: 浏览器显示loading，但一直不进入游戏

**原因**: 
- Observer没有收到Welcome包
- Observer没有收到Map数据

**调试 - 浏览器Console**:
```javascript
// F12 → Console
// 查找WebSocket消息
// 应该看到:
// Received: Welcome
// Received: Map
```

### 问题E: 看到两个角色

**症状**: 地图上有两个相同名字的角色

**原因**: `isObserverOnly`标志未生效，`intro()`仍然执行了

**解决**: 确认代码已更新：
```bash
grep -n "isObserverOnly" packages/server/src/game/entity/character/player/player.ts
# 应该看到:
# 189: private isObserverOnly: boolean = false;
# 398: if (this.isObserverOnly) {
```

## 🧪 手动测试脚本

创建测试文件 `test_observer.sh`:

```bash
#!/bin/bash

echo "🧪 Testing Observer Login..."

# 1. API Login
echo "1️⃣ API Login..."
RESPONSE=$(curl -s -X POST http://localhost:7030/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}')

echo "Response: $RESPONSE"

if echo "$RESPONSE" | grep -q "success"; then
    echo "✅ API login successful"
else
    echo "❌ API login failed"
    exit 1
fi

echo ""
echo "2️⃣ Now test Web UI:"
echo "   → Open http://localhost:7030 in browser"
echo "   → Login with: test / test"
echo "   → Should see one character and can control it"
echo ""
echo "3️⃣ Check server logs for:"
echo "   [INFO] Web UI observer connected for player: test"
echo "   [DEBUG] Observer fully initialized with map data"
```

## 🔧 完整配置检查

```bash
# 检查所有相关文件
echo "=== Config Check ==="
cat .env | grep SOCIAL
echo ""

echo "=== Code Check ==="
grep -n "socialModeAllowMonitor" packages/common/config.ts
grep -n "isObserverOnly" packages/server/src/game/entity/character/player/player.ts
grep -n "addObserver" packages/server/src/game/entity/character/player/incoming.ts
```

## 🎯 预期完整流程

```
1. Python API登录:
   POST /api/login → 创建Player1 → intro() → addPlayer()
   
2. Web UI登录:
   WebSocket连接 → Handshake → Login包
   → 检测isOnline(test) = true
   → config.socialMode && config.socialModeAllowMonitor = true
   → 创建Player2 (observer-only)
   → Player2.markAsObserverOnly()
   → Player1.addObserver(Player2.connection)
   → 发送Welcome包到observer
   → 发送Map包到observer
   → return (不执行Player2.intro())
   
3. 结果:
   → 世界中只有Player1
   → Player2连接作为observer
   → 两个连接都能控制Player1
```

## 📊 日志级别

如果需要更多调试信息，修改日志级别：

```typescript
// packages/common/util/log.ts
// 或在.env中
LOG_LEVEL=debug
```

## 🚨 紧急排查

如果以上都不行，检查：

```bash
# 1. TypeScript编译
yarn build

# 2. 检查编译错误
yarn tsc --noEmit

# 3. 清除缓存
rm -rf node_modules/.cache
yarn install

# 4. 检查git状态
git diff packages/server/src/game/entity/character/player/player.ts
git diff packages/server/src/game/entity/character/player/incoming.ts
```

## 💡 临时解决方案

如果observer功能暂时无法工作，可以：

1. **关闭monitoring**: 设置 `SOCIAL_MODE_ALLOW_MONITOR=false`
2. **使用单连接**: API或Web UI二选一
3. **使用不同账号**: API用account1，Web UI用account2

## ✅ 成功标志

Observer登录成功时，你应该看到：

**服务器日志**:
```
[INFO] test has logged in!
[INFO] Web UI observer connected for player: test
[DEBUG] Player test marked as observer-only
[DEBUG] Skipping intro for observer-only connection: test
[DEBUG] Observer fully initialized with map data for player: test
```

**浏览器**:
- 成功进入游戏画面
- 看到一个角色（不是两个）
- F12 Console无错误
- WebSocket连接状态: OPEN

**游戏内**:
- 可以通过Web UI移动角色
- 可以通过API移动角色
- 两边看到的是同一个角色

---

**如果还是无法解决，请提供**:
1. 服务器完整日志
2. 浏览器Console截图/日志
3. `.env` 文件内容
4. 具体的错误消息

