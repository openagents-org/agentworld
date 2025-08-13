# Mobs Reference

This document provides a comprehensive list of all mobs in the game, including their key names, display names, and key characteristics.

## Overview

The game contains **144 different mobs** ranging from basic creatures like rats and crabs to powerful bosses like dragons and elemental guardians. Mobs are defined in `/packages/server/data/mobs.json` and some have special behavior through plugins.

## Mob Classifications

### Basic Creatures (Level 1-20)
- **rat**: Rat - Basic starting mob with low stats
- **crab**: Crab - Coastal creature, defensive
- **bat**: Batterfly - Flying creature, slightly aggressive
- **wizard**: Wizard - Ranged magic attacker with projectiles
- **goblin**: Goblin - Mid-level humanoid
- **skeleton**: Spooky Skeleton - Undead warrior
- **snek**: Snek - Poisonous snake
- **cactus**: Cactus - Hidden name, always aggressive plant

### Mid-Level Enemies (Level 21-50)
- **ogre**: Ogre - Large humanoid with high defense
- **skeleton2**: Scary Skeleton - Stronger undead variant
- **spectre**: Spectre - Floating undead with magic resistance
- **eye**: Eye - Unique creature with special attacks
- **deathknight**: Death Knight - Heavy armored undead
- **adherer**: Dark Mage - High-level magic user
- **ant**: Worker Ant - Fast moving insect (has plugin)
- **beetle**: Beetle - High HP crusher
- **spider**: Spooder - Poisonous arachnid (has plugin)
- **babyspider**: Baby Spooder - Smaller spider variant

### Advanced Mobs (Level 51-100)
- **cowwarrior**: Cow Warrior - Armored bovine
- **rooster**: Angry Rooster - Aggressive bird
- **pirateskeleton**: Pirate Skeleton - Naval themed undead
- **greenpirateskeleton**: Green Pirate Skeleton
- **redpirateskeleton**: Red Pirate Skeleton  
- **blackpirateskeleton**: Blue Pirate Skeleton
- **blackwizard**: Dark Wizard - Advanced magic user
- **icewizard**: Ice Wizard - Freezing magic attacks
- **poisonspider**: Poison Spooder - Highly poisonous
- **firespider**: Fire Spooder - Fire damage dealer
- **blazespider**: Blaze Spooder - Enhanced fire spider
- **hellspider**: Hell Spooder - Ultimate spider variant
- **bluepreta**: Blue Preta - Special humanoid
- **cat**: Cat - Agile feline
- **clam**: Clam - Defensive shellfish
- **cobra**: Cobra - Deadly snake
- **crystalscorpion**: Crystal Scorpion - Crystalline arachnid

### Elemental & Mystical (Level 101+)
- **cursedhahoemask**: Cursed Hahoe Mask - Magical mask entity
- **curseddjangseung**: Cursed Djangseung - Mystical totem
- **darkogre**: Dark Ogre - Enhanced ogre variant
- **darkscorpion**: Dark Scorpion - Shadow arachnid
- **darkskeleton**: Dark Skeleton - Powerful undead
- **desertscorpion**: Desert Scorpion - Desert dwelling
- **devilkazya**: Devil Kazya - Demonic entity
- **earthworm**: Earthworm - Underground creature
- **flaredanceknight**: Flare Dance Knight - Fire warrior
- **frog**: Frog - Amphibious creature
- **ghostrider**: Ghost Rider - Spectral mount
- **goldgolem**: Gold Golem - Precious metal construct
- **golem**: Golem - Stone construct
- **icegolem**: Ice Golem - Frozen construct
- **livingarmor**: Living Armor - Animated equipment

### Fish & Aquatic
- **redfish**: Red Fish
- **yellowfish**: Yellow Fish  
- **greenfish**: Green Fish
- **hermitcrab**: Hermit Crab
- **mermaid**: Mermaid - Aquatic humanoid
- **mimic**: Mimic - Disguised treasure creature
- **squid**: Squid - Deep sea creature
- **seadragon**: Sea Dragon - Aquatic dragon
- **miniseadragon**: Mini Sea Dragon - Smaller variant

### Knights & Warriors
- **iceknight**: Ice Knight - Frozen warrior
- **miniiceknight1-5**: Mini Ice Knight variants
- **miniknight1-6**: Mini Knight variants
- **miniemperor**: Mini Emperor - Royal variant
- **infectedguard**: Infected Guard - Corrupted soldier
- **guardsword**: Guard (Sword) - Armed sentinel
- **guardmace**: Guard (Mace) - Mace wielding guard
- **redguard**: Red Guard - Elite warrior

### Mice & Small Creatures
- **redmouse**: Red Mouse
- **whitemouse**: White Mouse
- **yellowmouse**: Yellow Mouse
- **brownmouse**: Brown Mouse
- **icerat**: Ice Rat - Frozen rodent
- **icebat**: Ice Bat - Frozen flying creature
- **icecrab**: Ice Crab - Frozen crustacean

### Exotic & Unique
- **oldogre**: Old Ogre - Aged variant
- **orc**: Orc - Classic fantasy creature
- **pain**: Pain - Abstract entity
- **penguin**: Penguin - Arctic bird
- **pierrot**: Pierrot - Theatrical character
- **pinkelf**: Pink Elf - Magical humanoid
- **preta**: Preta - Hungry ghost
- **purplepreta**: Purple Preta - Variant ghost
- **yellowpreta**: Yellow Preta - Another variant
- **greencockroach**: Green Cockroach - Insect
- **redcockroach**: Red Cockroach - Variant insect
- **redelf**: Red Elf - Fire elf
- **skyelf**: Sky Elf - Aerial elf
- **snowelf**: Snow Elf - Ice elf
- **rhaphidophoridae**: Rhaphidophoridae - Cave cricket
- **rudolf**: Rudolf - Reindeer
- **santaelf**: Santa Elf - Holiday themed
- **scorpion**: Scorpion - Desert arachnid
- **slime**: Slime - Gelatinous creature
- **smalldevil**: Small Devil - Minor demon
- **snowman**: Snowman - Animated snow construct
- **rabbitman**: Rabbit Man - Anthropomorphic rabbit
- **snowrabbit**: Snow Rabbit - Arctic variant
- **snowwolf**: Snow Wolf - Arctic predator
- **icegoblin**: Ice Goblin - Frozen humanoid
- **soldierant**: Soldier Ant - Military insect
- **soybeanbug**: Soybean Bug - Agricultural pest
- **suicideghost**: Suicide Ghost - Dangerous spirit
- **vulture**: Vulture - Scavenging bird
- **icevulture**: Ice Vulture - Frozen scavenger
- **whitebear**: White Bear - Arctic predator
- **whitetiger**: White Tiger - Rare feline
- **wolf**: Wolf - Pack predator
- **darkwolf**: Dark Wolf - Shadow variant
- **yellowbat**: Yellow Bat - Colored variant
- **zombie**: Zombie - Undead humanoid
- **snowlady**: Snow Lady - Feminine snow construct
- **picklemob**: Pickle Mob - Food-based creature

## Boss Mobs (Special Plugins)

These mobs have custom plugins that provide special abilities and behaviors:

### **skeletonking** (Skeleton King)
- **Level**: 180+ (High-level boss)
- **Plugin**: `skeletonking`
- **Special Abilities**: 
  - Spawns skeleton minions when hit (1/4 chance)
  - Maximum of 6 minions
  - Minions spawn at fixed positions
- **Location**: Dungeon boss

### **ogrelord** (Ogre Lord)  
- **Level**: 185+ (High-level boss)
- **Plugin**: `ogrelord`
- **Special Abilities**:
  - Spawns minion waves at 50% and 25% health
  - First wave: Ogre minions
  - Second wave: Iron Ogre minions
  - Random combat dialogue every 15 seconds
- **Quotes**: "The great ogre lord will trample over you!", "No, do not touch my onions!", "Me smash you!"

### **piratecaptain** (Pirate Captain)
- **Level**: 175 (Elite boss)
- **Plugin**: `piratecaptain`
- **Special Abilities**:
  - Teleportation ability (1/12 chance when hit)
  - Spawns pirate skeleton minions (1/8 chance)
  - Transitions to ranged attacks after teleporting
  - Uses ice projectiles
- **Max Minions**: 8

### **queenant** (Queen Ant)
- **Level**: 200+ (Raid boss)  
- **Plugin**: `queenant`
- **Special Abilities**:
  - Spawns 4 worker ant minions at 50% health
  - Minions follow and heal the queen
  - Special ranged terror attacks (1/6 chance)
  - Area of effect attacks (1/12 chance during special)
- **Minion Behavior**: Ants heal the queen and follow her movements

### **hellhound** (Hell Hound)
- **Level**: 195+ (Elite boss)
- **Plugin**: `hellhound` 
- **Special Abilities**:
  - Spawns mixed minions when hit (1/6 chance)
  - Minion types: Dark Wolf or Black Wizard
  - Dynamic attack range (melee/ranged based on target)
  - Black wizard minions have extended range
- **Max Minions**: 8

### **forestdragon** (Forest Dragon)
- **Level**: 250+ (Raid boss)
- **Plugin**: `forestdragon`
- **Special Abilities**:
  - Special terror attacks (1/6 chance)
  - Dynamic combat style (melee vs ranged)
  - Fireball projectiles for ranged combat
  - Terror infliction with extended range

### **santa** (Santa)
- **Level**: 150+ (Holiday boss)
- **Plugin**: `santa`
- **Special Abilities**:
  - Self-healing at 50% health (33% of max HP)
  - Random gift projectiles (6 different types)
  - Area of effect attacks with gift6 projectile
  - Holiday-themed dialogue

### **ant** (Worker Ant)
- **Level**: 46 (Support mob)
- **Plugin**: `ant`
- **Special Abilities**:
  - Heals targeted mobs (35 HP healing)
  - Does not respond to player attacks
  - Used as minion by Queen Ant
  - Automatic healing intervals

### **spider** (Spooder)
- **Level**: 47 (Basic mob)
- **Plugin**: `spider`
- **Special Abilities**:
  - Basic plugin with default behavior
  - Poisonous attacks
  - No special combat mechanics

## Mob Characteristics

### Combat Stats
Each mob has the following combat statistics:
- **Hit Points**: Health/durability
- **Attack Level**: Offensive capability  
- **Defense Level**: Defensive capability
- **Level**: Overall mob difficulty
- **Attack Range**: Melee (1) or Ranged (2+)
- **Aggro Range**: Detection distance

### Special Properties
- **Aggressive**: Attacks players on sight
- **Always Aggressive**: Cannot be pacified
- **Roaming**: Moves around spawn area
- **Poisonous**: Inflicts poison on attack
- **Freezing**: Inflicts cold effects
- **Burning**: Inflicts fire effects
- **Hidden Name**: Name not displayed to players
- **Boss**: Major boss encounter
- **Miniboss**: Minor boss encounter

### Attack Types
- **Crush**: Blunt damage
- **Slash**: Slashing damage  
- **Stab**: Piercing damage
- **Archery**: Ranged physical damage
- **Magic**: Magical damage

### Defense Types
Mobs have resistance/weakness to all attack types. Negative values indicate weakness.

### Projectiles
Magic users and ranged mobs use various projectiles:
- `projectile-fireball`: Fire magic
- `projectile-iceball`: Ice magic  
- `projectile-terror`: Fear inducing
- `projectile-gift1-6`: Santa's gifts

## Plugin System

Mob plugins extend the default mob behavior with custom functionality:

### Default Plugin (`default.ts`)
- Base class for all mob plugins
- Provides minion spawning support
- Attack targeting and AoE utilities
- Health threshold checking (half/quarter health)

### Custom Plugin Features
- **Combat Callbacks**: Custom attack, hit, and death handling
- **Movement Override**: Special movement patterns
- **Minion Management**: Spawning and controlling subordinate mobs
- **Special Attacks**: Terror, AoE, status effects
- **Dialogue System**: Boss speech and taunts
- **Teleportation**: Advanced movement abilities

## Notes

- All mobs use the same base `Mob` class from `/packages/server/src/game/entity/character/mob/mob.ts`
- Mob data is loaded from `/packages/server/data/mobs.json`
- Plugin system allows for complex boss mechanics without modifying core mob code
- Drop tables and spawning locations are managed separately
- Combat formulas and damage calculations are handled by the Formulas system
