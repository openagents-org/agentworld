/**
 * Simulation module for stateless action simulation.
 * Allows simulating agent actions without requiring actual game sessions.
 * Used for automatic verification of task objectives.
 */

import { Modules } from '@kaetram/common/network';
import Utils from '@kaetram/common/util/utils';
import CraftingData from '../../data/crafting.json';
import Items from '../../data/items.json';
import Trees from '../../data/trees.json';
import Rocks from '../../data/rocks.json';
import Fishing from '../../data/fishing.json';
import Foraging from '../../data/foraging.json';
import Formulas from '../info/formulas';

import type World from '../game/world';

// ============================================================================
// Type Definitions
// ============================================================================

/**
 * Represents an item in inventory or equipment
 */
export interface SimulationItem {
    key: string;
    count: number;
}

/**
 * Complete agent state for simulation
 */
export interface SimulationState {
    // Position
    x: number;
    y: number;

    // Vitals
    hitPoints: number;
    maxHitPoints: number;
    mana: number;
    maxMana: number;
    level: number;
    dead: boolean;

    // Skills: skill type (number) -> experience (number)
    skills: { [skillType: number]: number };

    // Inventory: 25 slots, null means empty
    inventory: Array<SimulationItem | null>;

    // Equipment: slot type (number) -> item or null
    equipment: { [slotType: number]: SimulationItem | null };

    // Status effects
    poisoned: boolean;
    stunned: boolean;
}

/**
 * Action types for simulation
 */
export type SimulationAction =
    | { type: 'move'; x: number; y: number }
    | { type: 'craft'; skill: string; itemKey: string; count: number }
    | { type: 'collect'; resourceType: 'tree' | 'rock' | 'fish' | 'foraging'; resourceKey: string }
    | { type: 'attack'; targetInstance: string }
    | { type: 'equip'; inventoryIndex: number }
    | { type: 'unequip'; equipmentSlot: number }
    | { type: 'eat'; inventoryIndex: number }
    | { type: 'drop'; inventoryIndex: number; count?: number }
    | { type: 'use'; inventoryIndex: number }
    | { type: 'enter' };  // Enter warp/portal at current position

/**
 * Result of a simulation action
 */
export interface SimulationResult {
    success: boolean;
    message: string;
    state_after: SimulationState;
    // Additional info for specific actions
    details?: any;
}

/**
 * Environment observation at a position
 */
export interface SimulationObservation {
    location: {
        x: number;
        y: number;
        regionId: number;
        mapName: string;
    };
    map: {
        name: string;
        width: number;
        height: number;
        tileSize: number;
        version: number;
    };
    entries: Array<{
        x: number;
        y: number;
        destination: string;
        levelRequirement: number;
        distanceFrom: number;
    }>;
    mobs: Array<{
        instance: string;
        type: string;
        name: string;
        level: number;
        x: number;
        y: number;
        hitPoints: number;
        maxHitPoints: number;
        aggressive: boolean;
        distanceFrom: number;
    }>;
    resources: Array<{
        instance: string;
        type: number;
        resourceType: string;
        name: string;
        x: number;
        y: number;
        distanceFrom: number;
    }>;
    players: Array<{
        instance: string;
        name: string;
        level: number;
        x: number;
        y: number;
        rank: number;
        distanceFrom: number;
    }>;
    collisions: Array<{ x: number; y: number }>;
    doors: Array<{
        x: number;
        y: number;
        destX: number;
        destY: number;
        distanceFrom: number;
    }>;
    observationRadius: number;
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Calculate skill level from experience
 */
export function getSkillLevel(experience: number): number {
    return Formulas.expToLevel(experience);
}

/**
 * Calculate experience needed for a level
 */
export function getExperienceForLevel(level: number): number {
    return Formulas.LevelExp[level] || 0;
}

/**
 * Deep clone a simulation state
 */
export function cloneState(state: SimulationState): SimulationState {
    return {
        x: state.x,
        y: state.y,
        hitPoints: state.hitPoints,
        maxHitPoints: state.maxHitPoints,
        mana: state.mana,
        maxMana: state.maxMana,
        level: state.level,
        dead: state.dead,
        skills: { ...state.skills },
        inventory: state.inventory.map(item => item ? { ...item } : null),
        equipment: Object.fromEntries(
            Object.entries(state.equipment).map(([k, v]) => [k, v ? { ...v } : null])
        ),
        poisoned: state.poisoned,
        stunned: state.stunned
    };
}

/**
 * Validate simulation state structure
 */
export function validateState(state: any): { valid: boolean; error?: string } {
    if (!state || typeof state !== 'object') {
        return { valid: false, error: 'State must be an object' };
    }

    // Check required fields
    const requiredFields = ['x', 'y', 'hitPoints', 'maxHitPoints', 'level', 'skills', 'inventory', 'equipment'];
    for (const field of requiredFields) {
        if (state[field] === undefined) {
            return { valid: false, error: `Missing required field: ${field}` };
        }
    }

    // Validate inventory is array
    if (!Array.isArray(state.inventory)) {
        return { valid: false, error: 'Inventory must be an array' };
    }

    // Validate equipment is object
    if (typeof state.equipment !== 'object') {
        return { valid: false, error: 'Equipment must be an object' };
    }

    return { valid: true };
}

/**
 * Validate simulation action structure
 */
export function validateAction(action: any): { valid: boolean; error?: string } {
    if (!action || typeof action !== 'object') {
        return { valid: false, error: 'Action must be an object' };
    }

    if (!action.type) {
        return { valid: false, error: 'Action must have a type' };
    }

    const validTypes = ['move', 'craft', 'collect', 'attack', 'equip', 'unequip', 'eat', 'drop', 'use', 'enter'];
    if (!validTypes.includes(action.type)) {
        return { valid: false, error: `Invalid action type: ${action.type}. Valid types: ${validTypes.join(', ')}` };
    }

    return { valid: true };
}

/**
 * Find first empty inventory slot
 */
function findEmptySlot(inventory: Array<SimulationItem | null>): number {
    for (let i = 0; i < inventory.length; i++) {
        if (!inventory[i]) return i;
    }
    return -1;
}

/**
 * Count items in inventory by key
 */
function countItems(inventory: Array<SimulationItem | null>, key: string): number {
    let count = 0;
    for (const item of inventory) {
        if (item && item.key === key) {
            count += item.count;
        }
    }
    return count;
}

/**
 * Remove items from inventory
 */
function removeItems(inventory: Array<SimulationItem | null>, key: string, amount: number): boolean {
    let remaining = amount;

    for (let i = 0; i < inventory.length && remaining > 0; i++) {
        const item = inventory[i];
        if (item && item.key === key) {
            if (item.count <= remaining) {
                remaining -= item.count;
                inventory[i] = null;
            } else {
                item.count -= remaining;
                remaining = 0;
            }
        }
    }

    return remaining === 0;
}

/**
 * Add item to inventory
 */
function addItem(inventory: Array<SimulationItem | null>, key: string, count: number, maxStack: number = 2147483647): boolean {
    // First try to stack with existing items
    for (let i = 0; i < inventory.length; i++) {
        const item = inventory[i];
        if (item && item.key === key && item.count < maxStack) {
            const canAdd = Math.min(count, maxStack - item.count);
            item.count += canAdd;
            count -= canAdd;
            if (count === 0) return true;
        }
    }

    // Then try to find empty slots
    while (count > 0) {
        const slot = findEmptySlot(inventory);
        if (slot === -1) return false;

        const toAdd = Math.min(count, maxStack);
        inventory[slot] = { key, count: toAdd };
        count -= toAdd;
    }

    return true;
}

// ============================================================================
// Simulation Engine
// ============================================================================

export class SimulationEngine {
    constructor(private world: World) {}

    /**
     * Main simulation entry point
     */
    simulate(state: SimulationState, action: SimulationAction): SimulationResult {
        // Clone state to avoid modifying input
        const newState = cloneState(state);

        // Check if agent is dead
        if (newState.dead && action.type !== 'use') {
            return {
                success: false,
                message: 'Cannot perform action while dead',
                state_after: newState
            };
        }

        // Dispatch to appropriate handler
        switch (action.type) {
            case 'move':
                return this.simulateMove(newState, action.x, action.y);
            case 'craft':
                return this.simulateCraft(newState, action.skill, action.itemKey, action.count);
            case 'collect':
                return this.simulateCollect(newState, action.resourceType, action.resourceKey);
            case 'attack':
                return this.simulateAttack(newState, action.targetInstance);
            case 'equip':
                return this.simulateEquip(newState, action.inventoryIndex);
            case 'unequip':
                return this.simulateUnequip(newState, action.equipmentSlot);
            case 'eat':
                return this.simulateEat(newState, action.inventoryIndex);
            case 'drop':
                return this.simulateDrop(newState, action.inventoryIndex, action.count);
            case 'use':
                return this.simulateUse(newState, action.inventoryIndex);
            case 'enter':
                return this.simulateEnter(newState);
            default:
                return {
                    success: false,
                    message: `Unknown action type: ${(action as any).type}`,
                    state_after: newState
                };
        }
    }

    /**
     * Simulate movement to a position
     */
    private simulateMove(state: SimulationState, x: number, y: number): SimulationResult {
        // Check map bounds
        if (this.world.map.isOutOfBounds(x, y)) {
            return {
                success: false,
                message: `Position (${x}, ${y}) is out of map bounds`,
                state_after: state
            };
        }

        // Check collision
        if (this.world.map.isColliding(x, y)) {
            return {
                success: false,
                message: `Position (${x}, ${y}) is blocked by collision`,
                state_after: state
            };
        }

        // Update position
        const prevX = state.x;
        const prevY = state.y;
        state.x = x;
        state.y = y;

        return {
            success: true,
            message: `Moved from (${prevX}, ${prevY}) to (${x}, ${y})`,
            state_after: state,
            details: {
                previousPosition: { x: prevX, y: prevY },
                newPosition: { x, y },
                distance: Utils.getDistance(prevX, prevY, x, y)
            }
        };
    }

    /**
     * Simulate crafting an item
     */
    private simulateCraft(state: SimulationState, skillName: string, itemKey: string, count: number): SimulationResult {
        // Normalize skill name
        const normalizedSkill = skillName.toLowerCase();
        const craftingData = (CraftingData as any)[normalizedSkill];

        if (!craftingData) {
            return {
                success: false,
                message: `Invalid crafting skill: ${skillName}`,
                state_after: state
            };
        }

        const recipe = craftingData[itemKey];
        if (!recipe) {
            return {
                success: false,
                message: `Invalid item key: ${itemKey} for skill ${skillName}`,
                state_after: state
            };
        }

        // Get skill type for level check
        const skillTypeMap: { [key: string]: number } = {
            'smithing': Modules.Skills.Smithing,
            'cooking': Modules.Skills.Cooking,
            'crafting': Modules.Skills.Crafting,
            'alchemy': Modules.Skills.Magic,
            'fletching': Modules.Skills.Fletching,
            'smelting': Modules.Skills.Smithing
        };

        const skillType = skillTypeMap[normalizedSkill];
        if (skillType === undefined) {
            return {
                success: false,
                message: `Unknown skill type: ${skillName}`,
                state_after: state
            };
        }

        // Check skill level
        const skillExp = state.skills[skillType] || 0;
        const skillLevel = getSkillLevel(skillExp);

        if (skillLevel < recipe.level) {
            return {
                success: false,
                message: `Requires level ${recipe.level} ${skillName}, you have level ${skillLevel}`,
                state_after: state,
                details: {
                    requiredLevel: recipe.level,
                    currentLevel: skillLevel
                }
            };
        }

        // Check materials
        const missingMaterials: Array<{ key: string; required: number; available: number }> = [];
        for (const req of recipe.requirements) {
            const required = req.count * count;
            const available = countItems(state.inventory, req.key);

            if (available < required) {
                const itemData = (Items as any)[req.key];
                missingMaterials.push({
                    key: req.key,
                    required,
                    available
                });
            }
        }

        if (missingMaterials.length > 0) {
            return {
                success: false,
                message: 'Missing required materials',
                state_after: state,
                details: { missingMaterials }
            };
        }

        // Check inventory space for result
        const emptySlots = state.inventory.filter(i => !i).length;
        const resultCount = (recipe.count || 1) * count;

        // Remove materials
        for (const req of recipe.requirements) {
            removeItems(state.inventory, req.key, req.count * count);
        }

        // Add result item
        if (!addItem(state.inventory, itemKey, resultCount)) {
            return {
                success: false,
                message: 'Not enough inventory space for crafted items',
                state_after: state
            };
        }

        // Add experience
        const expGained = (recipe.experience || 0) * count;
        state.skills[skillType] = (state.skills[skillType] || 0) + expGained;

        return {
            success: true,
            message: `Crafted ${resultCount}x ${itemKey}`,
            state_after: state,
            details: {
                itemKey,
                count: resultCount,
                experienceGained: expGained,
                newSkillLevel: getSkillLevel(state.skills[skillType])
            }
        };
    }

    /**
     * Simulate resource collection
     */
    private simulateCollect(state: SimulationState, resourceType: string, resourceKey: string): SimulationResult {
        // Get resource data based on type
        let resourceData: any;
        let skillType: number;
        let itemKey: string;
        let experience: number;

        switch (resourceType) {
            case 'tree': {
                resourceData = (Trees as any)[resourceKey];
                skillType = Modules.Skills.Lumberjacking;
                break;
            }
            case 'rock': {
                resourceData = (Rocks as any)[resourceKey];
                skillType = Modules.Skills.Mining;
                break;
            }
            case 'fish': {
                resourceData = (Fishing as any)[resourceKey];
                skillType = Modules.Skills.Fishing;
                break;
            }
            case 'foraging': {
                resourceData = (Foraging as any)[resourceKey];
                skillType = Modules.Skills.Foraging;
                break;
            }
            default:
                return {
                    success: false,
                    message: `Invalid resource type: ${resourceType}`,
                    state_after: state
                };
        }

        if (!resourceData) {
            return {
                success: false,
                message: `Unknown ${resourceType} resource: ${resourceKey}`,
                state_after: state
            };
        }

        // Check skill level
        const skillExp = state.skills[skillType] || 0;
        const skillLevel = getSkillLevel(skillExp);
        const requiredLevel = resourceData.levelRequirement || 1;

        if (skillLevel < requiredLevel) {
            return {
                success: false,
                message: `Requires level ${requiredLevel} for this ${resourceType}, you have level ${skillLevel}`,
                state_after: state,
                details: {
                    requiredLevel,
                    currentLevel: skillLevel
                }
            };
        }

        // Check inventory space
        if (findEmptySlot(state.inventory) === -1) {
            return {
                success: false,
                message: 'Inventory is full',
                state_after: state
            };
        }

        // Get item and experience from resource
        itemKey = resourceData.item || resourceKey;
        experience = resourceData.experience || 10;

        // Add item to inventory
        addItem(state.inventory, itemKey, 1);

        // Add experience
        state.skills[skillType] = (state.skills[skillType] || 0) + experience;

        return {
            success: true,
            message: `Collected ${itemKey} from ${resourceKey}`,
            state_after: state,
            details: {
                resourceType,
                resourceKey,
                itemCollected: itemKey,
                experienceGained: experience,
                newSkillLevel: getSkillLevel(state.skills[skillType])
            }
        };
    }

    /**
     * Simulate attack (INFORMATIONAL ONLY)
     * Does not modify state, just returns info about potential attack
     */
    private simulateAttack(state: SimulationState, targetInstance: string): SimulationResult {
        // Find target entity
        const target = this.world.entities.get(targetInstance);

        if (!target) {
            return {
                success: false,
                message: `Target not found: ${targetInstance}`,
                state_after: state
            };
        }

        // Check if target is attackable
        if (!target.isMob() && !target.isPlayer()) {
            return {
                success: false,
                message: 'Target cannot be attacked',
                state_after: state
            };
        }

        // Calculate distance
        const distance = Utils.getDistance(state.x, state.y, target.x, target.y);

        // Get weapon info from equipment
        const weapon = state.equipment[Modules.Equipment.Weapon];
        const weaponData = weapon ? (Items as any)[weapon.key] : null;
        const attackRange = weaponData?.attackRange || 1;

        // Check if in range
        const inRange = distance <= attackRange;

        // Get target info
        const targetInfo = {
            instance: target.instance,
            name: target.name,
            level: target.level,
            x: target.x,
            y: target.y,
            hitPoints: target.hitPoints?.getHitPoints() || 0,
            maxHitPoints: target.hitPoints?.getMaxHitPoints() || 0,
            distance,
            inRange
        };

        // Estimate damage (simplified)
        const strengthLevel = getSkillLevel(state.skills[Modules.Skills.Strength] || 0);
        const accuracyLevel = getSkillLevel(state.skills[Modules.Skills.Accuracy] || 0);
        const weaponBonus = weaponData?.attackStats?.crush || weaponData?.attackStats?.slash || weaponData?.attackStats?.stab || 0;
        const estimatedMaxDamage = Math.floor((strengthLevel + weaponBonus) * 1.25);

        return {
            success: true,
            message: inRange
                ? `Can attack ${target.name} (estimated max damage: ${estimatedMaxDamage})`
                : `Target ${target.name} is out of range (${distance} tiles, need ${attackRange})`,
            state_after: state,  // State unchanged - attack is informational only
            details: {
                target: targetInfo,
                weapon: weapon ? { key: weapon.key, attackRange } : null,
                estimatedMaxDamage,
                yourStats: {
                    strengthLevel,
                    accuracyLevel
                }
            }
        };
    }

    /**
     * Simulate equipping an item from inventory
     */
    private simulateEquip(state: SimulationState, inventoryIndex: number): SimulationResult {
        // Validate index
        if (inventoryIndex < 0 || inventoryIndex >= state.inventory.length) {
            return {
                success: false,
                message: `Invalid inventory index: ${inventoryIndex}`,
                state_after: state
            };
        }

        const item = state.inventory[inventoryIndex];
        if (!item) {
            return {
                success: false,
                message: `No item at inventory index ${inventoryIndex}`,
                state_after: state
            };
        }

        // Get item data
        const itemData = (Items as any)[item.key];
        if (!itemData) {
            return {
                success: false,
                message: `Unknown item: ${item.key}`,
                state_after: state
            };
        }

        // Check if equippable
        if (!itemData.equippable) {
            return {
                success: false,
                message: `Item ${item.key} is not equippable`,
                state_after: state
            };
        }

        // Get equipment type
        const equipType = itemData.equipmentType;
        if (equipType === undefined) {
            return {
                success: false,
                message: `Item ${item.key} has no equipment type`,
                state_after: state
            };
        }

        // Check level requirement
        if (itemData.level && state.level < itemData.level) {
            return {
                success: false,
                message: `Requires level ${itemData.level} to equip ${item.key}`,
                state_after: state,
                details: {
                    requiredLevel: itemData.level,
                    currentLevel: state.level
                }
            };
        }

        // Swap with current equipment
        const currentEquip = state.equipment[equipType];

        // Remove from inventory
        state.inventory[inventoryIndex] = currentEquip;

        // Equip new item
        state.equipment[equipType] = { key: item.key, count: item.count };

        return {
            success: true,
            message: `Equipped ${item.key}${currentEquip ? `, unequipped ${currentEquip.key}` : ''}`,
            state_after: state,
            details: {
                equipped: item.key,
                unequipped: currentEquip?.key || null,
                slot: equipType
            }
        };
    }

    /**
     * Simulate unequipping an item
     */
    private simulateUnequip(state: SimulationState, equipmentSlot: number): SimulationResult {
        const equippedItem = state.equipment[equipmentSlot];

        if (!equippedItem) {
            return {
                success: false,
                message: `No item equipped in slot ${equipmentSlot}`,
                state_after: state
            };
        }

        // Check inventory space
        const emptySlot = findEmptySlot(state.inventory);
        if (emptySlot === -1) {
            return {
                success: false,
                message: 'Inventory is full',
                state_after: state
            };
        }

        // Move to inventory
        state.inventory[emptySlot] = { key: equippedItem.key, count: equippedItem.count };
        state.equipment[equipmentSlot] = null;

        return {
            success: true,
            message: `Unequipped ${equippedItem.key}`,
            state_after: state,
            details: {
                unequipped: equippedItem.key,
                slot: equipmentSlot,
                inventoryIndex: emptySlot
            }
        };
    }

    /**
     * Simulate eating an item
     */
    private simulateEat(state: SimulationState, inventoryIndex: number): SimulationResult {
        // Validate index
        if (inventoryIndex < 0 || inventoryIndex >= state.inventory.length) {
            return {
                success: false,
                message: `Invalid inventory index: ${inventoryIndex}`,
                state_after: state
            };
        }

        const item = state.inventory[inventoryIndex];
        if (!item) {
            return {
                success: false,
                message: `No item at inventory index ${inventoryIndex}`,
                state_after: state
            };
        }

        // Get item data
        const itemData = (Items as any)[item.key];
        if (!itemData) {
            return {
                success: false,
                message: `Unknown item: ${item.key}`,
                state_after: state
            };
        }

        // Check if edible
        if (!itemData.edible) {
            return {
                success: false,
                message: `Item ${item.key} is not edible`,
                state_after: state
            };
        }

        // Get healing amount
        const healAmount = itemData.healAmount || itemData.heal || 10;
        const prevHP = state.hitPoints;

        // Apply healing
        state.hitPoints = Math.min(state.hitPoints + healAmount, state.maxHitPoints);
        const actualHeal = state.hitPoints - prevHP;

        // Remove item (decrement count)
        if (item.count <= 1) {
            state.inventory[inventoryIndex] = null;
        } else {
            item.count--;
        }

        // If was dead and healed, revive
        if (state.dead && state.hitPoints > 0) {
            state.dead = false;
        }

        return {
            success: true,
            message: `Ate ${item.key}, healed ${actualHeal} HP`,
            state_after: state,
            details: {
                item: item.key,
                healAmount: actualHeal,
                previousHP: prevHP,
                currentHP: state.hitPoints
            }
        };
    }

    /**
     * Simulate dropping an item
     */
    private simulateDrop(state: SimulationState, inventoryIndex: number, count?: number): SimulationResult {
        // Validate index
        if (inventoryIndex < 0 || inventoryIndex >= state.inventory.length) {
            return {
                success: false,
                message: `Invalid inventory index: ${inventoryIndex}`,
                state_after: state
            };
        }

        const item = state.inventory[inventoryIndex];
        if (!item) {
            return {
                success: false,
                message: `No item at inventory index ${inventoryIndex}`,
                state_after: state
            };
        }

        const dropCount = count || item.count;

        if (dropCount > item.count) {
            return {
                success: false,
                message: `Cannot drop ${dropCount} items, only have ${item.count}`,
                state_after: state
            };
        }

        // Remove items
        if (dropCount >= item.count) {
            state.inventory[inventoryIndex] = null;
        } else {
            item.count -= dropCount;
        }

        return {
            success: true,
            message: `Dropped ${dropCount}x ${item.key}`,
            state_after: state,
            details: {
                item: item.key,
                count: dropCount
            }
        };
    }

    /**
     * Simulate using an item (potions, etc.)
     */
    private simulateUse(state: SimulationState, inventoryIndex: number): SimulationResult {
        // Validate index
        if (inventoryIndex < 0 || inventoryIndex >= state.inventory.length) {
            return {
                success: false,
                message: `Invalid inventory index: ${inventoryIndex}`,
                state_after: state
            };
        }

        const item = state.inventory[inventoryIndex];
        if (!item) {
            return {
                success: false,
                message: `No item at inventory index ${inventoryIndex}`,
                state_after: state
            };
        }

        // Get item data
        const itemData = (Items as any)[item.key];
        if (!itemData) {
            return {
                success: false,
                message: `Unknown item: ${item.key}`,
                state_after: state
            };
        }

        // Check if edible (food/potion)
        if (itemData.edible) {
            return this.simulateEat(state, inventoryIndex);
        }

        // Check for mana potion
        if (itemData.manaAmount || itemData.mana) {
            const manaAmount = itemData.manaAmount || itemData.mana || 10;
            const prevMana = state.mana;

            state.mana = Math.min(state.mana + manaAmount, state.maxMana);
            const actualMana = state.mana - prevMana;

            // Remove item
            if (item.count <= 1) {
                state.inventory[inventoryIndex] = null;
            } else {
                item.count--;
            }

            return {
                success: true,
                message: `Used ${item.key}, restored ${actualMana} mana`,
                state_after: state,
                details: {
                    item: item.key,
                    manaRestored: actualMana,
                    previousMana: prevMana,
                    currentMana: state.mana
                }
            };
        }

        // Item has no use effect
        return {
            success: false,
            message: `Item ${item.key} cannot be used`,
            state_after: state
        };
    }

    /**
     * Simulate entering a door/portal at current position
     * Doors teleport you to another location (destination door)
     */
    private simulateEnter(state: SimulationState): SimulationResult {
        const playerX = state.x;
        const playerY = state.y;

        // First, check for doors at the current position
        // Doors are indexed by tile index (y * width + x)
        const tileIndex = playerY * this.world.map.width + playerX;
        const door = this.world.map.doors[tileIndex];

        if (door) {
            // Found a door - teleport to destination
            const prevX = state.x;
            const prevY = state.y;
            state.x = door.x;
            state.y = door.y;

            return {
                success: true,
                message: `Entered door`,
                state_after: state,
                details: {
                    type: 'door',
                    previousPosition: { x: prevX, y: prevY },
                    newPosition: { x: door.x, y: door.y },
                    orientation: door.orientation
                }
            };
        }

        // Second, check for warps at the current position
        // Warps are spawn areas - entering means teleporting to a random spot in the warp area
        let foundWarp: any = null;
        for (const warp of this.world.map.warps) {
            // Check if the player is within the warp area
            const inWarpX = playerX >= warp.x && playerX < (warp.x + (warp.width || 1));
            const inWarpY = playerY >= warp.y && playerY < (warp.y + (warp.height || 1));

            if (inWarpX && inWarpY) {
                foundWarp = warp;
                break;
            }
        }

        // If no door or warp found at current position
        if (!foundWarp) {
            return {
                success: false,
                message: 'No entry point (door or warp) found at the current position',
                state_after: state,
                details: {
                    position: { x: playerX, y: playerY }
                }
            };
        }

        // Check if player meets level requirement for the warp
        if (foundWarp.level && state.level < foundWarp.level) {
            return {
                success: false,
                message: `Level ${foundWarp.level} required to enter this area`,
                state_after: state,
                details: {
                    playerLevel: state.level,
                    requiredLevel: foundWarp.level,
                    warpName: foundWarp.name || foundWarp.id
                }
            };
        }

        // For warps, you're already in the warp area - this is informational
        // In the actual game, using /warp command teleports you to a warp
        // But standing on a warp doesn't do anything special
        return {
            success: true,
            message: `At warp location: ${foundWarp.name || foundWarp.id}`,
            state_after: state,
            details: {
                type: 'warp',
                warpId: foundWarp.id,
                warpName: foundWarp.name || foundWarp.id,
                position: { x: playerX, y: playerY },
                warpArea: {
                    x: foundWarp.x,
                    y: foundWarp.y,
                    width: foundWarp.width || 1,
                    height: foundWarp.height || 1
                },
                levelRequirement: foundWarp.level || 0
            }
        };
    }

    /**
     * Get environment observation at a position
     */
    getEnvironmentAtPosition(x: number, y: number, radius: number = 64): SimulationObservation {
        // Location info
        const location = {
            x,
            y,
            regionId: this.world.map.regions.getRegion(x, y),
            mapName: 'World'
        };

        // Map info
        const map = {
            name: 'World',
            width: this.world.map.width,
            height: this.world.map.height,
            tileSize: this.world.map.tileSize,
            version: this.world.map.version
        };

        // Entries/warps
        const entries: SimulationObservation['entries'] = [];
        for (const warp of this.world.map.warps) {
            entries.push({
                x: warp.x,
                y: warp.y,
                destination: warp.name || 'Unknown',
                levelRequirement: warp.level || 0,
                distanceFrom: Utils.getDistance(x, y, warp.x, warp.y)
            });
        }

        // Nearby mobs
        const mobs: SimulationObservation['mobs'] = [];
        this.world.getGrids().forEachEntityNear(
            x,
            y,
            (entity) => {
                if (!entity.isMob()) return;

                const distance = Utils.getDistance(x, y, entity.x, entity.y);
                if (distance <= radius) {
                    mobs.push({
                        instance: entity.instance,
                        type: entity.type,
                        name: entity.name,
                        level: entity.level,
                        x: entity.x,
                        y: entity.y,
                        hitPoints: entity.hitPoints?.getHitPoints() || 0,
                        maxHitPoints: entity.hitPoints?.getMaxHitPoints() || 0,
                        aggressive: (entity as any).aggressive || false,
                        distanceFrom: distance
                    });
                }
            },
            radius
        );

        // Resources
        const resources: SimulationObservation['resources'] = [];

        // Trees
        const trees = this.world.globals.getTrees();
        for (const instance in trees.getResources()) {
            const resource = trees.getResources()[instance];
            const distance = Utils.getDistance(x, y, resource.x, resource.y);

            if (distance <= radius && resource.state === 0) {
                resources.push({
                    instance: resource.instance,
                    type: 10,
                    resourceType: 'tree',
                    name: resource.type.charAt(0).toUpperCase() + resource.type.slice(1) + ' Tree',
                    x: resource.x,
                    y: resource.y,
                    distanceFrom: distance
                });
            }
        }

        // Rocks
        const rocks = this.world.globals.getRocks();
        for (const instance in rocks.getResources()) {
            const resource = rocks.getResources()[instance];
            const distance = Utils.getDistance(x, y, resource.x, resource.y);

            if (distance <= radius && resource.state === 0) {
                resources.push({
                    instance: resource.instance,
                    type: 10,
                    resourceType: 'rock',
                    name: resource.type.charAt(0).toUpperCase() + resource.type.slice(1) + ' Rock',
                    x: resource.x,
                    y: resource.y,
                    distanceFrom: distance
                });
            }
        }

        // Fishing spots
        const fishSpots = this.world.globals.getFishingSpots();
        for (const instance in fishSpots.getResources()) {
            const resource = fishSpots.getResources()[instance];
            const distance = Utils.getDistance(x, y, resource.x, resource.y);

            if (distance <= radius && resource.state === 0) {
                resources.push({
                    instance: resource.instance,
                    type: 10,
                    resourceType: 'fish',
                    name: 'Fishing Spot',
                    x: resource.x,
                    y: resource.y,
                    distanceFrom: distance
                });
            }
        }

        // Foraging
        const foraging = this.world.globals.getForaging();
        for (const instance in foraging.getResources()) {
            const resource = foraging.getResources()[instance];
            const distance = Utils.getDistance(x, y, resource.x, resource.y);

            if (distance <= radius && resource.state === 0) {
                resources.push({
                    instance: resource.instance,
                    type: 10,
                    resourceType: 'foraging',
                    name: resource.type.charAt(0).toUpperCase() + resource.type.slice(1) + ' Plant',
                    x: resource.x,
                    y: resource.y,
                    distanceFrom: distance
                });
            }
        }

        // Nearby players
        const players: SimulationObservation['players'] = [];
        this.world.getGrids().forEachEntityNear(
            x,
            y,
            (entity) => {
                if (!entity.isPlayer()) return;

                const distance = Utils.getDistance(x, y, entity.x, entity.y);
                if (distance <= radius) {
                    players.push({
                        instance: entity.instance,
                        name: entity.name,
                        level: entity.level,
                        x: entity.x,
                        y: entity.y,
                        rank: (entity as any).rank || 0,
                        distanceFrom: distance
                    });
                }
            },
            radius
        );

        // Collisions (5x5 grid)
        const collisions: Array<{ x: number; y: number }> = [];
        for (let cy = y - 5; cy <= y + 5; cy++) {
            for (let cx = x - 5; cx <= x + 5; cx++) {
                if (this.world.map.isColliding(cx, cy)) {
                    collisions.push({ x: cx, y: cy });
                }
            }
        }

        // Nearby doors (teleporters)
        const doors: SimulationObservation['doors'] = [];
        const mapWidth = this.world.map.width;
        for (const [indexStr, door] of Object.entries(this.world.map.doors)) {
            const index = parseInt(indexStr);
            const doorX = index % mapWidth;
            const doorY = Math.floor(index / mapWidth);
            const distance = Utils.getDistance(x, y, doorX, doorY);

            if (distance <= radius) {
                doors.push({
                    x: doorX,
                    y: doorY,
                    destX: (door as any).x,
                    destY: (door as any).y,
                    distanceFrom: distance
                });
            }
        }

        return {
            location,
            map,
            entries,
            mobs,
            resources,
            players,
            collisions,
            doors,
            observationRadius: radius
        };
    }
}
