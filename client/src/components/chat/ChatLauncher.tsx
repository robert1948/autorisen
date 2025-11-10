import { useMemo, useRef, useState } from "react";

import ChatModal, { type ChatPlacement } from "./ChatModal";
import { useAuth } from "../../features/auth/AuthContext";

type LauncherOption = {
  id: "support" | "onboarding" | "developer" | "energy";
  placement: ChatPlacement;
  title: string;
  description: string;
  badge: string;
};

const OPTIONS: LauncherOption[] = [
  {
    id: "support",
    placement: "support",
    title: "Talk with Support",
    description: "Connect with CapeControl experts for billing, access, and troubleshooting.",
    badge: "Live team",
  },
  {
    id: "onboarding",
    placement: "onboarding",
    title: "CapeAI Onboarding",
    description: "Generate a personalized launch checklist with CapeAI and update tasks in chat.",
    badge: "CapeAI",
  },
  {
    id: "developer",
    placement: "developer",
    title: "Agent Workbench",
    description: "Inspect tool calls, replay flows, and validate prompts before publishing.",
    badge: "Dev",
  },
  {
    id: "energy",
    placement: "energy",
    title: "Energy Insights",
    description: "Ask why energy spiked and get proactive savings recommendations.",
    badge: "Insights",
  },
];

const ChatLauncher = () => {
  const { state } = useAuth();
  const panelRef = useRef<HTMLDivElement | null>(null);
  const [panelOpen, setPanelOpen] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [activeOption, setActiveOption] = useState<LauncherOption>(OPTIONS[0]);

  const isAuthenticated = Boolean(state.accessToken);
  const isVerified = state.isEmailVerified;
  const canLaunch = isAuthenticated && isVerified;

  const handleLaunch = (option: LauncherOption) => {
    if (!canLaunch) {
      return;
    }
    setActiveOption(option);
    setModalOpen(true);
    setPanelOpen(false);
  };

  const activePlacement = useMemo(() => activeOption.placement, [activeOption]);

  return (
    <>
      <div className="chat-launcher">
        <button
          type="button"
          className="chat-launcher__button"
          aria-haspopup="dialog"
          aria-expanded={panelOpen}
          onClick={() => setPanelOpen((prev) => !prev)}
        >
          <div className="chat-launcher__button-content">
            <span className="chat-launcher__pulse" aria-hidden="true" />
            <div>
              <p className="chat-launcher__label">Need a hand?</p>
              <strong>Chat with CapeAI</strong>
            </div>
          </div>
          <span className="chat-launcher__chevron" />
        </button>
        {panelOpen && (
          <div className="chat-launcher__panel" ref={panelRef}>
            <header className="chat-launcher__panel-header">
              <div>
                <p>ChatKit placements</p>
                <strong>Select an experience</strong>
              </div>
              <button
                type="button"
                className="chat-launcher__close"
                aria-label="Close chat launcher"
                onClick={() => setPanelOpen(false)}
              >
                ×
              </button>
            </header>
            {!canLaunch && (
              <div className="chat-launcher__notice">
                <p>
                  {isAuthenticated
                    ? "Verify your email to unlock ChatKit experiences."
                    : "Log in to launch ChatKit experiences."}
                </p>
                {!isAuthenticated && (
                  <button
                    type="button"
                    className="btn btn--tiny"
                    onClick={() => {
                      window.location.assign("/login");
                    }}
                  >
                    Go to login
                  </button>
                )}
              </div>
            )}
            <div className="chat-launcher__options">
              {OPTIONS.map((option) => (
                <button
                  type="button"
                  key={option.id}
                  className="chat-launcher__option"
                  onClick={() => handleLaunch(option)}
                  disabled={!canLaunch}
                >
                  <div className="chat-launcher__option-badge">{option.badge}</div>
                  <div>
                    <strong>{option.title}</strong>
                    <p>{option.description}</p>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
      <ChatModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        placement={activePlacement}
        title={activeOption.title}
        description={activeOption.description}
      />
    </>
  );
};

export default ChatLauncher;
