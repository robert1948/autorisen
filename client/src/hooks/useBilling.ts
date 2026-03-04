/**
 * useBilling — fetches subscription + plan data + invoice stats
 * for the Billing page. Reusable hook that calls the payments API.
 */

import { useCallback, useEffect, useState } from "react";
import { apiFetch } from "../lib/apiFetch";
import type { Plan, PlansResponse, Subscription } from "../types/payments";

interface InvoiceStats {
  total_count: number;
  total_amount: number;
  paid_count: number;
}

interface LatestInvoice {
  id: string;
  invoice_number: string | null;
  amount: string;
  currency: string;
  status: string;
  item_name: string;
  created_at: string | null;
}

export interface BillingData {
  subscription: Subscription | null;
  plans: Plan[];
  invoiceStats: InvoiceStats;
  latestInvoice: LatestInvoice | null;
  loading: boolean;
  error: string | null;
  refresh: () => void;
}

export function useBilling(): BillingData {
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [plans, setPlans] = useState<Plan[]>([]);
  const [invoiceStats, setInvoiceStats] = useState<InvoiceStats>({
    total_count: 0,
    total_amount: 0,
    paid_count: 0,
  });
  const [latestInvoice, setLatestInvoice] = useState<LatestInvoice | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      // Fetch in parallel
      const [plansRes, subData, invoicesData] = await Promise.all([
        apiFetch<PlansResponse>("/payments/plans", { auth: false }),
        apiFetch<Subscription>("/payments/subscription").catch(() => null),
        apiFetch<{ invoices: LatestInvoice[]; total: number }>("/payments/invoices?limit=50").catch(
          () => ({ invoices: [], total: 0 }),
        ),
      ]);

      setPlans(plansRes.plans);
      setSubscription(subData);

      // Compute stats from invoices
      const invoices = invoicesData.invoices ?? [];
      const paidInvoices = invoices.filter(
        (inv: LatestInvoice) => inv.status === "paid",
      );
      const totalAmount = paidInvoices.reduce(
        (sum: number, inv: LatestInvoice) => sum + parseFloat(inv.amount || "0"),
        0,
      );
      setInvoiceStats({
        total_count: invoicesData.total,
        total_amount: totalAmount,
        paid_count: paidInvoices.length,
      });

      // Latest invoice
      if (invoices.length > 0) {
        setLatestInvoice(invoices[0]);
      }
    } catch {
      setError("Failed to load billing data");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAll();
  }, [fetchAll]);

  return {
    subscription,
    plans,
    invoiceStats,
    latestInvoice,
    loading,
    error,
    refresh: fetchAll,
  };
}
