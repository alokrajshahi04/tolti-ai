import React, { useEffect, useRef, useState } from "react";
import { Icon } from "../components/Icon";
import { code, downloadText, note, people, sourceText } from "../fixtures";
import type {
  AgentState,
  EventItem,
  Mode,
  Panel,
  PersonId,
  ReviewState,
} from "../types";
interface Props {
  panel: Panel;
  close: () => void;
  identity: PersonId;
  setIdentity: (id: PersonId) => void;
  driver: PersonId;
  handoff: () => void;
  requestControl: () => void;
  events: EventItem[];
  mode: Mode;
  review: ReviewState;
  version: number;
  decision: (decision: ReviewState, reason: string) => void;
  agent: AgentState;
}
const titles: Record<string, string> = {
  people: "People & control",
  sources: "Room files",
  activity: "Shared activity",
  logs: "Execution details",
  review: "Review output",
  outputs: "Room outputs",
};
export function ContextPanel(p: Props) {
  const ref = useRef<HTMLDialogElement>(null);
  const [reason, setReason] = useState("");
  const [error, setError] = useState("");
  useEffect(() => {
    const trigger = document.activeElement as HTMLElement | null;
    ref.current?.showModal();
    return () => trigger?.focus();
  }, []);
  const reviewer = p.identity === "pallavi" && p.identity !== p.driver;
  const canReview =
    reviewer &&
    p.review === "pending" &&
    (p.mode !== "agent" || p.agent === "review");
  const status =
    p.review === "approved"
      ? "Approved"
      : p.review === "changes"
        ? "Changes requested"
        : "Awaiting review";
  function decide(d: ReviewState) {
    if (!canReview) return;
    if (d === "changes" && !reason.trim()) {
      setError("Add a short note describing the change.");
      return;
    }
    p.decision(d, reason);
  }
  return (
    <dialog
      ref={ref}
      className="context-dialog"
      onCancel={p.close}
      onClick={(e) => {
        if (e.target === ref.current) p.close();
      }}
      aria-labelledby="panel-title"
    >
      <div className="panel-head">
        <div>
          <div className="eyebrow">P-204 INSPECTION</div>
          <h2 id="panel-title">{titles[p.panel!]}</h2>
        </div>
        <button className="icon-btn" onClick={p.close} aria-label="Close panel">
          <Icon name="close" />
        </button>
      </div>
      <div className="panel-body">
        {p.panel === "people" && (
          <>
            <p className="muted">
              One person drives. Everyone keeps the context.
            </p>
            <div className="people-list">
              {people.map((person) => (
                <div className="person-row" key={person.id}>
                  <span
                    className={`avatar ${person.id === p.driver ? "driver-ring" : ""}`}
                  >
                    {person.initials}
                  </span>
                  <div>
                    <strong>
                      {person.name}
                      {person.id === p.identity ? " (you)" : ""}
                    </strong>
                    <span>
                      {person.id === p.driver
                        ? "Controls the active task"
                        : person.id === "pallavi"
                          ? "Reviews exact output versions"
                          : "Follows the room, read only"}
                    </span>
                  </div>
                  <span className="role-tag">
                    {person.id === p.driver
                      ? "Driver"
                      : person.id === "pallavi"
                        ? "Reviewer"
                        : "Watcher"}
                  </span>
                </div>
              ))}
            </div>
            <div className="panel-section">
              <h3>Task control</h3>
              {p.identity === p.driver ? (
                <>
                  <p className="muted">
                    Pass control to {p.driver === "alok" ? "Aditya" : "Alok"}{" "}
                    without losing the room's files or history.
                  </p>
                  <button
                    className="wide-btn"
                    onClick={p.handoff}
                    disabled={p.agent === "running"}
                  >
                    <Icon name="transfer" />
                    Hand off to {p.driver === "alok" ? "Aditya" : "Alok"}
                  </button>
                  {p.agent === "running" && (
                    <p className="micro">
                      Finish the active demo run before handoff.
                    </p>
                  )}
                </>
              ) : (
                <button className="wide-btn" onClick={p.requestControl}>
                  <Icon name="transfer" />
                  Request control
                </button>
              )}
            </div>
            <div className="preview-control">
              <label htmlFor="identity">Preview identity</label>
              <select
                id="identity"
                value={p.identity}
                onChange={(e) => p.setIdentity(e.target.value as PersonId)}
              >
                {people.map((person) => (
                  <option key={person.id} value={person.id}>
                    {person.name}
                  </option>
                ))}
              </select>
              <p>
                Design testing only. This switch must never grant permissions in
                the production app.
              </p>
            </div>
            <p className="micro">
              Invites and authenticated sessions require the backend. These are
              illustrated participants, not connected users.
            </p>
          </>
        )}
        {p.panel === "sources" && (
          <>
            <p className="muted">
              The same evidence is available in chat, documents, code and agent
              tasks.
            </p>
            <div className="file-row">
              <span className="pdf-icon">PDF</span>
              <div>
                <strong>inspection-report.pdf</strong>
                <span>1 page · synthetic fixture · local preview</span>
              </div>
            </div>
            <div className="source-excerpt">
              <div className="eyebrow">PAGE 1 / COMPLETE SOURCE EXCERPT</div>
              <p>{sourceText}</p>
            </div>
            <button
              className="wide-btn"
              onClick={() =>
                downloadText("inspection-report-source.txt", sourceText)
              }
            >
              <Icon name="download" />
              Download source text
            </button>
            <div className="panel-section">
              <h3>Real uploads come next</h3>
              <p className="muted">
                This reference uses an HTML-rendered PDF fixture. Production
                needs upload validation, extraction, a real PDF viewer and
                page-linked citations.
              </p>
              <p className="micro">
                Uploading should not start inference. Ask before sending
                selected source text to Modal.
              </p>
            </div>
          </>
        )}
        {p.panel === "activity" && (
          <>
            <p className="muted">
              A shared record of people, control and decisions.
            </p>
            <ol className="event-list">
              {p.events.map((e) => (
                <li key={e.id}>
                  <span className="event-marker" />
                  <div>
                    <strong>{e.actor}</strong> {e.text}
                    <span className="event-time">{e.time}</span>
                  </div>
                </li>
              ))}
            </ol>
            <p className="micro">
              In-memory preview events, not a durable audit log. Reload resets
              this scene.
            </p>
          </>
        )}
        {p.panel === "logs" && (
          <>
            <p className="muted">
              Local hosting and remote inference are different boundaries.
            </p>
            <div className="execution-row">
              <Icon name="terminal" />
              <div>
                <strong>Application</strong>
                <span>Planned: FastAPI + SQLite on your laptop</span>
              </div>
              <span className="role-tag">Local</span>
            </div>
            <div className="execution-row">
              <Icon name="spark" />
              <div>
                <strong>Model inference</strong>
                <span>Planned: protected Modal GPU endpoints</span>
              </div>
              <span className="role-tag">Cloud</span>
            </div>
            <div className="source-excerpt">
              <div className="eyebrow">
                ILLUSTRATIVE EVENT SCHEMA — NOT LIVE LOGS
              </div>
              <pre>{`service: tolti-api\nevent: inference.requested\nexecution_location: cloud\nprovider: modal\nrequest_id: example-only`}</pre>
            </div>
            <p className="micro">
              This prototype makes no network requests. The production app must
              display actual redacted logs and observed model status, not these
              fixtures. Modal inference requires internet and cannot prove
              air-gapped operation.
            </p>
          </>
        )}
        {p.panel === "review" && (
          <>
            <div
              className={`status-chip ${p.review === "approved" ? "green" : "amber"}`}
            >
              {status}
            </div>
            <h3 className="review-title">
              {p.mode === "code"
                ? "Code proposal"
                : p.mode === "agent"
                  ? "Inspection brief"
                  : "Handover summary"}{" "}
              <span className="muted">/ v{p.version}</span>
            </h3>
            <p className="muted">
              Review the exact draft. Approval does not execute code or certify
              equipment safety.
            </p>
            <dl className="review-meta">
              <div>
                <dt>Author</dt>
                <dd>Alok · demo fixture</dd>
              </div>
              <div>
                <dt>Reviewer</dt>
                <dd>Pallavi</dd>
              </div>
              <div>
                <dt>Version</dt>
                <dd>v{p.version} · fixture</dd>
              </div>
            </dl>
            <div className="review-preview">
              <div className="eyebrow">
                {p.mode === "agent"
                  ? "EXACT DEMO NOTE"
                  : "REVIEW THE OUTPUT IN THE WORKSPACE"}
              </div>
              {p.mode === "agent" && <pre tabIndex={0}>{note}</pre>}
            </div>
            <label className="field-label" htmlFor="review-reason">
              Review note <span className="muted">optional for approval</span>
            </label>
            <textarea
              id="review-reason"
              className="review-input"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              disabled={!canReview}
              placeholder="What did you check, or what should change?"
            />
            {error && (
              <p className="form-error" role="alert">
                {error}
              </p>
            )}
            <div className="review-buttons">
              <button
                className="primary"
                disabled={!canReview}
                onClick={() => decide("approved")}
              >
                <Icon name="check" />
                Approve v{p.version}
              </button>
              <button disabled={!canReview} onClick={() => decide("changes")}>
                Request changes
              </button>
            </div>
            {!reviewer && (
              <div className="permission-note">
                <Icon name="lock" />
                <span>
                  Only Pallavi, the reviewer, can decide. Use People → Preview
                  identity to try that view.
                </span>
              </div>
            )}
            {p.mode === "agent" &&
              p.agent !== "review" &&
              p.agent !== "approved" && (
                <p className="micro">
                  Run the demo workflow to reach its approval checkpoint.
                </p>
              )}
            <p className="micro">
              Simulated approval only. Production must verify role, author,
              version and hash on the server.
            </p>
          </>
        )}
        {p.panel === "outputs" && (
          <>
            <p className="muted">
              Keep the deliverable, not just the conversation.
            </p>
            <div className="output-item">
              <Icon name="code" size={26} />
              <div>
                <strong>validate_reading.py</strong>
                <p className="muted">Code example · not executed</p>
              </div>
              <button
                className="icon-btn"
                aria-label="Download example code"
                onClick={() => downloadText("validate_reading.py", code)}
              >
                <Icon name="download" />
              </button>
            </div>
            <div className="output-item">
              <Icon name="file" size={26} />
              <div>
                <strong>Inspection brief</strong>
                <p className="muted">
                  {p.agent === "approved"
                    ? "Approved in the preview"
                    : "Run the agent workflow to produce this"}
                </p>
              </div>
              <button
                className="icon-btn"
                disabled={p.agent !== "approved"}
                aria-label="Download approved example note"
                onClick={() => downloadText("P204-inspection-brief.md", note)}
              >
                <Icon name="download" />
              </button>
            </div>
            <p className="micro">
              Downloads contain fixed sample material, not model-generated or
              independently verified work.
            </p>
          </>
        )}
      </div>
    </dialog>
  );
}
