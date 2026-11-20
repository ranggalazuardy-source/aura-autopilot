# AURA Virtual AI Office

React 19 + Three.js + React Three Fiber isometric workspace for AURA's 15 registered agents.

## Run locally

1. Start the AURA Worker API on port 8787 with uv run pywrangler dev.
2. Install frontend dependencies with npm install.
3. Start Vite with npm run dev.
4. Open the URL printed by Vite, then enter the same AURA API key used by the operations dashboard.

Vite proxies /office/state to the local Worker at http://127.0.0.1:8787.

## Production

Run npm run build. Wrangler serves dist/ at /office/ using the root wrangler.jsonc static assets configuration.

The office polls authenticated GET /office/state every five seconds. It renders all 15 agents from the shared AURA registry, a real task queue from D1, working status only for a task with a valid unexpired lease, blocked tasks as waiting for owner input, and audit log entries from D1.

Queued tasks are not animated as active work. Expired leases are labeled stale. The visual office does not activate model inference, create background schedules, publish, or execute financial actions.