import React from "react";

export default function EarlyAccessPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-50">
      <div className="mx-auto w-full max-w-3xl px-4 py-14 sm:px-8">
        <h1 className="text-3xl font-semibold tracking-tight">
          CapeControl — Early Access Principles
        </h1>

        <div className="mt-10 space-y-8 text-slate-200">
          <section className="space-y-3">
            <h2 className="text-xl font-semibold text-slate-50">Why Early Access?</h2>
            <p>CapeControl is being built deliberately.</p>
            <p>
              Rather than launching everything at once, we’re releasing the platform in{" "}
              <strong>carefully shaped stages</strong>—so what you experience is thoughtful,
              stable, and improving over time.
            </p>
            <p>
              Early access means you’re seeing a system that is:
            </p>
            <ul className="list-disc space-y-1 pl-6">
              <li>real,</li>
              <li>alive,</li>
              <li>and still growing.</li>
            </ul>
          </section>

          <section className="space-y-3">
            <h2 className="text-xl font-semibold text-slate-50">What We Believe</h2>
            <p>
              <strong>Clarity beats complexity</strong>
              <br />
              We’d rather do a few things well than many things poorly.
            </p>
            <p>
              <strong>Honesty builds trust</strong>
              <br />
              If something is experimental, we’ll say so.
              <br />
              If something isn’t ready, it won’t pretend to be.
            </p>
            <p>
              <strong>Progress over polish</strong>
              <br />
              You may notice areas that are intentionally simple or marked as “preview.”
              <br />
              That’s by design.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-xl font-semibold text-slate-50">What You Can Expect</h2>
            <ul className="list-disc space-y-1 pl-6">
              <li>A stable core experience</li>
              <li>Clean authentication and predictable behavior</li>
              <li>No dark patterns or misleading promises</li>
              <li>Clear signals about what’s ready and what’s evolving</li>
            </ul>
            <p>If something is visible, it’s there for a reason.</p>
          </section>

          <section className="space-y-3">
            <h2 className="text-xl font-semibold text-slate-50">What You Won’t See (Yet)</h2>
            <ul className="list-disc space-y-1 pl-6">
              <li>Feature overload</li>
              <li>Inflated claims</li>
              <li>Artificial urgency</li>
              <li>Roadmaps designed to impress rather than inform</li>
            </ul>
            <p>
              CapeControl grows by <strong>earning confidence</strong>, not demanding attention.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-xl font-semibold text-slate-50">A Quiet Invitation</h2>
            <p>
              If you’re here early, you’re part of a small group helping shape something long-term.
            </p>
            <p>We’re glad you’re curious.</p>
            <p>We’re even happier you’re thoughtful.</p>
            <p>—</p>
            <p>CapeControl</p>
            <p>
              <em>Built with care. Released with intent.</em>
            </p>
          </section>
        </div>
      </div>
    </div>
  );
}
