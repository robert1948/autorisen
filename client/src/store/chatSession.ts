export type ChatPlacementKey = "support" | "onboarding" | "energy" | "developer" | "money" | "admin";

export type ChatSessionMeta = {
  placement: ChatPlacementKey;
  threadId?: string;
  userId?: string;
  orgId?: string;
  lastOpenedAt?: string;
};

/**
 * Lightweight placeholder for future session state management.
 * Until we introduce a global store (Zustand/Redux), components can cache
 * returned thread IDs in-memory or per-tab. This helper gives them a shared
 * shape and a place to extend later.
 */
export const createSessionMeta = (placement: ChatPlacementKey, threadId?: string): ChatSessionMeta => ({
  placement,
  threadId,
  lastOpenedAt: new Date().toISOString(),
});
