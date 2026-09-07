# Prototype verification

## Passed
- Production-mode esbuild bundle produced the self-contained preview.
- Browser smoke script passed: mode switching, local typed messages, driver handoff and read-only composer, simulated agent progression, blocked driver approval, exact-note review, reviewer approval and note download, change-request validation, context drawers and Escape dismissal.
- All four modes had no horizontal document overflow at 390px. Tested paths raised no JavaScript errors or external HTTP requests.
- Rendered and visually inspected desktop Documents, Code, Agent, Welcome, People, Sources, Activity, Execution details, agent review and approved output; mobile Chat and Outputs. No visible clipping/overlap defects found in those reference states. Hidden screen-reader labels intentionally use clipped 1px boxes. Desktop work areas and mobile pages intentionally scroll vertically.

## Selected contrast checks
- Primary text: 14.54:1 (#f2f2f0 on #202020).
- Secondary text: 6.42:1 (#ababab on #282828).
- Accent text: 7.71:1 (#89b4f7 on #202020).
- Primary button text: 7.30:1 (#16253b on #89b4f7).

These are selected token pairs, not a full accessibility conformance claim.

## Not verified / not implemented
- Full TypeScript checking was not run: React type definitions were unavailable in the authoring sandbox. They are declared in package.json. Install dependencies and run `npm run typecheck` before integrating.
- A fresh npm install/lockfile, cross-browser matrix, screen-reader audit and production security tests were not performed. No dependency lock is included.
- Real PDF ingestion, inference, multiplayer synchronization, authentication, server permissions, persistence, reconnect and production agent execution do not exist in this prototype.
- The smoke test verifies the note download event/filename, not an independently validated operational artifact. Fixture code is never executed.

## Re-run
Run `npm install`, then `npx playwright install chromium`, `npm run build` and `npm test`. To use an installed Chromium instead, set `CHROMIUM_PATH` to its executable when running the test. Review the smoke script before expanding it to backend integration tests.
