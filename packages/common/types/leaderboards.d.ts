export interface TotalExperience {
    username: string;
    totalExperience: number;
    cheater?: boolean;
}

export interface SkillExperience {
    username: string;
    experience: number;
    cheater?: boolean;
}

export interface MobAggregate {
    username: string;
    kills: number;
}

export interface PvpAggregate {
    username: string;
    pvpKills: number;
}

export interface TotalMobKillsAggregate {
    username: string;
    totalKills: number;
}

export interface TotalGoldAggregate {
    username: string;
    totalGold: number;
}
