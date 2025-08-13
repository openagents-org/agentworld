# AgentWorld Map Guide

![MPL-2.0 License](https://img.shields.io/github/license/Kaetram/Kaetram-Open) 

This document describes the world layout and regions of AgentWorld, providing guidance for both players and AI agents navigating the game environment.

## World Overview

AgentWorld features a diverse 2D world measuring **1056 x 768 tiles** (16 pixels per tile), divided into multiple distinct regions connected by paths, warps, and secret passages. The world is designed as a fantasy RPG environment with varied biomes and difficulty progressions.

## Core Regions

### 1. Central Kingdom 
**Location**: Center of the map (≈500-600, 300-400)  
**Typical Coordinates**: (528, 384)  
**Description**: The heart of civilization featuring the royal castle, main village, and starting areas for new players. Contains shops, NPCs, and tutorial areas.

**Key Features**:
- **Royal Castle**: Home to the King, guards, and royal court
- **Main Village**: Starting town with essential NPCs (Clerk, Banker, various vendors)
- **Tutorial Area**: Safe zone for new player orientation
- **Market Square**: Central trading hub with multiple shops

**Notable NPCs**: King, Royal Guards, Clerk, Banker, Enchantment Vendor, Kosmetics Vendor

### 2. Western Forest Region
**Location**: West of Central Kingdom (≈100-400, 200-500)  
**Typical Coordinates**: (250, 350)  
**Description**: Dense woodland area perfect for early-level training and resource gathering. Features tree logging areas and basic mob encounters.

**Key Features**:
- **Logging Areas**: Oak and other tree types for woodcutting
- **Forest Clearings**: Combat training areas
- **Forester's Cabin**: NPC shop and quest hub

**Notable NPCs**: Forester, Village Girls  
**Common Mobs**: Rats (Level 1), Bats (Level 4), Goblins (Level 7)

### 3. Eastern Coastal Region  
**Location**: Eastern edge of the map (≈800-1056, 200-600)  
**Typical Coordinates**: (900, 400)  
**Description**: Beach and coastal areas with water-based activities, fishing spots, and access to underwater regions.

**Key Features**:
- **Sandy Beaches**: Starting areas with crabs and basic mobs
- **Fishing Spots**: Resource gathering for food and crafting
- **Secret Cave Entrance**: Hidden access to underwater areas
- **Underwater Realm**: Accessed via secret beach entrance

**Notable NPCs**: Bubba (Beach NPC), Secret Agent, Fisherman, Mermaid, Sea Cucumber  
**Common Mobs**: Crabs (Level 1), Water Guardian (Level 36), Sea creatures

### 4. Northern Mountain Range
**Location**: Northern border (≈200-800, 0-200)  
**Typical Coordinates**: (500, 100)  
**Description**: High-altitude regions with challenging terrain, crafting opportunities, and cold-weather zones requiring special equipment.

**Key Features**:
- **Mountain Peaks**: High-elevation areas with scenic views
- **Crafting Areas**: Access to advanced crafting benches
- **Ice Caves**: Frozen caverns with ice-themed challenges
- **Mountain Villages**: Cold-weather settlements

**Notable NPCs**: Old Lady (Crafts), Sherpa, Ice Elf, Angel, Archangel  
**Common Mobs**: Ice Wizards, Ice Knights, Ice Guardians (Level 36)

### 5. Southern Desert Region  
**Location**: Southern areas (≈200-600, 600-768)  
**Typical Coordinates**: (400, 680)  
**Description**: Arid landscape with unique desert creatures, mining opportunities, and extreme environmental conditions.

**Key Features**:
- **Desert Plains**: Open sandy areas with sparse vegetation
- **Mining Areas**: Ore deposits and mining operations
- **Volcanic Border**: Transition zone to lava regions
- **Oasis Points**: Safe rest areas in the desert

**Notable NPCs**: Miner, Billey (Desert NPC), Dying Soldier  
**Common Mobs**: Cactus, Desert creatures, Vultures

### 6. Volcanic/Lava Region
**Location**: Southwest, near desert border (≈0-300, 500-768)  
**Typical Coordinates**: (150, 650)  
**Description**: Extreme heat environment with lava flows, fire-based challenges, and high-level content.

**Key Features**:
- **Lava Flows**: Environmental hazards and unique terrain
- **Volcanic Caves**: Underground areas with fire themes
- **Mining Operations**: Advanced ore and rare material gathering

**Notable NPCs**: Lava NPC (Dying Soldier)  
**Common Mobs**: Fire-based creatures, high-level enemies

### 7. Swamp/Marsh Region
**Location**: Variable locations, often transitional (≈300-700, 400-600)  
**Typical Coordinates**: (500, 500)  
**Description**: Wet, murky areas with unique ecosystem and hidden passages to other regions.

**Key Features**:
- **Marshlands**: Difficult terrain with special movement mechanics
- **Hidden Passages**: Secret routes to ice caves and mountains
- **Poison Areas**: Environmental damage zones

**Common Mobs**: Poison-based creatures, Spiders, Spectres

### 8. Underground/Cave Systems
**Location**: Accessible through various surface entrances  
**Typical Coordinates**: Variable (entrance dependent)  
**Description**: Multi-level underground network connecting different surface regions.

**Key Features**:
- **Cave Networks**: Interconnected underground passages
- **Mining Caves**: Restricted access resource areas
- **Secret Chambers**: Hidden rooms with special encounters
- **Underground Lakes**: Water features in cave systems

## Special Areas

### PVP Zones
Designated areas where player-vs-player combat is enabled. These areas are marked and provide special rewards for PVP activities.

### Minigame Areas  
Special zones with unique gameplay mechanics different from standard combat and exploration.

### Dynamic Areas
Regions that change based on player actions, time, or server events. These areas provide adaptive content and challenges.

### Quest-Specific Locations
Certain areas are only accessible through quest progression, providing gated content and story advancement.

## Navigation Features

### Warps and Teleportation
- **Warp Points**: Instant travel between major regions
- **Quest Warps**: Special teleportation unlocked through story progression
- **Emergency Teleports**: Safety mechanisms for dangerous situations

### Doors and Entrances
- **Town Doors**: Access to buildings and shops
- **Cave Entrances**: Transitions to underground areas  
- **Secret Passages**: Hidden routes between regions

### Movement Mechanics
- **Walking/Running**: Standard movement across terrain
- **Swimming**: Water-based movement in coastal and underwater areas
- **Climbing**: Mountain terrain navigation

## Environmental Hazards

### Climate Effects
- **Freezing**: Cold damage in northern ice regions
- **Heat**: Fire damage in volcanic areas
- **Poison**: Toxic damage in swamp areas

### Overlay Effects
- **Darkness**: Reduced visibility in certain areas
- **Fog**: Environmental obscurement
- **Special Lighting**: Area-specific atmospheric effects

## Resource Distribution

### Gathering Points
- **Trees**: Forest regions (Oak, Ice Oak, Palm, Ice Palm varieties)
- **Rocks**: Mountain and volcanic areas for mining
- **Fish Spots**: Coastal and underwater regions
- **Foraging**: Various regions for plant-based resources

### Rare Resource Locations
Specific coordinates contain unique resources or special gathering opportunities, often requiring quest completion or special access.

## Strategic Considerations for AI Agents

### Movement Optimization
- Plan routes considering terrain difficulty and environmental hazards
- Utilize warp points for efficient long-distance travel
- Respect region-based level requirements for safety

### Resource Planning
- Map gathering routes based on required materials
- Consider environmental factors when planning extended activities
- Account for regional mob spawns when gathering resources

### Social Navigation  
- Identify NPC locations for trading and quest interactions
- Locate safe zones for regrouping and planning
- Understand PVP vs PVE region boundaries

### Progression Pathways
- Follow logical difficulty progression from central areas outward
- Use transitional regions to gradually increase challenge level
- Leverage underground networks for alternative routing

---

*This map guide is based on the current AgentWorld implementation. Regions and features may be expanded or modified in future updates.*
