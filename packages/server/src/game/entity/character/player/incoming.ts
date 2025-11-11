import Commands from '../../../../controllers/commands';

import sanitizer from 'sanitizer';
import config from '@kaetram/common/config';
import log from '@kaetram/common/util/log';
import Utils from '@kaetram/common/util/utils';
import Filter from '@kaetram/common/util/filter';
import Creator from '@kaetram/common/database/mongodb/creator';
import { Spawn, Friends, Handshake, Movement } from '@kaetram/common/network/impl';
import { Modules, Opcodes, Packets } from '@kaetram/common/network';

import type MongoDB from '@kaetram/common/database/mongodb/mongodb';
import type Entities from '../../../../controllers/entities';
import type World from '../../../world';
import type Connection from '../../../../network/connection';
import type {
    AbilityPacket,
    ContainerPacket,
    EquipmentPacket,
    LoginPacket,
    MovementPacket,
    ReadyPacket,
    StorePacket,
    WarpPacket,
    FriendsPacket,
    TradePacket,
    HandshakePacket,
    EnchantPacket,
    GuildPacket,
    CraftingPacket
} from '@kaetram/common/types/messages/incoming';
import type Character from '../character';
import type Player from './player';
import type Entity from '../../entity';
import type NPC from '../../npc/npc';
import type Chest from '../../objects/chest';

export default class Incoming {
    private world: World;
    private connection: Connection;
    private entities: Entities;
    private database: MongoDB;
    private commands: Commands;

    public constructor(private player: Player) {
        this.connection = player.connection;
        this.world = player.world;
        this.entities = this.world.entities;
        this.database = player.database;
        this.commands = new Commands(player);

        this.connection.onMessage(([packet, message]) => {
            if (!Utils.validPacket(packet)) {
                log.error(`Non-existent packet received: ${packet} data: `);
                log.error(message);

                return;
            }

            player.connection.refreshTimeout();

            // Prevent server from crashing due to a packet malfunction.
            try {
                switch (packet) {
                    case Packets.Handshake: {
                        return this.handleHandshake(message);
                    }
                    case Packets.Login: {
                        return this.handleLogin(message);
                    }
                    case Packets.Ready: {
                        return this.handleReady(message);
                    }
                    case Packets.List: {
                        return this.player.updateEntityList();
                    }
                    case Packets.Who: {
                        return this.handleWho(message);
                    }
                    case Packets.Equipment: {
                        return this.handleEquipment(message);
                    }
                    case Packets.Movement: {
                        return this.handleMovement(message);
                    }
                    case Packets.Target: {
                        return this.handleTarget(message);
                    }
                    case Packets.Network: {
                        return this.handleNetwork(message);
                    }
                    case Packets.Chat: {
                        return this.handleChat(message);
                    }
                    case Packets.Command: {
                        return this.handleCommand(message);
                    }
                    case Packets.Container: {
                        return this.handleContainer(message);
                    }
                    case Packets.Ability: {
                        return this.handleAbility(message);
                    }
                    case Packets.Respawn: {
                        return this.player.respawn();
                    }
                    case Packets.Trade: {
                        return this.handleTrade(message);
                    }
                    case Packets.Enchant: {
                        return this.handleEnchant(message);
                    }
                    case Packets.Guild: {
                        return this.handleGuild(message);
                    }
                    case Packets.Warp: {
                        return this.handleWarp(message);
                    }
                    case Packets.Store: {
                        return this.handleStore(message);
                    }
                    case Packets.Friends: {
                        return this.handleFriends(message);
                    }
                    case Packets.Focus: {
                        return this.player.updateEntityPositions();
                    }
                    case Packets.Examine: {
                        return this.handleExamine(message);
                    }
                    case Packets.Crafting: {
                        return this.handleCrafting(message);
                    }
                }
            } catch (error) {
                log.error(error);
            }
        });
    }

    /**
     * The handshake is responsible for verifying the integrity of the client initially. We ensure
     * that the client is on the right version and reject it if it is not.
     * @param data Contains the version of the client.
     */

    private handleHandshake(data: HandshakePacket): void {
        log.debug(`Received handshake from client with version: ${data.gVer}, expected: ${config.gver}`);
        
        if (data.gVer !== config.gver) return this.connection.reject('updated');
        
        log.debug(`Sending handshake response to client with instance: ${this.player.instance}, serverId: ${config.serverId}`);
        
        // Send handshake response back to client with server info
        // In social mode, tell client to use social_map.json for tilesets/animations
        this.player.send(new Handshake({
            instance: this.player.instance,
            serverId: config.serverId,
            mapFile: config.socialMode ? 'social_map' : 'map'
        }));
    }

    /**
     * Handles the login process for Kaetram.
     * @param data The packet data for the login. Generally contains
     * username, password, (email if registering). If it's a guest login,
     * then we proceed with no username/password and no database saving.
     */

    private handleLogin(data: LoginPacket): void {
        let { opcode, username, password, email, channel } = data;

        if (username) {
            // Format username by making it all lower case, shorter than 32 characters, and no spaces.
            this.player.username = Filter.clean(username.toLowerCase().slice(0, 32).trim());

            if (password) this.player.password = password.slice(0, 32);
            if (email) this.player.email = email;
            if (channel) {
                this.player.channel = channel.slice(0, 32).trim();
                log.info(`Player ${this.player.username} set channel to: ${this.player.channel}`);
            }

            // Reject connection if player is already logged in.
            // In social mode with monitoring, allow Web UI to observe API-controlled players
            if (this.world.isOnline(this.player.username)) {
                log.debug(`Player ${this.player.username} is already online. SocialMode: ${config.socialMode}, AllowMonitor: ${config.socialModeAllowMonitor}`);
                
                // If monitoring is enabled in social mode, treat this as an observer connection
                if (config.socialMode && config.socialModeAllowMonitor) {
                    let existingPlayer = this.world.getPlayerByName(this.player.username);
                    if (existingPlayer) {
                        log.info(`✅ Setting up observer connection for: ${this.player.username}`);
                        
                        // Add this connection as an observer to the existing player
                        existingPlayer.addObserver(this.connection);
                        
                        // Track last movement request to prevent ping-pong loops
                        let lastMoveRequest = { x: -1, y: -1, time: 0 };
                        
                        // Set up message handling for observer (allows Web UI control)
                        this.connection.onMessage(([packet, message, ...rest]) => {
                            if (!Utils.validPacket(packet)) {
                                log.error(`Non-existent packet received from observer: ${packet}`);
                                return;
                            }
                            
                            existingPlayer.connection.refreshTimeout();
                            
                            // Forward input packets to the existing player
                            try {
                                switch (packet) {
                                    case Packets.Movement: {
                                        let msg = message as any;
                                        
                                        // ⚠️ CRITICAL: Only forward Movement.Request (opcode=0) from observers
                                        // Started/Step/Stop are server broadcasts that should NOT be echoed back
                                        if (msg.opcode !== 0) { // Not Movement.Request
                                            // Silently ignore server broadcast echoes (Started=1, Step=2, Stop=3)
                                            return;
                                        }
                                        
                                        // Anti-ping-pong: Ignore Movement.Request if it's rapidly alternating between adjacent tiles
                                        let now = Date.now();
                                        let dx = Math.abs(msg.requestX - lastMoveRequest.x);
                                        let dy = Math.abs(msg.requestY - lastMoveRequest.y);
                                        let timeDiff = now - lastMoveRequest.time;
                                        
                                        // If requesting to move back to previous position within 2 seconds, ignore it
                                        if (dx <= 1 && dy <= 1 && dx + dy > 0 && timeDiff < 2000) {
                                            log.info(`🚫 Ignoring ping-pong movement: (${msg.requestX},${msg.requestY}) ↔ (${lastMoveRequest.x},${lastMoveRequest.y}) within ${timeDiff}ms`);
                                            return;
                                        }
                                        
                                        lastMoveRequest = { x: msg.requestX, y: msg.requestY, time: now };
                                        
                                        log.info(`📍 Observer Movement.Request: ${existingPlayer.username} to (${msg.requestX},${msg.requestY}) from (${existingPlayer.x},${existingPlayer.y})`);
                                        
                                        // For observers (Web UI), use server-side movement to ensure position sync with Python API
                                        // Update server-side position (like NPC movement)
                                        existingPlayer.move(msg.requestX, msg.requestY);
                                        
                                        // Send Movement packet to all observers and nearby players for smooth animation
                                        // The client will interpolate movement from current position to target position
                                        existingPlayer.sendToRegions(new Movement(Opcodes.Movement.Move, {
                                            instance: existingPlayer.instance,
                                            x: msg.requestX,
                                            y: msg.requestY,
                                            movementSpeed: existingPlayer.movementSpeed
                                        }));
                                        
                                        log.info(`✅ Observer moved ${existingPlayer.username} to (${existingPlayer.x},${existingPlayer.y})`);
                                        return;
                                    }
                                    case Packets.Target: {
                                        return existingPlayer.incoming['handleTarget'](message);
                                    }
                                    case Packets.Network: {
                                        return existingPlayer.incoming['handleNetwork'](message);
                                    }
                                    case Packets.Container: {
                                        return existingPlayer.incoming['handleContainer'](message);
                                    }
                                    case Packets.Command: {
                                        return existingPlayer.incoming['handleCommand'](message);
                                    }
                                    case Packets.Chat: {
                                        return existingPlayer.incoming['handleChat'](message);
                                    }
                                    case Packets.List: {
                                        return existingPlayer.updateEntityList();
                                    }
                                    case Packets.Who: {
                                        return existingPlayer.incoming['handleWho'](message);
                                    }
                                    case Packets.Equipment: {
                                        return existingPlayer.incoming['handleEquipment'](message);
                                    }
                                    case Packets.Ability: {
                                        return existingPlayer.incoming['handleAbility'](message);
                                    }
                                    case Packets.Respawn: {
                                        return existingPlayer.respawn();
                                    }
                                    case Packets.Trade: {
                                        return existingPlayer.incoming['handleTrade'](message);
                                    }
                                    case Packets.Guild: {
                                        return existingPlayer.incoming['handleGuild'](message);
                                    }
                                    case Packets.Warp: {
                                        return existingPlayer.incoming['handleWarp'](message);
                                    }
                                    case Packets.Store: {
                                        return existingPlayer.incoming['handleStore'](message);
                                    }
                                    case Packets.Friends: {
                                        return existingPlayer.incoming['handleFriends'](message);
                                    }
                                    case Packets.Focus: {
                                        return existingPlayer.updateEntityPositions();
                                    }
                                    case Packets.Examine: {
                                        return existingPlayer.incoming['handleExamine'](message);
                                    }
                                    case Packets.Crafting: {
                                        return existingPlayer.incoming['handleCrafting'](message);
                                    }
                                    case Packets.Enchant: {
                                        return existingPlayer.incoming['handleEnchant'](message);
                                    }
                        case Packets.Ready: {
                            // Observer needs full initialization like handleReady
                            log.info(`📦 Observer received Ready packet for player: ${existingPlayer.username}`);
                            
                            try {
                                // Send full game state to observer (force=true to resend region data)
                                existingPlayer.updateRegion(true);
                                existingPlayer.updateEntities();
                                existingPlayer.updateEntityList();
                                            
                                            // Send all initialization data that would normally be sent via onLoaded callbacks
                                            // Since the player is already loaded, these callbacks won't be triggered for observers
                                            log.info(`📤 Sending initialization data to observer for: ${existingPlayer.username}`);
                                            
                                            // Send Skills data
                                            if (existingPlayer.skills) {
                                                existingPlayer.handler['handleSkills']();
                                            }
                                            
                                            // Send Abilities data
                                            if (existingPlayer.abilities) {
                                                existingPlayer.handler['handleAbilities']();
                                            }
                                            
                                            // Send Equipment data
                                            if (existingPlayer.equipment) {
                                                existingPlayer.handler['handleEquipment']();
                                            }
                                            
                                            // Send Inventory data
                                            if (existingPlayer.inventory) {
                                                existingPlayer.handler['handleInventory']();
                                            }
                                            
                                            // Send Quests data
                                            if (existingPlayer.quests) {
                                                existingPlayer.handler['handleQuests']();
                                            }
                                            
                                            // Send Achievements data
                                            if (existingPlayer.achievements) {
                                                existingPlayer.handler['handleAchievements']();
                                            }
                                            
                                            log.info(`✅ Observer Ready processing complete for: ${existingPlayer.username}`);
                                        } catch (error) {
                                            log.error(`❌ Error processing observer Ready: ${error}`);
                                        }
                                        
                                        return;
                                    }
                                    // Read-only packets that don't need handling
                                    case Packets.Effect:
                                    case Packets.Handshake:
                                    case Packets.Login:
                                        // Silently ignore these for observers
                                        return;
                                    default: {
                                        log.debug(`Observer sent unhandled packet: ${packet}`);
                                    }
                                }
                            } catch (error) {
                                log.error(`Error handling observer packet: ${error}`);
                            }
                        });
                        
                        // Clean up observer when connection closes
                        this.connection.onClose(() => {
                            existingPlayer.removeObserver(this.connection);
                        });
                        
                        log.info(`✅ Web UI observer fully connected for player: ${this.player.username}`);
                        log.info(`⏳ Waiting for client Ready packet...`);
                        return; // Complete observer setup, don't proceed with login
                    } else {
                        log.error(`❌ existingPlayer is null for ${this.player.username}`);
                    }
                } else {
                    log.debug(`❌ Cannot setup observer: socialMode=${config.socialMode}, allowMonitor=${config.socialModeAllowMonitor}`);
                }
                log.info(`Rejecting login for ${this.player.username} - already logged in`);
                return this.connection.reject('loggedin');
            }

            // Proceed directly to login with default player data if skip database is present.
            if (config.skipDatabase) {
                this.player.load(Creator.serializePlayer(this.player));
                return;
            }
        }

        // Handle login for each particular case.
        switch (opcode) {
            case Opcodes.Login.Login: {
                // Check the player in other servers first (defaults to false if hub is not present).
                return this.world.api.isPlayerOnline(this.player.username, (online: boolean) => {
                    if (online) return this.connection.reject('loggedin');

                    this.database.login(this.player);
                });
            }

            case Opcodes.Login.Register: {
                return this.database.register(this.player);
            }

            case Opcodes.Login.Guest: {
                // Authenticated so that we send the logout packet to the hub.
                this.player.authenticated = true;
                this.player.isGuest = true; // Makes sure player doesn't get saved to database.
                this.player.username = `guest${Utils.counter++}`; // Generate a random guest username.

                this.player.load(Creator.serializePlayer(this.player));
                return;
            }
        }
    }

    private handleReady(data: ReadyPacket): void {
        let { regionsLoaded, userAgent } = data;

        this.player.handleUserAgent(userAgent, regionsLoaded);

        this.player.handler.startUpdateInterval();

        this.player.ready = true;

        this.player.updateRegion();
        this.player.updateEntities();
        this.player.updateEntityList();

        this.world.syncFriendsList(this.player.username);
        this.world.syncGuildMembers(this.player.guild, this.player.username);

        this.world.discord.sendMessage(this.player.username, 'has logged in!');

        // Synchronize friends list cross-server by sending inactive friends to hub.
        this.player.friends.sync();

        if (this.player.isDead()) this.player.deathCallback?.();

        this.player.welcome();

        // A secondary check after the player has fully loaded in.
        this.world.api.isPlayerOnline(this.player.username, (online: boolean) => {
            if (online) this.player.connection.reject('loggedin');
        });
    }

    /**
     * Packet contains list of entity instances that the client is requesting to spawn. The client compares
     * all the entities in the region to the entities it has spawned and the difference is sent here. The difference
     * represents the entities that the client doesn't have spawned.
     * @param message Contains a list of entity instances
     */

    private handleWho(message: string[]): void {
        for (let instance of message) {
            let entity = this.entities.get(instance);

            if (!entity || entity.dead) continue;

            /* We handle player-specific entity statuses here. */
            this.player.send(
                new Spawn(entity, entity.hasDisplayInfo(this.player) ? this.player : undefined)
            );
        }
    }

    /**
     * Handles equipment packet. Generally involved in unequipping.
     * @param data Contains information about which slot to unequip.
     */

    private handleEquipment(data: EquipmentPacket): void {
        switch (data.opcode) {
            case Opcodes.Equipment.Unequip: {
                return this.player.equipment.unequip(data.type!);
            }

            case Opcodes.Equipment.Style: {
                return this.player.equipment.updateAttackStyle(data.style!);
            }
        }
    }

    /**
     * Handles movement packets for the player. We use these to verify the player's
     * position and implement a couple anti-cheating measures.
     * @param data Contains the type of movement we are performing and information about it.
     */

    private handleMovement(data: MovementPacket): void {
        let {
                opcode,
                requestX,
                requestY,
                playerX,
                playerY,
                movementSpeed,
                targetInstance,
                orientation,
                following,
                timestamp
            } = data,
            entity: Entity;

        if (this.player.isDead()) return;

        switch (opcode) {
            case Opcodes.Movement.Request: {
                // requestX/requestY are the target coordinates, playerX/playerY are current position
                log.info(`🚶 Movement.Request: ${this.player.username} from (${this.player.x},${this.player.y}) to (${requestX},${requestY}) [playerPos: ${playerX},${playerY}]`);
                return this.player.handleMovementRequest(
                    requestX!,
                    requestY!,
                    targetInstance!,
                    following!
                );
            }

            case Opcodes.Movement.Started: {
                log.info(`🏃 Movement.Started: ${this.player.username} at (${playerX},${playerY}), speed=${movementSpeed}`);
                return this.player.handleMovementStarted(
                    playerX!,
                    playerY!,
                    movementSpeed!,
                    targetInstance!
                );
            }

            case Opcodes.Movement.Step: {
                let oldX = this.player.x, oldY = this.player.y;
                this.player.handleMovementStep(playerX!, playerY!, timestamp);
                log.info(`👣 Movement.Step: ${this.player.username} (${oldX},${oldY}) → (${this.player.x},${this.player.y}) [client sent (${playerX},${playerY})]`);
                return;
            }

            case Opcodes.Movement.Stop: {
                let oldX = this.player.x, oldY = this.player.y;
                this.player.handleMovementStop(
                    playerX!,
                    playerY!,
                    targetInstance!,
                    orientation!
                );
                log.info(`🛑 Movement.Stop: ${this.player.username} (${oldX},${oldY}) → (${this.player.x},${this.player.y}) [client sent (${playerX},${playerY})]`);
                return;
            }

            case Opcodes.Movement.Entity: {
                entity = this.entities.get(targetInstance!) as Character;

                // Skip players or invalid entities.
                if (!entity || entity.isPlayer()) return;

                return entity.setPosition(requestX!, requestY!);
            }
        }
    }

    private handleTarget(message: [Opcodes.Target, string]): void {
        let [opcode, instance] = message;

        switch (opcode) {
            case Opcodes.Target.Talk: {
                let entity = this.entities.get(instance);

                if (!entity || !this.player.isAdjacent(entity)) return;

                this.player.cheatScore = 0;

                if (entity.isChest()) {
                    let chest = entity as unknown as Chest;
                    chest.openChest(this.player);
                    return;
                }

                if (entity.dead) return;

                this.player.npcTalkCallback?.(entity as NPC);

                break;
            }

            case Opcodes.Target.Attack: {
                return this.player.handleTargetAttack(instance);
            }

            case Opcodes.Target.Object: {
                return this.player.handleObjectInteraction(instance);
            }
        }
    }

    private handleNetwork(message: [Opcodes.Network]): void {
        let [opcode] = message;

        switch (opcode) {
            case Opcodes.Network.Pong: {
                let time = Date.now();

                this.player.notify(`Latency of ${time - this.player.pingTime}ms`, 'red');

                break;
            }
        }
    }

    /**
     * Receives a raw chat input from the client, sanitizes it, and parses
     * whether it is just a message or a command.
     * @param message Raw string input from the client.
     */

    private handleChat(message: [string]): void {
        // Message sanitization.
        let text = sanitizer.escape(sanitizer.sanitize(message[0]));

        if (!text || text.length === 0 || !/\S/.test(text)) return;

        // Handle commands if the prefix is / or ;
        if (text.startsWith('/') || text.startsWith(';')) return this.commands.parse(text);

        // Check for mute before filtering the message.
        if (this.player.isMuted()) return this.player.notify('You are currently muted.', 'crimson');

        this.player.chat(Filter.clean(text));
    }

    private handleCommand(message: [Opcodes.Command, Coordinate]): void {
        let [opcode, position] = message;

        if (this.player.rank !== Modules.Ranks.Admin) return;

        switch (opcode) {
            case Opcodes.Command.CtrlClick: {
                this.player.teleport(position.gridX, position.gridY, true);
                break;
            }
        }
    }

    /**
     * Handles data associated with containers. This can include removing
     * or selecting items in the container. Depending on the type, we route
     * to the appropriate action.
     * @param packet Packet data containing type of container and opcode information.
     */

    private handleContainer(packet: ContainerPacket): void {
        //log.debug(`Received container packet: ${packet.opcode} - ${packet.type}`);

        switch (packet.opcode) {
            case Opcodes.Container.Select: {
                // Ensure the packet has a valid index.
                if (isNaN(packet.fromIndex!) || packet.fromIndex === -1) return;

                return this.player.handleContainerSelect(
                    packet.type,
                    packet.fromContainer,
                    packet.fromIndex!,
                    packet.toContainer!,
                    packet.value
                );
            }

            case Opcodes.Container.Remove: {
                return this.player.handleContainerRemove(
                    packet.type,
                    packet.fromIndex!,
                    packet.value!
                );
            }

            case Opcodes.Container.Swap: {
                return this.player.handleContainerSwap(
                    packet.type,
                    packet.fromIndex!,
                    packet.value!
                );
            }
        }
    }

    /**
     * Handles incoming abilities actions from the client. Things such as using
     * an ability or moving one to a quick slot.
     * @param packet Contains infomration about which ability to use and where to move it.
     */

    private handleAbility(packet: AbilityPacket): void {
        switch (packet.opcode) {
            case Opcodes.Ability.Use: {
                return this.player.abilities.use(packet.key);
            }

            case Opcodes.Ability.QuickSlot: {
                return this.player.abilities.setQuickSlot(packet.key, packet.index!);
            }
        }
    }

    private handleTrade(packet: TradePacket): void {
        switch (packet.opcode) {
            case Opcodes.Trade.Request: {
                let oPlayer = this.entities.get(packet.instance!);

                if (!oPlayer?.isPlayer()) return;

                return this.player.trade.request(oPlayer);
            }

            case Opcodes.Trade.Accept: {
                return this.player.trade.accept();
            }

            case Opcodes.Trade.Close: {
                return this.player.trade.close();
            }

            case Opcodes.Trade.Add: {
                return this.player.trade.add(packet.index!, packet.count);
            }

            case Opcodes.Trade.Remove: {
                return this.player.trade.remove(packet.index!);
            }
        }
    }

    /**
     * Handles an incoming packet from the client regarding the enchantment table. Things like
     * selecting the item or confirming the selection are sent to the enchantment controller.
     * @param packet Contains the opcode and index of the item(s) selected.
     */

    private handleEnchant(packet: EnchantPacket): void {
        if (!this.player.canAccessContainer)
            return this.player.notify('You cannot do that right now.');

        switch (packet.opcode) {
            case Opcodes.Enchant.Select: {
                return this.world.enchanter.select(this.player, packet.index!);
            }

            case Opcodes.Enchant.Confirm: {
                return this.world.enchanter.enchant(this.player, packet.index!, packet.shardIndex!);
            }
        }
    }

    /**
     * Receives a packet regarding a guild action from the client. We respond accordingly.
     * @param packet Contains the opcode and information about the request.
     */

    private handleGuild(packet: GuildPacket): void {
        switch (packet.opcode) {
            case Opcodes.Guild.Create: {
                return this.world.guilds.create(
                    this.player,
                    packet.name!,
                    packet.colour!,
                    packet.outline!,
                    packet.crest!
                );
            }

            case Opcodes.Guild.Join: {
                return this.world.guilds.join(this.player, packet.identifier!);
            }

            case Opcodes.Guild.Leave: {
                return this.world.guilds.leave(this.player);
            }

            case Opcodes.Guild.List: {
                return this.world.guilds.get(this.player, packet.from!, packet.to!);
            }

            case Opcodes.Guild.Chat: {
                return this.world.guilds.chat(this.player, packet.message!);
            }
        }
    }

    /**
     * Receives a warp packet from the client containing the
     * id of the warp selected. The server then verifies
     * the request (whether the player can warp there or not
     * and if the requirements are fulfilled) and sends a teleport
     * packet later on.
     * @param data Contains information about the warp (such as id).
     */

    private handleWarp(data: WarpPacket): void {
        this.world.warps.warp(this.player, data.id);
    }

    /**
     * Receives store interaction packets from the client. This contains
     * the store key, the index of the item selected, and how much of the
     * item we are purchasing/sellling/selecting.
     * @param data Store packet data containing the store key, index, and amount.
     */

    private handleStore(data: StorePacket): void {
        // log.debug(`Received store packet: ${data.opcode}`);

        // Ignore invalid packets.
        if (data.index < 0) return;

        switch (data.opcode) {
            case Opcodes.Store.Buy: {
                return this.world.stores.purchase(this.player, data.key, data.index, data.count);
            }

            case Opcodes.Store.Sell: {
                return this.world.stores.sell(this.player, data.key, data.index, data.count);
            }

            case Opcodes.Store.Select: {
                return this.world.stores.select(this.player, data.key, data.index, data.count);
            }
        }
    }

    /**
     * Handles incoming packets from the client about the friends list. Contains
     * instructions such as adding or removing a friend from the list.
     * @param data Contains the opcode (type of action) and the username.
     */

    private handleFriends(data: FriendsPacket): void {
        switch (data.opcode) {
            case Opcodes.Friends.Add: {
                return this.player.friends.add(data.username);
            }

            case Opcodes.Friends.Remove: {
                return this.player.friends.remove(data.username);
            }
        }
    }

    /**
     * Handles the interaction with the examine button. Just displays
     * the description for the entity selected (generally a mob).
     * @param instance The instance of the entity.
     */

    private handleExamine(instance: string): void {
        let entity = this.entities.get(instance);

        if (!entity) return;

        if (!entity.isMob() && !entity.isItem()) return;

        this.player.statistics.addMobExamine(entity.key);

        if (!entity.description) return this.player.notify('I have no idea what that is.');

        this.player.notify(entity.getDescription());
    }

    /**
     * Handles incoming actions from the client regarding the crafting interface.
     * @param data Contains information about the kind of action.
     */

    private handleCrafting(data: CraftingPacket): void {
        // Ensure the player is not maliciously trying to craft something.
        if (this.player.activeCraftingInterface === -1)
            return this.player.notify(`You cannot do that right now.`);

        switch (data.opcode) {
            case Opcodes.Crafting.Select: {
                return this.world.crafting.select(this.player, data.key!);
            }

            case Opcodes.Crafting.Craft: {
                return this.world.crafting.craft(this.player, data.key!, data.count!);
            }
        }
    }
}
