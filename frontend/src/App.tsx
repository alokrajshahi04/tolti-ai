import React, { useEffect, useRef, useState } from "react";
import { WorkspaceShell } from "./components/WorkspaceShell";
import { Composer } from "./components/Composer";
import { RoomView } from "./views/RoomView";
import { ContextPanel } from "./panels/ContextPanel";
import { initialEvents, people } from "./fixtures";
import type {
  AgentState,
  EventItem,
  Message,
  Mode,
  Panel,
  PersonId,
  ReviewState,
} from "./types";
declare global {
  interface Window {
    __TOLTI_PREVIEW__?: string;
  }
}
const params = new URLSearchParams(
  window.__TOLTI_PREVIEW__ ?? window.location.search,
);
const initialMode = (
  ["chat", "documents", "code", "agent"].includes(params.get("mode") ?? "")
    ? params.get("mode")
    : "documents"
) as Mode;
const initialPanel = (
  ["people", "sources", "activity", "logs", "review", "outputs"].includes(
    params.get("panel") ?? "",
  )
    ? params.get("panel")
    : null
) as Panel;
const initialAgent = (
  ["ready", "review", "approved"].includes(params.get("agent") ?? "")
    ? params.get("agent")
    : "ready"
) as AgentState;
export default function App() {
  const [mode, setMode] = useState<Mode>(initialMode),
    [panel, setPanel] = useState<Panel>(initialPanel);
  const [identity, setIdentity] = useState<PersonId>(
    people.some((p) => p.id === params.get("identity"))
      ? (params.get("identity") as PersonId)
      : "alok",
  );
  const [driver, setDriver] = useState<PersonId>("alok"),
    [fresh, setFresh] = useState(params.get("fresh") === "1"),
    [mobileOpen, setMobileOpen] = useState(false);
  const [messages, setMessages] = useState<Record<Mode, Message[]>>({
    chat: [],
    documents: [],
    code: [],
    agent: [],
  });
  const [events, setEvents] = useState<EventItem[]>(initialEvents),
    [agent, setAgent] = useState<AgentState>(initialAgent),
    [step, setStep] = useState(0);
  const [versions, setVersions] = useState<Record<Mode, number>>({
    chat: 1,
    documents: 1,
    code: 1,
    agent: 1,
  });
  const [reviews, setReviews] = useState<Record<Mode, ReviewState>>({
    chat: "pending",
    documents: "pending",
    code: "pending",
    agent: initialAgent === "approved" ? "approved" : "pending",
  });
  const [toast, setToast] = useState("");
  const toastTimer = useRef<ReturnType<typeof setTimeout> | null>(null),
    sequence = useRef(4);
  const self = people.find((p) => p.id === identity)!,
    driverName = people.find((p) => p.id === driver)!.name,
    canDrive = identity === driver;
  function notify(message: string) {
    setToast(message);
    if (toastTimer.current) clearTimeout(toastTimer.current);
    toastTimer.current = setTimeout(() => setToast(""), 4200);
  }
  function record(actor: string, text: string) {
    const id = sequence.current++;
    setEvents((old) => [...old, { id, actor, text, time: "Preview action" }]);
  }
  function navigate(next: Mode) {
    setMode(next);
    setFresh(false);
  }
  function newTask() {
    setMode("chat");
    setFresh(true);
    setPanel(null);
    notify("New-task view. Existing room context is kept.");
  }
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        newTask();
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);
  useEffect(
    () => () => {
      if (toastTimer.current) clearTimeout(toastTimer.current);
    },
    [],
  );
  useEffect(() => {
    if (agent !== "running") return;
    const timer = setTimeout(() => {
      if (step < 2) setStep(step + 1);
      else {
        setAgent("review");
        record(
          "TOLTI demo",
          "prepared a fixed inspection brief and paused for review.",
        );
        notify("Demo paused. Switch to Pallavi in People to review.");
      }
    }, 900);
    return () => clearTimeout(timer);
  }, [agent, step]);
  function runAgent() {
    if (!canDrive || agent === "running") return;
    setStep(0);
    setAgent("running");
    setReviews((r) => ({ ...r, agent: "pending" }));
    record(self.name, "started the simulated report-to-note workflow.");
  }
  function send(text: string, route = "Auto route") {
    if (!canDrive) return;
    const target: Mode =
      route === "Code" ? "code" : route === "Summarise" ? "documents" : mode;
    if (target !== mode) setMode(target);
    setFresh(false);
    const id = sequence.current++;
    setMessages((old) => ({
      ...old,
      [target]: [
        ...old[target],
        { id, author: self.name, text, kind: "person" },
        {
          id: id + 10000,
          author: "TOLTI preview",
          text: "Your instruction is visible in this local preview. The output above is a fixed example, not a response generated for your request. Connect the backend to run real tasks.",
          kind: "assistant",
        },
      ],
    }));
    setVersions((old) => ({ ...old, [target]: old[target] + 1 }));
    setReviews((old) => ({ ...old, [target]: "pending" }));
    record(
      self.name,
      "added an instruction to the " + target + " view (preview only).",
    );
    notify("Instruction recorded locally. No model was called.");
  }
  function handoff() {
    if (!canDrive || agent === "running") return;
    const next = driver === "alok" ? "aditya" : "alok";
    setDriver(next);
    record(
      self.name,
      "handed task control to " + people.find((p) => p.id === next)!.name + ".",
    );
    notify("Control handed off in this preview. Room context is unchanged.");
  }
  function decision(value: ReviewState, reason: string) {
    if (
      identity !== "pallavi" ||
      identity === driver ||
      reviews[mode] !== "pending" ||
      (mode === "agent" && agent !== "review")
    )
      return;
    setReviews((old) => ({ ...old, [mode]: value }));
    record(
      self.name,
      (value === "approved" ? "approved" : "requested changes to") +
        " " +
        mode +
        " v" +
        versions[mode] +
        (reason ? ": " + reason : "."),
    );
    if (mode === "agent") setAgent(value === "approved" ? "approved" : "ready");
    notify(
      value === "approved"
        ? "Preview decision recorded for this version."
        : "Changes requested. The driver can revise the task.",
    );
  }
  function requestRole(role: string) {
    record(
      self.name,
      `requested ${role} permissions. The current ${role === "reviewer" ? "reviewer" : "host"} must approve.`,
    );
    notify(
      `${role.charAt(0).toUpperCase() + role.slice(1)} access request added to shared activity.`,
    );
  }
  return (
    <>
      <WorkspaceShell
        mode={mode}
        setMode={navigate}
        openPanel={setPanel}
        newTask={newTask}
        identity={identity}
        driver={driver}
        mobileOpen={mobileOpen}
        setMobileOpen={setMobileOpen}
      >
        <main className="work-content" id="main-work">
          <RoomView
            mode={mode}
            fresh={fresh}
            messages={messages[mode]}
            agent={agent}
            step={step}
            review={reviews[mode]}
            version={versions[mode]}
            canDrive={canDrive}
            openSources={() => setPanel("sources")}
            openReview={() => setPanel("review")}
            runAgent={runAgent}
            startExample={navigate}
          />
        </main>
        <Composer
          key={mode}
          mode={mode}
          canDrive={canDrive && agent !== "running"}
          driverName={driverName}
          onSend={send}
          onSources={() => setPanel("sources")}
          onPeople={() => setPanel("people")}
        />
      </WorkspaceShell>
      {panel && (
        <ContextPanel
          key={panel}
          panel={panel}
          close={() => setPanel(null)}
          identity={identity}
          setIdentity={setIdentity}
          driver={driver}
          handoff={handoff}
          requestControl={() => {
            record(
              self.name,
              "requested control. The current driver must accept.",
            );
            notify("Control request added to shared activity.");
          }}
          requestRole={requestRole}
          events={events}
          mode={mode}
          review={reviews[mode]}
          version={versions[mode]}
          decision={decision}
          agent={agent}
        />
      )}
      <div
        className={`toast ${toast ? "visible" : ""}`}
        role="status"
        aria-live="polite"
      >
        {toast}
      </div>
    </>
  );
}
