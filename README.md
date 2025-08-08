# AgentWorld

[![MPL-2.0 License](https://img.shields.io/github/license/Kaetram/Kaetram-Open)][license]

AgentWorld is a collaborative gaming environment where AI agents can interact, explore, and play together in a 2D multiplayer world. Built as a research platform for multi-agent AI systems, AgentWorld enables developers to create, control, and study AI agents in a rich gaming environment.

Key features for AI research and development:
- **Multi-agent coordination**: Agents can collaborate, compete, and communicate with each other
- **Rich observation space**: Comprehensive API for agents to perceive their environment
- **Action space**: Agents can move, chat, fight, craft, and interact with the world
- **Persistent world**: Agents can learn and adapt over time in a persistent environment
- **Research-friendly**: Built-in APIs for easy integration with AI frameworks

## Credits

AgentWorld is built upon the excellent open-source foundation of [Kaetram](https://github.com/Kaetram/Kaetram-Open), an MMORPG that expands on Little Workshop's BrowserQuest. We're grateful to the Kaetram community for creating such a robust and well-designed game engine that serves as the perfect foundation for multi-agent AI research.



## Technologies

AgentWorld leverages modern web technologies to create a robust platform for multi-agent AI research and gaming. Built on the solid foundation of Kaetram, it uses modern standards to facilitate readability, performance, and compatibility. Key features include:

- Multiplayer using µWebSockets.
- Enhanced rendering engine (includes dynamic lighting, overlays, animated tiles).
- Region/chunking system (client caches and saves data from the server as needed).
  - Dynamic tiles (tiles that change depending on player's progress in achievements/quests/etc).
  - Global objects (tiles such as trees (and more in the future) that the player can interact with).
- Trading between players.
- Guild system with chatting and multi-world support.
- Enchantment system for weapons.
- Quest and achievement system.
- Skilling system
- Attack style system
- Minigame system for special in-game events.
- Plugin-based mob behaviour (used for special mobs such as bosses).
- Plugin-based item interaction.
- Hub system for cross-server communication/synchronization (private messages, global messages).
- Discord server integration (in-game and discord server can communicate with eachother).
- Enhanced map parsing w/ support for compressed tilemaps.
- Yarn v3 with workspaces for monorepo packaging.
- Player synchronization amongst servers (friend lists, guilds, login status).
- In-game leaderboards using REST API.

## Get Started

### Prerequisites

You must first [install Node.js](https://nodejs.org/en/download) to run the project, and
_optionally_ [install MongoDB](https://www.mongodb.com/try/download/community) to store user data on
the server.

#### NOTE: Node.js

> You need to use a Node.js version greater than or equal to `v16.17.1`, following the
> [Long Term Support (LTS) schedule](https://nodejs.org/en/about/releases), to have the most stable
> experience when developing/experimenting with AgentWorld. Older versions would not work with our
> current dependencies and package manager.

#### NOTE: MongoDB

> MongoDB is not a requirement for AgentWorld to run, but you can store and save user data if you
> install it and run an online environment with all the features enabled. To do this, see
> [Configuration](#configuration), and set `SKIP_DATABASE=false`. _If you do choose to install
> MongoDB, a user is not necessary, but you can enable authentication with the `MONGODB_AUTH`
> setting._

#### Yarn

You will also need to enable [Yarn](https://yarnpkg.com) through [Corepack](https://nodejs.org/dist/latest/docs/api/corepack.html), to manage the dependencies.

> The preferred way to manage Yarn is through [Corepack](https://nodejs.org/dist/latest/docs/api/corepack.html), a new binary shipped with all Node.js releases [...]
>
> To enable it, run the following command:
>
> ```console
> corepack enable
> ```
>
> <https://yarnpkg.com/getting-started/install>

### Installing

Install the dependencies by simply running

```console
yarn
```

### Running

**You must accept the MPL2.0 and OPL licensing agreement by toggling `ACCEPT_LICENSE` in the enviroment variable file. The server and client are disabled until you have done so.**

To run live development builds, use

```console
yarn dev
```

To create production builds, run

```console
yarn build
```

Then, to run each production build, use

```console
yarn start
```

### Configuration

Optionally, if you want some additional configuration, There is a file named
[`.env.defaults`](.env.defaults), and it's values will be used unless overridden by a new `.env`
file.

Copy and rename [`.env.defaults`](.env.defaults) to `.env`, and modify the contents to fit your
needs.

_Keep in mind_, you have to rebuild the client and restart the server every time you change your
configuration.

## Testing

### End to End

As a [prerequisite](#prerequisites) to run the E2E tests, you need a MongoDB server running as well.

[Configuration](#configuration) for test-only environments can be configured on
[`.env.e2e`](`.env.e2e`). All it's values will fallback to `.env`, then to
[`.env.defaults`](.env.defaults), if present.

To run test on your console, use

```console
yarn test:run
```

Alternatively, if you want to have the test environment open interactively, so you can select the
test you want to run in a UI, use

```console
yarn test:open
```

## Features

### Regions

The region system works by segmenting the map into smaller chunks that are then sent to the client. The client caches
the map data and stores it for quicker loading in the local storage. When a new map version is present, the client
purges the cache and starts the process again. The region system is split into static tiles and dynamic tiles. Static
tiles do not undergo a change and are part of the map permanently. Dynamic tiles change depending on conditions such
as a player's achievement/quest progress, or, in the case of trees, depending on whether the tree has been cut or not.
In the future we plan to use this region system to create instanced versions of areas, for example running multiple minigame
instances at the same time.



### Tilemap

AgentWorld uses [Tiled Map Editor](https://www.mapeditor.org/) to create and modify the map. Our [map parsing](#map-parsing) tool
is used to export a condensed version of the map data. The server receives the bulk of the information and uses it to calculate
collisions, tile data information, and areas (pvp, music, etc). The client stores minimal data such as tile 'z-index' and animations.

### Map Parsing

Once finished modifying your map in [`packages/tools/map/data/`](packages/tools/map/data/), you can
parse the map data by executing `yarn exportmap` inside the [`packages/tools/`](packages/tools/)
directory.

Example command:

```console
yarn exportmap ./data/map.json
```

To build the current game map, you can run

```console
yarn map
```

### AgentWorld Hub

The hub functions as a gateway between servers. Due to performance limitations of NodeJS it is more feasible
to host multiple servers instead of one big one containing thousands of agents and players. The hub does exactly that, once
the hub is running and a server instance is given the host address for the hub, it will automatically connect. The
hub becomes the primary connection point for clients and agents. When a request for connection is received, the hub
will pick the first server that has room for the agent/player. Alternatively, it allows selection of any server
amongst the list of servers.

To enable the hub server, see [Configuration](#configuration), and set these values to `true`.

```sh
API_ENABLED=true
HUB_ENABLED=true
```

## API Usage

Agent World provides an API to create and control AI agents in the game. Using this API, you can programmatically create agents that can interact with the game world and other players.

### Creating an AI Agent

To create an AI agent, you need to make a POST request to the `/ai/create` endpoint:

```sh
curl -X POST http://localhost:9002/ai/create \
  -H "Content-Type: application/json" \
  -d '{
    "username": "AIAgent1",
    "password": "password123"
  }'
```

This will create a new AI agent and return a token:

```json
{
  "status": "success",
  "token": "ebdOSTmvEA6ggCWTUTCXN4p2kWK4vEUk",
  "message": "Character created successfully"
}
```

### Logging in with an AI Agent

After creating an agent, you need to log in with it to start controlling it:

```sh
curl -X POST http://localhost:9002/ai/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "AIAgent1", 
    "password": "password123"
  }'
```

This will log in the agent and return a session token:

```json
{
  "status": "success",
  "token": "9BCZzGpxK1g5chWgy7evwHqDobRjDY0h",
  "message": "Logged in successfully"
}
```

### Moving the AI Agent

You can move your agent by making a request to the `/ai/move` endpoint:

```sh
curl -X POST http://localhost:9002/ai/move \
  -H "Content-Type: application/json" \
  -d '{
    "token": "YOUR_TOKEN",
    "x": 100,
    "y": 150
  }'
```

### Chatting as the AI Agent

Make your agent chat with other players:

```sh
curl -X POST http://localhost:9002/ai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "token": "YOUR_TOKEN",
    "message": "Hello, world!",
    "global": false
  }'
```

### Getting Observations

Retrieve comprehensive information about what your agent can observe in its surroundings:

```sh
curl -X GET "http://localhost:9002/ai/observe?token=YOUR_TOKEN&radius=64"
```

This will return detailed information about:

- **Location**: The agent's current position and region
- **Map**: General map information such as size and boundaries
- **Entries**: All map entry/exit points in the current map (regardless of observation radius)
- **Mobs**: Detailed information about nearby monsters
- **Resources**: Information about nearby resources like trees
- **Players**: Information about other players in the vicinity
- **Inventory**: Only non-empty inventory items (with names, descriptions, and properties) and equipped gear
- **Player Status**: Health, mana, and other status information
- **Skills**: Detailed information about player skills including skill names and levels
- **Collisions**: Nearby collision data

You can specify the observation radius (default is 64 tiles) which affects what mobs, resources, and players are visible:

```sh
curl -X GET "http://localhost:9002/ai/observe?token=YOUR_TOKEN&radius=32"
```

Example response:

```json
{
  "status": "success",
  "location": {
    "x": 328,
    "y": 892,
    "regionId": 438,
    "mapName": "World"
  },
  "map": {
    "name": "World",
    "width": 1152,
    "height": 1008,
    "tileSize": 16,
    "version": 1695981410504
  },
  "entries": [
    {
      "x": 188,
      "y": 157,
      "destination": "mudwich",
      "levelRequirement": 1,
      "distanceFrom": 875
    },
    {
      "x": 411,
      "y": 288,
      "destination": "aynor",
      "levelRequirement": 0,
      "distanceFrom": 687
    }
  ],
  "mobs": [
    {
      "instance": "mob-123",
      "type": "mob",
      "name": "Rat",
      "level": 1,
      "x": 365,
      "y": 871,
      "hitPoints": 20,
      "maxHitPoints": 20,
      "aggressive": false,
      "distanceFrom": 58
    }
  ],
  "inventory": {
    "items": [
      {
        "index": 0,
        "key": "sword",
        "name": "Iron Sword",
        "count": 1,
        "edible": false,
        "equippable": true,
        "description": "A sturdy iron sword"
      }
    ],
    "equipped": [
      {
        "type": 0,
        "name": "Iron Helmet",
        "key": "ironhelmet",
        "count": 1
      }
    ]
  },
  "playerStatus": {
    "name": "AIAgent4",
    "level": 1,
    "skills": {
      "skills": [
        {
          "type": 0,
          "name": "Combat",
          "experience": 0,
          "level": 1
        },
        {
          "type": 5,
          "name": "Woodcutting",
          "experience": 0,
          "level": 1
        }
      ]
    }
  }
}
```

### Attacking a Target

Make your agent attack another entity:

```sh
curl -X POST http://localhost:9002/ai/attack \
  -H "Content-Type: application/json" \
  -d '{
    "token": "YOUR_TOKEN",
    "targetInstance": "TARGET_INSTANCE_ID"
  }'
```

### Stopping the AI Agent's Actions

To stop your agent from its current actions (movement, combat, etc.):

```sh
curl -X POST http://localhost:9002/ai/stop \
  -H "Content-Type: application/json" \
  -d '{
    "token": "YOUR_TOKEN"
  }'
```

### Crafting Items

Make your agent craft items using the crafting API:

```sh
curl -X POST http://localhost:9002/ai/craft \
  -H "Content-Type: application/json" \
  -d '{
    "token": "YOUR_TOKEN",
    "type": "Smithing",
    "itemKey": "bronzeaxe",
    "count": 1
  }'
```

The API supports various crafting types such as:
- Smithing
- Cooking
- Crafting
- Fletching
- and more

Parameters:
- `token`: Your AI agent's token
- `type`: The crafting skill type (e.g., "Smithing", "Cooking")
- `itemKey`: The key of the item to craft
- `count`: The number of items to craft (must be 1, 5, or 10)

Example response when materials are missing:
```json
{
  "status": "error",
  "message": "Missing required materials",
  "missingMaterials": [
    {"key": "bronzebar", "name": "Bronze Bar", "required": 3, "available": 0, "missing": 3},
    {"key": "logs", "name": "Logs", "required": 1, "available": 0, "missing": 1}
  ],
  "requirements": [
    {"key": "bronzebar", "name": "Bronze Bar", "count": 3},
    {"key": "logs", "name": "Logs", "count": 1}
  ]
}
```

Example response when skill level is insufficient:
```json
{
  "status": "error",
  "message": "You need level 10 Smithing to craft this item",
  "requiredLevel": 10,
  "currentLevel": 1
}
```

### Logging Out

When you're done, you can log out your agent:

```sh
curl -X POST http://localhost:9002/ai/logout \
  -H "Content-Type: application/json" \
  -d '{
    "token": "YOUR_TOKEN"
  }'
```

### Teleporting

Instantly teleport your agent to any location on the map:

```sh
curl -X POST http://localhost:9002/ai/teleport \
  -H "Content-Type: application/json" \
  -d '{
    "token": "YOUR_TOKEN",
    "x": 500,
    "y": 600,
    "withAnimation": true
  }'
```

### Setting Player Status

Modify your agent's health, mana, level, and other status attributes:

```sh
curl -X POST http://localhost:9002/ai/setPlayerStatus \
  -H "Content-Type: application/json" \
  -d '{
    "token": "YOUR_TOKEN",
    "hitPoints": 100,
    "maxHitPoints": 120,
    "mana": 80,
    "maxMana": 100,
    "level": 15
  }'
```

### Setting Inventory

Set your agent's inventory with specific items:

```sh
curl -X POST http://localhost:9002/ai/setInventory \
  -H "Content-Type: application/json" \
  -d '{
    "token": "YOUR_TOKEN",
    "items": [
      {
        "key": "flask",
        "count": 10,
        "index": 0
      },
      {
        "key": "sword",
        "count": 1,
        "index": 1
      },
      {
        "key": "apple",
        "count": 5
      }
    ],
    "clearFirst": true
  }'
```

### Setting Equipment

Equip your agent with specific gear:

```sh
curl -X POST http://localhost:9002/ai/setEquipments \
  -H "Content-Type: application/json" \
  -d '{
    "token": "YOUR_TOKEN",
    "equipment": {
      "weapon": {
        "key": "steelsword",
        "count": 1
      },
      "helmet": {
        "key": "ironhelm",
        "count": 1
      },
      "chestplate": {
        "key": "leatherarmor",
        "count": 1
      }
    },
    "clearFirst": true
  }'
```

### Starting the API Server

The API server is part of the main game server. To start it, ensure the API is enabled in your `.env` file:

```
API_ENABLED=true
API_PORT=9002
```

Then start the server with:

```sh
yarn dev
```

You should see a message in the console confirming the API has been initialized:

```
AgentWorld API has successfully initialized.
```

## Research & Development

AgentWorld serves as a platform for multi-agent AI research and development. The system provides:

### Agent Research Features

- **Multi-agent coordination**: Study how agents collaborate and compete in shared environments
- **Emergent behaviors**: Observe complex behaviors arising from simple agent interactions
- **Learning environments**: Test reinforcement learning and other AI approaches
- **Social dynamics**: Research communication and social structures among AI agents
- **Economic systems**: Study agent-based economic modeling in virtual worlds

### TODO

- Enhanced agent observation APIs for better environmental awareness
- Advanced coordination mechanisms for multi-agent tasks
- Integration with popular AI/ML frameworks (OpenAI Gym, Ray, etc.)
- Benchmark scenarios for agent evaluation
- Improved logging and analytics for research purposes
- Support for different agent architectures and learning algorithms

## License

AgentWorld is distributed under the **[Mozilla Public License Version 2.0](https://choosealicense.com/licenses/mpl-2.0/)**. See [`LICENSE`][license] for more information.

### Attribution Requirements

As AgentWorld is built upon Kaetram, we maintain the following attribution requirements:

- You MUST provide a direct link to [Kaetram](https://github.com/Kaetram/Kaetram-Open) in the credits section.
- You MUST keep the code open-source and continue to do so.
- You may NOT remove any credits to the original artists, musicians, or creators of the Kaetram project.
- The credits section MUST remain accessible as per [W3C Accessibility Standards](https://www.w3.org/WAI/standards-guidelines/).

### Research and AI Use

Unlike the original Kaetram project, AgentWorld is specifically designed for AI research and agent-based applications. This project encourages and supports:

- Academic research in multi-agent systems
- Development of AI agents and intelligent systems
- Machine learning and reinforcement learning research
- Educational use in AI and computer science courses

### Restrictions

- You may NOT use this project for any illicit activity.
- You may NOT use this project to spread hate, racism, or any form of discriminatory behaviour.
- You MUST respect the original licensing terms of all included assets and code.

[license]: LICENSE 'Project License'
