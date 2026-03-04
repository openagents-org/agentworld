import config from '@kaetram/common/config';
import log from '@kaetram/common/util/log';
import Utils from '@kaetram/common/util/utils';
import axios from 'axios';
import express from 'express';
import * as Sentry from '@sentry/node';
import * as Tracing from '@sentry/tracing';
import Filter from '@kaetram/common/util/filter';
import { Modules } from '@kaetram/common/network';
import CraftingData from '../../data/crafting';
import Items from '../../data/items.json';
import Formulas from '../info/formulas';

import type { Integration } from '@sentry/types';
import type { Router, Express, Request, Response } from 'express';
import type World from '../game/world';
import type Player from '../game/entity/character/player/player';
import type Entity from '../game/entity/entity';
import Character from '../game/entity/character/character';
import Item from '../game/entity/objects/item';
import type { EquipmentData, SerializedEquipment } from '@kaetram/common/network/impl/equipment';
import { SimulationEngine, validateState, validateAction } from './simulation';
import type { SimulationState, SimulationAction } from './simulation';

/**
 * API will have a variety of uses. Including communication
 * between multiple worlds (planned for the future).
 *
 * `accessToken` - A randomly generated token that can be used
 * to verify the validity between the client and the server.
 * This is a rudimentary security method, but is enough considering
 * the simplicity of the current API.
 */

export default class API {
    private hubConnected = false;
    private aiAgents: { [token: string]: Player } = {}; // Store AI agent sessions

    public constructor(private world: World) {
        let apiEnabled = config.apiEnabled || config.hubEnabled,
            app: Express | undefined,
            router: Router | undefined;

        // API must be initialized if the hub is enabled.
        if (apiEnabled) {
            app = express();

            if (config.sentryDsn)
                app.use(Sentry.Handlers.requestHandler())
                    .use(Sentry.Handlers.tracingHandler())
                    .use(Sentry.Handlers.errorHandler());

            app.use(express.urlencoded({ extended: true })).use(express.json());

            router = express.Router();

            this.handleRouter(router);

            app.use('/', router).listen(config.apiPort, () => {
                log.notice(`${config.name} API has successfully initialized.`);
            });
        }

        if (!config.sentryDsn) return;

        let integrations: Integration[] = [new Sentry.Integrations.Http({ tracing: true })];

        if (app && router) integrations.push(new Tracing.Integrations.Express({ app, router }));

        Sentry.init({
            dsn: config.sentryDsn,
            integrations,
            tracesSampleRate: 1
        });
    }

    /**
     * Default routing for the server API. We just display some basic infomration
     * about the server, such as the name, port, game version, and the amount of
     * players currently online.
     * @param router Router for endpoints.
     */

    private handleRouter(router: express.Router): void {
        router.get('/', (_request, response) => {
            response.json({
                name: config.name,
                port: config.port, // Sends the server port.
                gameVersion: config.gver,
                maxPlayers: config.maxPlayers,
                playerCount: this.world.getPopulation()
            });
        });

        // Public world status endpoint (no auth required, CORS enabled)
        router.get('/ai/world-status', (_request, response) => {
            response.header('Access-Control-Allow-Origin', '*');
            response.header('Access-Control-Allow-Methods', 'GET');
            try {
                let players: {
                    name: string;
                    x: number;
                    y: number;
                    level: number;
                    hitPoints: number;
                    maxHitPoints: number;
                    combat: boolean;
                    moving: boolean;
                    isAI: boolean;
                }[] = [];

                this.world.entities.forEachPlayer((player: Player) => {
                    players.push({
                        name: player.name,
                        x: player.x,
                        y: player.y,
                        level: player.level,
                        hitPoints: player.hitPoints.getHitPoints(),
                        maxHitPoints: player.hitPoints.getMaxHitPoints(),
                        combat: player.inCombat(),
                        moving: player.moving,
                        isAI: player.isAI
                    });
                });

                response.json({
                    status: 'success',
                    timestamp: new Date().toISOString(),
                    map: {
                        width: this.world.map.width,
                        height: this.world.map.height,
                        tileSize: this.world.map.tileSize
                    },
                    playerCount: this.world.getPopulation(),
                    players
                });
            } catch (error) {
                log.error(`Error getting world status: ${error}`);
                response.status(500).json({
                    status: 'error',
                    message: 'Internal server error'
                });
            }
        });

        // Public rankings endpoint (no auth required, CORS enabled)
        router.get('/ai/rankings', (_request, response) => {
            response.header('Access-Control-Allow-Origin', '*');
            response.header('Access-Control-Allow-Methods', 'GET');

            try {
                const db = this.world.database;

                // Run all 4 aggregations in parallel using callbacks wrapped in promises
                const totalXP = new Promise<any[]>((resolve) => {
                    db.getTotalExperienceAggregate((data) => resolve(data));
                });
                const pvpKills = new Promise<any[]>((resolve) => {
                    db.getPvpAggregate((data) => resolve(data));
                });
                const totalMobKills = new Promise<any[]>((resolve) => {
                    db.getTotalMobKillsAggregate((data) => resolve(data));
                });
                const totalGold = new Promise<any[]>((resolve) => {
                    db.getTotalGoldAggregate((data) => resolve(data));
                });

                Promise.all([totalXP, pvpKills, totalMobKills, totalGold]).then(
                    ([xpData, pvpData, mobData, goldData]) => {
                        const mapEntries = (data: any[], valueField: string) =>
                            data
                                .map((d: any) => ({ name: d._id, value: d[valueField] || 0 }))
                                .filter((e: any) => e.value > 0);

                        response.json({
                            status: 'success',
                            rankings: {
                                totalExperience: mapEntries(xpData, 'experience'),
                                pvpKills: mapEntries(pvpData, 'kills'),
                                totalMobKills: mapEntries(mobData, 'totalKills'),
                                totalGold: mapEntries(goldData, 'totalGold')
                            }
                        });
                    }
                );
            } catch (error) {
                log.error(`Error getting rankings: ${error}`);
                response.status(500).json({
                    status: 'error',
                    message: 'Internal server error'
                });
            }
        });

        // AI Agent API endpoints
        this.handleAIAgentRoutes(router);
    }

    /**
     * Handles all the AI agent API routes
     * @param router Express router
     */
    private handleAIAgentRoutes(router: express.Router): void {
        // Create a new character for an AI agent
        router.post('/ai/create', (request: Request, response: Response) => {
            try {
                const { username, password } = request.body;

                if (!username || !password) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Username and password are required'
                    });
                }

                // Check if username is valid
                if (Filter.isProfane(username)) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Username contains inappropriate language'
                    });
                }

                // Check if username already exists
                if (this.world.isOnline(username)) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Username already exists'
                    });
                }

                // Generate a unique token for this AI agent
                const token = Utils.generateRandomString(32);

                // Return the token to the client
                response.json({
                    status: 'success',
                    token,
                    message: 'Character created successfully'
                });
            } catch (error) {
                log.error(`Error creating AI agent: ${error}`);
                response.status(500).json({
                    status: 'error',
                    message: 'Internal server error'
                });
            }
        });

        // Login with an AI agent
        router.post('/ai/login', async (request: Request, response: Response) => {
            try {
                const { username, password, force } = request.body;

                if (!username || !password) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Username and password are required'
                    });
                }

                // Check if player is already logged in
                if (this.world.isOnline(username)) {
                    if (force) {
                        // Force logout the existing session
                        const existingPlayer = this.world.getPlayerByName(username);
                        if (existingPlayer) {
                            log.info(`Force logout: Disconnecting existing session for ${username}`);

                            // Remove from aiAgents if exists
                            for (const [token, player] of Object.entries(this.aiAgents)) {
                                if (player.username === username) {
                                    delete this.aiAgents[token];
                                    break;
                                }
                            }

                            // Disconnect the player
                            existingPlayer.connection.close();

                            // Wait for cleanup to complete before proceeding
                            await new Promise(resolve => setTimeout(resolve, 150));
                        }
                    } else {
                        return response.status(400).json({
                            status: 'error',
                            message: 'Player is already logged in'
                        });
                    }
                }

                // Generate a unique token for this AI agent session
                const token = Utils.generateRandomString(32);

                // Create a mock connection for the AI agent
                const connection = this.world.createAIConnection(username, password);

                if (!connection) {
                    return response.status(500).json({
                        status: 'error',
                        message: 'Failed to create connection'
                    });
                }

                // IMPORTANT: Wait for the player to be fully loaded from database
                // This prevents race conditions where skill modifications are overwritten
                // by async database loading that completes after the API returns
                log.info(`Waiting for player ${username} to be fully loaded...`);
                await connection.waitForPlayerLoaded();
                log.info(`Player ${username} fully loaded, proceeding with login response`);

                // Store the player reference for future API calls
                this.aiAgents[token] = connection.player;

                // Auto-initialize new/low-level characters with high skills and equipment
                const player = connection.player;
                const currentCombatLevel = player.skills.getCombatLevel();

                if (currentCombatLevel < 200) {
                    log.info(`Auto-initializing character ${username} (combat level ${currentCombatLevel})`);

                    try {
                        // --- Set ALL skills to level 45 ---
                        const allSkills = [
                            Modules.Skills.Accuracy,
                            Modules.Skills.Strength,
                            Modules.Skills.Defense,
                            Modules.Skills.Health,
                            Modules.Skills.Magic,
                            Modules.Skills.Archery,
                            Modules.Skills.Lumberjacking,
                            Modules.Skills.Mining,
                            Modules.Skills.Fishing,
                            Modules.Skills.Cooking,
                            Modules.Skills.Smithing,
                            Modules.Skills.Crafting,
                            Modules.Skills.Fletching,
                            Modules.Skills.Smelting,
                            Modules.Skills.Foraging
                        ];

                        const targetLevel = 45;

                        for (const skillType of allSkills) {
                            const skill = player.skills.get(skillType);
                            if (!skill) continue;

                            const experience = Formulas.LevelExp[targetLevel] || 0;
                            skill.setExperience(experience);
                        }

                        // Update Health HP and Magic Mana
                        const healthSkill = player.skills.get(Modules.Skills.Health);
                        if (healthSkill) {
                            const newMaxHP = Formulas.getMaxHitPoints(healthSkill.level);
                            player.hitPoints.setMaxHitPoints(newMaxHP);
                            player.hitPoints.setHitPoints(newMaxHP);
                        }

                        const magicSkill = player.skills.get(Modules.Skills.Magic);
                        if (magicSkill) {
                            const newMaxMana = Formulas.getMaxMana(magicSkill.level);
                            player.mana.setMaxMana(newMaxMana);
                            player.mana.setMana(newMaxMana);
                        }

                        // Update overall combat level
                        player.level = player.skills.getCombatLevel();
                        player.skills.sync();

                        // --- Equip good gear ---
                        // Equipment enum: Armour(0), Boots(1), Pendant(2), Ring(3), Weapon(4), Arrows(5)
                        const equipmentSetup: { type: number; key: string; count: number }[] = [
                            { type: Modules.Equipment.Weapon, key: 'bastardsword', count: 1 },
                            { type: Modules.Equipment.Armour, key: 'whitearmor', count: 1 },
                            { type: Modules.Equipment.Boots, key: 'lavaboots', count: 1 },
                            { type: Modules.Equipment.Ring, key: 'pytharring', count: 1 },
                            { type: Modules.Equipment.Pendant, key: 'rubypendant', count: 1 },
                            { type: Modules.Equipment.Arrows, key: 'pythararrow', count: 100 }
                        ];

                        for (const equip of equipmentSetup) {
                            try {
                                const item = new Item(equip.key, -1, -1, false, equip.count);
                                if (item.exists) {
                                    const slot = player.equipment.get(equip.type);
                                    if (slot) slot.update(item);
                                }
                            } catch (e) {
                                log.debug(`Could not equip ${equip.key}: ${e}`);
                            }
                        }

                        // --- Add useful inventory items ---
                        const inventoryItems = [
                            { key: 'rosebow', count: 1 },
                            { key: 'pythararrow', count: 100 },
                            { key: 'icestaff', count: 1 },
                            { key: 'flask', count: 15 },
                            { key: 'bigflask', count: 10 },
                            { key: 'manaflask', count: 10 },
                            { key: 'pickaxe', count: 1 },
                            { key: 'axe', count: 1 }
                        ];

                        for (const inv of inventoryItems) {
                            try {
                                const item = new Item(inv.key, -1, -1, false, inv.count);
                                if (item.exists) player.inventory.add(item);
                            } catch (e) {
                                log.debug(`Could not add ${inv.key}: ${e}`);
                            }
                        }

                        player.save();
                        player.sync();
                        log.info(`Auto-initialization complete for ${username} — combat level: ${player.level}`);
                    } catch (initError) {
                        log.error(`Auto-initialization failed for ${username}: ${initError}`);
                        // Non-fatal — player can still play, just without the boost
                    }
                }

                response.json({
                    status: 'success',
                    token,
                    message: 'Logged in successfully'
                });
            } catch (error) {
                log.error(`Error logging in AI agent: ${error}`);
                response.status(500).json({
                    status: 'error',
                    message: 'Internal server error'
                });
            }
        });

        // Move the AI agent's character
        router.post('/ai/move', (request: Request, response: Response) => {
            try {
                const { token, x, y } = request.body;

                if (!token || x === undefined || y === undefined) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Token, x, and y are required'
                    });
                }

                const player = this.aiAgents[token];

                if (!player) {
                    return response.status(401).json({
                        status: 'error',
                        message: 'Invalid token'
                    });
                }

                // Get current player position
                const startX = player.x;
                const startY = player.y;

                // Calculate Manhattan distance to target
                const distance = Math.abs(x - startX) + Math.abs(y - startY);
                const maxDistance = 200; // Actual limit is 200, but agents are told 120 for safety margin

                // Enforce distance limit of 30 tiles
                if (distance > maxDistance) {
                    return response.status(400).json({
                        status: 'error',
                        message: `Move distance exceeds limit. Maximum allowed: ${maxDistance} tiles, requested: ${distance} tiles`,
                        currentPosition: { x: startX, y: startY },
                        targetPosition: { x, y },
                        distance,
                        maxDistance
                    });
                }

                // Teleport the player to the target position
                // Since AI agents don't have actual clients, we use teleport instead of path movement
                // Enable noclip temporarily to bypass collision checking for AI movement
                const originalNoclip = player.noclip;
                player.noclip = true;

                player.teleport(x, y);

                // Restore original noclip setting
                player.noclip = originalNoclip;

                // Get actual position after teleport (may differ if collision occurred)
                const actualX = player.x;
                const actualY = player.y;
                const reachedTarget = actualX === x && actualY === y;

                response.json({
                    status: 'success',
                    message: reachedTarget
                        ? 'Character moved to the destination'
                        : `Character moved to nearest valid position (${actualX}, ${actualY}) instead of target (${x}, ${y})`,
                    startPosition: { x: startX, y: startY },
                    targetPosition: { x, y },
                    actualPosition: { x: actualX, y: actualY },
                    reachedTarget,
                    distance
                });
            } catch (error) {
                log.error(`Error moving AI agent: ${error}`);
                response.status(500).json({
                    status: 'error',
                    message: 'Internal server error'
                });
            }
        });

        // Chat as the AI agent's character
        router.post('/ai/chat', (request: Request, response: Response) => {
            try {
                const { token, message, global = false } = request.body;

                if (!token || !message) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Token and message are required'
                    });
                }

                const player = this.aiAgents[token];

                if (!player) {
                    return response.status(401).json({
                        status: 'error',
                        message: 'Invalid token'
                    });
                }

                // Send the chat message
                player.chat(message, global);

                response.json({
                    status: 'success',
                    message: 'Message sent successfully'
                });
            } catch (error) {
                log.error(`Error sending chat message: ${error}`);
                response.status(500).json({
                    status: 'error',
                    message: 'Internal server error'
                });
            }
        });

        // Get chat messages for the AI agent
        router.get('/ai/chat', (request: Request, response: Response) => {
            try {
                const token = request.query.token as string;

                if (!token) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Token is required'
                    });
                }

                const player = this.aiAgents[token];

                if (!player) {
                    return response.status(404).json({
                        status: 'error',
                        message: 'Invalid token'
                    });
                }

                // Get recent chat messages from the world's chat history
                const limit = parseInt(request.query.limit as string) || 20;
                const chatHistory = this.world.getChatHistory(limit);
                
                // Format messages for the AI agent
                const formattedMessages = chatHistory.map(msg => ({
                    timestamp: msg.timestamp,
                    player: msg.source,
                    message: msg.message,
                    global: msg.global
                }));

                response.json({
                    status: 'success',
                    messages: formattedMessages
                });
            } catch (error) {
                log.error(`Error retrieving chat messages: ${error}`);
                response.status(500).json({
                    status: 'error',
                    message: 'Internal server error'
                });
            }
        });

        // Get observations for the AI agent
        router.get('/ai/observe', (request: Request, response: Response) => {
            try {
                const token = request.query.token as string;

                if (!token) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Token is required'
                    });
                }

                const player = this.aiAgents[token];

                if (!player) {
                    return response.status(401).json({
                        status: 'error',
                        message: 'Invalid token'
                    });
                }

                // Get observation radius (default 64)
                const radius = parseInt(request.query.radius as string) || 64;

                // Get location information
                const location = {
                    x: player.x,
                    y: player.y,
                    regionId: this.world.map.regions.getRegion(player.x, player.y),
                    mapName: 'World' // Default name since map doesn't have a name property
                };

                // Get map information including boundaries
                const map = {
                    name: 'World', // Default name since map doesn't have a name property
                    width: this.world.map.width,
                    height: this.world.map.height,
                    tileSize: this.world.map.tileSize,
                    version: this.world.map.version
                };

                // Get all warp/entry points in the map - don't filter by radius
                const entries: any[] = [];
                for (let warp of this.world.map.warps) {
                    entries.push({
                        x: warp.x,
                        y: warp.y,
                        destination: warp.name || 'Unknown',
                        levelRequirement: warp.level || 0,
                        distanceFrom: Utils.getDistance(player.x, player.y, warp.x, warp.y)
                    });
                }

                // Get nearby mobs
                const mobs: any[] = [];
                this.world.getGrids().forEachEntityNear(
                    player.x,
                    player.y,
                    (entity) => {
                        // Skip if entity is not a mob
                        if (!entity.isMob()) return;
                        
                        // Check if the mob is within the radius
                        if (Utils.getDistance(player.x, player.y, entity.x, entity.y) <= radius) {
                            mobs.push({
                                instance: entity.instance,
                                type: entity.type,
                                name: entity.name,
                                level: entity.level,
                                x: entity.x,
                                y: entity.y,
                                hitPoints: entity.hitPoints?.getHitPoints() || 0,
                                maxHitPoints: entity.hitPoints?.getMaxHitPoints() || 0,
                                aggressive: entity.aggressive,
                                distanceFrom: Utils.getDistance(player.x, player.y, entity.x, entity.y)
                            });
                        }
                    },
                    radius
                );

                // Get nearby resources (trees, rocks, etc.) from regions
                const resources: any[] = [];
                
                // Get the current region and surrounding regions
                const currentRegion = this.world.map.regions.getRegion(player.x, player.y);
                
                // Get resources from trees
                const trees = this.world.globals.getTrees();
                for (let instance in trees.getResources()) {
                    const resource = trees.getResources()[instance];
                    const distance = Utils.getDistance(player.x, player.y, resource.x, resource.y);
                    
                    if (distance <= radius && resource.state === 0) { // Only available resources
                        resources.push({
                            instance: resource.instance,
                            type: 10, // Object type
                            name: resource.type.charAt(0).toUpperCase() + resource.type.slice(1) + ' Tree',
                            x: resource.x,
                            y: resource.y,
                            distanceFrom: distance
                        });
                    }
                }
                
                // Get resources from rocks
                const rocks = this.world.globals.getRocks();
                for (let instance in rocks.getResources()) {
                    const resource = rocks.getResources()[instance];
                    const distance = Utils.getDistance(player.x, player.y, resource.x, resource.y);
                    
                    if (distance <= radius && resource.state === 0) { // Only available resources
                        resources.push({
                            instance: resource.instance,
                            type: 10, // Object type
                            name: resource.type.charAt(0).toUpperCase() + resource.type.slice(1) + ' Rock',
                            x: resource.x,
                            y: resource.y,
                            distanceFrom: distance
                        });
                    }
                }
                
                // Get resources from fishing spots
                const fishSpots = this.world.globals.getFishingSpots();
                for (let instance in fishSpots.getResources()) {
                    const resource = fishSpots.getResources()[instance];
                    const distance = Utils.getDistance(player.x, player.y, resource.x, resource.y);
                    
                    if (distance <= radius && resource.state === 0) { // Only available resources
                        resources.push({
                            instance: resource.instance,
                            type: 10, // Object type
                            name: 'Fishing Spot',
                            x: resource.x,
                            y: resource.y,
                            distanceFrom: distance
                        });
                    }
                }
                
                // Get resources from foraging
                const foraging = this.world.globals.getForaging();
                for (let instance in foraging.getResources()) {
                    const resource = foraging.getResources()[instance];
                    const distance = Utils.getDistance(player.x, player.y, resource.x, resource.y);
                    
                    if (distance <= radius && resource.state === 0) { // Only available resources
                        resources.push({
                            instance: resource.instance,
                            type: 10, // Object type
                            name: resource.type.charAt(0).toUpperCase() + resource.type.slice(1) + ' Plant',
                            x: resource.x,
                            y: resource.y,
                            distanceFrom: distance
                        });
                    }
                }

                // Get nearby players
                const players: any[] = [];
                this.world.getGrids().forEachEntityNear(
                    player.x,
                    player.y,
                    (entity) => {
                        // Skip if entity is not a player or is the current player
                        if (!entity.isPlayer() || entity.instance === player.instance) return;
                        
                        // Check if the player is within the radius
                        if (Utils.getDistance(player.x, player.y, entity.x, entity.y) <= radius) {
                            // Cast to Player type
                            const otherPlayer = entity;
                            
                            players.push({
                                instance: otherPlayer.instance,
                                name: otherPlayer.name,
                                level: otherPlayer.level,
                                x: otherPlayer.x,
                                y: otherPlayer.y,
                                rank: (otherPlayer as any).rank,
                                distanceFrom: Utils.getDistance(player.x, player.y, otherPlayer.x, otherPlayer.y)
                            });
                        }
                    },
                    radius
                );

                // Get inventory items - filter out empty slots
                const inventoryItems: any[] = [];
                for (let i = 0; i < player.inventory.size; i++) {
                    const slot = player.inventory.get(i);
                    // Check slot exists, has items (count >= 1), AND has a valid key
                    if (slot && !slot.isEmpty() && slot.key) {
                        const item = player.inventory.getItem(slot);
                        // Only include items with count > -1
                        if (item.count > -1) {
                            inventoryItems.push({
                                index: i,
                                key: item.key,
                                name: item.name,
                                count: item.count,
                                edible: item.edible,
                                equippable: item.isEquippable(),
                                description: item.description || `A ${item.name}` // Add item description if available
                            });
                        }
                    }
                }

                // Get equipped items - filter out empty equipment and add attack range for weapons
                const rawEquipments = player.equipment.serialize().equipments.filter((equipment: any) => 
                    equipment && equipment.key && equipment.count > -1
                );
                
                // Add attack range information for weapons
                const equippedItems = rawEquipments.map((equipment: any) => {
                    const result = { ...equipment };
                    // If this is a weapon (type 4 is weapon slot), add attack range
                    if (equipment.type === 4) {
                        result.attackRange = player.attackRange;
                    }
                    return result;
                });

                // Get player status with enhanced skill information
                const skillsInfo = player.skills.serialize();
                
                // Map skill types to skill names
                const skillNames: { [key: number]: string } = {
                    0: 'Lumberjacking',   // Skills.Lumberjacking
                    1: 'Accuracy',        // Skills.Accuracy
                    2: 'Archery',         // Skills.Archery
                    3: 'Health',          // Skills.Health
                    4: 'Magic',           // Skills.Magic
                    5: 'Mining',          // Skills.Mining
                    6: 'Strength',        // Skills.Strength
                    7: 'Defense',         // Skills.Defense
                    8: 'Fishing',         // Skills.Fishing
                    9: 'Cooking',         // Skills.Cooking
                    10: 'Smithing',       // Skills.Smithing
                    11: 'Crafting',       // Skills.Crafting
                    12: 'Fletching',      // Skills.Fletching
                    13: 'Smelting',       // Skills.Smelting (not Foraging!)
                    14: 'Foraging',       // Skills.Foraging
                    15: 'Eating',         // Skills.Eating
                    16: 'Loitering'       // Skills.Loitering
                };
                
                // Add skill names to the skills information
                if (skillsInfo && skillsInfo.skills) {
                    for (let skill of skillsInfo.skills) {
                        if (skill.type !== undefined && skillNames[skill.type]) {
                            // Use type assertion to add name property
                            (skill as any).name = skillNames[skill.type];
                            
                            // Add level based on experience using the actual game formula
                            if (skill.experience !== undefined && skill.experience > 0) {
                                (skill as any).level = Formulas.expToLevel(skill.experience);
                            } else {
                                (skill as any).level = 1; // Default level if no experience
                            }
                        }
                    }
                }

                const playerStatus = {
                    name: player.name,
                    level: player.level,
                    experience: player.getTotalExperience(),
                    hitPoints: player.hitPoints.getHitPoints(),
                    maxHitPoints: player.hitPoints.getMaxHitPoints(),
                    mana: player.mana.getMana(),
                    maxMana: player.mana.getMaxMana(),
                    orientation: player.orientation,
                    combat: player.inCombat(),
                    poisoned: player.poison,
                    moving: player.moving,
                    skills: skillsInfo
                };

                // Detect collisions around the player
                const collisions = [];
                // Check collisions in a 5x5 grid around the player
                for (let y = player.y - 5; y <= player.y + 5; y++) {
                    for (let x = player.x - 5; x <= player.x + 5; x++) {
                        if (this.world.map.isColliding(x, y, player)) {
                            collisions.push({ x, y });
                        }
                    }
                }

                // Get nearby ground items (dropped loot from mobs, etc.)
                const groundItems: any[] = [];
                this.world.getGrids().forEachEntityNear(
                    player.x,
                    player.y,
                    (entity) => {
                        // Check if entity is an Item (dropped on ground)
                        if (entity instanceof Item) {
                            const distance = Utils.getDistance(player.x, player.y, entity.x, entity.y);
                            if (distance <= radius) {
                                groundItems.push({
                                    instance: entity.instance,
                                    key: entity.key,
                                    name: entity.name,
                                    count: entity.count,
                                    x: entity.x,
                                    y: entity.y,
                                    owner: (entity as any).owner || '',  // Who has pickup priority
                                    distanceFrom: distance
                                });
                            }
                        }
                    },
                    radius
                );

                response.json({
                    status: 'success',
                    location,
                    map,
                    entries,
                    mobs,
                    resources,
                    players,
                    groundItems,
                    inventory: {
                        items: inventoryItems,
                        equipped: equippedItems
                    },
                    playerStatus,
                    collisions,
                    observationRadius: radius
                });
            } catch (error) {
                log.error(`Error getting observations: ${error}`);
                response.status(500).json({
                    status: 'error',
                    message: 'Internal server error'
                });
            }
        });

        // Attack a target
        router.post('/ai/attack', (request: Request, response: Response) => {
            try {
                const { token, targetInstance } = request.body;

                if (!token || !targetInstance) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Token and targetInstance are required'
                    });
                }

                const player = this.aiAgents[token];

                if (!player) {
                    return response.status(401).json({
                        status: 'error',
                        message: 'Invalid token'
                    });
                }

                // Find the target entity
                const target = this.world.entities.get(targetInstance);

                if (!target) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Target not found'
                    });
                }

                // Check if target is a character that can be attacked
                if (!(target instanceof Character)) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Cannot attack this type of entity'
                    });
                }

                // Initiate attack
                player.combat.attack(target);

                response.json({
                    status: 'success',
                    message: 'Attack initiated successfully'
                });
            } catch (error) {
                log.error(`Error attacking target: ${error}`);
                response.status(500).json({
                    status: 'error',
                    message: 'Internal server error'
                });
            }
        });

        // Equip an item from the inventory
        router.post('/ai/equip', (request: Request, response: Response) => {
            try {
                const { token, index } = request.body;

                if (!token || index === undefined) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Token and index are required'
                    });
                }

                const player = this.aiAgents[token];

                if (!player) {
                    return response.status(401).json({
                        status: 'error',
                        message: 'Invalid token'
                    });
                }

                // Get the item at the specified inventory index
                const slot = player.inventory.get(index);
                
                if (slot.isEmpty()) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'No item found at specified inventory index'
                    });
                }
                
                const item = player.inventory.getItem(slot);
                
                // Check if the item is equippable
                if (!item.isEquippable()) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'This item cannot be equipped'
                    });
                }
                
                // Check if the player meets requirements to equip this item
                if (!item.canEquip(player)) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Requirements not met to equip this item'
                    });
                }
                
                // Equip the item
                player.equipment.equip(item, index);
                
                // Get equipment type that was equipped
                const equipmentType = item.getEquipmentType();
                
                response.json({
                    status: 'success',
                    message: 'Item equipped successfully',
                    item: {
                        key: item.key,
                        name: item.name,
                        equipmentType: equipmentType
                    }
                });
            } catch (error) {
                log.error(`Error equipping item: ${error}`);
                response.status(500).json({
                    status: 'error',
                    message: 'Internal server error'
                });
            }
        });

        // Collect a resource (tree, rock, fish, etc.)
        router.post('/ai/collect', (request: Request, response: Response) => {
            try {
                const { token, targetInstance } = request.body;

                if (!token || !targetInstance) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Token and targetInstance are required'
                    });
                }

                const player = this.aiAgents[token];

                if (!player) {
                    return response.status(401).json({
                        status: 'error',
                        message: 'Invalid token'
                    });
                }

                // Find the target resource from globals (trees, rocks, fish spots, foraging)
                let resource = null;
                let resourceGlobalType = null;
                
                // Check trees
                const treesResources = this.world.globals.getTrees().getResources();
                if (treesResources[targetInstance]) {
                    resource = treesResources[targetInstance];
                    resourceGlobalType = 'tree';
                }
                
                // Check rocks
                if (!resource) {
                    const rocksResources = this.world.globals.getRocks().getResources();
                    if (rocksResources[targetInstance]) {
                        resource = rocksResources[targetInstance];
                        resourceGlobalType = 'rock';
                    }
                }
                
                // Check fishing spots
                if (!resource) {
                    const fishResources = this.world.globals.getFishingSpots().getResources();
                    if (fishResources[targetInstance]) {
                        resource = fishResources[targetInstance];
                        resourceGlobalType = 'fishing spot';
                    }
                }
                
                // Check foraging
                if (!resource) {
                    const forageResources = this.world.globals.getForaging().getResources();
                    if (forageResources[targetInstance]) {
                        resource = forageResources[targetInstance];
                        resourceGlobalType = 'plant';
                    }
                }

                if (!resource) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Target resource not found'
                    });
                }

                // Calculate distance between player and resource
                const distance = Utils.getDistance(player.x, player.y, resource.x, resource.y);

                // Ensure player is close enough to the resource
                if (distance > 2) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Too far from resource',
                        distance: distance,
                        maxDistance: 2
                    });
                }

                let result = { status: 'error', message: 'Unknown resource type' };

                // Use the appropriate skill based on resource type
                if (resourceGlobalType === 'tree') {
                    player.skills.getLumberjacking().cut(player, resource);
                    result = { status: 'success', message: 'Started cutting tree' };
                }
                else if (resourceGlobalType === 'rock') {
                    player.skills.getMining().mine(player, resource);
                    result = { status: 'success', message: 'Started mining rock' };
                }
                else if (resourceGlobalType === 'fishing spot') {
                    player.skills.getFishing().catch(player, resource);
                    result = { status: 'success', message: 'Started fishing' };
                }
                else if (resourceGlobalType === 'plant') {
                    player.skills.getForaging().harvest(player, resource);
                    result = { status: 'success', message: 'Started foraging' };
                }
                else {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Cannot collect this type of entity'
                    });
                }

                // Return information about the collection attempt
                response.json({
                    ...result,
                    resource: {
                        instance: resource.instance,
                        type: resourceGlobalType,
                        name: resource.type.charAt(0).toUpperCase() + resource.type.slice(1),
                        x: resource.x,
                        y: resource.y,
                        distance: distance
                    }
                });
            } catch (error) {
                log.error(`Error collecting resource: ${error}`);
                response.status(500).json({
                    status: 'error',
                    message: 'Internal server error'
                });
            }
        });

        // Pick up a ground item (dropped loot from mobs, etc.)
        router.post('/ai/pickup', (request: Request, response: Response) => {
            try {
                const { token, targetInstance } = request.body;

                if (!token || !targetInstance) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Token and targetInstance are required'
                    });
                }

                const player = this.aiAgents[token];

                if (!player) {
                    return response.status(401).json({
                        status: 'error',
                        message: 'Invalid token'
                    });
                }

                // Find the ground item entity
                const entity = this.world.entities.get(targetInstance);

                if (!entity) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Item not found on ground'
                    });
                }

                // Check if it's actually an Item
                if (!(entity instanceof Item)) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Target is not a ground item'
                    });
                }

                const item = entity as Item;

                // Check distance - player must be close enough to pick up
                const distance = Utils.getDistance(player.x, player.y, item.x, item.y);
                if (distance > 2) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Too far from item',
                        distance: distance,
                        maxDistance: 2
                    });
                }

                // Ownership check disabled - anyone can pick up any drop
                // const itemOwner = (item as any).owner;
                // if (itemOwner && itemOwner !== '' && itemOwner !== player.instance) {
                //     const ownershipExpired = (item as any).ownershipExpired || false;
                //     if (!ownershipExpired) {
                //         return response.status(400).json({
                //             status: 'error',
                //             message: 'Item is reserved for another player',
                //             owner: itemOwner
                //         });
                //     }
                // }

                // Store item info before pickup for response
                const itemInfo = {
                    key: item.key,
                    name: item.name,
                    count: item.count,
                    x: item.x,
                    y: item.y
                };

                // Add to player inventory
                const added = player.inventory.add(item);

                if (added) {
                    // Remove item from the ground/world
                    this.world.entities.removeItem(item);

                    log.info(`[AI Pickup] ${player.name} picked up ${item.count}x ${item.name} at (${item.x}, ${item.y})`);

                    response.json({
                        status: 'success',
                        message: 'Item picked up successfully',
                        item: itemInfo
                    });
                } else {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Inventory full - cannot pick up item'
                    });
                }
            } catch (error) {
                log.error(`Error picking up item: ${error}`);
                response.status(500).json({
                    status: 'error',
                    message: 'Internal server error'
                });
            }
        });

        // Craft an item
        router.post('/ai/craft', (request: Request, response: Response) => {
            try {
                const { token, type, itemKey, count = 1 } = request.body;

                if (!token || !type || !itemKey) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Token, type, and itemKey are required'
                    });
                }

                const player = this.aiAgents[token];

                if (!player) {
                    return response.status(401).json({
                        status: 'error',
                        message: 'Invalid token'
                    });
                }

                // Convert the string type to the Skills enum value
                const skillType = Modules.Skills[type as keyof typeof Modules.Skills];
                if (skillType === undefined) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Invalid crafting skill type'
                    });
                }

                // Check if player can craft (cooldown)
                if (!player.canCraft()) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Crafting is on cooldown'
                    });
                }

                // For some skill types, check if the player has the necessary quest requirements
                if (skillType === Modules.Skills.Crafting && !player.canUseCrafting()) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'You need to start the crafting quest to use crafting'
                    });
                }

                if (skillType === Modules.Skills.Alchemy && !player.canUseAlchemy()) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'You need to start the alchemy quest to use alchemy'
                    });
                }

                // Check if count is valid
                if (count !== 1 && count !== 5 && count !== 10) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Count must be 1, 5, or 10'
                    });
                }

                // Open the crafting interface for the player to set the activeCraftingInterface
                this.world.crafting.open(player, skillType);

                // Get the crafting data to check if player has materials
                const skillName = Modules.Skills[skillType].toLowerCase();
                const craftingData = (CraftingData as any)[skillName];

                // Check if the crafting data exists
                if (!craftingData) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Invalid crafting data'
                    });
                }

                // Check if the item exists in the crafting data
                const craftingItem = craftingData[itemKey];
                if (!craftingItem) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Invalid item key'
                    });
                }

                // Ensure the player has the correct level to craft the item
                // Since we can't access the private getSkillByInterface method, we'll map the skills directly
                let skillToCheck = skillType;
                if (skillType === Modules.Skills.Smelting) {
                    skillToCheck = Modules.Skills.Smithing;
                } else if (skillType === Modules.Skills.Chiseling) {
                    skillToCheck = Modules.Skills.Crafting;
                }
                
                const skill = player.skills.get(skillToCheck);
                if (skill.level < craftingItem.level) {
                    return response.status(400).json({
                        status: 'error',
                        message: `You need level ${craftingItem.level} ${type} to craft this item`,
                        requiredLevel: craftingItem.level,
                        currentLevel: skill.level
                    });
                }

                // Check if the player has all required materials
                const missingMaterials = [];
                for (const requirement of craftingItem.requirements) {
                    const required = requirement.count * count;
                    const available = player.inventory.count(requirement.key);
                    
                    if (available < required) {
                        // Add item information to missing materials
                        const itemData = (Items as any)[requirement.key];
                        missingMaterials.push({
                            key: requirement.key,
                            name: itemData?.name || requirement.key,
                            required: required,
                            available: available,
                            missing: required - available
                        });
                    }
                }

                // If there are missing materials, return them in the response
                if (missingMaterials.length > 0) {
                    // Create requirements with names
                    const requirements = craftingItem.requirements.map((req: { key: string, count: number }) => {
                        const item = (Items as any)[req.key];
                        return {
                            key: req.key,
                            name: item?.name || req.key,
                            count: req.count * count
                        };
                    });
                    
                    return response.status(400).json({
                        status: 'error',
                        message: 'Missing required materials',
                        missingMaterials: missingMaterials,
                        requirements: requirements
                    });
                }

                // Try to craft the item
                this.world.crafting.craft(player, itemKey, count);

                // Record the time of crafting
                player.lastCraft = Date.now();

                // Return success response
                response.json({
                    status: 'success',
                    message: `Crafted ${count}x ${itemKey} using ${type} skill`,
                    details: {
                        skill: type,
                        itemKey: itemKey,
                        count: count
                    }
                });
            } catch (error) {
                log.error(`Error crafting item: ${error}`);
                response.status(500).json({
                    status: 'error',
                    message: 'Internal server error'
                });
            }
        });

        // Logout the AI agent
        router.post('/ai/logout', (request: Request, response: Response) => {
            try {
                const { token } = request.body;

                if (!token) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Token is required'
                    });
                }

                const player = this.aiAgents[token];

                if (!player) {
                    return response.status(401).json({
                        status: 'error',
                        message: 'Invalid token'
                    });
                }

                // Disconnect the player
                player.connection.close();

                // Remove the player from the AI agents list
                delete this.aiAgents[token];

                response.json({
                    status: 'success',
                    message: 'Logged out successfully'
                });
            } catch (error) {
                log.error(`Error logging out AI agent: ${error}`);
                response.status(500).json({
                    status: 'error',
                    message: 'Internal server error'
                });
            }
        });

        // Stop an AI agent's movement or combat
        router.post('/ai/stop', (request: Request, response: Response) => {
            try {
                const { token } = request.body;

                if (!token) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Token is required'
                    });
                }

                const player = this.aiAgents[token];

                if (!player) {
                    return response.status(401).json({
                        status: 'error',
                        message: 'Invalid token'
                    });
                }
                
                // Store current state to report in response
                const wasMoving = player.moving;
                const wasInCombat = player.inCombat();
                
                // Stop movement if player is moving
                if (player.moving) {
                    player.stopMovement();
                }
                
                // Stop combat if player is in combat
                if (player.inCombat()) {
                    player.combat.stop();
                }
                
                // Prepare response message
                let message = 'No actions were stopped';
                if (wasMoving && wasInCombat) {
                    message = 'Movement and combat stopped';
                } else if (wasMoving) {
                    message = 'Movement stopped';
                } else if (wasInCombat) {
                    message = 'Combat stopped';
                }
                
                response.json({
                    status: 'success',
                    message,
                    stopped: {
                        movement: wasMoving,
                        combat: wasInCombat
                    }
                });
            } catch (error) {
                log.error(`Error stopping AI agent actions: ${error}`);
                response.status(500).json({
                    status: 'error',
                    message: 'Internal server error'
                });
            }
        });

        // Teleport the AI agent to a specific location
        router.post('/ai/teleport', (request: Request, response: Response) => {
            try {
                const { token, x, y, withAnimation = false } = request.body;

                if (!token || x === undefined || y === undefined) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Token, x, and y coordinates are required'
                    });
                }

                const player = this.aiAgents[token];

                if (!player) {
                    return response.status(401).json({
                        status: 'error',
                        message: 'Invalid token'
                    });
                }

                // Validate coordinates are within map bounds
                if (this.world.map.isOutOfBounds(x, y)) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Coordinates are out of map bounds',
                        mapBounds: {
                            width: this.world.map.width,
                            height: this.world.map.height
                        }
                    });
                }

                // Store the previous position for response
                const previousPosition = { x: player.x, y: player.y };

                // Enable noclip temporarily to bypass collision checking for AI teleport
                const originalNoclip = player.noclip;
                player.noclip = true;

                // Perform the teleport
                player.teleport(x, y, withAnimation);

                // Restore original noclip setting
                player.noclip = originalNoclip;

                // Save position to database immediately to ensure persistence
                player.save();

                // Verify the teleport actually worked
                const actualPosition = { x: player.x, y: player.y };

                response.json({
                    status: 'success',
                    message: 'Player teleported successfully',
                    previousPosition,
                    newPosition: actualPosition,
                    requestedPosition: { x, y },
                    withAnimation
                });
            } catch (error) {
                log.error(`Error teleporting AI agent: ${error}`);
                response.status(500).json({
                    status: 'error',
                    message: 'Internal server error'
                });
            }
        });

        // Set player status (health, mana, level, etc.)
        router.post('/ai/setPlayerStatus', (request: Request, response: Response) => {
            try {
                const { token, hitPoints, maxHitPoints, mana, maxMana, level, experience, poison } = request.body;

                if (!token) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Token is required'
                    });
                }

                const player = this.aiAgents[token];

                if (!player) {
                    return response.status(401).json({
                        status: 'error',
                        message: 'Invalid token'
                    });
                }

                const updates: string[] = [];

                // Update hit points
                if (hitPoints !== undefined) {
                    const validHitPoints = Math.max(0, Math.min(hitPoints, player.hitPoints.getMaxHitPoints()));
                    player.hitPoints.setHitPoints(validHitPoints);
                    updates.push(`hitPoints: ${validHitPoints}`);
                }

                // Update max hit points
                if (maxHitPoints !== undefined && maxHitPoints > 0) {
                    player.hitPoints.setMaxHitPoints(maxHitPoints);
                    updates.push(`maxHitPoints: ${maxHitPoints}`);
                }

                // Update mana
                if (mana !== undefined) {
                    const validMana = Math.max(0, Math.min(mana, player.mana.getMaxMana()));
                    player.mana.setMana(validMana);
                    updates.push(`mana: ${validMana}`);
                }

                // Update max mana
                if (maxMana !== undefined && maxMana > 0) {
                    player.mana.setMaxMana(maxMana);
                    updates.push(`maxMana: ${maxMana}`);
                }

                // Update level
                if (level !== undefined && level > 0 && level <= Modules.Constants.MAX_LEVEL) {
                    player.level = level;
                    updates.push(`level: ${level}`);
                }

                // Update experience (note: this requires updating skills individually)
                if (experience !== undefined && experience >= 0) {
                    // Experience in this game is calculated from skill totals, so we cannot set it directly
                    // Instead, we notify that this functionality would require skill-level modifications
                    updates.push(`experience update not supported (experience is calculated from skills)`);
                }

                // Update poison status
                if (poison !== undefined) {
                    if (poison.type !== undefined && poison.remaining !== undefined) {
                        player.setPoison(poison.type, poison.remaining);
                        updates.push(`poison: type ${poison.type}, remaining ${poison.remaining}ms`);
                    }
                }

                // Sync the player's status to other players
                player.sync();

                response.json({
                    status: 'success',
                    message: 'Player status updated successfully',
                    updates,
                    currentStatus: {
                        hitPoints: player.hitPoints.getHitPoints(),
                        maxHitPoints: player.hitPoints.getMaxHitPoints(),
                        mana: player.mana.getMana(),
                        maxMana: player.mana.getMaxMana(),
                        level: player.level,
                        experience: player.getTotalExperience(),
                        poison: player.poison
                    }
                });
            } catch (error) {
                log.error(`Error setting player status: ${error}`);
                response.status(500).json({
                    status: 'error',
                    message: 'Internal server error'
                });
            }
        });

        // Set player inventory
        router.post('/ai/setInventory', (request: Request, response: Response) => {
            try {
                const { token, items, clearFirst = true, targetPlayer } = request.body;

                if (!token) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Token is required'
                    });
                }

                if (!Array.isArray(items)) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Items must be an array'
                    });
                }

                let player = this.aiAgents[token];

                // If targetPlayer is specified, try to find that player
                if (targetPlayer && targetPlayer !== player?.username) {
                    // Find the target player by username
                    const targetPlayerInstance = this.world.getPlayerByName(targetPlayer);
                    if (targetPlayerInstance) {
                        player = targetPlayerInstance;
                    } else {
                        return response.status(404).json({
                            status: 'error',
                            message: `Target player '${targetPlayer}' not found`
                        });
                    }
                }

                if (!player) {
                    return response.status(401).json({
                        status: 'error',
                        message: 'Invalid token'
                    });
                }

                // Clear inventory first if requested
                if (clearFirst) {
                    for (let i = 0; i < player.inventory.size; i++) {
                        if (!player.inventory.get(i).isEmpty()) {
                            player.inventory.remove(i, player.inventory.get(i).count);
                        }
                    }
                }

                const addedItems: any[] = [];
                const failedItems: any[] = [];

                // Add new items to inventory
                for (let itemData of items) {
                    try {
                        const { key, count = 1, enchantments, index } = itemData;

                        if (!key || typeof key !== 'string') {
                            failedItems.push({ ...itemData, reason: 'Invalid item key' });
                            continue;
                        }

                        // Validate the item exists in the game
                        const itemInstance = new Item(key, -1, -1, false, count, enchantments);
                        if (!itemInstance.exists) {
                            failedItems.push({ ...itemData, reason: 'Item does not exist' });
                            continue;
                        }

                        // If specific index is provided, try to place item there
                        if (index !== undefined && index >= 0 && index < player.inventory.size) {
                            const slot = player.inventory.get(index);
                            
                            // If slot is not empty and we're not clearing first, skip
                            if (!slot.isEmpty() && !clearFirst) {
                                failedItems.push({ ...itemData, reason: 'Slot already occupied' });
                                continue;
                            }

                            // Clear the slot if it has items
                            if (!slot.isEmpty()) {
                                player.inventory.remove(index, slot.count);
                            }

                            // Set the item directly to the slot
                            slot.update(itemInstance);
                            addedItems.push({ key, count, index, enchantments });
                        } else {
                            // Add to next available slot
                            const amountAdded = player.inventory.add(itemInstance);
                            if (amountAdded > 0) {
                                addedItems.push({ key, count: amountAdded, enchantments });
                            } else {
                                failedItems.push({ ...itemData, reason: 'No inventory space' });
                            }
                        }
                    } catch (itemError) {
                        failedItems.push({ ...itemData, reason: `Error: ${itemError}` });
                    }
                }

                // Save inventory to database immediately to ensure persistence
                player.save();

                response.json({
                    status: 'success',
                    message: 'Inventory updated successfully',
                    results: {
                        addedItems,
                        failedItems,
                        clearedFirst: clearFirst
                    }
                });
            } catch (error) {
                log.error(`Error setting inventory: ${error}`);
                response.status(500).json({
                    status: 'error',
                    message: 'Internal server error'
                });
            }
        });

        // Set player equipment
        router.post('/ai/setEquipments', (request: Request, response: Response) => {
            try {
                const { token, equipment, clearFirst = true } = request.body;

                if (!token) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Token is required'
                    });
                }

                if (!equipment || typeof equipment !== 'object') {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Equipment must be an object'
                    });
                }

                const player = this.aiAgents[token];

                if (!player) {
                    return response.status(401).json({
                        status: 'error',
                        message: 'Invalid token'
                    });
                }

                // Clear all equipment first if requested
                if (clearFirst) {
                    // Equipment enum has 8 types: Armour, Boots, Pendant, Ring, Weapon, Arrows, WeaponSkin, ArmourSkin
                    for (let type = 0; type < 8; type++) {
                        const currentEquipment = player.equipment.get(type);
                        if (currentEquipment && !currentEquipment.isEmpty()) {
                            // Add current equipment back to inventory if there's space
                            if (player.inventory.hasSpace()) {
                                player.inventory.add(new Item(
                                    currentEquipment.key,
                                    -1,
                                    -1,
                                    false,
                                    currentEquipment.count,
                                    currentEquipment.enchantments
                                ));
                            }
                            currentEquipment.empty();
                        }
                    }
                }

                const equippedItems: any[] = [];
                const failedItems: any[] = [];

                // Equipment type mapping
                const equipmentTypes: { [key: string]: number } = {
                    weapon: Modules.Equipment.Weapon,
                    helmet: Modules.Equipment.Helmet,
                    pendant: Modules.Equipment.Pendant,
                    arrows: Modules.Equipment.Arrows,
                    chestplate: Modules.Equipment.Chestplate,
                    shield: Modules.Equipment.Shield,
                    ring: Modules.Equipment.Ring,
                    legplates: Modules.Equipment.Legplates,
                    cape: Modules.Equipment.Cape,
                    boots: Modules.Equipment.Boots
                };

                // Equip each item
                for (let [typeName, itemData] of Object.entries(equipment)) {
                    try {
                        const equipmentType = equipmentTypes[typeName.toLowerCase()];
                        
                        if (equipmentType === undefined) {
                            failedItems.push({ type: typeName, itemData, reason: 'Invalid equipment type' });
                            continue;
                        }

                        // Ensure itemData is an object with the expected properties
                        if (!itemData || typeof itemData !== 'object') {
                            failedItems.push({ type: typeName, itemData, reason: 'Invalid item data' });
                            continue;
                        }

                        const { key, count = 1, enchantments } = itemData as any;

                        if (!key || typeof key !== 'string') {
                            failedItems.push({ type: typeName, ...itemData, reason: 'Invalid item key' });
                            continue;
                        }

                        // Create and validate the item
                        const itemInstance = new Item(key, -1, -1, false, count, enchantments);
                        
                        if (!itemInstance.exists) {
                            failedItems.push({ type: typeName, ...itemData, reason: 'Item does not exist' });
                            continue;
                        }

                        if (!itemInstance.isEquippable()) {
                            failedItems.push({ type: typeName, ...itemData, reason: 'Item is not equippable' });
                            continue;
                        }

                        if (itemInstance.getEquipmentType() !== equipmentType) {
                            failedItems.push({ type: typeName, ...itemData, reason: 'Item type does not match equipment slot' });
                            continue;
                        }

                        // Check if player meets requirements
                        if (!itemInstance.canEquip(player)) {
                            failedItems.push({ type: typeName, ...itemData, reason: 'Player does not meet requirements' });
                            continue;
                        }

                        // Get the equipment slot and update it
                        const equipmentSlot = player.equipment.get(equipmentType);
                        
                        // Handle two-handed weapons and shields
                        if (itemInstance.isTwoHanded() && !player.equipment.getShield().isEmpty()) {
                            const shield = player.equipment.getShield();
                            if (player.inventory.hasSpace()) {
                                player.inventory.add(new Item(shield.key, -1, -1, false, shield.count, shield.enchantments));
                            }
                            player.equipment.getShield().empty();
                        }

                        if (equipmentType === Modules.Equipment.Shield && player.equipment.getWeapon().isTwoHanded()) {
                            const weapon = player.equipment.getWeapon();
                            if (player.inventory.hasSpace()) {
                                player.inventory.add(new Item(weapon.key, -1, -1, false, weapon.count, weapon.enchantments));
                            }
                            player.equipment.getWeapon().empty();
                        }

                        // Update the equipment slot
                        equipmentSlot.update(itemInstance);
                        
                        equippedItems.push({ type: typeName, key, count, enchantments });
                                            } catch (equipError) {
                            failedItems.push({ type: typeName, itemData, reason: `Error: ${equipError}` });
                        }
                    }

                    // Note: Player stats will be automatically recalculated when equipment is updated
                    // The calculateStats method is called internally by the equipment system

                // Save equipment to database immediately to ensure persistence
                player.save();

                response.json({
                    status: 'success',
                    message: 'Equipment updated successfully',
                    results: {
                        equippedItems,
                        failedItems,
                        clearedFirst: clearFirst
                    }
                });
            } catch (error) {
                log.error(`Error setting equipment: ${error}`);
                response.status(500).json({
                    status: 'error',
                    message: 'Internal server error'
                });
            }
        });

        // New endpoint to allow an AI agent to enter a portal/warp
        router.post('/ai/enter', (request: Request, response: Response) => {
            try {
                const { token } = request.body;

                if (!token) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Token is required'
                    });
                }

                const player = this.aiAgents[token];

                if (!player) {
                    return response.status(401).json({
                        status: 'error',
                        message: 'Invalid token'
                    });
                }
                
                // Check if player is standing on a warp point
                const playerX = player.x;
                const playerY = player.y;
                let foundWarp = null;
                
                // Check all warps to see if player is on a warp point
                for (const warp of this.world.map.warps) {
                    // Check if the player is within the warp area
                    const inWarpX = playerX >= warp.x && playerX < (warp.x + warp.width);
                    const inWarpY = playerY >= warp.y && playerY < (warp.y + warp.height);
                    
                    if (inWarpX && inWarpY) {
                        foundWarp = warp;
                        break;
                    }
                }
                
                // If no warp found at current position
                if (!foundWarp) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'No entry point found at the current position',
                        position: { x: playerX, y: playerY }
                    });
                }
                
                // Check if player meets level requirement for the warp
                if (foundWarp.level && player.level < foundWarp.level) {
                    return response.status(400).json({
                        status: 'error',
                        message: `Level ${foundWarp.level} required to enter this area`,
                        playerLevel: player.level,
                        requiredLevel: foundWarp.level
                    });
                }
                
                // Use the world's warp controller to handle teleportation
                this.world.warps.warp(player, foundWarp.id);
                
                response.json({
                    status: 'success',
                    message: `Entered ${foundWarp.name || 'new area'}`,
                    previousPosition: { x: playerX, y: playerY },
                    destination: foundWarp.name || 'unknown'
                });
                
            } catch (error) {
                log.error(`Error using entry point: ${error}`);
                response.status(500).json({
                    status: 'error',
                    message: 'Internal server error'
                });
            }
        });

        // Set combat level by adjusting combat skills
        router.post('/ai/setCombatLevel', (request: Request, response: Response) => {
            try {
                log.info(`setCombatLevel endpoint called with data: ${JSON.stringify(request.body)}`);
                const { token, level } = request.body;

                if (!token) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Token is required'
                    });
                }

                if (!level || level < 1 || level > Modules.Constants.MAX_LEVEL) {
                    return response.status(400).json({
                        status: 'error',
                        message: `Level must be between 1 and ${Modules.Constants.MAX_LEVEL}`
                    });
                }

                const player = this.aiAgents[token];

                if (!player) {
                    return response.status(401).json({
                        status: 'error',
                        message: 'Invalid token'
                    });
                }

                const targetLevel = parseInt(level);
                
                // Combat skills: Accuracy, Strength, Defense, Health, Magic, Archery (6 skills)
                const combatSkills = [
                    Modules.Skills.Accuracy,
                    Modules.Skills.Strength, 
                    Modules.Skills.Defense,
                    Modules.Skills.Health,
                    Modules.Skills.Magic,
                    Modules.Skills.Archery
                ];

                // Set each combat skill to the target level directly
                // This means if target is 45, each skill becomes level 45
                if (targetLevel < 1) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Minimum skill level is 1'
                    });
                }
                
                const updates: string[] = [];
                let actualTotalLevel = 0;

                // Set each combat skill level to the target level
                for (let i = 0; i < combatSkills.length; i++) {
                    try {
                        const skillType = combatSkills[i];
                        const skill = player.skills.get(skillType);
                        
                        if (!skill) {
                            updates.push(`Warning: Could not find skill ${Modules.Skills[skillType]}`);
                            continue;
                        }

                        // Set each skill to the target level directly
                        const skillLevel = targetLevel;
                        
                        // Ensure skillLevel is within valid range
                        if (skillLevel < 1 || skillLevel > Modules.Constants.MAX_LEVEL) {
                            updates.push(`Warning: Invalid skill level ${skillLevel} for ${Modules.Skills[skillType]}`);
                            continue;
                        }
                        
                        // Calculate experience needed for this level using Kaetram's experience table
                        const experience = Formulas.LevelExp[skillLevel] || 0;
                        
                        // Set the skill's experience (this will automatically update the level)
                        skill.setExperience(experience);
                        
                        actualTotalLevel += skill.level;
                        updates.push(`${Modules.Skills[skillType]}: level ${skill.level} (${experience} exp)`);
                    } catch (skillError) {
                        updates.push(`Error setting skill ${i}: ${skillError}`);
                    }
                }

                // Update player's combat level
                player.level = player.skills.getCombatLevel();
                
                // Sync the player to update other players
                player.sync();

                const result = {
                    status: 'success',
                    message: 'Combat level updated successfully',
                    updates,
                    combatLevel: {
                        requested: targetLevel,
                        actual: player.level,
                        calculated: actualTotalLevel
                    }
                };
                
                log.info(`setCombatLevel completed successfully: ${JSON.stringify(result)}`);
                response.json(result);

            } catch (error) {
                log.error(`Error setting combat level: ${error}`);
                log.error(`Stack trace: ${(error as Error).stack}`);
                response.status(500).json({
                    status: 'error',
                    message: `Internal server error: ${(error as Error).message}`
                });
            }
        });

        // Set individual skill level
        router.post('/ai/setSkillLevel', (request: Request, response: Response) => {
            try {
                log.info(`setSkillLevel endpoint called with data: ${JSON.stringify(request.body)}`);
                const { token, skill, level } = request.body;

                if (!token) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Token is required'
                    });
                }

                if (!skill) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Skill name is required'
                    });
                }

                if (!level || level < 1 || level > Modules.Constants.MAX_LEVEL) {
                    return response.status(400).json({
                        status: 'error',
                        message: `Level must be between 1 and ${Modules.Constants.MAX_LEVEL}`
                    });
                }

                const player = this.aiAgents[token];

                if (!player) {
                    return response.status(401).json({
                        status: 'error',
                        message: 'Invalid token'
                    });
                }

                const targetLevel = parseInt(level);
                
                // Create skill name mapping (console names -> enum names)
                const skillNameMapping: { [key: string]: keyof typeof Modules.Skills } = {
                    'lumberjacking': 'Lumberjacking',  // Skills.Lumberjacking = 0
                    'accuracy': 'Accuracy',            // Skills.Accuracy = 1
                    'archery': 'Archery',              // Skills.Archery = 2
                    'health': 'Health',                // Skills.Health = 3
                    'magic': 'Magic',                  // Skills.Magic = 4
                    'mining': 'Mining',                // Skills.Mining = 5
                    'strength': 'Strength',            // Skills.Strength = 6
                    'defense': 'Defense',              // Skills.Defense = 7
                    'fishing': 'Fishing',              // Skills.Fishing = 8
                    'cooking': 'Cooking',              // Skills.Cooking = 9
                    'smithing': 'Smithing',            // Skills.Smithing = 10
                    'crafting': 'Crafting',            // Skills.Crafting = 11
                    'fletching': 'Fletching',          // Skills.Fletching = 12
                    'smelting': 'Smelting',            // Skills.Smelting = 13
                    'foraging': 'Foraging',            // Skills.Foraging = 14
                    'eating': 'Eating',                // Skills.Eating = 15
                    'loitering': 'Loitering'           // Skills.Loitering = 16
                };
                
                // Normalize input skill name and get proper enum name
                const inputSkillLower = skill.toLowerCase();
                const skillEnumName = skillNameMapping[inputSkillLower];
                
                if (!skillEnumName) {
                    return response.status(400).json({
                        status: 'error',
                        message: `Invalid skill name: ${skill}. Valid skills: ${Object.keys(skillNameMapping).join(', ')}`
                    });
                }
                
                // Get the skill type from the Modules.Skills enum
                const skillType = Modules.Skills[skillEnumName];
                
                if (skillType === undefined) {
                    return response.status(400).json({
                        status: 'error',
                        message: `Could not find skill enum for: ${skillEnumName}`
                    });
                }

                // Get the player's skill
                const playerSkill = player.skills.get(skillType);
                
                if (!playerSkill) {
                    return response.status(400).json({
                        status: 'error',
                        message: `Could not find skill: ${skillEnumName}`
                    });
                }

                // Debug: Log current state
                const initialLevel = playerSkill.level;
                const initialExp = playerSkill.experience;
                
                // Use EXACTLY the same logic as admin /setlevel command (lines 512-516 in commands.ts)
                if (targetLevel < playerSkill.level) {
                    playerSkill.setExperience(0);
                    playerSkill.addExperience(0);
                } else {
                    const expToAdd = Formulas.levelsToExperience(playerSkill.level, targetLevel);
                    playerSkill.addExperience(expToAdd);
                }
                
                // Debug: Log results
                console.log(`[SETLEVEL DEBUG] ${skillEnumName}: ${initialLevel}(${initialExp}) -> ${playerSkill.level}(${playerSkill.experience}), target: ${targetLevel}`);

                // IMPORTANT: Directly update maxHitPoints/maxMana when setting health/magic skills
                // This bypasses the sync() check for this.loaded which may return early for AI agents
                if (skillEnumName === 'Health') {
                    const newMaxHP = Formulas.getMaxHitPoints(playerSkill.level);
                    player.hitPoints.setMaxHitPoints(newMaxHP);
                    player.hitPoints.setHitPoints(newMaxHP); // Also restore HP to max
                    console.log(`[SETLEVEL DEBUG] Updated maxHitPoints to ${newMaxHP} for health level ${playerSkill.level}`);
                } else if (skillEnumName === 'Magic') {
                    const newMaxMana = Formulas.getMaxMana(playerSkill.level);
                    player.mana.setMaxMana(newMaxMana);
                    player.mana.setMana(newMaxMana); // Also restore mana to max
                    console.log(`[SETLEVEL DEBUG] Updated maxMana to ${newMaxMana} for magic level ${playerSkill.level}`);
                }

                // Sync the skills to update player level and other stats
                player.skills.sync();

                // Save skills to database immediately to ensure persistence
                player.save();

                response.json({
                    status: 'success',
                    message: `${skillEnumName} level updated successfully`,
                    skill: {
                        name: skillEnumName,
                        level: playerSkill.level,
                        experience: playerSkill.experience,
                        requested: targetLevel,
                        actual: playerSkill.level
                    },
                    playerLevel: player.level
                });

            } catch (error) {
                log.error(`Error setting skill level: ${error}`);
                log.error(`Stack trace: ${(error as Error).stack}`);
                response.status(500).json({
                    status: 'error',
                    message: `Internal server error: ${(error as Error).message}`
                });
            }
        });

        // ====================================================================
        // Simulation API Endpoints
        // These endpoints allow stateless simulation of agent actions
        // without requiring actual game sessions.
        // ====================================================================

        /**
         * Get environment observation at a position
         * Input: x, y coordinates, optional radius
         * Output: Environment data (mobs, resources, players, collisions, etc.)
         */
        router.get('/ai/simulation/observe', (request: Request, response: Response) => {
            try {
                const x = parseInt(request.query.x as string);
                const y = parseInt(request.query.y as string);
                const radius = parseInt(request.query.radius as string) || 64;

                if (isNaN(x) || isNaN(y)) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'x and y coordinates are required'
                    });
                }

                // Validate coordinates are within map bounds
                if (this.world.map.isOutOfBounds(x, y)) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Coordinates are out of map bounds',
                        mapBounds: {
                            width: this.world.map.width,
                            height: this.world.map.height
                        }
                    });
                }

                // Create simulation engine and get observation
                const engine = new SimulationEngine(this.world);
                const observation = engine.getEnvironmentAtPosition(x, y, radius);

                response.json({
                    status: 'success',
                    ...observation
                });
            } catch (error) {
                log.error(`Error in simulation observe: ${error}`);
                response.status(500).json({
                    status: 'error',
                    message: 'Internal server error'
                });
            }
        });

        /**
         * Simulate an action with a given state
         * Input: state (SimulationState), action (SimulationAction)
         * Output: state_after, success, message
         */
        router.post('/ai/simulation/act', (request: Request, response: Response) => {
            try {
                const { state, action } = request.body;

                // Validate state
                const stateValidation = validateState(state);
                if (!stateValidation.valid) {
                    return response.status(400).json({
                        status: 'error',
                        message: `Invalid state: ${stateValidation.error}`
                    });
                }

                // Validate action
                const actionValidation = validateAction(action);
                if (!actionValidation.valid) {
                    return response.status(400).json({
                        status: 'error',
                        message: `Invalid action: ${actionValidation.error}`
                    });
                }

                // Create simulation engine and execute action
                const engine = new SimulationEngine(this.world);
                const result = engine.simulate(state as SimulationState, action as SimulationAction);

                response.json({
                    status: result.success ? 'success' : 'error',
                    success: result.success,
                    message: result.message,
                    state_after: result.state_after,
                    details: result.details
                });
            } catch (error) {
                log.error(`Error in simulation act: ${error}`);
                response.status(500).json({
                    status: 'error',
                    message: 'Internal server error'
                });
            }
        });

        /**
         * BENCHMARK: Spawn a mob at a specific location for task setup
         * This endpoint is used to ensure required mobs exist before benchmark tasks run.
         * Input: { mobKey: string, x: number, y: number, masterPassword: string }
         * Output: { status, message, mobInstance }
         */
        router.post('/ai/benchmark/spawn-mob', (request: Request, response: Response) => {
            try {
                const { mobKey, x, y, masterPassword } = request.body;

                // Validate master password for security
                if (masterPassword !== 'agentworld-benchmark') {
                    return response.status(403).json({
                        status: 'error',
                        message: 'Invalid master password'
                    });
                }

                // Validate required parameters
                if (!mobKey || typeof x !== 'number' || typeof y !== 'number') {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Missing required parameters: mobKey, x, y'
                    });
                }

                // Check if a mob already exists at this location
                const existingMobs: any[] = [];
                this.world.entities.forEachEntity((entity: any) => {
                    if (entity.isMob && entity.isMob()) {
                        const dist = Math.abs(entity.x - x) + Math.abs(entity.y - y);
                        if (dist <= 2) {
                            existingMobs.push({
                                instance: entity.instance,
                                name: entity.name,
                                x: entity.x,
                                y: entity.y
                            });
                        }
                    }
                });

                if (existingMobs.length > 0) {
                    return response.json({
                        status: 'success',
                        message: `Mob(s) already exist near (${x}, ${y})`,
                        existingMobs
                    });
                }

                // Spawn the mob
                const mob = this.world.entities.spawnMob(mobKey, x, y);

                if (!mob) {
                    return response.status(400).json({
                        status: 'error',
                        message: `Failed to spawn mob: ${mobKey}. Check if mob key exists in mobs.json`
                    });
                }

                log.info(`[BENCHMARK] Spawned mob ${mobKey} (${mob.name}) at (${x}, ${y}), instance: ${mob.instance}`);

                response.json({
                    status: 'success',
                    message: `Spawned ${mob.name} at (${x}, ${y})`,
                    mobInstance: mob.instance,
                    mobName: mob.name,
                    mobLevel: mob.level,
                    mobHitPoints: mob.hitPoints
                });
            } catch (error) {
                log.error(`Error in benchmark spawn-mob: ${error}`);
                response.status(500).json({
                    status: 'error',
                    message: 'Internal server error'
                });
            }
        });

        /**
         * BENCHMARK: Reset/respawn mobs at their original spawn points
         * This endpoint forces mobs to respawn even if they were killed.
         * Input: { spawnLocations: [{x, y}], masterPassword: string }
         * Output: { status, message, respawnedMobs }
         */
        router.post('/ai/benchmark/reset-mobs', (request: Request, response: Response) => {
            try {
                const { spawnLocations, masterPassword } = request.body;

                // Validate master password for security
                if (masterPassword !== 'agentworld-benchmark') {
                    return response.status(403).json({
                        status: 'error',
                        message: 'Invalid master password'
                    });
                }

                if (!spawnLocations || !Array.isArray(spawnLocations)) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Missing spawnLocations array'
                    });
                }

                const results: any[] = [];

                // For each spawn location, check spawns.json and respawn if needed
                const Spawns = require('../../../../data/spawns.json');
                
                for (const loc of spawnLocations) {
                    const key = `${loc.x}-${loc.y}`;
                    const spawnData = Spawns[key];

                    if (!spawnData) {
                        results.push({
                            location: loc,
                            status: 'skipped',
                            message: `No spawn defined at (${loc.x}, ${loc.y})`
                        });
                        continue;
                    }

                    // Check if mob already exists near this location
                    let existingMob: any = null;
                    this.world.entities.forEachEntity((entity: any) => {
                        if (entity.isMob && entity.isMob() && entity.spawnX === loc.x && entity.spawnY === loc.y) {
                            existingMob = entity;
                        }
                    });

                    if (existingMob && !existingMob.dead) {
                        results.push({
                            location: loc,
                            status: 'exists',
                            message: `${existingMob.name} already exists at spawn point`,
                            mobInstance: existingMob.instance
                        });
                        continue;
                    }

                    // Need to spawn a new mob - use the mob key from spawn data or derive it
                    // The name in spawns.json is display name, we need the mob key
                    // For bosses, we need to find the base mob type or spawn directly
                    const mobKey = spawnData.mobKey || 'wizard'; // Default to wizard for Ancient Wizard
                    
                    const mob = this.world.entities.spawnMob(mobKey, loc.x, loc.y);
                    
                    if (mob) {
                        log.info(`[BENCHMARK] Respawned ${mob.name} at (${loc.x}, ${loc.y}), instance: ${mob.instance}`);
                        results.push({
                            location: loc,
                            status: 'spawned',
                            message: `Spawned ${mob.name}`,
                            mobInstance: mob.instance,
                            mobName: mob.name
                        });
                    } else {
                        results.push({
                            location: loc,
                            status: 'failed',
                            message: `Failed to spawn mob at (${loc.x}, ${loc.y})`
                        });
                    }
                }

                response.json({
                    status: 'success',
                    message: `Processed ${results.length} spawn locations`,
                    results
                });
            } catch (error) {
                log.error(`Error in benchmark reset-mobs: ${error}`);
                response.status(500).json({
                    status: 'error',
                    message: 'Internal server error'
                });
            }
        });
    }

    /**
     * Checks whether the player is online on another server.
     * @param username The username of the player we are checking for.
     */

    public isPlayerOnline(username: string, callback: (online: boolean) => void): void {
        if (!config.hubEnabled) return callback(false);

        let url = Utils.getUrl(config.hubHost, config.hubPort, 'isOnline'),
            data = {
                hubAccessToken: config.hubAccessToken,
                serverId: config.serverId,
                username
            };

        axios
            .post(url, data)
            .then(({ data }) => callback(data.online))
            .catch(() => log.error('Could not send `isOnline` to hub.'));
    }
}
