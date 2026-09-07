# TOLTI AIs — UI integration specification

## Product concept

A shared workspace for knowledge work. The **room** owns participants, source files, instructions, runs, artifacts and review decisions. Modes are lenses on that shared context. A person should never have to re-invite the team or reattach the same evidence just to move from Chat to Documents or Agent.

## Information architecture

- Workspace sidebar: New task, Files, Outputs, Room activity, room list and execution details.
- Room header: title and participant/role entry point.
- Mode navigation: Chat / Documents / Code / Agent.
- Contextual work surface: reading-oriented chat, document plus answer, code artifact, or task plan.
- Shared control strip: current driver, room visibility and handoff.
- Composer: instruction, room files, routing choice and one primary action.
- Context drawers: people, files, activity, diagnostics, review and outputs.

This prototype has one synthetic room. Multi-room creation, searching and switching need backend integration; do not advertise them as implemented.

## Four modes

**Chat:** a continuous discussion with distinguishable human and AI authors. Keep room contributions separate from model reasoning. Production human messages must be visibly attributed and timestamped from actual events.

**Documents:** local document reader beside source-grounded responses. Click citations to reveal exact page/excerpt. Preserve source scope across modes; let the driver choose what is sent remotely. Real PDFs need upload validation, extraction and a renderer; the fixture is not those capabilities.

**Code:** readable proposal with filename, language, version, execution status and export. Do not present the prototype's `<pre>` as a full editor. If editing is required, integrate an editor behind the same design and create new artifact versions from changes.

**Agent:** show intended steps and observed state, not private model reasoning. The demo assembles a fixed report-to-note example and stops for a reviewer. A real implementation must run allowlisted tools and emit persistent events. Download is the only real output action in this prototype.

## Multiplayer is a domain model, not decoration

- Persistent participant cluster; open People to see roles.
- One driver controls submission/cancellation. Everyone can inspect permitted room context.
- Reviewer decides on an exact artifact version, never their own output.
- Watcher stays read-only and can request control if enabled.
- Handoff is explicit, atomic and preferably idle-only for v1. Keep original task authorship, evidence and event history.
- Shared activity records actual join/control/run/review events. Presence is ephemeral; committed history is durable. Do not persist every streaming token as an audit event.
- Production invitations are revocable, expiring and authenticated; display names never confer authority.

## Visual tokens

- Canvas `#191919`, sidebar `#151515`, surfaces `#202020` / `#282828`.
- Primary text `#f2f2f0`; secondary `#ababab`; accent `#89b4f7`.
- Positive `#8ac8a4`; attention `#e2af75`; error `#f0948b`.
- System sans; 16px body, 14px metadata, 24–32px headings. Code uses local monospace.
- Spacing: 4/8/12/16/24/32/48px. Controls 8px radius; major surfaces 12px.
- No CDN assets. Use colour with text, never as the only state signal.

## Responsive and accessibility

Desktop has a stable shell with the work surface scrolling independently above the composer. Documents uses a task-specific split pane, not a permanent global inspector. At narrow widths, stack document/answer, collapse navigation, and retain access to participants and files. Wide code scrolls within its own surface, not the page.

Use visible focus, named controls, keyboard-accessible dialogs and screen-reader announcements for meaningful changes. Native dialog handles focus containment for context drawers. Mobile navigation still needs a full production focus-trap/return-focus pass. Do not claim a completed accessibility audit.

## Backend-driven states still required

Local disconnected / reconnecting; model cold start; streaming; cancellation; clarification needed; busy; expired session; forbidden; invalid/scanned/oversized upload; extraction failure; missing consent; no supporting evidence; upstream unavailable; stale approval; interrupted run after restart. Never turn one of these into a fabricated success.

## Handoff boundaries

Keep `src/fixtures.ts` and preview identity/query controls in demo-only code. Replace in-memory decisions, counters and timer steps with server contracts. Approval must compare the submitted version/hash; a revised artifact begins unapproved. Actual output author may differ from the driver after handoff and must be stored, not inferred from current presence.

Acceptance: two real devices see the same task and decisions; watchers cannot mutate via direct requests; stale and self-approval fail; source links resolve; both models genuinely run; the agent pauses before approval; production logs truthfully separate local hosting and Modal inference.
