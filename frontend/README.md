# TOLTI AIs — dark workspace UI

**Start here:** open `dist/index.html` in a browser. It is self-contained and needs no server, CDN, login or model connection.

This is a React + TypeScript **UI reference and interaction prototype**, not the product backend. All participants, model responses, document pages, logs and agent steps are labelled fixtures. Reload resets demo state. Text entered here stays in this page; no inference requests are made.

## Explore in 3 minutes

1. Documents: read the synthetic report alongside the answer; open its source.
2. Chat: use the same room for general work. Enter a message to see how shared messages are presented; the response is explicitly a fixed preview response.
3. Code: inspect the proposed code and download the sample `.py` file. Nothing is executed.
4. People: switch preview identity, hand off control and inspect the read-only composer. This is NOT authentication.
5. Agent: as Alok, click Run demo workflow. Wait for review. Open People, preview as Pallavi, then open Review and approve the exact example note. Close Review and download the Markdown file.
6. Files, Outputs, Activity and Execution details open on demand. No permanent right-side dashboard.

## Take it to your coding platform

Upload this folder/ZIP. Start with `HANDOFF_PROMPT.md`, `UI_SPEC.md` and `src/`. `dist/index.html` is the visual reference, not the source to edit. Screenshots provide supporting references.

## Build from source

Requires Node 20+ and npm. Install dependencies with `npm install`, then run `npm run build`. The build script bundles React and CSS into `dist/index.html`. No runtime CDN is used. Review generated dependency locks before treating this as a production repo.

`npm run typecheck` performs full TypeScript checking after installing the declared type packages. The reference was bundled and browser-tested in the authoring environment; see `QA.md` for exact checks and limitations. esbuild transpilation alone is not a TypeScript type check.

## Structure

- `src/App.tsx`: preview state and action coordination.
- `src/components/`: shell, composer and local icons.
- `src/views/RoomView.tsx`: four mode layouts, ready to split by feature during integration.
- `src/panels/ContextPanel.tsx`: contextual drawers and review.
- `src/fixtures.ts`: synthetic material and real local text downloads.
- `src/styles.css`: shared visual tokens, layouts and responsive rules.
- `scripts/build.mjs`: reproducible single-file bundler.

No FastAPI, WebSocket transport, PDF extraction, real inference, authenticated invitations, code sandbox, durable storage or live multi-device synchronization is included. The visual design is broader than the first backend milestone; implement it in slices.
