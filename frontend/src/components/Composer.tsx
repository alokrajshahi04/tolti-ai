import React, { useState } from "react";
import { Icon } from "./Icon";
import type { Mode } from "../types";
interface Props {
  mode: Mode;
  canDrive: boolean;
  driverName: string;
  onSend: (text: string, route: string) => void;
  onSources: () => void;
  onPeople: () => void;
}
export function Composer({
  mode,
  canDrive,
  driverName,
  onSend,
  onSources,
  onPeople,
}: Props) {
  const [text, setText] = useState("");
  const [route, setRoute] = useState("Auto route");
  function send(e: React.FormEvent) {
    e.preventDefault();
    if (!canDrive || !text.trim()) return;
    onSend(text.trim(), route);
    setText("");
  }
  return (
    <div className="composer-wrap">
      <div className="control-line">
        <span className="presence-dot" />
        <span>
          <strong>{driverName}</strong> is driving
        </span>
        <span className="control-separator">·</span>
        <span>Shared with the room</span>
        <button className="text-btn control-action" onClick={onPeople}>
          {canDrive ? "Hand off" : "View roles"}
          <Icon name="transfer" size={15} />
        </button>
      </div>
      <form
        className={`composer ${!canDrive ? "read-only" : ""}`}
        onSubmit={send}
      >
        <label className="sr-only" htmlFor={`prompt-${mode}`}>
          Task instruction
        </label>
        <textarea
          id={`prompt-${mode}`}
          value={text}
          onChange={(e) => setText(e.target.value)}
          disabled={!canDrive}
          placeholder={
            canDrive
              ? mode === "documents"
                ? "Ask about the report. Your team follows along…"
                : mode === "code"
                  ? "Describe the code you want to work on…"
                  : "What should we work on together?"
              : `${driverName} controls this task. You can still inspect the shared work.`
          }
          onKeyDown={(e) => {
            if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
              e.preventDefault();
              if (canDrive && text.trim()) {
                onSend(text.trim(), route);
                setText("");
              }
            }
          }}
        />
        <div className="composer-tools">
          <button
            type="button"
            className="icon-btn"
            onClick={onSources}
            aria-label="Open room files"
          >
            <Icon name="clip" />
          </button>
          <label className="route-select">
            <Icon name="spark" size={15} />
            <span className="sr-only">Routing mode preview</span>
            <select
              value={route}
              onChange={(e) => setRoute(e.target.value)}
              disabled={!canDrive}
            >
              <option>Auto route</option>
              <option>Code</option>
              <option>Summarise</option>
            </select>
          </label>
          <span className="composer-spacer" />
          <span className="shortcut" aria-hidden="true">
            ⌘ ↵
          </span>
          <button
            type="submit"
            className="send-btn"
            disabled={!canDrive || !text.trim()}
            aria-label="Send simulated message"
          >
            <Icon name="arrow" size={19} />
          </button>
        </div>
      </form>
      <div className="composer-disclosure">
        Preview only · prewritten responses · selected context would go to Modal
        in the real app.
      </div>
    </div>
  );
}
