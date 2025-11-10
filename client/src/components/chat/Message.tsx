import type { ClientMessage } from "../../types/chat";

type Props = {
  message: ClientMessage;
  onRetry?: (message: ClientMessage) => void;
};

const ROLE_LABELS: Record<string, string> = {
  user: "You",
  assistant: "CapeAI",
  system: "System",
  tool: "Tool",
};

const roleClass = (role: ClientMessage["role"]) => {
  switch (role) {
    case "user":
      return "chat-message--user";
    case "assistant":
      return "chat-message--assistant";
    case "system":
      return "chat-message--system";
    case "tool":
      return "chat-message--tool";
    default:
      return "";
  }
};

const formatTimestamp = (timestamp: string) => {
  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) {
    return "";
  }
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
};

const Message = ({ message, onRetry }: Props) => {
  const hasToolPayload =
    message.toolName || (message.eventMetadata && Object.keys(message.eventMetadata).length > 0);

  return (
    <article className={`chat-message ${roleClass(message.role)}`} data-role={message.role}>
      <header className="chat-message__meta">
        <span className="chat-message__author">{ROLE_LABELS[message.role] ?? message.role}</span>
        <span className="chat-message__timestamp">{formatTimestamp(message.createdAt)}</span>
      </header>
      <p className="chat-message__content">{message.content}</p>
      {hasToolPayload && (
        <div className="chat-message__tool">
          {message.toolName && <p className="chat-message__tool-name">{message.toolName}</p>}
          {message.eventMetadata && (
            <pre className="chat-message__tool-payload">
              {JSON.stringify(message.eventMetadata, null, 2)}
            </pre>
          )}
        </div>
      )}
      {message.status && message.status !== "sent" && (
        <footer className={`chat-message__status chat-message__status--${message.status}`}>
          {message.status === "sending" && "Sending…"}
          {message.status === "error" && (
            <>
              Failed to deliver{message.error ? ` – ${message.error}` : ""}
              {onRetry && (
                <button
                  type="button"
                  className="chat-message__retry"
                  onClick={() => onRetry(message)}
                >
                  Retry
                </button>
              )}
            </>
          )}
        </footer>
      )}
    </article>
  );
};

export default Message;
