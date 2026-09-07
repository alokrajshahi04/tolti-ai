# Local run and recovery runbook

**Draft v0.1 Â· Operations: Tipsy Â· Implementation: Alok**

This pack has no runnable app, locks or scripts. Setup below is a proposed procedure, **NOT RUN**, to finalize against the actual repository and demo operating system.

## Setup sequence

1. Confirm permitted cloud use, budget, public/synthetic inputs and demo OS/network.
2. Inspect the existing UI handoff; merge source into the Vite frontend, not a standalone preview embed.
3. Create real npm/uv dependency locks and validated configuration during G1. Ignore secrets, runtime DB/uploads/logs and builds. Keep Modal dependencies separate.
4. Bind development to loopback. Vite proxies `/api` and `/ws` to FastAPI. Test actual health plus backend-unavailable UI.
5. Build frontend assets; apply reviewed migrations; serve frontend/API/WS through one FastAPI worker. Verify API errors do not fall through to the SPA.
6. For LAN, approve/trust HTTPS certificates on both devices and configure exact Host/Origin allowlists and secure cookies. Do not expose a development server publicly or silently disable security.
7. Configure protected Modal endpoints server-side only after approval and real smoke tests. Missing config must read Not configured, never Ready.

## Required scripts to implement and verify

| Script responsibility | Verification |
| --- | --- |
| Development start/stop | No orphan process; clear local URLs |
| Production build/start | Correct assets, migrations, one worker and persistent data |
| Health/check | Local readiness separate from model configuration and inference evidence |
| Backup/restore | Consistent SQLite plus referenced source files; actual restore tested |

Do not present invented script filenames or platform commands as working setup. Add exact verified commands and observed outcomes to this runbook once implemented.

## Before the demo

Record build, device/browser versions, route/model revisions, allowed inputs, configured limits and PASS/FAIL/NOT RUN evidence. Test two actual devices, both real models, independent review, forbidden/stale actions, duplicate clicks, refresh and restart. Keep one genuine recording clearly labeled recorded.

## Recovery

- Backend down: preserve browser draft; restore the approved local process; reconnect via fresh snapshot/replay.
- Provider unavailable: retain local history; show error; manual new preflight/consent for another paid attempt. Never silently retry.
- Restart during work: mark queued/running/cancelling work interrupted before readiness. Do not redispatch; remote cost/outcome may be unknown.
- Lost host session: do not reclaim roles by name. MVP may require a fresh room; document what old data remains accessible.
- Database backup: use SQLite's supported backup mechanism or a verified stopped-app procedure; copying a live `.db` alone can miss WAL state. Include matching source files. Restore to a safe local directory first and verify citations/versions before use.

## Three-minute narrative

Show local app/Modal disclosure â†’ two devices/roles â†’ consented code or summary run â†’ inspect saved version/evidence â†’ independent approval â†’ forbidden/stale-action proof. Show the second real workflow separately if time is tight. Claim only demonstrated scope; unsupported image, offline or agent features remain unavailable/planned.