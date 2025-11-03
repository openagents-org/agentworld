# Social Mode - 完整实现与修复

## 🎯 最终方案

社交模式是一个**简化的单区域环境**，专为 agent 社交互动设计。

## 🐛 解决的所有问题

### 问题 1: 地图尺寸不匹配
```
❌ 100x100 无法被 48 整除
✅ 48x48 = 1个完整region
```

### 问题 2: 瓦片数据错误
```javascript
❌ data: [0, 0, 0, ...]  // !0 = true → 所有都是碰撞
✅ data: [1, 1, 1, ...]  // !1 = false → 正常地面
```

### 问题 3: 出生点未配置
```
❌ SPAWN_POINT: '405,27'  // 超出 48x48 范围
✅ SOCIAL_SPAWN_POINT: '24,24'  // 地图中心
```

### 问题 4: Region 系统复杂度
```typescript
❌ 检查 dynamic areas、周围 regions
✅ 社交模式跳过这些检查
```

### 问题 5: 访问不存在的 Regions
```typescript
❌ this.regions[surrounding] → undefined
✅ 添加存在性检查
```

## 📁 修改的所有文件

### 1. `packages/server/data/map/social_world.json`
```json
{
  "width": 48,
  "height": 48,
  "tileSize": 16,
  "data": [1, 1, 1, ...],  // 2304个瓦片，ID=1
  "collisions": [...]       // 188个边界瓦片
}
```

### 2. `packages/common/network/modules.ts`
```typescript
export const Constants = {
    MAP_DIVISION_SIZE: 48,
    SPAWN_POINT: '405,27',
    SOCIAL_SPAWN_POINT: '24,24',  // ← 新增
    TUTORIAL_SPAWN_POINT: '579,7',
    ...
};
```

### 3. `packages/server/src/game/entity/character/player/player.ts`
```typescript
import config from '@kaetram/common/config';  // ← 新增

public getSpawn(): Position {
    // 社交模式优先
    if (config.socialMode)
        return Utils.getPositionFromString(Modules.Constants.SOCIAL_SPAWN_POINT);
    
    if (!this.quests.isTutorialFinished())
        return Utils.getPositionFromString(Modules.Constants.TUTORIAL_SPAWN_POINT);
    
    if (this.inMinigame()) 
        return this.getMinigame()!.getRespawnPoint(this.team);
    
    return Utils.getPositionFromString(Modules.Constants.SPAWN_POINT);
}
```

### 4. `packages/server/src/game/map/map.ts`
```typescript
import config from '@kaetram/common/config';

public isColliding(x: number, y: number, player?: Player): boolean {
    if (this.isOutOfBounds(x, y)) return true;

    // 社交模式：跳过 region/dynamic area 检查
    if (!config.socialMode && player) {
        let region = this.regions.get(this.regions.getRegion(x, y));
        
        if (region && region.hasDynamicAreas()) {
            // ... dynamic area logic
        }
    }

    let index = this.coordToIndex(x, y);
    return !this.data[index] || this.isCollisionIndex(index);
}
```

### 5. `packages/server/src/game/map/regions.ts`
**多处添加安全检查**:

```typescript
// ✅ forEachSurroundingRegion
public forEachSurroundingRegion(region: number, callback: RegionCallback): void {
    for (let surrounding of this.getSurroundingRegions(region)) {
        if (this.regions[surrounding]) callback(surrounding);  // ← 检查
    }
}

// ✅ enter()
this.forEachSurroundingRegion(region, (surroundingRegion: number) => {
    let regionObj = this.regions[surroundingRegion];
    if (regionObj) {  // ← 检查
        regionObj.addEntity(entity);
        newRegions.push(surroundingRegion);
    }
});

if (entity.isPlayer() && this.regions[region])  // ← 检查
    this.regions[region].addPlayer(entity);

// ✅ getOldRegions()
this.forEachSurroundingRegion(entity.region, (surroundingRegion: number) => {
    let region = this.regions[surroundingRegion];
    if (!region || !region.hasEntity(entity)) return;  // ← 检查
    ...
});

// ✅ getRegionData()
this.forEachSurroundingRegion(region, (surroundingRegion: number) => {
    let regionObj = this.regions[surroundingRegion];
    if (!regionObj) return;  // ← 检查
    
    // 使用 regionObj 而不是 region (变量名混淆bug)
    if (regionObj.hasResources()) { ... }
    if (regionObj.hasDynamicAreas()) { ... }
});
```

## 🎯 设计原则

### 正常模式
```
复杂的 MMORPG 环境
├── 22x16 = 352 个 regions
├── 811,008 瓦片
├── Dynamic areas (动态地图)
├── NPCs/怪物/资源
└── 任务/成就系统
```

### 社交模式
```
简化的社交空间
├── 1x1 = 1 个 region
├── 2,304 瓦片 (↓99.7%)
├── 无 dynamic areas
├── 无 NPCs/怪物
└── 纯社交互动 ✨
```

## 🔍 技术细节

### 碰撞检测逻辑
```typescript
// 第 1 步: 边界检查
if (this.isOutOfBounds(x, y)) return true;

// 第 2 步: 社交模式跳过复杂检查
if (!config.socialMode && player) {
    // 只在正常模式检查 dynamic areas
}

// 第 3 步: 基础碰撞检测
let index = this.coordToIndex(x, y);
return !this.data[index] || this.isCollisionIndex(index);

// 解释:
// - !this.data[index]: 如果没有瓦片数据 → 碰撞
// - isCollisionIndex(): 如果在碰撞列表中 → 碰撞
```

### Region 边界计算问题
```
对于 48x48 (1个region) 的地图:
- region 0 的周围 regions: [-1, 1, -48, 48, 等]
- 但实际只有 regions[0] 存在
- regions[-1], regions[1], regions[48] 都是 undefined
- 解决: 添加 if (this.regions[surrounding]) 检查
```

### 地图布局
```
48x48 Social World (768x768 像素)

┌────────────────────────────────┐
│ ████████████████████████████ │ ← 边界碰撞
│ █                          █ │
│ █                          █ │
│ █                          █ │
│ █           ●              █ │ ← (24,24) 出生点
│ █                          █ │
│ █                          █ │
│ █                          █ │
│ ████████████████████████████ │
└────────────────────────────────┘
     46x46 可活动区域
     (736x736 像素)
```

## ✅ 测试验证

### 地图验证
```bash
node -e "
const map = require('./packages/server/data/map/social_world.json');
console.log('Width:', map.width, '- Height:', map.height);
console.log('Width % 48:', map.width % 48);
console.log('Height % 48:', map.height % 48);
console.log('Data length:', map.data.length);
console.log('Spawn tile value:', map.data[24 * 48 + 24]);
"
# 输出:
# Width: 48 - Height: 48
# Width % 48: 0
# Height % 48: 0
# Data length: 2304
# Spawn tile value: 1
```

### 服务器启动预期日志
```
✅ Loaded 0 entities!
✅ Loaded 0 static chests!
✅ Loaded 0 tree
✅ Loaded 0 rock
✅ Map: 48x48 - divisions: 48
✅ Server is now listening on port: 7030
✅ [No errors]
```

### 玩家登录预期
```
1. Agent 创建角色/登录
2. getSpawn() → 检测到 config.socialMode = true
3. 返回 (24, 24)
4. setPosition(24, 24)
5. verifyCollision(24, 24)
   - isColliding(24, 24, player)
   - !config.socialMode → 跳过 region 检查
   - data[1176] = 1 → !1 = false
   - collisions 中无 1176 → false
   - 返回 false (非碰撞)
6. ✅ 成功出生在 (24, 24)
```

## 📊 性能对比

| 指标 | 正常模式 | 社交模式 | 节省 |
|------|---------|---------|------|
| 瓦片数 | 811,008 | 2,304 | 99.7% |
| Region数 | 352 | 1 | 99.7% |
| 内存占用 | ~100% | ~0.3% | 99.7% |
| 碰撞检查 | 复杂 | 简单 | - |
| Region查找 | 是 | 跳过 | - |
| Dynamic areas | 是 | 跳过 | - |

## 🚀 下一步

### Phase 2: 基于距离的消息系统
- [ ] 计算 agent 之间的距离
- [ ] 实现距离阈值配置
- [ ] 消息传递机制
- [ ] 距离内可见性

### Phase 3: 元素互动
- [ ] 可互动对象系统
- [ ] 点击/触摸检测
- [ ] 状态同步

### Phase 4: Agent 样式切换
- [ ] 外观系统
- [ ] 样式数据结构
- [ ] 实时切换

## 📝 关键学习点

1. **简单就是好**: 社交模式不需要复杂的 MMORPG 系统
2. **防御性编程**: 添加存在性检查避免 undefined 错误
3. **条件跳过**: 用 `!config.socialMode` 跳过不需要的逻辑
4. **瓦片 ID 重要性**: 0 会被认为是空/碰撞，使用正整数
5. **变量命名**: 避免 region/regionObj 混淆

## 🎉 状态

✅ **所有问题已解决**
✅ **代码已优化**
✅ **安全检查已添加**
✅ **准备生产环境测试**

---

**最后更新**: 2025-10-27  
**状态**: 完成并准备测试  
**版本**: Phase 1 Complete

