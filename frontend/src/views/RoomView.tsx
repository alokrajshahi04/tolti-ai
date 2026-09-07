import React from "react";
import { Icon } from "../components/Icon";
import { code, downloadText, note, sourceText } from "../fixtures";
import type { AgentState, Message, Mode, ReviewState } from "../types";
interface Props {
  mode: Mode;
  fresh: boolean;
  messages: Message[];
  agent: AgentState;
  step: number;
  review: ReviewState;
  version: number;
  canDrive: boolean;
  openSources: () => void;
  openReview: () => void;
  runAgent: () => void;
  startExample: (mode: Mode) => void;
}
function Author({
  initials,
  name,
  detail,
  ai = false,
}: {
  initials: string;
  name: string;
  detail: string;
  ai?: boolean;
}) {
  return (
    <div className="author">
      <span className={`avatar avatar-small ${ai ? "ai-avatar" : ""}`}>
        {ai ? <Icon name="spark" size={15} /> : initials}
      </span>
      <strong>{name}</strong>
      <span>{detail}</span>
    </div>
  );
}
function ExtraMessages({ messages }: { messages: Message[] }) {
  return (
    <>
      {messages.map((m) => (
        <div key={m.id} className="extra-message">
          <Author
            initials={m.kind === "person" ? "AR" : ""}
            name={m.author}
            detail={
              m.kind === "assistant" ? "Simulated response" : "Visible to room"
            }
            ai={m.kind === "assistant"}
          />
          <p>{m.text}</p>
        </div>
      ))}
    </>
  );
}
export function RoomView(p: Props) {
  if (p.fresh && p.mode === "chat")
    return (
      <div className="welcome">
        <span className="welcome-mark">
          <Icon name="spark" size={32} />
        </span>
        <div className="eyebrow">ONE ROOM. SHARED CONTEXT.</div>
        <h2>
          Good work starts
          <br />
          with a conversation.
        </h2>
        <p>Bring your team, your documents and your next idea.</p>
        <div className="suggestions">
          <button onClick={() => p.startExample("documents")}>
            <Icon name="file" />
            Ask a PDF
            <Icon name="chevron" size={16} />
          </button>
          <button onClick={() => p.startExample("code")}>
            <Icon name="code" />
            Work on code
            <Icon name="chevron" size={16} />
          </button>
          <button onClick={() => p.startExample("agent")}>
            <Icon name="spark" />
            Delegate a task
            <Icon name="chevron" size={16} />
          </button>
        </div>
      </div>
    );
  if (p.mode === "documents")
    return (
      <div className="document-layout">
        <div className="document-chat">
          <div className="question">
            <Author initials="AR" name="Alok" detail="Driver" />
            <p>What do we know about P-204, and what still needs checking?</p>
            <button className="attachment" onClick={p.openSources}>
              <span className="pdf-icon">PDF</span>
              <span>
                inspection-report.pdf
                <span className="muted">1 page · synthetic source</span>
              </span>
              <Icon name="chevron" size={16} />
            </button>
          </div>
          <div className="answer">
            <Author
              initials=""
              name="TOLTI"
              detail="Qwen3-8B · example output"
              ai
            />
            <h2>
              A clear observation.
              <br />
              Not yet a diagnosis.
            </h2>
            <p>
              The shift reported vibration at <strong>Pump P-204</strong>. The
              report does not establish a cause or severity.
            </p>
            <div className="finding">
              <Icon name="check" />
              <div>
                <strong>What is recorded</strong>
                <p>Vibration was reported. An inspection is pending.</p>
              </div>
            </div>
            <div className="finding">
              <Icon name="clock" />
              <div>
                <strong>What is missing</strong>
                <p>
                  No measured vibration value or confirmed cause is included.
                </p>
              </div>
            </div>
            <div className="source-row">
              <button onClick={p.openSources}>
                <Icon name="file" size={15} />
                Source 1 · page 1
              </button>
              <span className="muted">Whole supplied page</span>
            </div>
            <div className="collaborator-note">
              <span className="avatar avatar-small">AD</span>
              <div>
                <strong>
                  Aditya <span className="muted">· evidence check</span>
                </strong>
                <p>Keep the missing measurements explicit in the note.</p>
              </div>
            </div>
            <button className="text-btn accent" onClick={p.openReview}>
              Review summary v{p.version}
              <Icon name="chevron" size={15} />
            </button>
          </div>
          <ExtraMessages messages={p.messages} />
        </div>
        <section className="pdf-view" aria-label="Synthetic PDF page preview">
          <div className="pdf-toolbar">
            <Icon name="file" size={16} />
            <span>inspection-report.pdf</span>
            <span className="muted">1 / 1</span>
          </div>
          <div className="pdf-stage">
            <article className="pdf-page">
              <div className="paper-meta">
                TOLTI / FIELD NOTES <span>001</span>
              </div>
              <div className="paper-label">SYNTHETIC INSPECTION REPORT</div>
              <h3>
                Pump P-204
                <br />
                Shift inspection
              </h3>
              <div className="paper-rule" />
              <dl className="paper-fields">
                <div>
                  <dt>Asset</dt>
                  <dd>P-204</dd>
                </div>
                <div>
                  <dt>Document status</dt>
                  <dd>For review</dd>
                </div>
              </dl>
              <h4>01 — Observation</h4>
              <p>The incoming shift reported vibration at Pump P-204.</p>
              <p className="paper-highlight">
                No measured vibration value or confirmed cause was recorded.
              </p>
              <h4>02 — Follow-up</h4>
              <p>
                Inspection is pending. No operating or maintenance action is
                authorised by this report.
              </p>
              <div className="paper-footer">
                Demonstration material only <span>01</span>
              </div>
            </article>
          </div>
          <div className="pdf-bottom">
            <span className="blue-dot" />
            Source excerpt shown in context
            <span className="muted">HTML fixture</span>
          </div>
        </section>
      </div>
    );
  if (p.mode === "code")
    return (
      <div className="code-layout">
        <div className="code-intro">
          <Author initials="AR" name="Alok" detail="Driver" />
          <p>
            Write a small validator for pump readings. No input mutation, and
            reject invalid numeric values.
          </p>
        </div>
        <section className="editor">
          <div className="editor-tabs">
            <span>
              <Icon name="code" size={16} />
              validate_reading.py
            </span>
            <span className="muted">Python · v{p.version}</span>
          </div>
          <div className="editor-body">
            <div className="line-numbers" aria-hidden="true">
              {code.split("\n").map((_, i) => (
                <div key={i}>{i + 1}</div>
              ))}
            </div>
            <pre>
              <code>{code}</code>
            </pre>
          </div>
          <div className="editor-footer">
            <span>
              <span className="blue-dot" />
              Qwen2.5-Coder-7B · example output
            </span>
            <span>Not executed</span>
          </div>
        </section>
        <div className="code-under">
          <div>
            <strong>Proposed checks</strong>
            <p className="muted">
              Missing asset · booleans · non-finite values · unchanged input
            </p>
          </div>
          <div className="button-row">
            <button onClick={() => downloadText("validate_reading.py", code)}>
              <Icon name="download" />
              Save code
            </button>
            <button className="primary" onClick={p.openReview}>
              Review v{p.version}
              <Icon name="chevron" size={16} />
            </button>
          </div>
        </div>
        <ExtraMessages messages={p.messages} />
      </div>
    );
  if (p.mode === "agent") {
    const labels = [
      "Read the selected report",
      "Extract findings and source references",
      "Draft an inspection brief",
      "Pause for a human review",
      "Export the approved note",
    ];
    return (
      <div className="agent-layout">
        <div className="agent-heading">
          <span className="agent-icon">
            <Icon name="spark" size={26} />
          </span>
          <div>
            <div className="eyebrow">BOUNDED WORKFLOW · SIMULATED</div>
            <h2>From report to review-ready note.</h2>
            <p className="muted">
              One task. Five visible steps. You stay in control.
            </p>
          </div>
        </div>
        <div className="agent-command">
          <Icon name="file" />
          <span>
            Read the inspection report, extract the findings and prepare an
            approval note.
          </span>
        </div>
        <div className="agent-columns">
          <section className="steps" aria-label="Agent plan">
            {labels.map((label, i) => {
              const done =
                p.agent === "approved" ||
                (p.agent === "review" && i < 3) ||
                (p.agent === "running" && i < p.step);
              const active =
                (p.agent === "running" && i === p.step) ||
                (p.agent === "review" && i === 3);
              return (
                <div
                  className={`step ${done ? "done" : ""} ${active ? "active" : ""}`}
                  key={label}
                >
                  <span className="step-number">
                    {done ? <Icon name="check" size={16} /> : i + 1}
                  </span>
                  <div>
                    <strong>{label}</strong>
                    <p>
                      {i === 0
                        ? "Room file · read only"
                        : i === 1
                          ? "Only supported facts"
                          : i === 2
                            ? "Versioned draft, not an action"
                            : i === 3
                              ? "Independent reviewer required"
                              : "Downloadable Markdown artifact"}
                    </p>
                  </div>
                </div>
              );
            })}
          </section>
          <section className="agent-result">
            <div className="eyebrow">TASK OUTPUT</div>
            <Icon name="file" size={32} />
            <h3>Inspection brief</h3>
            <p className="muted">
              A short note with the observation, missing information and
              proposed follow-up.
            </p>
            {p.agent === "ready" ? (
              <button
                className="primary"
                onClick={p.runAgent}
                disabled={!p.canDrive}
              >
                <Icon name="play" size={16} />
                Run demo workflow
              </button>
            ) : p.agent === "running" ? (
              <div className="working" role="status">
                Simulating step {p.step + 1} of 3…
              </div>
            ) : p.agent === "review" ? (
              <>
                <div className="status-chip amber">Waiting for reviewer</div>
                <button className="primary" onClick={p.openReview}>
                  Open review
                  <Icon name="chevron" size={16} />
                </button>
              </>
            ) : (
              <>
                <div className="status-chip green">
                  Approved in this preview
                </div>
                <button
                  className="primary"
                  onClick={() => downloadText("P204-inspection-brief.md", note)}
                >
                  <Icon name="download" />
                  Download note
                </button>
              </>
            )}
            <p className="micro">
              Fixed fixtures only. No model, tool execution or real approval
              occurs.
            </p>
          </section>
        </div>
        <ExtraMessages messages={p.messages} />
      </div>
    );
  }
  return (
    <div className="chat-layout">
      <div className="question">
        <Author initials="AR" name="Alok" detail="Driver" />
        <p>
          Help us turn this handover into something the next shift can actually
          use.
        </p>
      </div>
      <div className="answer">
        <Author
          initials=""
          name="TOLTI"
          detail="General chat · example output"
          ai
        />
        <h2>
          Keep the context.
          <br />
          Make the next step obvious.
        </h2>
        <p>
          Let's organise the handover around three things your team can review
          together:
        </p>
        <ol className="chat-outline">
          <li>
            <strong>What was observed</strong>
            <span>Record the source facts, without inferring a cause.</span>
          </li>
          <li>
            <strong>What remains unknown</strong>
            <span>Keep missing measurements and open questions visible.</span>
          </li>
          <li>
            <strong>What needs review</strong>
            <span>
              Turn the draft into a versioned note for a teammate to check.
            </span>
          </li>
        </ol>
        <div className="inline-actions">
          <button onClick={() => p.startExample("documents")}>
            <Icon name="file" />
            Look at the report
          </button>
          <button onClick={() => p.startExample("agent")}>
            <Icon name="spark" />
            Prepare the note
          </button>
        </div>
      </div>
      <div className="collaborator-note">
        <span className="avatar avatar-small">PB</span>
        <div>
          <strong>
            Pallavi <span className="muted">· reviewer</span>
          </strong>
          <p>I'll review the final note once the evidence is attached.</p>
        </div>
      </div>
      <ExtraMessages messages={p.messages} />
    </div>
  );
}
