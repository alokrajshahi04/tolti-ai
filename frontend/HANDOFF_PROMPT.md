# Paste this into your coding platform

You are implementing the TOLTI AIs workspace. Use the supplied React/TypeScript source and `dist/index.html` as the visual baseline. Preserve the design; do not replace it with your own generic dashboard.

First read `README.md`, `UI_SPEC.md`, the source, the existing repository rules and the approved product plan. Do not change files yet. Report what can be reused, which contracts are missing, your proposed changed files, implementation order and tests. Ask before changing architecture or crossing an agreed ownership boundary.

## Design to preserve

- Matte charcoal surfaces, restrained blue, readable system typography, subtle borders and generous spacing. No neon, gradients, KPI cards, decorative agents or permanent inspector panel.
- One workspace shell and one shared room. Chat, Documents, Code and Agent are modes of that room, not separate disconnected applications.
- The participant cluster, driver ownership above the composer, handoff, contextual review and shared activity are core workflow elements—not an added collaboration widget.
- Documents gets an intentional source-reading split view. Code gets an artifact/editor surface. Chat stays conversational. Agent shows bounded steps and an explicit review checkpoint.
- Files, outputs, people, activity and execution details open only when requested. Preserve responsive layouts and accessible focus behaviour.

## Replace the demo, not the design

The fixture layer is deliberately non-production. Do not ship preview identity switching, prewritten responses, simulated logs, timer-driven agent steps or fixed participants as real functionality. The Auto selector in this reference does not implement a semantic router. Selecting a fixed example is not evidence of inference.

Build typed interfaces for room snapshots, membership, source references, runs, stream events, artifact versions and review decisions. Derive API types from the backend contract. Keep UI state separate from server-authoritative state. Use the existing Python/FastAPI backend plan rather than inventing a hosted database or login service.

Server owns room access, roles, one active driver/run, route policy, durable event ordering, version hashes and approvals. Enforce all permissions server-side. Browser hiding/disabled controls are not security. Reconnect must replay committed events without duplicates. Handle stale review with a conflict, never silent approval of newer content.

All provider credentials remain on the local server. Actual model calls go from FastAPI to the two protected Modal endpoints. Label this Local app / Modal inference. Show genuine errors, health and redacted correlated logs. Do not invent zero-egress or offline-model claims.

Implement real upload/extraction and a local PDF viewer before claiming PDF support. The supplied PDF page is HTML, not a parser. Coding initially produces downloadable proposals marked Not executed; execution needs a separately approved isolated sandbox.

The first agent workflow is bounded: read selected permitted report → extract supported findings → draft a versioned note → pause for an independent reviewer → export the approved version. Use real backend events and tool allowlists, not timers. Reviewer must see the exact draft being approved. Do not add autonomous shell, Git or equipment actions.

## Work in reviewed slices

1. Reuse the shell/tokens and remove no required design state.
2. Wire real room identity, membership, roles and shared event recovery.
3. Connect one task flow end-to-end, then the second model-backed function.
4. Add source-linked PDF Q&A and exact-version artifacts/review.
5. Add the bounded agent workflow and output export.
6. Test role denial, cross-room access, stale approval, duplicate submit, upstream failure, reconnect/restart, and two real devices.

Add an acceptance test with each slice. Run formatting, lint, type, unit/integration and browser checks. Report actual results and anything not run. Do not suppress failures or replace unavailable providers with hidden mock success. Stop after the current approved slice; do not generate the entire application in one pass.
