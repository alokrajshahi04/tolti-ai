# Product requirements â€” TOLTI AI

**Draft v0.1 Â· 7 September 2026 Â· Product: Pallavi & Bhargavi Â· Technical reviewers: Alok + Anshuman**

## 1. Problem and outcome

An engineer needs to work on a bounded code or document task with teammates without passing disconnected chat screenshots. The room must retain selected context, progress, saved artifacts and a version-specific human decision.

**Core journey:** create room â†’ invite teammate â†’ establish driver/reviewer roles â†’ select a task and permitted context â†’ consent to Modal inference â†’ receive a saved artifact â†’ submit its exact version for independent review â†’ retain the decision and export the approved artifact.

This is advisory drafting software, not an equipment controller, engineering certification system, unattended agent platform or arbitrary code runner.

## 2. Users and authority

- **Driver:** chooses context, starts/cancels work, edits saved drafts and requests review.
- **Reviewer:** inspects evidence and decides on an exact submitted version; cannot approve content they authored or submitted.
- **Watcher:** reads authorized room context and history without modifying tasks or decisions.
- **Host:** an administrative relationship to the room, separate from task role. Grants roles, manages invitations and transfers control. Host status alone does not authorize a run or review.

A new room's creator is its host and initial driver. Invited participants join as watchers. Browser sessions are not verified human identities; trusted host assignment and a real second human are required for the demonstration. See [security](security.md).

## 3. Scope and delivery gates

| Gate | Required outcome | Exclusions at this gate |
| --- | --- | --- |
| G0 â€” contract review | Approved scope, role matrix, API/events and blocking decisions | No scaffold or deployment |
| G1 â€” skeleton | Existing dark UI opens; actual FastAPI health; honest backend-unavailable state; one-origin production serving | No pretend auth, model readiness or multiplayer |
| G2 â€” multiplayer | Revocable sessions, invites, server roles, durable events, snapshot/replay; two sessions see committed state | No inference or review approval |
| G3 â€” provider proof | Both approved real models answer, deterministic routing and per-run consent, bounded errors | No silent fallback or paid automatic retry |
| G4 â€” core demo | Code and bounded document summary artifacts, provenance, exact-version independent review, restart recovery | No image/P&ID claim, arbitrary execution or general agent |
| G5 â€” focused extensions | Chat; page-cited PDF Q&A; one bounded report-to-note agent workflow | No autonomous tools, host actions or multi-agent framework |
| G6 â€” rehearsal | Required tests/evidence, actual-device run, failure recovery and accurate claims | No readiness claim from documents alone |

G6 validates the scope actually delivered. G5 is not a prerequisite for rehearsing the G4 core, but undelivered modes must remain visibly unavailable. Confirm whether official requirements make a G5 capability mandatory before freezing the scope.

## 4. Navigation modes versus backend workflows

The UI has four room modes, not four separate applications and not four models:

| Room mode | Initial behavior | Later bounded behavior | Model family |
| --- | --- | --- | --- |
| Chat | Visible but unavailable until enabled | General bounded text conversation, no tools | Text |
| Documents | Text/text-PDF summaries from selected local sources | Page-cited PDF Q&A | Text |
| Code | Generate or explain code; saved code artifact marked Not executed | Improvements only after core proof | Code |
| Agent | Visible but unavailable until enabled | Selected report â†’ supported findings â†’ note draft â†’ independent review â†’ approved Markdown export | Text |

All modes share membership, files, the event timeline, artifacts and review. Changing navigation mode cannot change a role, active run or selected artifact silently. See [UI spec](ui-spec.md) and [contracts](contracts.md).

## 5. Functional acceptance requirements

- **FR-01 â€” rooms and access:** create/join using authorized sessions; a nonmember cannot enumerate or read another room's sources, runs, events or artifacts.
- **FR-02 â€” roles and control:** one designated driver per active room; one active run per room. Host-only role grants and handoff are atomic. Watcher/reviewer task writes are denied by the server.
- **FR-03 â€” synchronization:** committed events are ordered per room; refresh/reconnect resumes without duplicated durable output. New members receive history. A missing sequence triggers recovery, not guesswork.
- **FR-04 â€” task routing:** explicit workflow selection wins after validation. Auto uses only the user's direct requested intent. Ambiguous/mixed intent asks for clarification before creating a paid run.
- **FR-05 â€” cloud consent:** the initiating driver sees the exact selected context scope and destination. Consent binds to a fresh preflight input digest. A changed task/source needs a new preflight and consent.
- **FR-06 â€” code artifact:** proposed code, explanation, assumptions and suggested tests are saved. Output is never executed or written into a repository automatically.
- **FR-07 â€” summary artifact:** covers only extracted/selected text; displays source references, limitations and extraction coverage. Invalid source references cannot become invented citations.
- **FR-08 â€” review:** a stored version/hash is submitted. An authorized independent reviewer approves or requests changes. Stale, concurrent and self-review decisions are rejected. New content creates a new unapproved version.
- **FR-09 â€” persistence:** completed artifacts and decisions survive a restart. Interrupted work is labeled; the app never silently restarts paid inference.
- **FR-10 â€” failure truth:** unavailable backend/provider, denied actions, partial extraction and connection loss are understandable states, not simulated success.
- **FR-11 â€” focused extensions:** PDF Q&A can abstain when evidence is missing. Agent work uses one selected report and one bounded generation step; independent review precedes final export.
- **FR-12 â€” diagnostics:** authorized diagnostics distinguish local app activity from outbound Modal activity. Logs contain correlation metadata, not raw documents, prompts, outputs or credentials.

## 6. Quality requirements

- Use locally bundled assets; React/TypeScript/Vite in `frontend/`, Python/FastAPI in `backend/`, Modal deployment code in `infra/modal/`.
- Accessible dark interface: keyboard operation, visible focus, labeled roles/states, readable contrast and no page-level horizontal overflow at 390px.
- Store authoritative state locally in SQLite; keep user uploads behind authorized routes and outside the public asset mount.
- Bound files, parsing, queues, model input/output and timeouts. Numeric starting limits require team approval and model-specific verification.
- Do not claim latency, throughput, GPU fit, security assurance or model quality before observing them. Record real observations rather than made-up service-level targets.
- Record tests as PASS, FAIL, NOT RUN or BLOCKED with the build and evidence path.

## 7. Explicit non-goals

Air-gapped inference under the Modal baseline; production identity/accounts; SSO; multiple backend workers; Redis; five specialist agents; autonomous equipment action; arbitrary tools or code execution; unrestricted URL retrieval; scan/OCR/vision support; public internet hosting; immutable/tamper-proof audit claims; automatic production deployment; hidden model fallback.

## 8. Demo scenario and success

Use public, licensed or explicitly synthetic inputs. A fictional Pump P-204 case must carry **Synthetic demonstration scenario**. Do not suggest it represents a real incident or that the output is safe operating advice.

The minimum live proof is two actual devices sharing a room, both intended real model workflows producing saved outputs, inspectable evidence, an independent exact-version decision, rejection of a forbidden/stale action, and truthful provider failure on internet loss while local history remains usable. Two browser contexts on one device are useful evidence, but must not be relabeled as two-device testing.

## 9. Blocking questions

Official deadline/submission format; whether cloud inference is permitted; any mandatory offline/vision capability; actual demo OS/LAN setup; Modal budget; tested model revisions; permitted inputs; prototype reconciliation. Owners and approval gates are in [decisions](decisions.md).