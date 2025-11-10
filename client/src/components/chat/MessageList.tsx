import { useEffect, useRef } from "react";

import type { ClientMessage, SocketStatus } from "../../types/chat";
import Message from "./Message";

type Props = {
  messages: ClientMessage[];
  isLoading?: boolean;
  socketStatus?: SocketStatus;
  onRetryMessage?: (message: ClientMessage) => void;
};

const MessageList = ({ messages, isLoading, socketStatus, onRetryMessage }: Props) => {
  const viewportRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const node = viewportRef.current;
    if (!node) {
      return;
    }
    if (typeof node.scrollTo === "function") {
      node.scrollTo({ top: node.scrollHeight, behavior: "smooth" });
    } else {
      node.scrollTop = node.scrollHeight;
    }
  }, [messages.length]);

  return (
    <div className="chat-timeline" ref={viewportRef}>
      {socketStatus && (
        <div className={`chat-connection chat-connection--${socketStatus}`}>
          <span className="chat-connection__dot" aria-hidden="true" />
          <span className="chat-connection__label">
            {socketStatus === "open" && "Live"}
            {socketStatus === "connecting" && "Connecting…"}
            {socketStatus === "closed" && "Paused"}
            {socketStatus === "error" && "Connection issue"}
            {socketStatus === "idle" && "Idle"}
          </span>
        </div>
      )}
      {isLoading && (
        <div className="chat-timeline__state">
          <div className="chat-modal__spinner" aria-hidden="true" />
          <p>Fetching conversation…</p>
        </div>
      )}
      {!isLoading && messages.length === 0 && (
        <div className="chat-timeline__empty">
          <p>No messages yet.</p>
          <p>Start the conversation to see CapeAI respond in real-time.</p>
        </div>
      )}
      {messages.map((message) => (
        <Message
          key={message.id ?? message.clientId}
          message={message}
          onRetry={message.status === "error" ? onRetryMessage : undefined}
        />
      ))}
    </div>
  );
};

export default MessageList;
