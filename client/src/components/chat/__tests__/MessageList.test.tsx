import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";

import MessageList from "../MessageList";
import type { ClientMessage } from "../../../types/chat";

const baseMessage: ClientMessage = {
  id: "message-1",
  clientId: "client-1",
  threadId: "thread-1",
  role: "user",
  content: "Hello",
  createdAt: "2024-01-01T00:00:00Z",
};

describe("MessageList", () => {
  it("renders chat messages with metadata", () => {
    const messages: ClientMessage[] = [
      baseMessage,
      {
        ...baseMessage,
        id: "message-2",
        role: "assistant",
        content: "Hi there",
      },
    ];

    render(<MessageList messages={messages} socketStatus="open" />);

    expect(screen.getByText("Live")).toBeInTheDocument();
    expect(screen.getByText("You")).toBeInTheDocument();
    expect(screen.getByText("CapeAI")).toBeInTheDocument();
    expect(screen.getByText("Hi there")).toBeInTheDocument();
  });

  it("shows placeholder when no messages are present", () => {
    render(<MessageList messages={[]} isLoading={false} />);

    expect(screen.getByText("No messages yet.")).toBeInTheDocument();
  });
});
