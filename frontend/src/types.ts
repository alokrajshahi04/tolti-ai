export type Mode = "chat" | "documents" | "code" | "agent";
export type Panel =
  "people" | "sources" | "activity" | "logs" | "review" | "outputs" | null;
export type PersonId = "alok" | "pallavi" | "aditya";
export type AgentState = "ready" | "running" | "review" | "approved";
export type ReviewState = "pending" | "approved" | "changes";
export interface Person {
  id: PersonId;
  name: string;
  initials: string;
  role: string;
}
export interface EventItem {
  id: number;
  actor: string;
  text: string;
  time: string;
}
export interface Message {
  id: number;
  author: string;
  text: string;
  kind: "person" | "assistant";
}
export interface Room {
  id: string;
  name: string;
}
