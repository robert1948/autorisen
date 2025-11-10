import { describe, expect, it } from "vitest";

import { chatApi, type ChatEventResponse, type ChatThreadResponse } from "../chatApi";

describe("chatApi transformers", () => {
  it("converts snake_case thread fields into camelCase", () => {
    const payload: ChatThreadResponse = {
      id: "thread-1",
      placement: "developer",
      title: "Thread title",
      status: "active",
      context: { origin: "test" },
      created_at: "2024-01-01T00:00:00Z",
      updated_at: "2024-01-01T01:00:00Z",
      last_event_at: "2024-01-01T00:30:00Z",
      metadata: { foo: "bar" },
    };

    const thread = chatApi.toThread(payload);

    expect(thread).toEqual({
      id: "thread-1",
      placement: "developer",
      title: "Thread title",
      status: "active",
      context: { origin: "test" },
      createdAt: "2024-01-01T00:00:00Z",
      updatedAt: "2024-01-01T01:00:00Z",
      lastEventAt: "2024-01-01T00:30:00Z",
      metadata: { foo: "bar" },
    });
  });

  it("transforms chat events", () => {
    const payload: ChatEventResponse = {
      id: "evt-1",
      thread_id: "thread-1",
      role: "assistant",
      content: "Hello",
      tool_name: "tool.test",
      event_metadata: { answer: "World" },
      created_at: "2024-01-01T00:00:05Z",
    };

    const event = chatApi.toMessage(payload);

    expect(event).toEqual({
      id: "evt-1",
      threadId: "thread-1",
      role: "assistant",
      content: "Hello",
      toolName: "tool.test",
      eventMetadata: { answer: "World" },
      createdAt: "2024-01-01T00:00:05Z",
    });
  });
});
