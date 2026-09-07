# Application contracts â€” TOLTI AI

**Draft v0.1 Â· 7 September 2026 Â· Joint approval: Alok + Anshuman**

Proposed Gate G0 contract. These routes and types are not implemented or generated OpenAPI. Endpoint names, anonymous identity, consent preflight, numeric limits and revision semantics require review before coding. Update this document and regenerate client/event types together when an approved contract changes.

## 1. Conventions

- HTTP base `/api/v1`; WebSocket `/ws/v1/rooms/{room_id}`. JSON uses `snake_case`, UTF-8, UUID entity IDs, UTC ISO-8601 timestamps and integer revisions/sequences.
- Every resource lookup is scoped to its authorized room. Unauthenticated: 401. Nonmember/foreign resource: generic 404. An authorized member without a capability: 403.
- Same-origin opaque session cookie: HttpOnly, SameSite=Strict, Secure outside explicit loopback development. Exact Origin validation for session creation, mutations and WS handshakes; mutations also require `X-CSRF-Token`, except initial session creation. Enforce allowed Host headers.
- JSON mutations require `Content-Type: application/json`. Source upload uses bounded multipart with CSRF/Origin protection. Download routes require session + membership even if their URLs are known.
- `Idempotency-Key` is a client-generated UUID, required on room creation, source upload, role/removal/handoff commands, preflight creation, run/cancel commands, version creation, review submission and review decisions. Invite creation and session creation are explicit exceptions; see section 7.
- HTTP responses include a generated request correlation ID; secrets and raw request bodies are not operational-log fields.
- Unknown fields are rejected on command schemas. Client-supplied actor IDs, roles, provider URLs or authoritative status cannot override server decisions.

Error envelope:

```json
{
  "error": {
    "code": "STALE_REVIEW",
    "message": "This review is no longer current. Reload the artifact.",
    "request_id": "40000000-0000-4000-8000-000000000001",
    "details": { "current_review_revision": 2 }
  }
}
```

Errors must not echo document/prompt bodies, provider responses, raw paths or another room's metadata. All examples use synthetic values.

## 2. Capabilities

| Action | Host relationship | Driver role | Reviewer role | Watcher role |
| --- | --- | --- | --- | --- |
| Read room, allowed sources, artifacts/events | Membership required | Yes | Yes | Yes |
| Issue/revoke invitations; assign reviewer/watcher; remove non-host/non-driver | Required | No grant from task role | No grant from task role | No grant from task role |
| Transfer driver control while idle | Required | No grant from task role | No grant from task role | No grant from task role |
| Upload source; preflight; start/cancel run; create revision; submit review | No grant from host alone | Yes | No | No |
| Approve/request changes | No grant from host alone | No | Yes, if independent | No |
| Official current-approved-version export | Membership required | Yes | Yes | Yes |
| View sanitized room diagnostics | Membership required | Yes | Yes | Yes |

A host has one task role like any member. Creation gives host + driver. Joining always gives watcher. Granting a role does not prove that two principals correspond to two humans. Removing/changing the current driver requires an atomic handoff; removing the host is out of scope.

## 3. Core response shapes

Types below are minimum contracts. Bounded lengths/counts are in section 12. Optional fields are explicitly marked; all omitted-to-clear semantics require a separate approved contract rather than guessing.

| Type | Fields |
| --- | --- |
| `SessionView` | `principal_id`, `display_name`, `expires_at`, `csrf_token`; never session token |
| `MembershipView` | `principal_id`, `display_name`, `role: driver/reviewer/watcher`, `is_host`, server-computed `capabilities` |
| `RoomView` | `id`, `name`, `revision`, `host_principal_id`, `driver_principal_id`, `last_seq` |
| `SourceView` | `id`, `room_id`, `filename`, `media_type`, `byte_size`, `content_hash`, `parse_state`, `coverage`, safe error code if rejected |
| `ExcerptView` | `id`, `source_id`, `source_content_hash`, `page_number` or `line_start/line_end`, `text`, `text_hash` |
| `RouteDecision` | `workflow`, `provider_key: code/text`, `model_id`, `model_revision`, `selected_by: explicit/auto`, `reason_code`, `prompt_version` |
| `PreflightView` | `id`, `room_id`, `initiator_principal_id`, `expires_at`, `route`, `input_digest`, `egress_manifest`, `warnings` |
| `RunView` | `id`, `room_id`, `initiator_principal_id`, `preflight_id`, `status`, `route`, created/started/finished timestamps (latter two nullable), safe `error` (nullable), `remote_outcome_unknown`, `artifact_id` (nullable) |
| `ArtifactVersionView` | `id`, `artifact_id`, `version_number`, `content`, `content_hash`, `author_principal_ids`, `created_at`, `run_id` (nullable for manual revision), derived `review_state` |
| `ReviewView` | `id`, `artifact_id`, `version_id`, `content_hash`, `submitted_by`, `revision`, `state`, `decision` (nullable) |

`coverage` includes source pages/lines present, successfully extracted locations, locations included in this run and exclusions/reasons. Full parsing is not a claim of full model context. Hashes use `sha256:` followed by 64 lowercase hex characters.

A `RoomSnapshot` includes `room`, `memberships`, `sources`, `active_run` (nullable), artifact summaries/current version pointers, open/historical review summaries, `snapshot_seq` and `capabilities`. Historical bodies/events use paginated authorized routes; do not load unbounded artifacts into the initial snapshot. Each list endpoint returns `items`, `next_cursor` (nullable); default 50, maximum 100 except event replay. Cursors are opaque server-validated values.

## 4. HTTP inventory

Path parameters are room-scoped. `expected_room_revision`, `expected_current_version_id` and `expected_review_revision` are mandatory concurrency preconditions, not optional UI hints.

### Health, identity and rooms

| Method / path | Request | Response / behavior |
| --- | --- | --- |
| `GET /health/live` | None | 200 process status; no sensitive config |
| `GET /health/ready` | None | 200 local DB/migration/asset readiness or 503; independent of paid inference success |
| `POST /sessions` | `{display_name}` | 201 session + cookie; valid existing cookie returns 200 current session instead of minting another principal |
| `GET /sessions/current` | Cookie | 200 `SessionView`; 401 expired/revoked |
| `DELETE /sessions/current` | CSRF | 204 revoke current session and close its sockets; does not hand off host/driver automatically |
| `POST /rooms` | `{name}` | 201 `RoomView`; creator becomes host + driver |
| `GET /rooms` | Pagination | 200 only this principal's rooms |
| `GET /rooms/{r}/snapshot` | None | 200 consistent `RoomSnapshot` and high-water sequence |
| `POST /rooms/{r}/invites` | `{expires_in_seconds}` | 201 `{invite_id, token, expires_at}`; host only; no token in events/logs |
| `GET /rooms/{r}/invites` | Pagination | Host-only metadata, no plaintext tokens |
| `DELETE /rooms/{r}/invites/{i}` | None | 204 revoke; host only; repeat revoke is a no-op |
| `POST /rooms/join` | `{invite_token}` | 200 room/membership; valid token is consumed atomically; same principal retry on its just-consumed valid token returns prior membership; others cannot reuse it |
| `POST /rooms/{r}/memberships/{p}/role` | `{role: reviewer/watcher, expected_room_revision}` | Updated snapshot metadata; host only; cannot demote current driver via this path |
| `DELETE /rooms/{r}/memberships/{p}` | `{expected_room_revision}` | 204; host only; reject host/current driver removal |
| `POST /rooms/{r}/handoff` | `{target_principal_id, expected_room_revision}` | Updated room/memberships; target becomes driver, old driver becomes watcher; host only; active run blocks handoff |

Host creates expiring single-use invites. A lost invite-creation response is handled by listing/revoking that invite and creating another, not retrieving its plaintext secret. Join retries are tied to the consumed token and principal; names alone cannot reclaim membership.

### Sources, preflight and runs

| Method / path | Request | Response / behavior |
| --- | --- | --- |
| `POST /rooms/{r}/sources` | Multipart `file`, permitted-use confirmation | 202 `SourceView` in extracting state; driver only; local processing |
| `GET /rooms/{r}/sources` | Pagination | `SourceView` list |
| `GET /rooms/{r}/sources/{s}` | None | Source parse/coverage metadata |
| `GET /rooms/{r}/sources/{s}/file` | None | Authorized bytes with safe MIME/disposition; never a public storage URL |
| `GET /rooms/{r}/sources/{s}/excerpts` | Pagination; optional page filter | Fixed extracted text with page/line provenance |
| `POST /rooms/{r}/preflights` | `TaskIntent` below | 201 `PreflightView`; local routing/context work only, never model inference |
| `GET /rooms/{r}/preflights/{p}` | None | Initiating current driver only; exact manifest preview |
| `POST /rooms/{r}/runs` | `{preflight_id, input_digest, consent: {accepted: true, destination: modal}}` | 202 committed `RunView`; one accepted preflight can create only one run |
| `GET /rooms/{r}/runs` | Pagination | Persisted runs |
| `GET /rooms/{r}/runs/{run}` | None | Persisted run; never fabricated successful output |
| `POST /rooms/{r}/runs/{run}/cancel` | Empty JSON object | Current run state; queued â†’ cancelled, running â†’ cancelling; driver only |

`TaskIntent` fields: `workflow` from `auto/code_generate/code_explain/summarise/chat/pdf_qa/inspection_note`; `instruction`; `source_ids` (possibly empty); `conversation_version_ids` (possibly empty); optional `language` for code. Server rejects unsupported/disabled workflows and cross-room, unready or excessive context. Agent requires exactly one selected report; PDF Q&A requires a ready text-PDF source. Code/chat cannot use unspecified ambient room context.

The preflight stores immutable normalized intent, exact selected excerpts/messages and route. Its digest covers that manifest and route/prompt version. A start request cannot alter the prompt, model or source selection. Reject expired/consumed/mismatched preflights or changed source hashes. No consent checkbox is accepted as a substitute for a server-known manifest. Source selection is not consent.

Proposed egress manifest: destination `modal`, model ID/revision, direct instruction, bounded selected conversation content, source/excerpt IDs, exact excerpt text/hashes, included/excluded locations and input-size estimate. Do not include original binary files, unrelated room history or participant emails. Room members share source visibility; only the initiating driver sees their unpublished preflight instruction.

### Artifacts and review

| Method / path | Request | Response / behavior |
| --- | --- | --- |
| `GET /rooms/{r}/artifacts` | Pagination | Artifact summaries + current version pointer |
| `GET /rooms/{r}/artifacts/{a}/versions` | Pagination | Version metadata/history |
| `GET /rooms/{r}/artifacts/{a}/versions/{v}` | None | Exact stored `ArtifactVersionView` |
| `POST /rooms/{r}/artifacts/{a}/versions` | `{expected_current_version_id, content}` | 201 new draft version; driver only; server computes hash/provenance/author set |
| `POST /rooms/{r}/artifacts/{a}/review-requests` | `{version_id, content_hash}` | 201 current-version review request; driver only |
| `POST /rooms/{r}/reviews/{review}/decision` | `{version_id, content_hash, expected_review_revision, decision: approve/request_changes, comment}` | 200 terminal review; reviewer and independence checks; nonempty comment required for changes |
| `GET /rooms/{r}/artifacts/{a}/versions/{v}/export?format=markdown` | None | Current approved version only; attachment includes advisory/version/source/decision metadata; older/draft versions return 409 |
| `GET /rooms/{r}/events?after_seq=S&limit=N` | Integer sequence | Ordered durable events; maximum 500 per response; `next_after_seq`, `has_more`, `high_water_seq` |
| `GET /rooms/{r}/diagnostics` | None | Allowlisted room/request/provider metadata, never raw logs or credentials |

Source evidence used by an artifact version remains resolvable. No unrestricted source delete, artifact overwrite or rollback of a terminal review exists in v0.1.

## 5. Artifact content and hashing

The `content` schema is discriminated by `kind`: `code`, `summary`, `chat`, `pdf_answer`, `inspection_note`. Shared fields: `schema_version: 1`, `kind`, `title`, typed `body`, `citations`, `coverage` (nullable for non-document work), `limitations`.

- Code body: `language`, `code`, `explanation`, `assumptions[]`, `suggested_tests[]`. Tests are suggestions, not execution results.
- Summary/chat/PDF-answer body: `markdown`; PDF answer also has `answer_status: supported/insufficient_evidence`.
- Inspection-note body: `markdown`, `supported_findings[]` with excerpt references. Do not output a real-plant safety certification or autonomous next action.
- Citation: allowlisted excerpt/source IDs, source content hash, exact page/line location and quoted excerpt text/hash attached by the server from fixed records. A model may reference excerpt IDs but may not author authoritative evidence metadata.

Reject unknown citation IDs. Schema-valid citations do not prove a claim is supported; human evidence review remains required. Unsupported questions may produce an honest insufficient-evidence artifact with limitations, not fake citations.

Canonicalization: UTF-8 JSON of the stored `content` with lexicographically sorted object keys, compact separators, no non-finite numbers, arrays in stored order and only safe integers where numeric values are needed. Use the Python canonical serialization contract `json.dumps(content, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)`, then SHA-256. Preserve string bytes; normalize at content creation if needed, not later when reviewing. Hash the exact persisted canonical bytes; clients display/send the server hash rather than implementing another algorithm.

Changing any content/provenance/coverage creates another version. Current-version pointer and author union are server-maintained. Model outputs are not independent human reviewers.

## 6. State transitions and race rules

**Run:**

```text
queued -> running -> succeeded
queued -> cancelled
running -> cancelling -> cancelled
queued/running/cancelling -> interrupted   (restart/shutdown recovery)
queued/running -> failed
```

`failed`, `cancelled`, `interrupted`, `succeeded` are terminal. `cancelling` blocks success commit: late provider chunks/output are discarded. If success committed first, cancel returns 409 `RUN_TERMINAL`. Cancellation means local cancellation, not guaranteed remote termination/no billing. If cancelling is interrupted by a process crash, recovery marks interrupted and flags remote outcome unknown when appropriate.

**Source parse:** `extracting -> ready/partial/rejected`. Only approved usable excerpts of ready/partial sources enter preflight. No automatic OCR or unlimited parse retry.

**Version/review:**

```text
new version -> draft
current draft -> in_review
in_review -> approved | changes_requested
new version while old review is open -> old request superseded; new draft
```

Only one review request per version in v0.1. After changes requested, create a new version before re-submission. A terminal old approval remains historical after a newer draft appears. Decision requires an open request for the current version, exact content hash and matching review revision. Multiple concurrent decisions: one wins, others get 409. Duplicate same-key submissions return the prior result.

## 7. Idempotency and transaction rules

Key scope is `(principal_id, HTTP method, canonical resource path, Idempotency-Key)`; normalize path/query parameters relevant to the command. Fingerprint canonical validated payload; for upload use file bytes hash + declared fields, never a raw body log. Proposed retention: at least the controlled demo plus 24 hours after a key's first acceptance.

- Same key + same fingerprint returns the prior semantic resource/result, with no duplicate event or provider dispatch. In-flight run duplicates return the existing queued/running resource.
- Same key + changed payload returns 409 `IDEMPOTENCY_CONFLICT`.
- Different key + same consumed preflight returns 409 `PREFLIGHT_CONSUMED`; never a second paid run.
- Perform key claim, invariant checks, mutation, result reference and event insertion in one short transaction. Unique indexes handle races; in-memory checks alone do not.
- Room revision increments on membership/driver changes. Review revision increments on transition. A read-then-unconditional-write is not sufficient.
- Session/invite creation exceptions avoid storing plaintext secrets in an idempotency cache. Invite revoke is naturally idempotent; join replay uses consumed-token/principal binding. Health/read requests do not require a key.

## 8. Durable event envelope

```json
{
  "schema_version": 1,
  "event_id": "50000000-0000-4000-8000-000000000001",
  "room_id": "10000000-0000-4000-8000-000000000001",
  "seq": 18,
  "type": "run.queued",
  "occurred_at": "2026-09-07T06:30:00Z",
  "actor_principal_id": "30000000-0000-4000-8000-000000000001",
  "payload": {
    "run_id": "20000000-0000-4000-8000-000000000001",
    "status": "queued",
    "provider_key": "code"
  }
}
```

Minimum event families: `room.created`, `membership.joined`, `membership.role_changed`, `membership.removed`, `driver.handed_off`, `source.created`, `source.parse_finished`, `run.queued`, `run.started`, `run.cancelling`, `run.terminal`, `artifact.version_created`, `review.requested`, `review.decided`, `review.superseded`.

Payloads contain validated resource IDs and the minimal state needed for a reducer; full saved bodies load through authorized routes. A payload is a type-discriminated schema, not an arbitrary dictionary. Define/export each implemented event payload in the same contract patch. Actor may be null for recovery/system events. Never broadcast invitation/session secrets, preflight bodies or operational raw logs.

`seq` is increasing, gap-free for committed room events. Assign by transactional update to room `last_seq`; rollback leaves no committed gap. Multiple events in one transaction are ordered explicitly. Commit state/events before publishing; durable clients deduplicate by room/seq.

## 9. Transient stream and reconnect

Transient envelope is separate; it never carries a durable `seq`:

```json
{
  "schema_version": 1,
  "type": "run.delta",
  "room_id": "10000000-0000-4000-8000-000000000001",
  "run_id": "20000000-0000-4000-8000-000000000001",
  "delta_index": 7,
  "text": "Provisional output fragment"
}
```

Only server-authorized room members receive it. It is lossy, safe-text-rendered and bounded. Ignore chunks for terminal/foreign runs and duplicate delta indexes. A snapshot/terminal artifact replaces preview state; no preview is silently promoted to saved content.

Reconnect algorithm:

1. Disable mutations while authoritative connection state is uncertain. Fetch consistent snapshot and `S`.
2. Open `/ws/v1/rooms/{room_id}?after_seq=S` with session cookie; no secret query token.
3. Server authenticates Origin/session/membership, registers a bounded live buffer, then reads replay high-water `H` and replays `(S, H]` in order. Drain buffer above last sent sequence, deduplicating overlap.
4. Client ignores events at/below applied sequence, applies exactly the next sequence and recovers on a gap. Fetch replay pages or a fresh snapshot; never advance over a missing event.
5. Buffer overflow/cursor invalidation sends `recovery.required` control message and closes. Snapshot again rather than keeping unbounded memory.

Control messages include `connection.ready` after replay, `recovery.required` with safe reason and heartbeat acknowledgements. They have no durable sequence. Reject commands over WS; mutation remains HTTP. Revalidate session/membership during connection and close immediately on known local revocation/removal. Proposed heartbeat 15s; clients declare disconnect after two missed heartbeats.

Use safe application close codes: 4401 expired session; 4404 unavailable room/membership; 4409 recovery required. Reject bad Origin before accepting the socket. Exact framework handshake mechanics require implementation tests.

## 10. Error taxonomy

| Status | Codes / use |
| --- | --- |
| 400 | `INVALID_REQUEST`, `ORIGIN_NOT_ALLOWED`, malformed cursor |
| 401 | `SESSION_REQUIRED`, `SESSION_EXPIRED` |
| 403 | `ROLE_FORBIDDEN`, `SELF_REVIEW_FORBIDDEN`, `CSRF_INVALID` |
| 404 | `RESOURCE_NOT_FOUND`, invalid/unavailable invite without leaking metadata |
| 409 | `ROOM_REVISION_CONFLICT`, `ACTIVE_RUN_EXISTS`, `DRIVER_REPLACEMENT_REQUIRED`, `IDEMPOTENCY_CONFLICT`, `PREFLIGHT_CONSUMED`, `PREFLIGHT_CHANGED`, `STALE_VERSION`, `STALE_REVIEW`, `REVIEW_NOT_OPEN`, `RUN_TERMINAL`, `EXPORT_NOT_APPROVED` |
| 410 | `PREFLIGHT_EXPIRED` for a known authorized preflight |
| 413 | `FILE_TOO_LARGE`, `CONTEXT_TOO_LARGE` |
| 415 | `UNSUPPORTED_FILE_TYPE` |
| 422 | `ROUTE_CLARIFICATION_REQUIRED`, `CONSENT_REQUIRED`, `SOURCE_NOT_READY`, invalid workflow/content |
| 429 | `RATE_LIMITED`, bounded local queue capacity; optional safe retry-after, never auto-paid retry |
| 503 | `LOCAL_NOT_READY`, `PROVIDER_NOT_CONFIGURED`, `WORKFLOW_UNAVAILABLE` before run admission |

After a run is accepted with 202, provider errors are persisted terminal run errors and delivered through events/GET, not retroactively changed HTTP responses. Codes include `PROVIDER_AUTH_FAILED`, `PROVIDER_RATE_LIMITED`, `PROVIDER_UNAVAILABLE`, `PROVIDER_TIMEOUT`, `PROVIDER_PROTOCOL_ERROR`, `OUTPUT_INVALID`, `EMPTY_COMPLETION`. Preserve whether remote completion/billing is unknown.

## 11. Provider boundary

See [provider contract](provider-contract.md). Router ordering is access/limits/consent readiness â†’ explicit mode â†’ clear Auto intent â†’ clarification â†’ allowlisted provider. Preflight constructs the consentable selection; actual consent is required again at run admission. Never classify based on document instructions or dispatch merely to obtain a route suggestion.

## 12. Proposed limits requiring G0 review

Source file 10 MiB; PDF 20 pages; up to 3 selected sources; 12 excerpts; direct instruction 8,000 characters; preflight expiry 10 minutes; invite default expiry 30 minutes (maximum 24 hours); session absolute expiry 12 hours. Proposed model input 6,000 tokens including system/instruction/context and reserved output 1,500 tokens; real tokenizer/context validation is mandatory before activation.

These are adjustable **design defaults**, not official rules, model capacity measurements or verified safe universal limits. Exact excerpts included in preflight reflect the enforced token budget; reject or visibly narrow before consent rather than silently truncating later. App limits plus provider timeouts/queue bounds must have tests. Final approved config/schema is the implementation's source of truth.