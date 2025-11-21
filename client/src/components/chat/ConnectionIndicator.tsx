import type { ConnectionHealth } from "../../types/websocket";

type Props = {
  health: ConnectionHealth | null;
  queueLength?: number;
  variant?: "compact" | "full";
};

const STATUS_LABEL: Record<ConnectionHealth["status"], string> = {
  idle: "Idle",
  connecting: "Connecting",
  open: "Connected",
  closed: "Disconnected",
  error: "Error",
};

const QUALITY_LABEL: Record<ConnectionHealth["connectionQuality"], string> = {
  excellent: "Excellent",
  good: "Good",
  poor: "Poor",
  critical: "Critical",
};

const formatLatency = (latency: number) => {
  if (!Number.isFinite(latency) || latency <= 0) {
    return null;
  }
  return `${Math.max(1, Math.round(latency))} ms`;
};

const ConnectionIndicator = ({ health, queueLength = 0, variant = "full" }: Props) => {
  if (!health) {
    return null;
  }

  const latency = formatLatency(health.latency);
  const quality = QUALITY_LABEL[health.connectionQuality];
  const statusLabel = STATUS_LABEL[health.status];

  const classes = ["chat-status"];
  if (variant === "compact") {
    classes.push("chat-status--compact");
  }

  return (
    <div className={classes.join(" ")}>
      <span
        className="chat-status__dot"
        data-status={health.status}
        aria-label={`Chat connection ${statusLabel}`}
      />
      <div className="chat-status__text">
        <span className="chat-status__label">{statusLabel}</span>
        {variant === "full" && (
          <span className="chat-status__meta">
            {quality && <span>{quality} link</span>}
            {latency && <span>{latency}</span>}
            {queueLength > 0 && <span>Queue {queueLength}</span>}
            {health.reconnectAttempts > 0 && (
              <span>Retry {health.reconnectAttempts}</span>
            )}
          </span>
        )}
      </div>
    </div>
  );
};

export default ConnectionIndicator;
