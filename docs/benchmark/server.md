# Local game server

The game runs from the TypeScript workspace in `packages/`; the Python benchmark
runner connects to its HTTP API. These are separate processes.

From the repository root, install Node.js (the existing setup recommends Node 20)
and enable the repository's Yarn version through Corepack:

```bash
corepack enable
yarn install
cp .env.defaults .env
yarn dev
```

Copy `.env.defaults` only for a new setup; retain an existing `.env`. Review its
ports before starting: the defaults are game port `7030`, HTTP API port `7031`,
and `SKIP_DATABASE=true`. MongoDB is optional for a disposable instance. Set
`SKIP_DATABASE=false` and configure MongoDB when persistence is needed.

Set the runner's `AGENTWORLD_BASE_URL=http://localhost:7031` to match `API_PORT`.
A browser client URL or the public website API is not the game-control endpoint.
Use the HTTP API rather than the game's WebSocket port.

For production builds, the existing commands are `yarn build` and `yarn start`.
The workspace's historical Node engine declaration differs from the Node 20
recommendation; the onboarding checks do not certify a full game build across
Node versions. See [legacy setup](../legacy-usage.md) for the earlier engine docs.

Use a dedicated local instance for benchmark runs. Concurrent task runs sharing
characters and world state can contaminate each other's observations and scores.
