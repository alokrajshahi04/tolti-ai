# Decisions and open questions

**Draft v0.1 Â· 7 September 2026 Â· No implementation approval implied**

## Carried from the current plan

- One monorepo with separate React/TypeScript/Vite frontend, Python 3.12/FastAPI backend and Modal deployment code.
- Local SQLite state and private source storage; HTTP commands, authenticated WebSocket events; one backend worker.
- Two candidate model families, deterministic routing, server-side credentials and explicit cloud disclosure.
- Driver/reviewer/watcher roles, host distinct from task role, exact-version independent review and no generated-code execution.
- Preserve the dark UI handoff; rooms first, code/summary next, PDF Q&A/bounded agent afterward.

These reflect the current proposed build plan, not proof of implementation or a newly obtained human approval.

## Decisions requiring sign-off

| ID | Decision / recommendation | Owner | Blocks |
| --- | --- | --- | --- |
| D01 | Confirm official cloud/offline/vision requirements. Modal is not air-gapped. If offline is mandatory, obtain approved onsite compute and revise the adapter/deployment plan. | Pallavi & Bhargavi | Cloud demo/deployment scope |
| D02 | Confirm deadline, submission format and actual availability; do not reuse old preparation dates blindly. | Pallavi & Bhargavi | Final release schedule |
| D03 | Approve Modal spending cap, endpoint protection and actual model/revision/GPU smoke tests. No assumed GPU fit or paid deployment authorization. | Alok | MODEL-07 and real inference |
| D04 | Inspect TOLTI-AIs-UI-Handoff.zip; reconcile real source/components/screenshots. Current plan supersedes the older no-prototype wording but does not imply final design approval. | Anshuman | UI implementation mapping |
| D05 | Accept anonymous-principal demo identity limitation; host verifies a real independent reviewer. Strong verified identity is later scope. | Alok + product owners | Room/review security approval |
| D06 | Approve HTTPS/certificate/origin/cookie configuration on actual LAN devices. No silent insecure exception. | Alok + Tipsy | Two-device release |
| D07 | Review proposed API/schema, preflight, idempotency, event envelopes and revision/cancellation semantics. | Alok + Anshuman | Corresponding implementation slices |
| D08 | Approve limits, parsing isolation, input policy and evidence/retention handling; tune with real model/tokenizer tests. | Alok + Aditya | Source/model activation |
| D09 | Decide whether Chat, PDF Q&A and bounded Agent are required for the official demo. Keep unavailable until real integration. | Product owners + Alok | Final acceptance scope |
| D10 | Confirm demo OS and verified setup/start/backup/restore commands. | Tipsy + Alok | Rehearsal/readiness |

All entries above are **OPEN** until a named reviewer records a decision and date. Local skeleton/room work can proceed under an explicitly approved limited scope while cloud deployment remains blocked; pending budget is never an implicit authorization.

## Record a decision

```text
Decision ID / date:
Approved by:
Chosen option and rationale:
Affected contracts/files:
Acceptance evidence required:
Risks / deferred alternatives:
```

Numeric defaults and endpoint shapes in this pack are proposals, not official requirements or measurements. When they change, update docs, Pydantic schemas, generated frontend types and affected tests together.