# 客户端调试代码

## 添加调试日志

在 `packages/client/src/network/connection.ts` 文件中找到 `handleWelcome` 方法，修改为：

```typescript
private handleWelcome(data: PlayerData): void {
    console.log('🔵 [DEBUG] handleWelcome called');
    console.log('🔵 [DEBUG] Welcome data:', data);
    
    try {
        console.log('🔵 [DEBUG] Calling player.load()...');
        this.game.player.load(data);
        console.log('✅ [DEBUG] player.load() completed');
        
        console.log('🔵 [DEBUG] Calling game.start()...');
        this.game.start();
        console.log('✅ [DEBUG] game.start() completed');
        
        console.log('🔵 [DEBUG] Calling game.postLoad()...');
        this.game.postLoad();
        console.log('✅ [DEBUG] game.postLoad() completed - Ready packet sent');
    } catch (error) {
        console.error('🔴 [DEBUG] Error in handleWelcome:', error);
        throw error;
    }
}
```

## 添加Ready发送日志

在 `packages/client/src/game.ts` 文件中找到 `postLoad` 方法，修改为：

```typescript
public postLoad(): void {
    console.log('🔵 [DEBUG] postLoad() called');
    
    this.entities.addEntity(this.player);
    console.log('✅ [DEBUG] addEntity completed');

    this.player.setSprite(this.sprites.get(this.player.getSpriteName()));
    this.player.idle();
    console.log('✅ [DEBUG] setSprite completed');

    if (this.storage) {
        this.player.setOrientation(this.storage.data.player.orientation);
        this.camera.setZoom(this.storage.data.player.zoom);
        this.renderer.resize();
    }
    console.log('✅ [DEBUG] camera/storage completed');

    this.camera.centreOn(this.player);
    console.log('✅ [DEBUG] camera centreOn completed');

    this.player.handler = new Handler(this.player);
    console.log('✅ [DEBUG] handler created');

    this.renderer.updateAnimatedTiles();
    console.log('✅ [DEBUG] updateAnimatedTiles completed');

    console.log('🔵 [DEBUG] About to send Ready packet...');
    console.log('🔵 [DEBUG] Packet data:', {
        regionsLoaded: this.map.regionsLoaded,
        userAgent: agent
    });
    
    this.socket.send(Packets.Ready, {
        regionsLoaded: this.map.regionsLoaded,
        userAgent: agent
    });
    
    console.log('✅ [DEBUG] Ready packet sent!');

    if (this.storage.data.new) {
        this.storage.data.new = false;
        this.storage.save();
    }

    if (this.map.hasCachedDate()) this.app.fadeMenu();
    
    console.log('✅ [DEBUG] postLoad() completed');
}
```

## 重新编译客户端

```bash
cd /home/ubuntu/works/agentworld
yarn build:client
```

或者如果使用dev模式：
```bash
yarn dev:client
```

## 测试

刷新浏览器并登录，查看Console输出。

你会清楚地看到卡在哪一步！

