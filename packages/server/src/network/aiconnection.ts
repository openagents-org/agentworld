import log from '@kaetram/common/util/log';
import Utils from '@kaetram/common/util/utils';
import Player from '../game/entity/character/player/player';
import Creator from '@kaetram/common/database/mongodb/creator';

import type World from '../game/world';
import type MongoDB from '@kaetram/common/database/mongodb/mongodb';

/**
 * A mock connection for AI agents to interact with the game.
 * This class simulates a real connection but without the WebSocket.
 */
export default class AIConnection {
    public instance: string;
    public address: string = '127.0.0.1'; // Mock IP address
    public player: Player;
    public closed: boolean = false;

    // Connection interface compatibility
    public messageCallback?: (message: string) => void;
    public messageRate: number = 0;

    private closeCallback?: () => void;

    public constructor(
        world: World,
        database: MongoDB,
        public username: string,
        public password: string
    ) {
        this.instance = Utils.createInstance();
        
        // Create a player instance for this connection
        this.player = new Player(world, database, this as any);
        
        // Set up the player with the provided credentials
        this.player.username = username.toLowerCase();
        this.player.password = password;
        
        // Mark the player as an AI agent
        this.player.isAI = true;
        this.player.authenticated = true; // AI agents are automatically authenticated
        
        log.info(`Created AI connection for: ${this.username}`);
        
        // Try to load existing character from database first, then fallback to new character
        this.loadPlayerData(world, database);
    }

    /**
     * Attempts to load existing player data from database or creates new character
     */
    private loadPlayerData(world: World, database: MongoDB): void {
        // Use the database's existing loginAI method or fallback to fresh character
        database.loginAI(this.player, async (success: boolean, playerInfo?: any) => {
            if (success && playerInfo) {
                // Found existing character - load it
                log.info(`Loading existing AI character for ${this.username}`);
                try {
                    await this.player.load(playerInfo);
                    // Mark AI player as ready immediately after loading to avoid timeout rejection
                    this.makePlayerReady();
                    log.info(`AI agent ${this.username} has been loaded with existing character data`);
                } catch (error) {
                    log.error(`Error loading existing AI character data for ${this.username}: ${error}`);
                    await this.loadFreshCharacter(world);
                }
            } else {
                // No existing character found or database unavailable - create new one
                log.info(`No existing character found for ${this.username}, creating new character`);
                await this.loadFreshCharacter(world);
            }
        });
    }

    /**
     * Creates a fresh character with default data
     */
    private async loadFreshCharacter(world: World): Promise<void> {
        await this.player.load(Creator.serializePlayer(this.player));
        // Mark AI player as ready immediately after loading to avoid timeout rejection
        this.makePlayerReady();
        log.info(`AI agent ${this.username} has been loaded with fresh character data`);
    }

    /**
     * Marks the AI player as ready and starts necessary intervals
     * This simulates the ready packet that normal clients send
     */
    private makePlayerReady(): void {
        // Clear any existing ready timeout to prevent rejection
        if (this.player.readyTimeout) {
            clearTimeout(this.player.readyTimeout);
            this.player.readyTimeout = null;
        }

        // Mark player as ready
        this.player.ready = true;

        // Start the update interval (normally done in handleReady)
        this.player.handler.startUpdateInterval();

        // Update regions and entities (normally done in handleReady)
        this.player.updateRegion();
        this.player.updateEntities();
        this.player.updateEntityList();

        log.info(`AI agent ${this.username} marked as ready`);
    }

    // Store received messages for AI agents to retrieve via API
    private messageQueue: any[] = [];
    private maxQueueSize: number = 100;

    /**
     * Sends a message to the AI agent
     * AI agents don't have a socket, but we can store messages for them to retrieve
     */
    public send(message: unknown): void {
        // Store message in queue for AI agents to retrieve via API
        this.messageQueue.push({
            timestamp: Date.now(),
            message: message
        });
        
        // Keep queue size limited
        if (this.messageQueue.length > this.maxQueueSize) {
            this.messageQueue.shift(); // Remove oldest message
        }
        
        // Log for debugging
        if (typeof message === 'object' && message !== null && 'constructor' in message) {
            log.debug(`AI agent ${this.username} received message: ${message.constructor.name}`);
        }
    }
    
    /**
     * Gets messages from the queue (for AI agents to retrieve via API)
     */
    public getMessages(): any[] {
        return [...this.messageQueue]; // Return a copy
    }
    
    /**
     * Clears the message queue
     */
    public clearMessages(): void {
        this.messageQueue = [];
    }

    /**
     * Sends a UTF8 message to the AI agent (no-op since there's no actual socket)
     */
    public sendUTF8(message: string): void {
        // No-op, AI agents don't need to receive messages
    }

    /**
     * Rejects the connection with a reason
     */
    public reject(reason: string): void {
        log.info(`AI connection rejected: ${reason}`);
        this.close(reason);
    }

    /**
     * Closes the AI connection
     */
    public close(reason?: string): void {
        if (this.closed) return;

        log.info(`AI connection closed${reason ? ': ' + reason : ''}`);
        
        // Save player data before closing to ensure data persistence
        if (this.player && this.player.authenticated && this.player.ready) {
            log.info(`Attempting to save AI player data for ${this.username} - authenticated: ${this.player.authenticated}, ready: ${this.player.ready}, isGuest: ${this.player.isGuest}`);
            this.player.save();
            log.info(`Save method called for AI player ${this.username}`);
        } else {
            log.info(`Skipping save for ${this.username} - player: ${!!this.player}, authenticated: ${this.player?.authenticated}, ready: ${this.player?.ready}`);
        }
        
        this.closed = true;
        
        this.closeCallback?.();
    }

    /**
     * Handles the closing of the connection
     */
    public handleClose(reason?: string): void {
        this.close(reason);
    }

    /**
     * Sets a callback for when the connection is closed
     */
    public onClose(callback: () => void): void {
        this.closeCallback = callback;
    }

    /**
     * Sets a callback for when a message is received (no-op for AI agents)
     */
    public onMessage(_callback: (message: string) => void): void {
        // No-op, AI agents don't send messages through sockets
    }
    
    /**
     * Updates the timeout duration for the connection
     */
    public updateTimeout(_duration: number): void {
        // No-op, AI agents don't need timeouts
    }

    /**
     * Refreshes the timeout (no-op for AI agents)
     */
    public refreshTimeout(): void {
        // No-op, AI agents don't need timeouts
    }

    /**
     * Checks if a message is duplicate (always returns false for AI agents)
     */
    public isDuplicate(_message: string): boolean {
        return false; // AI agents don't need duplicate message filtering
    }
} 