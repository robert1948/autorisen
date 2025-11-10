import { useMemo } from "react";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";

import ChatThread from "../components/chat/ChatThread";
import type { ChatPlacement } from "../components/chat/ChatModal";
import { useChatSession } from "../hooks/useChatSession";

const PLACEMENTS: ChatPlacement[] = ["support", "onboarding", "developer", "energy", "money", "admin"];

const ChatConsole = () => {
  const navigate = useNavigate();
  const { threadId } = useParams<{ threadId?: string }>();
  const [searchParams, setSearchParams] = useSearchParams();
  const placement = useMemo<ChatPlacement>(() => {
    const value = searchParams.get("placement");
    return (PLACEMENTS.includes(value as ChatPlacement) ? value : "developer") as ChatPlacement;
  }, [searchParams]);

  const { token, loading, error, refreshing, expiryCountdown, startSession } = useChatSession({
    placement,
    threadId,
    enabled: true,
  });

  const handlePlacementChange = (next: ChatPlacement) => {
    const params = new URLSearchParams(searchParams);
    params.set("placement", next);
    setSearchParams(params);
    navigate("/chat");
  };

  const handleThreadChange = async (nextThreadId: string) => {
    await startSession({ threadId: nextThreadId, mode: "initial" });
    const params = new URLSearchParams(searchParams);
    params.set("placement", placement);
    navigate({
      pathname: `/chat/${nextThreadId}`,
      search: params.toString(),
    });
  };

  return (
    <div className="chat-page">
      <header className="chat-page__header">
        <div>
          <p className="chat-page__eyebrow">ChatKit</p>
          <h1>Agent Workbench</h1>
          <p className="chat-page__subtitle">
            Manage chat threads, inspect events, and collaborate with CapeAI in real-time.
          </p>
        </div>
        <div className="chat-page__actions">
          <label className="chat-page__label" htmlFor="placement-select">
            Placement
          </label>
          <select
            id="placement-select"
            className="chat-page__select"
            value={placement}
            onChange={(event) => handlePlacementChange(event.target.value as ChatPlacement)}
          >
            {PLACEMENTS.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
          <Link to="/dashboard" className="btn btn--ghost">
            Back to dashboard
          </Link>
        </div>
      </header>

      {loading && (
        <div className="chat-modal__state">
          <div className="chat-modal__spinner" aria-hidden="true" />
          <p>Loading session…</p>
        </div>
      )}

      {error && (
        <div className="chat-modal__state chat-modal__state--error">
          <p>{error}</p>
        </div>
      )}

      {token && (
        <>
          <div className="chat-page__session">
            <p>
              Thread <strong>{token.threadId}</strong> · Expires in {expiryCountdown ?? "--"}s
            </p>
            <button
              type="button"
              className="btn btn--tiny"
              onClick={() => startSession({ mode: "refresh" })}
              disabled={refreshing}
            >
              {refreshing ? "Refreshing…" : "Refresh token"}
            </button>
          </div>
          <ChatThread placement={placement} token={token} onThreadChange={handleThreadChange} />
        </>
      )}
    </div>
  );
};

export default ChatConsole;
