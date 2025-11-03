# Social Mode Implementation - Phase 1

## Overview
Phase 1 successfully implements a social mode for AgentWorld, creating an empty dedicated map for agents to interact in a social environment.

## Changes Made

### 1. Environment Configuration
- **File**: `.env` and `.env.defaults`
- **Change**: Added `SOCIAL_MODE=false` configuration flag
- **Location**: Added under "World Configurations" section
- **Purpose**: Controls whether the game loads the social world map or the standard world map

### 2. TypeScript Configuration Interface
- **File**: `packages/common/config.ts`
- **Change**: Added `socialMode: boolean` field to the Config interface (line 45)
- **Purpose**: Makes the social mode flag available throughout the application

### 3. Server Map Loading Logic
- **File**: `packages/server/src/game/map/map.ts`
- **Changes**:
  - Imported both `worldMapData` and `socialWorldMapData`
  - Imported `config` from `@kaetram/common/config`
  - Added conditional logic to load the appropriate map based on `config.socialMode`
- **Code**: `let map = (config.socialMode ? socialWorldMapData : worldMapData) as ProcessedMap;`
- **Purpose**: Dynamically loads the correct map based on configuration

### 4. Social World Map
- **File**: `packages/server/data/map/social_world.json`
- **Structure**:
  - Dimensions: 100x100 tiles
  - Tile size: 16 pixels
  - Border collisions: All edges are walled (396 collision tiles)
  - Empty interior: Open space for agents to spawn and interact
  - No entities, resources, or NPCs
- **Purpose**: Provides a clean, empty environment for social interactions

### 5. Client Map (Optional)
- **File**: `packages/client/data/maps/social_map.json`
- **Purpose**: Client-side map metadata for the social world

## How to Use

### Enable Social Mode
1. Edit `.env` file:
```bash
SOCIAL_MODE=true
```

2. Restart the AgentWorld server

### Disable Social Mode (Return to Normal World)
1. Edit `.env` file:
```bash
SOCIAL_MODE=false
```

2. Restart the AgentWorld server

## Technical Details

### Map Structure
The social world map is a minimal ProcessedMap with:
- **Data array**: Empty (allows for dynamic content)
- **Collisions**: Border tiles only (creates a safe contained area)
- **Areas**: All area types initialized as empty arrays
- **Resources**: No trees, rocks, fish spots, or foraging points
- **Entities**: No NPCs or static entities

### Configuration Flow
1. Environment variables loaded from `.env` → `config.ts`
2. Config object created with `socialMode` property
3. Map loader checks `config.socialMode` at import time
4. Appropriate map data imported and initialized
5. All map-dependent systems use the loaded map

## Benefits

1. **Clean Environment**: No distractions from NPCs, resources, or complex terrain
2. **Controlled Space**: Border collisions prevent agents from wandering off
3. **Scalable**: 100x100 tiles provides enough space for multiple agents
4. **Simple Toggle**: Easy to switch between social and normal mode via config
5. **Performance**: Minimal map data reduces server load

## Next Steps (Future Phases)

- **Phase 2**: Implement distance-based messaging system
- **Phase 3**: Add interactive elements for agents
- **Phase 4**: Implement agent style switching functionality
- **Phase 5**: Add monitoring and analytics for social interactions

## Testing

The implementation has been validated:
- ✅ Configuration files updated successfully
- ✅ TypeScript compilation successful (no new errors)
- ✅ Map files created with proper structure
- ✅ Server-side map loading logic implemented
- ✅ No linter errors introduced

To test in production:
1. Set `SOCIAL_MODE=true` in `.env`
2. Start the server: `yarn dev:server` (or your start command)
3. Agents will spawn in the 100x100 empty social world
4. Verify agents can move within the bordered area

## Files Modified
- `.env`
- `.env.defaults`
- `packages/common/config.ts`
- `packages/server/src/game/map/map.ts`

## Files Created
- `packages/server/data/map/social_world.json`
- `packages/client/data/maps/social_map.json`
- `SOCIAL_MODE_PHASE1.md` (this file)

## Completion Status
✅ Phase 1 Complete - Empty social world map created and configured

