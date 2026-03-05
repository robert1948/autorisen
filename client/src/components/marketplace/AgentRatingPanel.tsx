/**
 * AgentRatingPanel — displays rating summary + review list + submit form.
 *
 * Drop this into any agent detail view:
 *   <AgentRatingPanel agentId={agent.id} />
 */

import React, { useCallback, useEffect, useState } from "react";
import { apiFetch } from "../../lib/apiFetch";
import { StarRating } from "./StarRating";

interface RatingItem {
  user_id: string;
  rating: number;
  review: string | null;
  created_at: string;
  helpful_votes: number;
}

interface RatingSummary {
  agent_id: string;
  average_rating: number;
  total_ratings: number;
  distribution: Record<string, number>;
}

interface RatingsResponse {
  summary: RatingSummary;
  ratings: RatingItem[];
  page: number;
  pages: number;
}

interface AgentRatingPanelProps {
  agentId: string;
}

export function AgentRatingPanel({ agentId }: AgentRatingPanelProps) {
  const [data, setData] = useState<RatingsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [myRating, setMyRating] = useState(0);
  const [myReview, setMyReview] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const loadRatings = useCallback(async () => {
    try {
      const resp = await apiFetch<RatingsResponse>(`/marketplace/agents/${agentId}/ratings`);
      setData(resp);
    } catch {
      // Non-critical — render empty state
    } finally {
      setIsLoading(false);
    }
  }, [agentId]);

  useEffect(() => {
    loadRatings();
  }, [loadRatings]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (myRating < 1) return;
    setSubmitting(true);
    setSubmitError(null);
    try {
      await apiFetch(`/marketplace/agents/${agentId}/rate`, {
        method: "POST",
        body: { rating: myRating, review: myReview || null },
        auth: true,
      });
      setMyRating(0);
      setMyReview("");
      await loadRatings();
    } catch (err) {
      setSubmitError((err as Error).message ?? "Failed to submit rating");
    } finally {
      setSubmitting(false);
    }
  };

  if (isLoading) {
    return <div className="animate-pulse h-32 bg-slate-100 rounded-lg dark:bg-slate-700" />;
  }

  const summary = data?.summary;
  const ratings = data?.ratings ?? [];

  return (
    <div className="space-y-6">
      {/* Summary bar */}
      {summary && summary.total_ratings > 0 && (
        <div className="flex items-center gap-6 rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
          <div className="text-center">
            <p className="text-3xl font-bold text-slate-900 dark:text-white">
              {summary.average_rating.toFixed(1)}
            </p>
            <StarRating value={summary.average_rating} readonly size="sm" />
            <p className="mt-1 text-xs text-slate-500">{summary.total_ratings} rating{summary.total_ratings !== 1 ? "s" : ""}</p>
          </div>

          {/* Distribution bars */}
          <div className="flex-1 space-y-1">
            {[5, 4, 3, 2, 1].map((star) => {
              const count = summary.distribution[String(star)] ?? 0;
              const pct = summary.total_ratings > 0 ? (count / summary.total_ratings) * 100 : 0;
              return (
                <div key={star} className="flex items-center gap-2 text-xs">
                  <span className="w-3 text-right text-slate-500">{star}</span>
                  <div className="h-2 flex-1 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-700">
                    <div className="h-full rounded-full bg-amber-400" style={{ width: `${pct}%` }} />
                  </div>
                  <span className="w-6 text-right text-slate-400">{count}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Submit rating form */}
      <form onSubmit={handleSubmit} className="rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
        <h4 className="mb-3 text-sm font-semibold text-slate-900 dark:text-white">Leave a Rating</h4>
        <div className="mb-3">
          <StarRating value={myRating} onChange={setMyRating} size="lg" />
        </div>
        <textarea
          className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 dark:border-slate-600 dark:bg-slate-700 dark:text-white"
          rows={3}
          maxLength={1000}
          placeholder="Write an optional review…"
          value={myReview}
          onChange={(e) => setMyReview(e.target.value)}
        />
        {submitError && <p className="mt-1 text-xs text-red-600">{submitError}</p>}
        <button
          type="submit"
          disabled={myRating < 1 || submitting}
          className="mt-2 rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {submitting ? "Submitting…" : "Submit Rating"}
        </button>
      </form>

      {/* Review list */}
      {ratings.length > 0 && (
        <div className="space-y-3">
          <h4 className="text-sm font-semibold text-slate-900 dark:text-white">Reviews</h4>
          {ratings.map((r, idx) => (
            <div key={idx} className="rounded-lg border border-slate-200 bg-white p-3 dark:border-slate-700 dark:bg-slate-800">
              <div className="flex items-center gap-2">
                <StarRating value={r.rating} readonly size="sm" />
                <span className="text-xs text-slate-400">
                  {new Date(r.created_at).toLocaleDateString()}
                </span>
              </div>
              {r.review && <p className="mt-1 text-sm text-slate-700 dark:text-slate-300">{r.review}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
