# UI specification
# UI specification â€” TOLTI AI

**Draft v0.1 Â· 7 September 2026 Â· Owner: Anshuman Â· Reviewers: Alok + Aditya**

Canonical path: `docs/uispec.md`. `docs/ui-spec.md` is a compatibility pointer for the earlier build plan. This specifies behavior and visual constraints; it is not a replacement prototype, pixel-perfect inspection of the handoff, or evidence that the backend works.

## 1. Reference and product character

Preserve the delivered dark React/TypeScript prototype's layout, components and CSS where appropriate. Do not use the rejected light-theme mockup, rewrite everything into Tailwind, or embed a standalone preview HTML as the production frontend.

The actual handoff archive was not available during drafting. Component names below are proposed responsibilities, not claims about the archive's exports. Before implementation, inspect its source, screenshots, `UI_SPEC.md` and `HANDOFF_PROMPT.md`; record real paths and discrepancies in [decisions](decisions.md).

**Character:** a focused collaborative workspace, not a dashboard. One primary work area, compact navigation, sparse accent color and context revealed when requested. No gradients, glow, decorative metrics, agent-avatar carousel, fake terminal or permanently open inspector.

## 2. Layout and tokens

```text
Desktop
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ Collapsible  â”‚ Room name Â· participants/roles Â· locality label   â”‚
â”‚ rooms +      â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ four modes   â”‚ Conversation / selected artifact                  â”‚
â”‚              â”‚ Source/review/activity controls open on demand    â”‚
â”‚              â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚              â”‚ Instruction Â· sources Â· mode Â· primary action     â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

Narrow viewport
Header with room/menu and role â†’ work area â†’ composer.
Rooms, participants, sources and review open as accessible drawers.
```

Proposed defaults; reconcile with the handoff rather than replacing its tokens:

| Token | Value / behavior |
| --- | --- |
| Canvas | `#191919` |
| Surface | `#202020` |
| Raised/hover | `#383836` |
| Main text | `#F5F5F5` |
| Secondary text | `#B3B3B3` |
| Accent/focus | `#5E9FE8` |
| Positive / warning / danger | `#72BC8F` / `#DE9255` / `#E97366`, always with words/icons |
| Border | `rgba(255,255,255,0.20)`; decorative only unless contrast is verified |
| Typography | Existing local/system sans stack; code in local system monospace; no external font request |
| Sizes | Body 16px, supporting text at least 14px, compact headings 20â€“24px |
| Spacing / radius | 4/8/12/16/24/32px spacing; about 8px radius |
| Navigation | Approximately 224px expanded; collapsible; not a content-width requirement |
| Main text | Readable measure around 680â€“760px; code/document editor may expand |

For a solid blue button, use dark text on `#5E9FE8`; do not assume white-on-blue meets contrast. Verify actual rendered pairs: 4.5:1 normal text, 3:1 large text and meaningful control/focus boundaries. Decorative borders need not be primary input outlines. Layout values are provisional, not measured from the prototype.

## 3. Routes and information architecture

Proposed browser routes:

- `/` â€” create room or join with invitation; real loading/errors.
- `/rooms/:roomId` â€” room shell; preserve the current view locally.
- Query state may identify mode/artifact for navigation, but never contain session tokens, invite tokens, cloud consent or private prompt/source text.
- Unknown/inaccessible rooms show a generic unavailable/access message; do not expose another room's title.

The room owns files, participants, one current driver, active run, output versions and activity. Switching Chat/Documents/Code/Agent is a view change, not a new session or room. Confirm before discarding unsent text. Do not cancel a run merely because its view is hidden.

## 4. Proposed component map

| Component responsibility | Proposed area | Data boundary |
| --- | --- | --- |
| `RoomShell`, `RoomSidebar`, `RoomHeader` | components | Snapshot + contiguous durable reducer |
| `ParticipantControl`, `ControlHandoffDialog` | panels | Membership/capability response; host-only HTTP commands |
| `TaskComposer`, `ModeSelector`, `SourcePicker` | components | Local draft â†’ server preflight; no provider call |
| `CloudConsentDialog`, `RouteStrip` | components | Exact preflight manifest/digest and selected model |
| `ChatView`, `DocumentsView`, `CodeView`, `AgentView` | views | Shared room state plus capability flags |
| `ArtifactViewer`, `ExpandedCodeView` | views/components | Persisted version; separate provisional stream |
| `SourcesDrawer`, `ReviewDrawer`, `ActivityDrawer` | panels | Authorized source/review/event routes |
| `ConnectionBanner`, `DiagnosticsPanel` | components/panels | Real local connection and sanitized model status |
| API client, generated types, event reducer | lib | One transport layer and one durable state model |

Names may adapt to existing code. Do not invent a matching implementation file merely to satisfy this table.

## 5. Core interaction sequence

1. **Create/join.** A valid session is required. Creating makes the person host + driver. Joining makes them watcher; a display name never grants capabilities. Invitations are entered without putting their token in a URL query.
2. **Assign review.** Host uses People to grant the other participant reviewer. Show role and driver ownership persistently but compactly. A disabled control includes a reason, not just reduced opacity.
3. **Prepare task.** Driver enters instruction and explicitly selects context. Documents show filename/type/coverage; selecting a source is not cloud consent.
4. **Preflight.** â€œReview & runâ€ requests a local preflight. Show the actual selected model, code/text family, route reason, context excerpts/coverage and cloud boundary. Ambiguity asks a focused question rather than starting anything.
5. **Consent.** Require an unchecked acknowledgement: â€œSend this selected context to Modal for this run.â€ Show instruction and included excerpts/conversation scope; offer local preview. â€œRun on Modalâ€ submits the preflight ID/digest. Any changed draft/source invalidates this approval.
6. **Running.** Immediately display queued/running state and request status. Double click reuses the same command key. Provisional streamed text is labeled and not exportable as saved success. Offer Cancel to the current driver; label best-effort cancellation.
7. **Saved output.** Render the server's committed artifact version. Show model/location, version and review state. Sources and limitations stay inspectable without occupying a permanent column.
8. **Review.** Driver submits exact version. Reviewer opens read-only content and source excerpts, sees version/hash identifier and chooses Approve or Request changes. Require a reason for changes. The server's response determines the badge.
9. **Revision/export.** Edits create a new draft version; historic decisions remain on their versions. Only the current approved version exposes official Export. Code always shows â€œNot executedâ€; approval does not execute it.

Do not start the task on pressing Enter inside a multiline instruction. Support a documented Ctrl/Cmd+Enter shortcut for â€œReview & runâ€; it never bypasses the consent step.

## 6. Mode-specific behavior

### Code

Generate/explain choice maps to explicit backend workflow. Render code as inert text with syntax highlighting only. Show explanation, assumptions and suggested tests; never label tests Passed without independent executed evidence. Copy code is allowed but is not execution. â€œRun codeâ€, automatic repository writes and shell controls are absent.

### Documents

Summary first; PDF Q&A only when enabled by actual capability. Select ready sources; show extracting/ready/partial/rejected state and which pages were included. A citation opens the stored source, exact page/line and excerpt. Unknown citation shows an invalid-reference warning and blocks unsupported presentation; never fabricate a source drawer entry.

A mixed text/scan PDF may only expose extracted pages with explicit partial coverage. Fully scanned, encrypted or unsupported files show a reason and suggested text-based alternative. No simulated OCR.

### Chat

Unavailable until real text workflow integration is enabled. When enabled, display the bounded history included in preflight; old room conversations must not be silently sent wholesale. No tools, web browsing or fictional citations.

### Agent

One bounded report-to-note workflow: choose one report â†’ preview evidence scope â†’ run â†’ show supported findings and advisory note â†’ request independent review â†’ approved Markdown export. The stages derive from real state, not animated fictitious tool calls. It uses the text model; no third model or autonomous tool loop.

## 7. Required states and copy

| State | User-visible behavior |
| --- | --- |
| No room/history | Explain next action; no seeded live-looking activity |
| Backend checking/unavailable | â€œChecking local appâ€¦â€ / â€œLocal app unavailableâ€; Retry preserves draft |
| Model unconfigured | â€œNot configuredâ€; never Ready just because URL fields exist |
| Queued/running | Show model/location and real state; single active action |
| Streaming | Provisional output; safe text rendering; no final approval controls |
| Awaiting review | â€œDraft Â· awaiting reviewâ€ with exact version |
| Approved | â€œApproved Â· version Nâ€; retain advisory / Not executed labels |
| Changes requested | Decision comment and explicit new-version action |
| Forbidden | â€œOnly the current driver can start this taskâ€ or matching capability reason |
| Stale conflict | â€œThis version changed. Reload the current version before reviewing.â€ Preserve comment for manual reconsideration; never resubmit automatically. |
| Reconnecting | Keep saved content with a stale-state notice; disable mutations until authoritative state is restored |
| Provider unavailable/timeout | â€œModal inference unavailable. Local history is still available.â€ Manual retry requires new preflight/consent. |
| Cancel requested | â€œCancellingâ€¦ Remote work may continue briefly.â€ Wait for terminal server result. |
| Interrupted after restart | â€œInterrupted by app restart. No automatic retry was started.â€ |
| Session expired | Rejoin/authenticate flow; never reclaim a role from a display name |
| Fixture mode | Persistent â€œDemo fixtures â€” not live backendâ€ banner; production build rejects fixture mode |
| Capability not implemented | â€œNot available in this buildâ€; no successful-looking fake behavior |

HTTP/WS state names come from [contracts](contracts.md). Local UI state must not be renamed into an incompatible server enum.

## 8. Drawers, diagnostics and responsive behavior

- Desktop: open context only on request; one drawer at a time. Opening Sources from a citation focuses the requested excerpt. Closing restores focus to the opener.
- Below the handoff's approved narrow breakpoint (proposed 768px): navigation becomes a drawer; work remains first; review/source surfaces fit the viewport. At 390px, no page overflow.
- Wide code and tables scroll within their own bounded region. The composer remains reachable above the virtual keyboard. Safe areas and sticky regions must not cover content or focused controls.
- Use semantic dialogs, Escape, focus containment for modal drawers, keyboard tabs and accessible names for icon-only buttons. Target touch controls at least 44Ã—44px.
- Announce meaningful run/status changes in a polite live region, not every generated token. Respect reduced motion.
- â€œLocal app / Modal cloud inferenceâ€ is one compact persistent header indicator. Repeat detailed egress disclosure in preflight, not every panel.
- Activity is real committed events. Diagnostics is sanitized structured metadata; never expose raw server log files, secret configuration or a fake terminal.

## 9. Frontend state and safety

Server snapshot + one tested durable-event reducer own room state. Transient stream buffer is keyed by run ID/delta index and discarded after terminal state/snapshot. Local component state owns drawer, tab, draft and focus only. No optimistic approved badge, role grant or fake model success.

Render Markdown using a safe allowlisted renderer; disable raw HTML and unsafe URL schemes. Render code inertly. External links do not fetch automatically; use appropriate isolation when opened. Serve documents through authorized local routes, not arbitrary returned URLs. Never include secrets in Vite variables.

## 10. UI acceptance evidence

Run keyboard/focus and no-overflow checks, long-output tests, role-state tests and reducer recovery tests. Two-browser integration must hit the real server; it is not proven by a static preview. No visual acceptance, accessibility conformance or multiplayer-test pass is claimed by this document.