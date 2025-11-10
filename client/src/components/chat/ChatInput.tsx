import { FormEvent, useCallback, useState } from "react";
import type { ConnectionHealth } from "../../types/websocket";

type Props = {
  placeholder?: string;
  onSend: (value: string) => Promise<void> | void;
  isSending?: boolean;
  disabled?: boolean;
  connectionHealth?: ConnectionHealth;
  queueLength?: number;
};

const ChatInput = ({ 
  placeholder, 
  onSend, 
  isSending = false, 
  disabled = false, 
  connectionHealth,
  queueLength = 0 
}: Props) => {
  const [value, setValue] = useState("");
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = useCallback(
    async (e?: FormEvent) => {
      e?.preventDefault();
      if (!value.trim()) {
        setError("Enter a message to continue.");
        return;
      }
      setError(null);
      const nextValue = value;
      setValue("");
      try {
        await onSend(nextValue.trim());
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to send message.");
        setValue(nextValue);
      }
    },
    [value, onSend],
  );

  const getConnectionMessage = () => {
    if (!connectionHealth) return null;
    
    switch (connectionHealth.status) {
      case 'connecting':
        return "Connecting to chat...";
      case 'error':
        return "Connection error - messages will be queued";
      case 'closed':
        return "Connection closed - messages will be queued";
      default:
        return null;
    }
  };

  const connectionMessage = getConnectionMessage();
  const isOffline = connectionHealth?.status !== 'open';

  return (
    <form className="chat-input" onSubmit={handleSubmit}>
      {connectionMessage && (
        <div className="text-xs text-amber-600 mb-2 flex items-center gap-1">
          <span>⚠️</span>
          {connectionMessage}
          {queueLength > 0 && (
            <span className="ml-2">({queueLength} queued)</span>
          )}
        </div>
      )}
      <textarea
        className="chat-input__field"
        placeholder={placeholder ?? "Type your question"}
        value={value}
        onChange={(event) => setValue(event.target.value)}
        rows={3}
        disabled={disabled || isSending}
        onKeyDown={(event) => {
          if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            void handleSubmit();
          }
        }}
      />
      {error && <p className="chat-input__error">{error}</p>}
      <div className="chat-input__actions">
        <span className="chat-input__hint">
          Shift + Enter for newline
          {isOffline && queueLength < 10 && " • Messages will be queued"}
          {queueLength >= 10 && " • Queue full, please wait"}
        </span>
        <button 
          type="submit" 
          className="btn btn--primary chat-input__submit" 
          disabled={isSending || disabled}
        >
          {isSending ? "Sending…" : isOffline && queueLength > 0 ? "Queue" : "Send"}
        </button>
      </div>
    </form>
  );
};

export default ChatInput;
