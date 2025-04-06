import config from '@kaetram/common/config';
import log from '@kaetram/common/util/log';
import Utils from '@kaetram/common/util/utils';
import axios from 'axios';
import express from 'express';
import * as Sentry from '@sentry/node';
import * as Tracing from '@sentry/tracing';
import Filter from '@kaetram/common/util/filter';
import { Modules } from '@kaetram/common/network';

import type { Integration } from '@sentry/types';
import type { Router, Express, Request, Response } from 'express';
import type World from '../game/world';
import type Player from '../game/entity/character/player/player';
import type Entity from '../game/entity/entity';
import Character from '../game/entity/character/character';
import type { EquipmentData, SerializedEquipment } from '@kaetram/common/network/impl/equipment';

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
        router.post('/ai/login', (request: Request, response: Response) => {
            try {
                const { username, password } = request.body;

                if (!username || !password) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Username and password are required'
                    });
                }

                // Check if player is already logged in
                if (this.world.isOnline(username)) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Player is already logged in'
                    });
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

                // Store the player reference for future API calls
                this.aiAgents[token] = connection.player;

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
                
                // Teleport the player to the target position
                // Since AI agents don't have actual clients, we use teleport instead of path movement
                player.teleport(x, y);
                
                response.json({
                    status: 'success',
                    message: 'Character moved to the destination',
                    startPosition: { x: startX, y: startY },
                    targetPosition: { x, y }
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

                // Get nearby resources (trees, rocks, etc.)
                const resources: any[] = [];
                this.world.getGrids().forEachEntityNear(
                    player.x,
                    player.y,
                    (entity) => {
                        // Skip if entity is not a resource
                        if (!entity.isResource()) return;
                        
                        // Check if the resource is within the radius
                        if (Utils.getDistance(player.x, player.y, entity.x, entity.y) <= radius) {
                            resources.push({
                                instance: entity.instance,
                                type: entity.type,
                                name: entity.name,
                                x: entity.x,
                                y: entity.y,
                                distanceFrom: Utils.getDistance(player.x, player.y, entity.x, entity.y)
                            });
                        }
                    },
                    radius
                );

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

                // Get inventory items - filter out empty slots with count -1
                const inventoryItems: any[] = [];
                for (let i = 0; i < player.inventory.size; i++) {
                    const slot = player.inventory.get(i);
                    if (slot) {
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

                // Get equipped items - filter out empty equipment
                const equippedItems = player.equipment.serialize().equipments.filter((equipment: any) => 
                    equipment && equipment.key && equipment.count > -1
                );

                // Get player status with enhanced skill information
                const skillsInfo = player.skills.serialize();
                
                // Map skill types to skill names
                const skillNames: { [key: number]: string } = {
                    0: 'Combat',
                    1: 'Archery',
                    2: 'Magic',
                    3: 'Defense',
                    4: 'Mining',
                    5: 'Woodcutting',
                    6: 'Fishing',
                    7: 'Cooking',
                    8: 'Smithing',
                    9: 'Crafting',
                    10: 'Cheesemaking',
                    11: 'Brewing',
                    13: 'Foraging',
                    15: 'Accuracy',
                    16: 'Strength',
                    17: 'Health',
                    18: 'Looting'
                };
                
                // Add skill names to the skills information
                if (skillsInfo && skillsInfo.skills) {
                    for (let skill of skillsInfo.skills) {
                        if (skill.type !== undefined && skillNames[skill.type]) {
                            // Use type assertion to add name property
                            (skill as any).name = skillNames[skill.type];
                            
                            // Add estimated level based on experience (simple formula)
                            if (skill.experience) {
                                const estimatedLevel = Math.floor(Math.sqrt(skill.experience / 100)) + 1;
                                (skill as any).level = estimatedLevel;
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

                response.json({
                    status: 'success',
                    location,
                    map,
                    entries,
                    mobs,
                    resources,
                    players,
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
