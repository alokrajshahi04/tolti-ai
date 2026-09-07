import type { Mode, Person } from "./types";

// All source material, participants and activity in this prototype are synthetic.
export const people: Person[] = [
  { id: "alok", name: "Alok", initials: "AR", role: "Driver" },
  { id: "pallavi", name: "Pallavi", initials: "PB", role: "Reviewer" },
  { id: "aditya", name: "Aditya", initials: "AD", role: "Watcher" },
];
export const modes: { id: Mode; label: string; icon: string }[] = [
  { id: "chat", label: "Chat", icon: "chat" },
  { id: "documents", label: "Documents", icon: "file" },
  { id: "code", label: "Code", icon: "code" },
  { id: "agent", label: "Agent", icon: "spark" },
];
export const code = `from math import isfinite\n\ndef validate_reading(record: dict) -> list[str]:\n    """Check structure without changing the input."""\n    errors: list[str] = []\n\n    if not isinstance(record.get("asset"), str):\n        errors.append("asset must be a string")\n\n    value = record.get("value")\n    if isinstance(value, bool) or not isinstance(\n        value, (int, float)\n    ):\n        errors.append("value must be numeric")\n    elif not isfinite(value):\n        errors.append("value must be finite")\n\n    return errors\n`;
export const note = `# P-204 — Inspection brief\n\nSYNTHETIC DEMONSTRATION — NOT AN OPERATIONAL INSTRUCTION\n\n## Recorded observation\nThe shift reported vibration at Pump P-204. No measured value was recorded.\n\n## Open questions\nCause and severity have not been established. Inspection remains pending.\n\n## Proposed follow-up\nRequest the missing measurements and inspection findings before drawing conclusions.\nThis is a proposed next step, not a fact recorded in the source.\n\nSource: synthetic inspection report, page 1.\n\nThis file was assembled from a fixed UI demo fixture. No model or local tool ran.\n`;
export const sourceText =
  "The incoming shift reported vibration at Pump P-204. No measured vibration value or confirmed cause was recorded. Inspection is pending. No operating or maintenance action is authorised by this report.";
export const initialEvents = [
  {
    id: 1,
    actor: "Alok",
    text: "created the room and added the inspection report.",
    time: "Scene · 01",
  },
  {
    id: 2,
    actor: "Aditya",
    text: "joined to check the evidence.",
    time: "Scene · 02",
  },
  {
    id: 3,
    actor: "Pallavi",
    text: "joined as the reviewer.",
    time: "Scene · 03",
  },
];
export function downloadText(filename: string, content: string) {
  const url = URL.createObjectURL(
    new Blob([content], { type: "text/plain;charset=utf-8" }),
  );
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
