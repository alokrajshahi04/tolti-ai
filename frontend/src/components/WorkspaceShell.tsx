import React from "react";
import { Icon } from "./Icon";
import { modes, people } from "../fixtures";
import type { Mode, Panel, PersonId } from "../types";
interface Props {
  children: React.ReactNode;
  mode: Mode;
  setMode: (m: Mode) => void;
  openPanel: (p: Panel) => void;
  newTask: () => void;
  identity: PersonId;
  driver: PersonId;
  mobileOpen: boolean;
  setMobileOpen: (v: boolean) => void;
}
export function WorkspaceShell(p: Props) {
  const self = people.find((x) => x.id === p.identity)!;
  const role =
    p.identity === p.driver
      ? "Driver"
      : self.id === "pallavi"
        ? "Reviewer"
        : "Watcher";
  const open = (panel: Panel) => {
    p.openPanel(panel);
    p.setMobileOpen(false);
  };
  return (
    <div className="workspace-shell">
      {p.mobileOpen && (
        <button
          className="nav-backdrop"
          aria-label="Close navigation"
          onClick={() => p.setMobileOpen(false)}
        />
      )}
      <aside
        className={`sidebar ${p.mobileOpen ? "is-open" : ""}`}
        aria-label="Workspace navigation"
      >
        <div className="wordmark">
          <span className="logo-symbol">t</span>
          <strong>
            TOLTI<span> AIs</span>
          </strong>
          <button
            className="icon-btn mobile-close"
            aria-label="Close navigation"
            onClick={() => p.setMobileOpen(false)}
          >
            <Icon name="close" />
          </button>
        </div>
        <div className="workspace-label">
          <span className="workspace-monogram">TL</span>
          <div>
            <strong>Tolti Labs</strong>
            <span>Team workspace</span>
          </div>
        </div>
        <button
          className="new-task"
          onClick={() => {
            p.newTask();
            p.setMobileOpen(false);
          }}
        >
          <Icon name="plus" />
          New task<span className="key-hint">⌘ K</span>
        </button>
        <nav className="main-nav">
          <button onClick={() => open("sources")}>
            <Icon name="folder" />
            Files<span className="nav-count">1</span>
          </button>
          <button onClick={() => open("outputs")}>
            <Icon name="grid" />
            Outputs
          </button>
          <button onClick={() => open("activity")}>
            <Icon name="activity" />
            Room activity
          </button>
        </nav>
        <div className="section-label">
          SHARED ROOMS<span>01</span>
        </div>
        <button
          className="room-item selected"
          onClick={() => {
            p.setMode("documents");
            p.setMobileOpen(false);
          }}
        >
          <span className="room-symbol">
            <Icon name="chat" size={17} />
          </span>
          <div>
            <strong>P-204 inspection</strong>
            <span>3 participants · synthetic demo</span>
          </div>
        </button>
        <div className="room-mini">
          <span className="presence-dot" />
          <span>All four modes share this room.</span>
        </div>
        <div className="sidebar-bottom">
          <button className="system-link" onClick={() => open("logs")}>
            <Icon name="terminal" size={16} />
            <span>Local app / Modal cloud inference</span>
            <Icon name="chevron" size={14} />
          </button>
          <button className="profile" onClick={() => open("people")}>
            <span className="avatar">{self.initials}</span>
            <div>
              <strong>{self.name}</strong>
              <span>{role} · preview identity</span>
            </div>
            <Icon name="down" size={15} />
          </button>
        </div>
      </aside>
      <div className="main-shell">
        <div className="prototype-strip">
          <span className="prototype-label">SKELETON</span>
          <span>Local app / Modal cloud inference · Model: Not configured</span>
          <button className="text-btn" onClick={() => open("logs")}>
            Diagnostics
            <Icon name="chevron" size={14} />
          </button>
        </div>
        <header className="room-header">
          <div className="room-heading">
            <button
              className="icon-btn mobile-menu"
              aria-label="Open navigation"
              onClick={() => p.setMobileOpen(true)}
            >
              <Icon name="menu" />
            </button>
            <div>
              <div className="breadcrumb">
                Workspace <span>/</span> Shared room
              </div>
              <h1>P-204 inspection</h1>
            </div>
          </div>
          <div className="header-actions">
            <button
              className="presence-group"
              onClick={() => open("people")}
              aria-label="View participants and roles"
            >
              <span className="avatar-stack">
                {people.map((person) => (
                  <span
                    className={`avatar ${person.id === p.driver ? "driver-ring" : ""}`}
                    key={person.id}
                  >
                    {person.initials}
                  </span>
                ))}
              </span>
              <span className="presence-label">
                3 people
                <Icon name="down" size={14} />
              </span>
            </button>
            <button
              className="icon-btn"
              onClick={() => open("activity")}
              aria-label="Open shared activity"
            >
              <Icon name="activity" />
            </button>
          </div>
        </header>
        <div className="modebar">
          <nav className="mode-tabs" aria-label="Workspace mode">
            {modes.map((m) => (
              <button
                key={m.id}
                aria-current={p.mode === m.id ? "page" : undefined}
                className={p.mode === m.id ? "active" : ""}
                onClick={() => p.setMode(m.id)}
              >
                <Icon name={m.icon} size={17} />
                {m.label}
              </button>
            ))}
          </nav>
          <button
            className="text-btn file-control"
            onClick={() => open("sources")}
          >
            <Icon name="file" size={15} />
            <span>1 room file</span>
          </button>
        </div>
        {p.children}
      </div>
    </div>
  );
}
