import { FormEvent, useCallback, useState } from "react";

type Props = {
  placeholder?: string;
  onSend: (value: string) => Promise<void> | void;
  isSending?: boolean;
  disabled?: boolean;
};

const ChatInput = ({ placeholder, onSend, isSending = false, disabled = false }: Props) => {
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

  return (
    <form className="chat-input" onSubmit={handleSubmit}>
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
        <span className="chat-input__hint">Shift + Enter for newline</span>
        <button type="submit" className="btn btn--primary chat-input__submit" disabled={isSending || disabled}>
          {isSending ? "Sending…" : "Send"}
        </button>
      </div>
    </form>
  );
};

export default ChatInput;
