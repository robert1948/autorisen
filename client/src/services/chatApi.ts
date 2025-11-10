import { apiRequest } from "../lib/api";
import type {
  ChatMessage,
  ChatThread,
  CreateThreadPayload,
  SendMessagePayload,
} from "../types/chat";

export type ChatThreadResponse = {
  id: string;
  placement: string;
  title?: string | null;
  status?: string | null;
  context?: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
  last_event_at?: string | null;
  metadata?: Record<string, unknown> | null;
};

export type ChatEventResponse = {
  id: string;
  thread_id: string;
  role: string;
  content: string;
  tool_name?: string | null;
  event_metadata?: Record<string, unknown> | null;
  created_at: string;
};

type ThreadListResponse =
  | ChatThreadResponse[]
  | {
      results: ChatThreadResponse[];
    };

type EventListResponse =
  | ChatEventResponse[]
  | {
      results: ChatEventResponse[];
    };

const toThread = (payload: ChatThreadResponse): ChatThread => ({
  id: payload.id,
  placement: payload.placement,
  title: payload.title ?? null,
  status: payload.status ?? undefined,
  context: payload.context ?? null,
  createdAt: payload.created_at,
  updatedAt: payload.updated_at,
  lastEventAt: payload.last_event_at ?? null,
  metadata: payload.metadata ?? null,
});

const toMessage = (payload: ChatEventResponse): ChatMessage => ({
  id: payload.id,
  threadId: payload.thread_id,
  role: (payload.role ?? "assistant") as ChatMessage["role"],
  content: payload.content ?? "",
  createdAt: payload.created_at,
  toolName: payload.tool_name ?? null,
  eventMetadata: payload.event_metadata ?? null,
});

const unwrapList = <T>(payload: T[] | { results: T[] } | undefined): T[] => {
  if (!payload) return [];
  if (Array.isArray(payload)) return payload;
  if ("results" in payload && Array.isArray(payload.results)) {
    return payload.results;
  }
  return [];
};

export type ListThreadsParams = {
  placement?: string;
  limit?: number;
};

export async function listThreads(params?: ListThreadsParams): Promise<ChatThread[]> {
  const search = new URLSearchParams();
  if (params?.placement) {
    search.set("placement", params.placement);
  }
  if (params?.limit) {
    search.set("limit", String(params.limit));
  }
  const query = search.toString();
  const data = await apiRequest<ThreadListResponse>(`/chat/threads${query ? `?${query}` : ""}`);
  return unwrapList(data).map(toThread);
}

export async function getThread(threadId: string): Promise<ChatThread> {
  const data = await apiRequest<ChatThreadResponse>(`/chat/threads/${threadId}`);
  return toThread(data);
}

export type ListEventsParams = {
  before?: string;
  limit?: number;
};

export async function listEvents(
  threadId: string,
  params?: ListEventsParams,
): Promise<ChatMessage[]> {
  const search = new URLSearchParams();
  if (params?.before) {
    search.set("before", params.before);
  }
  if (params?.limit) {
    search.set("limit", String(params.limit));
  }
  const query = search.toString();
  const data = await apiRequest<EventListResponse>(
    `/chat/threads/${threadId}/events${query ? `?${query}` : ""}`,
  );
  return unwrapList(data).map(toMessage);
}

export async function createThread(payload: CreateThreadPayload): Promise<ChatThread> {
  const data = await apiRequest<ChatThreadResponse>("/chat/threads", {
    method: "POST",
    body: payload,
  });
  return toThread(data);
}

export async function sendMessage(
  threadId: string,
  payload: SendMessagePayload,
): Promise<ChatMessage> {
  const data = await apiRequest<ChatEventResponse>(`/chat/threads/${threadId}/events`, {
    method: "POST",
    body: {
      content: payload.content,
      role: payload.role ?? "user",
      event_metadata: payload.metadata,
      tool_name: payload.toolName,
    },
  });
  return toMessage(data);
}

export const chatApi = {
  listThreads,
  getThread,
  listEvents,
  createThread,
  sendMessage,
  toThread,
  toMessage,
};
