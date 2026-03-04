import Creator from './creator';
import Loader from './loader';

import Filter from '@kaetram/common/util/filter';
import log from '@kaetram/common/util/log';
import config from '@kaetram/common/config';
import bcryptjs from 'bcryptjs';
import { MongoClient } from 'mongodb';

import type { Db } from 'mongodb';
import type { PlayerInfo } from './creator';
import type { Modules } from '@kaetram/common/network';
import type Player from '@kaetram/server/src/game/entity/character/player/player';
import type {
    MobAggregate,
    PvpAggregate,
    SkillExperience,
    TotalExperience,
    TotalMobKillsAggregate,
    TotalGoldAggregate
} from '@kaetram/common/types/leaderboards';

export default class MongoDB {
    private connectionUrl: string;

    private database!: Db;

    public loader!: Loader;
    public creator!: Creator;

    public readyCallback?: () => void;
    public failCallback?: (error: Error) => void;

    public constructor(
        host: string,
        port: number,
        username: string,
        password: string,
        private databaseName: string,
        private tls: boolean,
        srv: boolean,
        authSource: string
    ) {
        let srvInsert = srv ? 'mongodb+srv' : 'mongodb',
            authInsert = username && password ? `${username}:${password}@` : '',
            portInsert = port > 0 ? `:${port}` : '',
            authSourceInsert = authSource ? `?authSource=${authSource}` : '';
        this.connectionUrl = `${srvInsert}://${authInsert}${host}${portInsert}/${databaseName}${authSourceInsert}`;

        // Attempt to connect to MongoDB.
        this.createConnection();
    }

    /**
     * Attempts to connect to MongoDB. Times out after 10 seconds if
     * no MongoDB server is present for the given host.
     */

    private createConnection(): void {
        let client = new MongoClient(this.connectionUrl, {
            connectTimeoutMS: 5000,
            serverSelectionTimeoutMS: 5000,
            wtimeoutMS: 10,
            tls: this.tls
        });

        client.connect((error: Error | undefined, _client: MongoClient | undefined) => {
            if (error) {
                // Initializes an empty loader controller.
                this.loader = new Loader();
                return this.failCallback?.(error);
            }

            this.database = _client!.db(this.databaseName);

            this.loader = new Loader(this.database);
            this.creator = new Creator(this.database);

            this.readyCallback?.();

            log.notice('Successfully connected to the MongoDB server.');
        });
    }

    /**
     * Takes the player's username and extracts the data from the server. Checks
     * the password and creates a callback if an error is present.
     * @param player The player object to extract password and username from.
     */

    public login(player: Player): void {
        if (!this.hasDatabase()) return;

        let cursor = this.database
            .collection<PlayerInfo>('player_info')
            .find({ username: player.username });

        cursor.toArray().then((playerInfo) => {
            // Reject if we cannot find any data about the player.
            if (playerInfo.length === 0) player.connection.reject('invalidlogin');
            else {
                let [info] = playerInfo;

                bcryptjs.compare(player.password, info.password, (error: Error | null, result) => {
                    if (error) throw error;

                    // Reject if the password is incorrect.
                    if (!result) return player.connection.reject('invalidlogin');

                    // Successfully passed login checks, we can send packets now.
                    player.authenticated = true;

                    // Login successful, load player data.
                    player.load(info);
                });
            }
        });
    }

    /**
     * Attempts to load existing AI character data from the database without password verification.
     * This is specifically for AI agents that don't require password authentication.
     * @param player The AI player object to load data for.
     * @param callback Function called with success status and player info if found.
     */

    public loginAI(player: Player, callback: (success: boolean, playerInfo?: PlayerInfo) => void): void {
        if (!this.hasDatabase()) return callback(false);

        let cursor = this.database
            .collection<PlayerInfo>('player_info')
            .find({ username: player.username });

        cursor.toArray().then((playerInfo) => {
            if (playerInfo.length === 0) {
                // No existing character found
                callback(false);
            } else {
                // Found existing character
                let [info] = playerInfo;
                callback(true, info);
            }
        }).catch((error) => {
            log.error(`Error querying database for AI character ${player.username}: ${error}`);
            callback(false);
        });
    }

    /**
     * Creates a new user and adds it to the database.
     * @param player Basic information about the player such as username, password, and email.
     */

    public register(player: Player): void {
        if (!this.hasDatabase()) return;

        // Verify account credentials for input validity and ensure username isn't profane.
        if (!Creator.verifyPlayer(player) || Filter.isProfane(player.username))
            return player.connection.reject('invalidinput');

        let collection = this.database.collection<PlayerInfo>('player_info'),
            usernameCursor = collection.find({ username: player.username }),
            emailCursor = collection.find({ email: player.email });

        // Check if email exists.
        emailCursor.toArray().then((emailData) => {
            // If email exists and is specified by player, we check database for duplicates and reject if that's the case.
            if (emailData.length > 0 && player.email !== '')
                return player.connection.reject('emailexists');

            // Check if username exists.
            usernameCursor.toArray().then((playerInfo) => {
                // User exists and so we reject instead of double registering.
                if (playerInfo.length > 0) return player.connection.reject('userexists');

                // Successfully managed to create a new user.
                player.authenticated = true;

                log.debug(`No player data found for ${player.username}, creating user.`);

                player.statistics.creationTime = Date.now();

                player.load(Creator.serializePlayer(player));
            });
        });
    }

    /**
     * Checks whether or not the username exists in the database.
     * @param username The username to check for.
     * @param callback Contains the result of the check.
     */

    public exists(username: string, callback: (exists: boolean) => void): void {
        if (!this.hasDatabase()) return;

        let cursor = this.database.collection('player_info').find({ username });

        cursor.toArray().then((playerInfo) => {
            callback(playerInfo.length > 0);
        });
    }

    /**
     * Removes a guild from our database.
     * @param identifier The identifier of the guild to remove.
     */

    public deleteGuild(identifier: string): void {
        if (!this.hasDatabase()) return;

        let collection = this.database.collection('guilds');

        collection.deleteOne({ identifier });
    }

    /**
     * Sets a rank of a player in the database. For use when the player is offline.
     * @param username The username of the player.
     * @param rankId The rank id of the player (relative to the Modules enum).
     */

    public setRank(username: string, rankId: number): void {
        if (!this.hasDatabase()) return;

        let collection = this.database.collection('player_info');

        collection
            .find({ username })
            .toArray()
            .then((info) => {
                if (info.length === 0)
                    return log.warning(`No player found with the username ${username}.`);

                collection.updateOne(
                    { username },
                    {
                        $set: {
                            rank: rankId
                        }
                    },
                    { upsert: true }
                );
            });
    }

    /**
     * Checks the amount of players registered and returns it in the form of a callback.
     * @param callback Returns the number of players registered.
     */

    public registeredCount(callback: (count: number) => void): void {
        if (!this.hasDatabase()) return;

        let collection = this.database.collection('player_info');

        collection.countDocuments().then((count) => {
            callback(count);
        });
    }

    /**
     * Uses MongoDB aggregations to extract the total experience from
     * each of the players. The data is then sorted in descending order.
     */

    public getTotalExperienceAggregate(
        callback: (totalExperience: TotalExperience[]) => void
    ): void {
        if (!this.hasDatabase()) return;

        let skills = this.database.collection('player_skills');

        // Unwinds array, groups by total experience, sorts in descending order.
        skills
            .aggregate([
                { $unwind: '$skills' }, // Unwinds (transforms into multiple objects for each skill).
                {
                    $group: {
                        _id: '$username',
                        experience: { $sum: '$skills.experience' },
                        cheater: { $first: '$cheater' }
                    }
                },
                { $sort: { experience: -1 } },
                { $limit: 150 }
            ])
            .toArray()
            .then((data) => callback(data as TotalExperience[]));
    }

    /**
     * Aggregates data for a specific skill. The data is then sorted in descending order.
     * @param skill The skill to aggregate data for.
     * @param callback Contains a list of players and their experience for the skill.
     */

    public getSkillAggregate(
        skill: Modules.Skills,
        callback: (experience: SkillExperience[]) => void
    ): void {
        if (!this.hasDatabase()) return;

        let skills = this.database.collection('player_skills');

        // Unwind the array, match the skill, sort in descending order, limit to 250.
        skills
            .aggregate([
                { $unwind: '$skills' },
                { $match: { 'skills.type': skill } },
                {
                    $group: {
                        _id: '$username',
                        experience: { $first: '$skills.experience' },
                        cheater: { $first: '$cheater' }
                    }
                },
                { $sort: { experience: -1 } },
                { $limit: 150 }
            ])
            .toArray()
            .then((data) => callback(data as SkillExperience[]));
    }

    /**
     * Gathers the aggregate data (in descending order) for the mob specified.
     * @param key The mob key to gather data for.
     * @param callback Contains aggregate data for the mob.
     */

    public getMobAggregate(key: string, callback: (data: MobAggregate[]) => void): void {
        if (!this.hasDatabase()) return;

        let mobs = this.database.collection('player_statistics');

        mobs.aggregate([
            {
                $group: {
                    _id: '$username',
                    kills: { $sum: `$mobKills.${key}` },
                    cheater: { $first: '$cheater' }
                }
            },
            { $sort: { kills: -1 } },
            { $limit: 150 }
        ])
            .toArray()
            .then((data) => callback(data as MobAggregate[]));
    }

    /**
     * Gathers the aggregate data (in descending order) for the pvp kills.
     * @param callback Contains aggregate data for the pvp kills.
     */

    public getPvpAggregate(callback: (data: PvpAggregate[]) => void): void {
        if (!this.hasDatabase()) return;

        let pvp = this.database.collection('player_statistics');

        pvp.aggregate([
            {
                $group: {
                    _id: '$username',
                    kills: { $sum: '$pvpKills' },
                    cheater: { $first: '$cheater' }
                }
            },
            { $sort: { kills: -1 } },
            { $limit: 150 }
        ])
            .toArray()
            .then((data) => callback(data as PvpAggregate[]));
    }

    /**
     * Aggregates total mob kills across all mob types per player.
     * @param callback Contains aggregate data for total mob kills.
     */

    public getTotalMobKillsAggregate(callback: (data: TotalMobKillsAggregate[]) => void): void {
        if (!this.hasDatabase()) return;

        let stats = this.database.collection('player_statistics');

        stats.aggregate([
            {
                $project: {
                    username: 1,
                    cheater: 1,
                    killsArray: { $objectToArray: { $ifNull: ['$mobKills', {}] } }
                }
            },
            { $unwind: { path: '$killsArray', preserveNullAndEmptyArrays: true } },
            {
                $group: {
                    _id: '$username',
                    totalKills: { $sum: { $ifNull: ['$killsArray.v', 0] } },
                    cheater: { $first: '$cheater' }
                }
            },
            { $match: { totalKills: { $gt: 0 } } },
            { $sort: { totalKills: -1 } },
            { $limit: 150 }
        ])
            .toArray()
            .then((data) => callback(data as TotalMobKillsAggregate[]));
    }

    /**
     * Aggregates total gold from player inventories.
     * @param callback Contains aggregate data for total gold.
     */

    public getTotalGoldAggregate(callback: (data: TotalGoldAggregate[]) => void): void {
        if (!this.hasDatabase()) return;

        let inventory = this.database.collection('player_inventory');

        inventory.aggregate([
            { $unwind: '$slots' },
            { $match: { 'slots.key': 'gold' } },
            {
                $group: {
                    _id: '$username',
                    totalGold: { $sum: '$slots.count' }
                }
            },
            { $match: { totalGold: { $gt: 0 } } },
            { $sort: { totalGold: -1 } },
            { $limit: 150 }
        ])
            .toArray()
            .then((data) => callback(data as TotalGoldAggregate[]));
    }

    /**
     * Checks whether or not a connection has been established.
     * @returns If the database element is present.
     */

    private hasDatabase(): boolean {
        if (!this.database) log.error('No connection established for the database.');

        return !!this.database;
    }

    /**
     * Callback signal if connection is successfully established.
     */

    public onReady(callback: () => void): void {
        this.readyCallback = callback;
    }

    /**
     * Callback for connection failure.
     */

    public onFail(callback: (error: Error) => void): void {
        this.failCallback = callback;
    }

    /**
     * Checks if an IP address is banned.
     * @param ip The IP address to check.
     * @param callback Callback function that receives a boolean indicating if the IP is banned.
     */

    public isIpBanned(ip: string, callback: (banned: boolean) => void): void {
        // Used for when we're working without a database.
        if (!this.database || config.skipDatabase) return callback(false);

        this.database
            .collection('ip_bans')
            .findOne({ ip }, (error, result) => {
                if (error) {
                    log.error(`Error checking IP ban for ${ip}: ${error}`);
                    return callback(false);
                }

                // Check if the IP is banned and if the ban hasn't expired
                if (result && (!result.expiry || result.expiry > Date.now())) {
                    return callback(true);
                }

                callback(false);
            });
    }

    /**
     * Sets or removes an IP ban.
     * @param ip The IP address to ban/unban.
     * @param banned Whether to ban (true) or unban (false) the IP.
     * @param duration Optional duration in milliseconds. If not provided, ban is permanent.
     */

    public setIpBan(ip: string, banned: boolean, duration?: number): void {
        // Used for when we're working without a database.
        if (!this.database || config.skipDatabase) return;

        if (banned) {
            let banData: { ip: string; timestamp: number; expiry?: number } = {
                ip,
                timestamp: Date.now()
            };

            // Add expiry if duration is provided
            if (duration) banData.expiry = Date.now() + duration;

            this.database.collection('ip_bans').updateOne(
                { ip },
                { $set: banData },
                { upsert: true },
                (error) => {
                    if (error) log.error(`Error setting IP ban for ${ip}: ${error}`);
                    else log.info(`IP ${ip} has been banned.`);
                }
            );
        } else {
            this.database.collection('ip_bans').deleteOne({ ip }, (error) => {
                if (error) log.error(`Error removing IP ban for ${ip}: ${error}`);
                else log.info(`IP ${ip} has been unbanned.`);
            });
        }
    }
}
