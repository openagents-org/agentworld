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
import type Character from '../game/entity/character/character';

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

                // Move the player to the specified position
                player.setPosition(x, y);

                response.json({
                    status: 'success',
                    message: 'Character moved successfully',
                    position: { x: player.x, y: player.y }
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

                // Get nearby entities
                const nearbyEntities: any[] = [];
                const radius = 5; // Observation radius

                this.world.getGrids().forEachEntityNear(
                    player.x,
                    player.y,
                    (entity: Entity) => {
                        // Skip the player itself
                        if (entity.instance === player.instance) return;

                        // Add entity to the list
                        nearbyEntities.push({
                            instance: entity.instance,
                            type: entity.type,
                            name: entity.name,
                            x: entity.x,
                            y: entity.y,
                            distance: Utils.getDistance(player.x, player.y, entity.x, entity.y)
                        });
                    },
                    radius
                );

                // Get player status
                const playerStatus = {
                    instance: player.instance,
                    name: player.name,
                    x: player.x,
                    y: player.y,
                    hitPoints: player.hitPoints.getHitPoints(),
                    maxHitPoints: player.hitPoints.getMaxHitPoints(),
                    mana: player.mana.getMana(),
                    maxMana: player.mana.getMaxMana(),
                    level: player.level,
                    orientation: player.orientation,
                    moving: player.moving,
                    combat: player.inCombat()
                };

                response.json({
                    status: 'success',
                    player: playerStatus,
                    entities: nearbyEntities,
                    region: player.region
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

                // Get the target entity
                const target = this.world.entities.get(targetInstance);

                if (!target || !target.isCharacter()) {
                    return response.status(400).json({
                        status: 'error',
                        message: 'Target not found or not attackable'
                    });
                }

                // Attack the target (using the target as a Character instance)
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
