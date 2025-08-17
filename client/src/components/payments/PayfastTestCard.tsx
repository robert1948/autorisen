import { useState } from "react";

export default function PayfastTestCard() {
  const [loading, setLoading] = useState(false);
  const [lastUrl, setLastUrl] = useState<string | null>(null);
  const [amount, setAmount] = useState("100.00");

  const startCheckout = async () => {
    try {
      setLoading(true);
      const resp = await fetch("/api/payfast/checkout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          amount: Number(amount).toFixed(2),
          item_name: "Cape Control Test Product",
          item_description: "Sandbox test payment",
          email_address: "test@example.com",
          m_payment_id: "test-" + Math.random().toString(36).slice(2) + "-" + Date.now(),
        }),
      });
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({} as any));
        throw new Error(err?.detail || `Checkout failed (${resp.status})`);
      }
      const data = await resp.json();
      setLastUrl(data.redirect_url);
      window.location.href = data.redirect_url; // redirect to PayFast
    } catch (e: any) {
      console.error(e);
      alert(e?.message || "Failed to start PayFast checkout");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md w-full mx-auto rounded-2xl shadow p-6 border">
      <h2 className="text-xl font-semibold mb-2">PayFast Sandbox Test</h2>
      <p className="text-sm opacity-80 mb-4">
        Try a test payment in the PayFast Sandbox. No real money moves.
      </p>

      <label className="block text-sm mb-1">Amount (ZAR)</label>
      <input
        className="w-full border rounded-xl px-3 py-2 mb-4"
        value={amount}
        onChange={(e) => setAmount(e.target.value)}
        inputMode="decimal"
      />

      <button
        onClick={startCheckout}
        disabled={loading}
        className="w-full rounded-2xl px-4 py-3 font-medium shadow hover:shadow-md disabled:opacity-60 border"
      >
        {loading ? "Starting…" : "Start Sandbox Checkout"}
      </button>

      {lastUrl && (
        <p className="text-xs mt-4 break-all">
          Redirected to: <span className="font-mono">{lastUrl}</span>
        </p>
      )}
    </div>
  );
}

