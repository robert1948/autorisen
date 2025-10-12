import { useEffect, useMemo, useRef, useState } from "react";

import type { ChatToken } from "./ChatKitProvider";

type Props = {
  token: ChatToken;
  placement: string;
};

type ScriptStatus = "idle" | "loading" | "ready" | "error";

type ChatKitRenderHandle = {
  destroy?: () => void;
  unmount?: () => void;
};

declare global {
  interface Window {
    ChatKit?: {
      render: (options: {
        container: HTMLElement;
        token: string;
        placement: string;
        threadId: string;
        metadata?: Record<string, unknown>;
      }) => ChatKitRenderHandle | void;
    };
  }
}

const widgetSrc = import.meta.env.VITE_CHATKIT_WIDGET_URL as string | undefined;

const loadScript = (src: string) => {
  return new Promise<void>((resolve, reject) => {
    const existing = document.querySelector<HTMLScriptElement>(`script[data-chatkit="${src}"]`);
    if (existing) {
      if (existing.getAttribute("data-loaded") === "true") {
        resolve();
        return;
      }
      existing.addEventListener("load", () => resolve(), { once: true });
      existing.addEventListener("error", () => reject(new Error("ChatKit script failed to load")), {
        once: true,
      });
      return;
    }

    const script = document.createElement("script");
    script.src = src;
    script.async = true;
    script.defer = true;
    script.dataset.chatkit = src;
    script.addEventListener(
      "load",
      () => {
        script.dataset.loaded = "true";
        resolve();
      },
      { once: true },
    );
    script.addEventListener(
      "error",
      () => {
        reject(new Error("ChatKit script failed to load"));
      },
      { once: true },
    );
    document.head.appendChild(script);
  });
};

const ChatKitWidget = ({ token, placement }: Props) => {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [status, setStatus] = useState<ScriptStatus>(widgetSrc ? "loading" : "error");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    let handle: ChatKitRenderHandle | void;

    const mount = async () => {
      if (!widgetSrc) {
        setError("ChatKit widget URL is not configured.");
        setStatus("error");
        return;
      }
      try {
        setStatus("loading");
        await loadScript(widgetSrc);
        if (cancelled) return;
        if (!window.ChatKit || typeof window.ChatKit.render !== "function") {
          throw new Error("ChatKit global is unavailable after script load.");
        }
        const container = containerRef.current;
        if (!container) {
          throw new Error("Chat container not mounted.");
        }
        handle = window.ChatKit.render({
          container,
          token: token.token,
          placement,
          threadId: token.threadId,
          metadata: {
            expiresAt: token.expiresAt,
            allowedTools: token.allowedTools,
          },
        });
        if (!cancelled) {
          setStatus("ready");
        }
      } catch (err) {
        if (!cancelled) {
          const message = err instanceof Error ? err.message : "Unable to mount ChatKit widget.";
          setError(message);
          setStatus("error");
        }
      }
    };

    mount();

    return () => {
      cancelled = true;
      if (handle && typeof handle.destroy === "function") {
        handle.destroy();
      } else if (handle && typeof handle.unmount === "function") {
        handle.unmount();
      }
    };
  }, [placement, token]);

  const message = useMemo(() => {
    if (status === "loading") return "Loading ChatKit experience…";
    if (status === "error" && error) return error;
    return null;
  }, [status, error]);

  return (
    <div className="chat-widget-shell">
      <div ref={containerRef} className="chat-widget-container" />
      {message && <p className="chat-widget-message">{message}</p>}
    </div>
  );
};

export default ChatKitWidget;
