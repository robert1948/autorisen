import type { PaymentStatusProps } from "../../types/payments";
import { DEFAULT_CURRENCY } from "../../types/payments";

const STATUS_CONFIG: Record<
  PaymentStatusProps["status"],
  { label: string; description: string; tone: "info" | "success" | "danger" | "warning" }
> = {
  pending: {
    label: "Pending",
    description: "Waiting for confirmation from PayFast.",
    tone: "info",
  },
  paid: {
    label: "Paid",
    description: "Payment completed successfully.",
    tone: "success",
  },
  cancelled: {
    label: "Cancelled",
    description: "Checkout was cancelled before completion.",
    tone: "warning",
  },
  failed: {
    label: "Failed",
    description: "Payment failed. Please retry.",
    tone: "danger",
  },
  refunded: {
    label: "Refunded",
    description: "Amount refunded to the original source.",
    tone: "warning",
  },
};

const ICONS: Record<PaymentStatusProps["status"], string> = {
  pending: "⏳",
  paid: "✅",
  cancelled: "⚠️",
  failed: "❌",
  refunded: "↩️",
};

export function PaymentStatus({
  status,
  amount,
  currency = DEFAULT_CURRENCY,
  transactionId,
  createdAt,
  className = "",
}: PaymentStatusProps) {
  const config = STATUS_CONFIG[status];

  return (
    <section className={`payment-status ${className}`}>
      <header className="payment-status__header">
        <span className={`payment-status__badge payment-status__badge--${config.tone}`}>
          <span aria-hidden="true" className="payment-status__icon">
            {ICONS[status]}
          </span>
          {config.label}
        </span>
        {createdAt && (
          <time className="payment-status__timestamp" dateTime={createdAt}>
            {new Date(createdAt).toLocaleString()}
          </time>
        )}
      </header>

      <p className="payment-status__description">{config.description}</p>

      {amount !== undefined && (
        <dl className="payment-status__details">
          <div>
            <dt>Amount</dt>
            <dd>
              {currency} {amount.toFixed(2)}
            </dd>
          </div>
          {transactionId && (
            <div>
              <dt>Transaction ID</dt>
              <dd>
                <code>{transactionId}</code>
              </dd>
            </div>
          )}
        </dl>
      )}
    </section>
  );
}

export default PaymentStatus;
