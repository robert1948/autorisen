import { useMemo, useState } from "react";
import type { PaymentMethod, PaymentMethodManagerProps } from "../../types/payments";
import { usePaymentSecurity } from "./PaymentSecurityProvider";

const METHOD_TYPE_CONFIG: Record<
  PaymentMethod["methodType"],
  { label: string; description: string; icon: string }
> = {
  card: { label: "Card", description: "Visa & Mastercard", icon: "💳" },
  eft: { label: "EFT", description: "Manual bank transfer", icon: "🏦" },
  instant_eft: { label: "Instant EFT", description: "Ozow / PayFast", icon: "⚡" },
  bank_transfer: { label: "Bank Transfer", description: "Direct account transfer", icon: "🔁" },
};

interface ConfirmationState {
  method: PaymentMethod | null;
  action: "delete" | "set_default";
}

export function PaymentMethodManager({
  methods,
  onAdd,
  onEdit,
  onDelete,
  onSetDefault,
  className,
}: PaymentMethodManagerProps) {
  const { isSecureContext, csrfToken, securityEvents } = usePaymentSecurity();
  const [confirmation, setConfirmation] = useState<ConfirmationState | null>(null);

  const defaultMethod = useMemo(() => methods.find((method) => method.isDefault) || null, [methods]);
  const activeMethods = methods.filter((method) => method.isActive);

  const handleDelete = (method: PaymentMethod) => {
    setConfirmation({ method, action: "delete" });
  };

  const handleSetDefault = (method: PaymentMethod) => {
    if (method.isDefault) return;
    setConfirmation({ method, action: "set_default" });
  };

  const confirmAction = () => {
    if (!confirmation?.method) return;
    if (confirmation.action === "delete") {
      onDelete(confirmation.method.id);
    } else {
      onSetDefault(confirmation.method.id);
    }
    setConfirmation(null);
  };

  const cancelConfirmation = () => setConfirmation(null);

  const renderMethodCard = (method: PaymentMethod) => {
    const config = METHOD_TYPE_CONFIG[method.methodType];

    return (
      <article
        key={method.id}
        className="border border-gray-200 rounded-xl p-5 bg-white shadow-sm flex flex-col gap-4"
        aria-label={`${config.label} ending ${method.lastFour || "••••"}`}
      >
        <div className="flex items-start gap-4">
          <div className="text-2xl" aria-hidden="true">
            {config.icon}
          </div>
          <div>
            <p className="text-base font-semibold text-gray-900">
              {method.cardBrand || config.label} •••• {method.lastFour || "••••"}
            </p>
            <p className="text-sm text-gray-500">
              {config.label} · {config.description}
            </p>
          </div>
          <div className="ml-auto flex gap-2">
            {method.isDefault && (
              <span className="inline-flex items-center px-2 py-1 text-xs font-medium rounded-full bg-blue-50 text-blue-700">
                Default
              </span>
            )}
            {!method.isActive && (
              <span className="inline-flex items-center px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-600">
                Inactive
              </span>
            )}
          </div>
        </div>

        <dl className="grid grid-cols-2 gap-3 text-sm text-gray-600">
          <div>
            <dt className="text-gray-500">Provider</dt>
            <dd className="capitalize font-medium text-gray-900">{method.provider}</dd>
          </div>
          {method.expiryMonth && method.expiryYear && (
            <div>
              <dt className="text-gray-500">Expiry</dt>
              <dd className="font-medium text-gray-900">
                {String(method.expiryMonth).padStart(2, "0")}/{String(method.expiryYear).slice(-2)}
              </dd>
            </div>
          )}
          <div>
            <dt className="text-gray-500">Status</dt>
            <dd className="font-medium text-gray-900">{method.isActive ? "Active" : "Disabled"}</dd>
          </div>
          <div>
            <dt className="text-gray-500">Updated</dt>
            <dd className="font-medium text-gray-900">{new Date(method.updatedAt).toLocaleDateString()}</dd>
          </div>
        </dl>

        <div className="flex flex-wrap gap-3">
          <button
            type="button"
            className="inline-flex items-center px-3 py-2 text-sm font-medium rounded-md border border-gray-300 text-gray-700 hover:bg-gray-50 transition-colors"
            onClick={() => onEdit(method)}
          >
            Edit
          </button>
          <button
            type="button"
            className="inline-flex items-center px-3 py-2 text-sm font-medium rounded-md border border-blue-200 text-blue-700 hover:bg-blue-50 disabled:opacity-50 transition-colors"
            onClick={() => handleSetDefault(method)}
            disabled={method.isDefault || !method.isActive}
          >
            {method.isDefault ? "Default" : "Make default"}
          </button>
          <button
            type="button"
            className="inline-flex items-center px-3 py-2 text-sm font-medium rounded-md bg-red-50 text-red-700 hover:bg-red-100 transition-colors"
            onClick={() => handleDelete(method)}
          >
            Remove
          </button>
        </div>
      </article>
    );
  };

  return (
    <section className={`space-y-6 ${className ?? ""}`}>
      <div className="bg-white rounded-lg shadow p-6 space-y-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h2 className="text-2xl font-semibold text-gray-900">Payment methods</h2>
            <p className="text-sm text-gray-500">
              All tokens are stored securely via PayFast. CSRF token is {csrfToken ? "active" : "pending"}.
            </p>
          </div>
          <button
            type="button"
            className="inline-flex items-center justify-center rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors"
            onClick={onAdd}
          >
            Add payment method
          </button>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-xs uppercase tracking-wide text-gray-500">Secure context</p>
            <p className="mt-1 text-sm font-semibold text-gray-900">
              {isSecureContext ? "HTTPS verified" : "Requires HTTPS"}
            </p>
          </div>
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-xs uppercase tracking-wide text-gray-500">Active methods</p>
            <p className="mt-1 text-2xl font-semibold text-gray-900">{activeMethods.length}</p>
          </div>
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-xs uppercase tracking-wide text-gray-500">Alerts (24h)</p>
            <p className="mt-1 text-2xl font-semibold text-gray-900">{securityEvents.length}</p>
          </div>
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-xs uppercase tracking-wide text-gray-500">Default method</p>
            <p className="mt-1 text-sm font-semibold text-gray-900">
              {defaultMethod ? defaultMethod.cardBrand || defaultMethod.methodType : "Not set"}
            </p>
          </div>
        </div>

        {methods.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-4xl mb-3" aria-hidden="true">
              💳
            </div>
            <h3 className="text-lg font-semibold text-gray-900">No payment methods yet</h3>
            <p className="mt-2 text-sm text-gray-500">Add a card or EFT profile to start processing payments.</p>
            <button
              type="button"
              className="mt-6 inline-flex items-center justify-center rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors"
              onClick={onAdd}
            >
              Add payment method
            </button>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            {methods.map((method) => renderMethodCard(method))}
          </div>
        )}
      </div>

      {confirmation?.method && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center px-4 z-50" role="presentation">
          <div className="bg-white rounded-xl shadow-xl p-6 max-w-sm w-full space-y-4" role="dialog" aria-modal="true">
            <h3 className="text-lg font-semibold text-gray-900">
              {confirmation.action === "delete" ? "Remove payment method" : "Set as default method"}
            </h3>
            <p className="text-sm text-gray-600">
              {confirmation.action === "delete"
                ? `This will remove ${confirmation.method.cardBrand || confirmation.method.methodType} ending ${
                    confirmation.method.lastFour || "••••"
                  }.`
                : `Make ${confirmation.method.cardBrand || confirmation.method.methodType} ending ${
                    confirmation.method.lastFour || "••••"
                  } the default payment method?`}
            </p>
            <div className="flex justify-end gap-3">
              <button
                type="button"
                className="inline-flex items-center px-4 py-2 text-sm font-medium rounded-md border border-gray-300 text-gray-700 hover:bg-gray-50 transition-colors"
                onClick={cancelConfirmation}
              >
                Cancel
              </button>
              <button
                type="button"
                className={`inline-flex items-center px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                  confirmation.action === "delete"
                    ? "bg-red-600 text-white hover:bg-red-700"
                    : "bg-blue-600 text-white hover:bg-blue-700"
                }`}
                onClick={confirmAction}
              >
                {confirmation.action === "delete" ? "Remove" : "Confirm"}
              </button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}

export default PaymentMethodManager;
