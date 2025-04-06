import log from '@kaetram/common/util/log';
import Utils from '@kaetram/common/util/utils';
import Player from '../game/entity/character/player/player';

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
        
        log.info(`Created AI connection for: ${this.username}`);
        
        // Automatically mark the player as ready after a short delay
        // This prevents the readyTimeout from rejecting the connection
        setTimeout(() => {
            if (this.player && !this.closed) {
                this.player.ready = true;
                
                // Clear the readyTimeout to prevent rejection
                if (this.player.readyTimeout) {
                    clearTimeout(this.player.readyTimeout);
                    this.player.readyTimeout = null;
                }
                
                // Update the player's state
                this.player.updateRegion();
                this.player.updateEntities();
                this.player.updateEntityList();
                
                log.info(`AI agent ${this.username} is now ready`);
            }
        }, 1000);
    }

    /**
     * Sends a message to the AI agent (no-op since there's no actual socket)
     */
    public send(message: unknown): void {
        // No-op, AI agents don't need to receive messages
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
} 