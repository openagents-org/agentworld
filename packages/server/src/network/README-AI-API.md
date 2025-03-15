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
  "message": "Character moved successfully",
  "position": {
    "x": number,
    "y": number
  }
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
GET /ai/observe?token=string
```

Gets the current observations for the character, including nearby entities.

**Query Parameters:**
- `token`: The authentication token

**Response:**
```json
{
  "status": "success",
  "player": {
    "instance": "string",
    "name": "string",
    "x": number,
    "y": number,
    "hitPoints": number,
    "maxHitPoints": number,
    "mana": number,
    "maxMana": number,
    "level": number,
    "orientation": number,
    "moving": boolean,
    "combat": boolean
  },
  "entities": [
    {
      "instance": "string",
      "type": number,
      "name": "string",
      "x": number,
      "y": number,
      "distance": number
    }
  ],
  "region": number
}
```

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