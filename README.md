# TOLTI AI â€” Project docs

**Draft v0.1 Â· 7 September 2026 Â· Review before implementation**

Repository-ready Markdown for a locally hosted shared AI room with Modal cloud inference. These are proposed implementation contracts, not a working app or a tested release.

## Save the files like this

```text
tolti-ai/
â”œâ”€â”€ README.md
â”œâ”€â”€ AGENTS.md
â””â”€â”€ docs/
    â”œâ”€â”€ prd.md
    â”œâ”€â”€ architecture.md
    â”œâ”€â”€ uispec.md
    â”œâ”€â”€ ui-spec.md
    â”œâ”€â”€ contracts.md
    â”œâ”€â”€ provider-contract.md
    â”œâ”€â”€ security.md
    â”œâ”€â”€ testing.md
    â”œâ”€â”€ runbook.md
    â”œâ”€â”€ backlog.md
    â””â”€â”€ decisions.md
```

`uispec.md` is the full UI specification. `ui-spec.md` is a compatibility pointer for existing prompts; it is not a second specification.

## Read and use

1. [PRD](docs/prd.md): scope, roles, delivery gates and acceptance requirements.
2. [Architecture](docs/architecture.md): monorepo, boundaries, data model, run/review/recovery flow.
3. [UI specification](docs/uispec.md): dark workspace, components, modes, states and accessibility.
4. [Contracts](docs/contracts.md): proposed HTTP schemas, errors, permissions, durable/transient events and version rules.
5. [Provider contract](docs/provider-contract.md): two-model adapter, routing, consent, timeouts and real smoke-test requirements.
6. [Security](docs/security.md), [testing](docs/testing.md) and [runbook](docs/runbook.md): implementation safeguards and verification.
7. [Decisions](docs/decisions.md) and [backlog](docs/backlog.md): human approvals and the next bounded task.

Keep [AGENTS.md](AGENTS.md) as the coding assistant's canonical engineering rules. Compare and merge these files into the existing repository; do not overwrite unrelated work.

## Basis and honest limits

Derived from the current Build Plan â€” Start Here, AI Coding Prompts and the TOLTI AIs team page as available on 7 September 2026. The current local-app/Modal plan takes precedence over historical offline/local-model goals. Planning owners: Alok (backend/integration), Anshuman (frontend), Aditya (evidence), Pallavi & Bhargavi (product/submission), Tipsy (QA/demo).

The actual UI handoff archive, application repository, official problem statement and model deployments were not available for inspection. Preserve the existing dark prototype; reconcile its real components before coding. Endpoint/schema details, anonymous identity, numeric limits and security/deployment choices are proposed and need team review. Model revisions, GPU fit, cloud permission and budget remain unverified.

This delivery contains Markdown only: no app code, dependency locks, environment/secrets, deployments, screenshots or passing runtime-test evidence. Local document links and JSON examples were checked during packaging; application, model, visual and device tests were not run.

## Next coding-platform request

```text
Review this TOLTI AI documentation pack and the existing repository/UI handoff.
Read AGENTS.md, README.md, docs/prd.md, docs/architecture.md,
docs/contracts.md, docs/uispec.md and docs/decisions.md first.
Do not implement application behavior, install dependencies or deploy anything.
Identify existing files, contradictions, security decisions and missing inputs.
Propose the smallest corrections and an approved G1 skeleton issue with exact
files, acceptance tests and exclusions. Do not claim missing tests passed.
Stop for Alok and Anshuman's review before generating the scaffold.
```