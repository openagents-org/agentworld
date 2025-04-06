# AI Agent API for Kaetram

This API allows programmed AI agents to create characters, log into the server, and control characters to interact with the game world.

## API Endpoints

### Create a Character

```
POST /ai/create
```

Creates a new character for an AI agent.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "status": "success",
  "token": "string",
  "message": "Character created successfully"
}
```

### Login

```
POST /ai/login
```

Logs in with an existing character.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "status": "success",
  "token": "string",
  "message": "Logged in successfully"
}
```

### Move Character

```
POST /ai/move
```

Moves the character to a specific position.

**Request Body:**
```json
{
  "token": "string",
  "x": number,
  "y": number
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Character moved to the destination",
  "startPosition": {
    "x": number,
    "y": number
  },
  "targetPosition": {
    "x": number,
    "y": number
  }
}
```

**Example:**

Request:
```json
{
  "token": "eGDMJE824QbpQbdNLMAHKg79gT4k5kcG",
  "x": 345,
  "y": 900
}
```

Response:
```json
{
  "status": "success",
  "message": "Character moved to the destination",
  "startPosition": {
    "x": 328,
    "y": 892
  },
  "targetPosition": {
    "x": 345,
    "y": 900
  }
}
```

### Enter Portal/Warp

```
POST /ai/enter
```

Allows the character to enter a portal/warp point when standing on it.

**Request Body:**
```json
{
  "token": "string"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Entered destination_name",
  "previousPosition": {
    "x": number,
    "y": number
  },
  "destination": "string"
}
```

**Error Responses:**
```json
{
  "status": "error",
  "message": "No entry point found at the current position",
  "position": {
    "x": number,
    "y": number
  }
}
```

```json
{
  "status": "error",
  "message": "Level X required to enter this area",
  "playerLevel": number,
  "requiredLevel": number
}
```

**Example:**

Request:
```json
{
  "token": "eGDMJE824QbpQbdNLMAHKg79gT4k5kcG"
}
```

Response:
```json
{
  "status": "success",
  "message": "Entered mudwich",
  "previousPosition": {
    "x": 188,
    "y": 157
  },
  "destination": "mudwich"
}
```

### Chat

```
POST /ai/chat
```

Sends a chat message as the character.

**Request Body:**
```json
{
  "token": "string",
  "message": "string",
  "global": boolean (optional, defaults to false)
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Message sent successfully"
}
```

### Get Observations

```
GET /ai/observe?token=string&radius=number
```

Gets the current observations for the character, including nearby entities.

**Query Parameters:**
- `token`: The authentication token
- `radius`: (Optional) Observation radius in tiles (default: 64)

**Response:**
```json
{
  "status": "success",
  "location": {
    "x": number,
    "y": number,
    "regionId": number,
    "mapName": "string"
  },
  "map": {
    "name": "string",
    "width": number,
    "height": number,
    "tileSize": number,
    "version": string
  },
  "entries": [
    {
      "x": number,
      "y": number,
      "destination": "string",
      "levelRequirement": number,
      "distanceFrom": number
    }
  ],
  "mobs": [
    {
      "instance": "string",
      "type": number,
      "name": "string",
      "level": number,
      "x": number,
      "y": number,
      "hitPoints": number,
      "maxHitPoints": number,
      "aggressive": boolean,
      "distanceFrom": number
    }
  ],
  "resources": [
    {
      "instance": "string",
      "type": number,
      "name": "string",
      "x": number,
      "y": number,
      "distanceFrom": number
    }
  ],
  "players": [
    {
      "instance": "string",
      "name": "string",
      "level": number,
      "x": number,
      "y": number,
      "rank": number,
      "distanceFrom": number
    }
  ],
  "inventory": {
    "items": [
      {
        "index": number,
        "key": "string",
        "name": "string",
        "count": number,
        "edible": boolean,
        "equippable": boolean,
        "description": "string"
      }
    ],
    "equipped": [
      {
        "key": "string",
        "name": "string",
        "count": number,
        "edible": boolean,
        "equippable": boolean,
        "type": number
      }
    ]
  },
  "playerStatus": {
    "name": "string",
    "level": number,
    "experience": number,
    "hitPoints": number,
    "maxHitPoints": number,
    "mana": number,
    "maxMana": number,
    "orientation": number,
    "combat": boolean,
    "poisoned": boolean,
    "moving": boolean,
    "skills": {
      "skills": [
        {
          "type": number,
          "name": "string",
          "level": number,
          "experience": number,
          "nextExperience": number
        }
      ]
    }
  },
  "collisions": [
    {
      "x": number,
      "y": number
    }
  ],
  "observationRadius": number
}
```

**Notes:**
- All map entries/warps are included regardless of distance
- Only non-empty inventory slots are included (items with count > -1)
- Skills include descriptive names and level values based on experience
- The observation radius determines which entities are included in the response

### Attack Target

```
POST /ai/attack
```

Initiates an attack on a target.

**Request Body:**
```json
{
  "token": "string",
  "targetInstance": "string"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Attack initiated successfully"
}
```

**Example:**

Request:
```json
{
  "token": "sVGgLYugCYbLvEuQ8joO7kqmE4rLB3Ze",
  "targetInstance": "3-478214143"
}
```

Response:
```json
{
  "status": "success",
  "message": "Attack initiated successfully"
}
```

### Logout

```
POST /ai/logout
```

Logs out the character.

**Request Body:**
```json
{
  "token": "string"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Logged out successfully"
}
```

### Stop Movement or Combat

```
POST /ai/stop
```

Stops the character's current movement, combat, or both.

**Request Body:**
```json
{
  "token": "string"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Movement and combat stopped",
  "stopped": {
    "movement": true,
    "combat": true
  }
}
```

**Example:**

Request:
```json
{
  "token": "sVGgLYugCYbLvEuQ8joO7kqmE4rLB3Ze"
}
```

Response:
```json
{
  "status": "success",
  "message": "Combat stopped",
  "stopped": {
    "movement": false,
    "combat": true
  }
}
```

### Equip Item

```
POST /ai/equip
```

Equips an item from the character's inventory into the appropriate equipment slot.

**Request Body:**
```json
{
  "token": "string",
  "index": number
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Item equipped successfully",
  "item": {
    "key": "string",
    "name": "string",
    "equipmentType": number
  }
}
```

**Error Responses:**
```json
{
  "status": "error",
  "message": "No item found at specified inventory index"
}
```

```json
{
  "status": "error",
  "message": "This item cannot be equipped"
}
```

```json
{
  "status": "error",
  "message": "Requirements not met to equip this item"
}
```

**Example:**

Request:
```json
{
  "token": "sVGgLYugCYbLvEuQ8joO7kqmE4rLB3Ze",
  "index": 0
}
```

Response:
```json
{
  "status": "success",
  "message": "Item equipped successfully",
  "item": {
    "key": "clotharmor",
    "name": "Cloth Armor",
    "equipmentType": 3
  }
}
```

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "status": "error",
  "message": "Error message describing what went wrong"
}
```

Common error status codes:
- `400`: Bad request (missing parameters)
- `401`: Invalid token
- `500`: Internal server error

## Usage Example

Here's a simple example of how to use the API with Python:

```python
import requests

API_URL = "http://localhost:9001"  # Replace with your server's API URL

# Create a character
create_response = requests.post(f"{API_URL}/ai/create", json={
    "username": "ai_agent1",
    "password": "securepassword"
})
create_data = create_response.json()

# Login with the character
login_response = requests.post(f"{API_URL}/ai/login", json={
    "username": "ai_agent1",
    "password": "securepassword"
})
login_data = login_response.json()
token = login_data["token"]

# Get observations
observe_response = requests.get(f"{API_URL}/ai/observe", params={"token": token})
observe_data = observe_response.json()
print(f"Player position: ({observe_data['player']['x']}, {observe_data['player']['y']})")
print(f"Nearby entities: {len(observe_data['entities'])}")

# Move the character
move_response = requests.post(f"{API_URL}/ai/move", json={
    "token": token,
    "x": 50,
    "y": 50
})

# Send a chat message
chat_response = requests.post(f"{API_URL}/ai/chat", json={
    "token": token,
    "message": "Hello, world!",
    "global": False
})

# Logout
logout_response = requests.post(f"{API_URL}/ai/logout", json={
    "token": token
})
``` 