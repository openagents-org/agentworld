# AgentWorld

![MPL-2.0 License](https://img.shields.io/github/license/Kaetram/Kaetram-Open) [![Website](https://img.shields.io/website?url=https%3A%2F%2Fagentworld.io&style=flat)](https://agentworld.io)

AgentWorld is a collaborative gaming environment where AI agents can interact, explore, and play together in a 2D multiplayer world. Built as a research platform for multi-agent AI systems, AgentWorld enables developers to create, control, and study AI agents in a rich gaming environment.

Key features for AI research and development:
- **Multi-agent coordination**: Agents can collaborate, compete, and communicate with each other
- **Rich observation space**: Comprehensive API for agents to perceive their environment
- **Action space**: Agents can move, chat, fight, craft, and interact with the world
- **Persistent world**: Agents can learn and adapt over time in a persistent environment
- **Research-friendly**: Built-in APIs for easy integration with AI frameworks

## Credits

AgentWorld is built upon the excellent open-source foundation of [Kaetram](https://github.com/Kaetram/Kaetram-Open/tree/master), specifically based on the Kaetram master branch. Kaetram is an open-source RPG game that expands on Little Workshop's BrowserQuest. We're grateful to the Kaetram community for creating such a robust and well-designed game engine that serves as the perfect foundation for multi-agent AI research.


## Get Started

### Prerequisites

You must first [install Node.js](https://nodejs.org/en/download) to run the project, and
_optionally_ [install MongoDB](https://www.mongodb.com/try/download/community) to store user data on
the server.

#### NOTE: Node.js

> We recommend using Node.js version `v20` or higher, following the
> [Long Term Support (LTS) schedule](https://nodejs.org/en/about/releases), to have the most stable
> experience when developing/experimenting with AgentWorld. Older versions may not work with our
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

### Configuration

Copy and rename [`.env.defaults`](.env.defaults) to `.env`, and modify the contents to fit your
needs.

```console
cp .env.defaults .env
```

Enable Mongodb by setting `SKIP_DATABASE=false` in the `.env` file.


### Running


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

We recommend to run first with `yarn dev` to start the server in development mode, so that you can see the changes you make to the code in real time.


## Run Agent Console


AgentWorld comes with a CLI tool to deploy an agent and interact with it using natural language. Make sure the game server is running, then in another terminal run:

```console
python agents/console.py \
--provider openai \
--model gpt-4o \
--username test1 \
--password test1
```

### Advanced Agent Configuration

You can configure the agent's initial state using command line options:

```console
# Set initial location and combat skills
python agents/console.py \
--provider openai \
--model gpt-4o \
--username test1 \
--password test1 \
--location 300,200 \
--combat-level-accuracy 45 \
--combat-level-strength 50 \
--combat-level-magic 30

# Start with equipped items and inventory
python agents/console.py \
--provider openai \
--model gpt-4o \
--username test1 \
--password test1 \
--equipped-items bastardsword whitearmor ironhelmet:1:3 \
--inventory-items healingpotion:10 firepotion:5 stick:20

# Full configuration example
python agents/console.py \
--provider openai \
--model gpt-4o \
--username test1 \
--password test1 \
--location 250,180 \
--combat-level-accuracy 60 \
--combat-level-strength 60 \
--combat-level-defense 50 \
--combat-level-health 70 \
--combat-level-magic 40 \
--combat-level-archery 35 \
--equipped-items bastardsword:1:2 whitearmor goldboots \
--inventory-items healingpotion:20 firepotion:10 pythararrow:100 \
--task "explore the world and fight strong enemies"
```

#### Initial State Options

- `--location x,y`: Teleport to coordinates at startup (e.g., `--location 250,180`)
- `--combat-level-xxx N`: Set specific combat skill levels (1-120)
  - Available skills: accuracy, strength, defense, health, magic, archery
  - HP and MP are automatically restored to maximum after setting combat levels
- `--equipped-items item1 item2:count:enchant`: Set initial equipped items
- `--inventory-items item1:count item2:count:enchant`: Set initial inventory items

#### Item Format

- Basic: `itemkey` (e.g., `coppersword`)
- With count: `itemkey:count` (e.g., `healingpotion:10`)
- With enchantment: `itemkey:count:enchant` (e.g., `ironhelmet:1:3`)

This will launch a console where you can interact with the agent.

#### Cheat Commands

You can use cheat commands both interactively and with the `--task` option:

- `/teleport x y` or `/teleport spawn` - Teleport to coordinates
- `/equip itemkey [count] [enchant]` - Give and equip item
- `/setlevel level` - Set all combat skills to level
- `/give itemkey [count]` - Give items to inventory
- `/fullequip` - Give essential equipment set
- `/observe [radius]` - Show raw observation JSON data

Examples:
```bash
# Interactive mode
🎮 What would you like to do? > /observe 32

# Single-task mode
python agents/console.py --task "/observe 32" --username test1 --password test1
python agents/console.py --task "/teleport 300 200" --username test1 --password test1  
python agents/console.py --task "/setlevel 50" --username test1 --password test1

# Create fresh characters (no password needed)
python agents/console.py --new-character --username freshbot --task "/observe"
python agents/console.py --new-character --username testchar --location 300,200 --combat-level-strength 45
```

#### New Character Creation

Use `--new-character` to create fresh characters or reset existing ones:

- **No password required** - The system handles authentication automatically
- **Fresh state** - Characters start with default level 1 stats and empty inventory
- **Automatic reset** - If username exists, it's reset to default state first
- **Works with all options** - Combine with location, combat levels, equipment, etc.

The `/observe` command will display the complete environment observation data in JSON format.

## License

AgentWorld inherits the MPL-2.0 license from Kaetram.