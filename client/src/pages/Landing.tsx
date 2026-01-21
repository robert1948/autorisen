import React, { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";

import logoUrl from "../assets/CapeControl_Logo_Transparent.png";

type StageKey = "spark" | "touch" | "trail" | "forYou" | "invite";

const STAGES: Array<{ key: StageKey; label: string; hint: string }> = [
  { key: "spark", label: "Spark", hint: "A question, not an explanation" },
  { key: "touch", label: "Touch", hint: "Small interactions, small clarity" },
  { key: "trail", label: "Trail", hint: "Breadcrumbs, not a dump" },
  { key: "forYou", label: "For you", hint: "Find yourself in it" },
  { key: "invite", label: "Invitation", hint: "A next step—optional" },
];

function classNames(...parts: Array<string | false | undefined | null>) {
  return parts.filter(Boolean).join(" ");
}

function TrailNav({
  activeIndex,
  maxUnlockedIndex,
  onSelect,
}: {
  activeIndex: number;
  maxUnlockedIndex: number;
  onSelect: (index: number) => void;
}) {
  return (
    <nav aria-label="Curiosity trail" className="w-full">
      <div className="flex flex-wrap items-center gap-2">
        {STAGES.map((stage, index) => {
          const isLocked = index > maxUnlockedIndex;
          const isActive = index === activeIndex;

          return (
            <button
              key={stage.key}
              type="button"
              onClick={() => !isLocked && onSelect(index)}
              disabled={isLocked}
              className={classNames(
                "group inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-[11px] sm:text-xs transition",
                isLocked
                  ? "border-slate-800/80 text-slate-600 cursor-not-allowed"
                  : "border-slate-800/80 text-slate-300 hover:border-slate-700 hover:text-slate-100",
                isActive && "border-sky-500/40 text-slate-50"
              )}
              aria-current={isActive ? "step" : undefined}
              title={stage.hint}
            >
              <span
                className={classNames(
                  "h-1.5 w-1.5 rounded-full",
                  isLocked
                    ? "bg-slate-700"
                    : isActive
                      ? "bg-sky-400"
                      : "bg-slate-500 group-hover:bg-slate-300"
                )}
              />
              <span className="font-medium">{stage.label}</span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}

function RevealCard({
  title,
  teaser,
  reveal,
  isOpen,
  onToggle,
}: {
  title: string;
  teaser: string;
  reveal: string;
  isOpen: boolean;
  onToggle: () => void;
}) {
  return (
    <div
      className={classNames(
        "rounded-3xl sm:rounded-2xl border border-slate-800/80 bg-slate-900/50 backdrop-blur-sm p-5 sm:p-5 transition",
        "hover:border-slate-700 hover:bg-slate-900/65"
      )}
    >
      <button
        type="button"
        className="w-full text-left"
        onClick={onToggle}
        aria-expanded={isOpen}
      >
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="text-sm font-semibold tracking-tight text-slate-50">
              {title}
            </div>
            <div className="mt-2 sm:mt-1 text-xs sm:text-sm text-slate-400">
              {teaser}
            </div>
          </div>
          <div
            className={classNames(
              "shrink-0 rounded-full border border-slate-800 px-2 py-1 text-[10px] text-slate-400 transition",
              isOpen && "border-sky-500/40 text-slate-200"
            )}
          >
            {isOpen ? "Hide" : "Peek"}
          </div>
        </div>
      </button>

      <div
        className={classNames(
          "grid transition-[grid-template-rows,opacity] duration-300 ease-out",
          isOpen ? "grid-rows-[1fr] opacity-100" : "grid-rows-[0fr] opacity-0"
        )}
      >
        <div className="overflow-hidden">
          <div className="mt-3 rounded-2xl sm:rounded-xl bg-slate-950/40 border border-slate-800/60 p-4 sm:p-3 text-xs sm:text-sm text-slate-200">
            {reveal}
          </div>
        </div>
      </div>
    </div>
  );
}

const LandingPage: React.FC = () => {
  const [activeStage, setActiveStage] = useState(0);
  const [maxUnlockedStage, setMaxUnlockedStage] = useState(0);

  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const [openClue, setOpenClue] = useState<string | null>(null);
  const [trailStep, setTrailStep] = useState<"signal" | "shift" | "control" | null>(null);
  const [persona, setPersona] = useState<
    "ops" | "builder" | "leader" | "explorer" | "risk" | null
  >(null);

  const canAdvance = useMemo(() => {
    const stageKey = STAGES[activeStage]?.key;
    if (stageKey === "spark") return true;
    if (stageKey === "touch") return Boolean(openClue);
    if (stageKey === "trail") return Boolean(trailStep);
    if (stageKey === "forYou") return Boolean(persona);
    return true;
  }, [activeStage, openClue, trailStep, persona]);

  const unlockAndGo = (nextIndex: number) => {
    setMaxUnlockedStage((prev) => Math.max(prev, nextIndex));
    setActiveStage(nextIndex);
  };

  const stageKey = STAGES[activeStage]?.key;

  useEffect(() => {
    if (!isMobileMenuOpen) return;

    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setIsMobileMenuOpen(false);
    };

    window.addEventListener("keydown", onKeyDown);
    return () => {
      window.removeEventListener("keydown", onKeyDown);
      document.body.style.overflow = prevOverflow;
    };
  }, [isMobileMenuOpen]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 flex flex-col">
      <header className="w-full max-w-6xl mx-auto px-4 sm:px-8 py-4 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2" aria-label="CapeControl">
          <img src={logoUrl} alt="CapeControl" className="h-9 w-auto" loading="lazy" />
          <span className="sr-only">CapeControl</span>
        </Link>
        <div className="flex items-center gap-3">
          <span className="hidden sm:inline text-[11px] text-slate-500">
            Explore quietly. Decide later.
          </span>
          <Link
            to="/auth/login"
            className="text-[11px] sm:text-xs text-slate-300 hover:text-white transition"
          >
            Log in
          </Link>

          <button
            type="button"
            onClick={() => setIsMobileMenuOpen((prev) => !prev)}
            className="sm:hidden inline-flex h-11 w-11 items-center justify-center rounded-xl border border-slate-800/80 bg-slate-950/40 hover:bg-slate-900/60 transition"
            aria-label={isMobileMenuOpen ? "Close menu" : "Open menu"}
            aria-haspopup="dialog"
            aria-expanded={isMobileMenuOpen}
          >
            <svg
              viewBox="0 0 24 24"
              width="24"
              height="24"
              aria-hidden="true"
              focusable="false"
              className="text-slate-200"
            >
              <path
                fill="currentColor"
                d="M4 6a1 1 0 0 1 1-1h14a1 1 0 1 1 0 2H5A1 1 0 0 1 4 6Zm0 6a1 1 0 0 1 1-1h14a1 1 0 1 1 0 2H5a1 1 0 0 1-1-1Zm1 5a1 1 0 1 0 0 2h14a1 1 0 1 0 0-2H5Z"
              />
            </svg>
          </button>
        </div>
      </header>

      {isMobileMenuOpen && (
        <div className="sm:hidden fixed inset-0 z-50">
          <button
            type="button"
            className="absolute inset-0 z-50 bg-slate-950/70 backdrop-blur-sm transition-opacity"
            aria-label="Close menu"
            onClick={() => setIsMobileMenuOpen(false)}
          />

          <div className="absolute right-0 top-0 z-[60] h-full w-[86%] max-w-sm border-l border-slate-800/80 bg-slate-950/90 shadow-2xl">
            <div className="pt-[calc(env(safe-area-inset-top)+1rem)] px-5 pb-6">
              <div className="flex items-center justify-between">
                <div className="text-sm font-semibold text-slate-50">Menu</div>
                <button
                  type="button"
                  onClick={() => setIsMobileMenuOpen(false)}
                  className="inline-flex h-11 w-11 items-center justify-center rounded-xl border border-slate-800/80 bg-slate-950/40 hover:bg-slate-900/60 transition"
                  aria-label="Close menu"
                >
                  <span className="text-xl leading-none">×</span>
                </button>
              </div>

              <nav className="mt-6 grid gap-3">
                <Link
                  to="/docs"
                  onClick={() => setIsMobileMenuOpen(false)}
                  className="inline-flex min-h-12 items-center justify-between rounded-2xl border border-slate-800/80 bg-slate-900/40 px-4 py-3 text-sm font-medium text-slate-100"
                >
                  <span>Docs</span>
                  <span className="text-slate-500">›</span>
                </Link>
                <Link
                  to="/subscribe"
                  onClick={() => setIsMobileMenuOpen(false)}
                  className="inline-flex min-h-12 items-center justify-between rounded-2xl border border-slate-800/80 bg-slate-900/40 px-4 py-3 text-sm font-medium text-slate-100"
                >
                  <span>Early access</span>
                  <span className="text-slate-500">›</span>
                </Link>
                <Link
                  to="/auth/login"
                  onClick={() => setIsMobileMenuOpen(false)}
                  className="inline-flex min-h-12 items-center justify-between rounded-2xl border border-slate-800/80 bg-slate-900/40 px-4 py-3 text-sm font-medium text-slate-100"
                >
                  <span>Log in</span>
                  <span className="text-slate-500">›</span>
                </Link>
              </nav>

              <div className="mt-6 text-[11px] text-slate-500">
                Tip: Tap outside the sheet to close.
              </div>
            </div>
          </div>
        </div>
      )}

      <main className="flex-1">
        <div className="relative w-full">
          <div className="pointer-events-none hidden lg:block absolute inset-y-0 right-0">
            <div className="h-80 w-80 rounded-full bg-gradient-to-tr from-purple-500/40 via-sky-500/20 to-transparent blur-3xl translate-x-16 -translate-y-8" />
          </div>

          <section className="relative max-w-6xl mx-auto px-4 sm:px-8 py-10 md:py-14">
            <div className="flex flex-col gap-6">
              <div className="flex items-start justify-between gap-6">
                <div>
                  <p className="text-[11px] sm:text-xs font-semibold tracking-[0.25em] text-sky-400 uppercase">
                    The Curiosity Trail
                  </p>
                  <h1 className="mt-3 text-3xl sm:text-4xl md:text-5xl font-semibold tracking-tight">
                    What if AI felt calm…
                    <span className="text-slate-400"> before it felt powerful?</span>
                  </h1>
                  <p className="mt-4 max-w-2xl text-sm sm:text-base text-slate-300">
                    CapeControl doesn’t start by telling you everything. It starts by giving you one useful
                    thing—then letting the next question appear.
                  </p>
                </div>
              </div>

              <TrailNav
                activeIndex={activeStage}
                maxUnlockedIndex={maxUnlockedStage}
                onSelect={(index) => setActiveStage(index)}
              />

              {/* Stage content */}
              <div className="mt-2 rounded-3xl border border-slate-800/80 bg-slate-900/40 backdrop-blur-sm p-6 sm:p-7">
                {stageKey === "spark" && (
                  <div className="grid gap-6 sm:gap-5">
                    <div className="text-sm sm:text-base text-slate-200">
                      You already have the tools. You might even have the models.
                      <span className="text-slate-400"> The missing piece is the feeling of control.</span>
                    </div>
                    <div className="grid gap-2 text-xs sm:text-sm text-slate-400">
                      <div>Start with a single clue—nothing more.</div>
                      <div>Then choose whether to follow the trail.</div>
                    </div>

                    <div className="flex flex-col sm:flex-row gap-3 sm:items-center">
                      <button
                        type="button"
                        onClick={() => unlockAndGo(1)}
                        className="inline-flex w-full sm:w-auto min-h-12 items-center justify-center rounded-full px-6 py-3 text-sm font-medium bg-gradient-to-r from-fuchsia-500 via-purple-500 to-sky-500 shadow-lg shadow-purple-500/30 hover:shadow-purple-500/50 transition"
                      >
                        Show me one clue
                      </button>
                      <Link
                        to="/explore"
                        className="inline-flex w-full sm:w-auto min-h-12 items-center justify-center rounded-full px-6 py-3 text-sm font-medium border border-slate-500/60 bg-slate-100/5 text-slate-200 hover:bg-slate-100/10 hover:border-slate-400/70 hover:text-slate-100 active:bg-slate-100/15 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-200/40 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 transition"
                      >
                        Browse quietly (no account)
                      </Link>
                    </div>
                  </div>
                )}

                {stageKey === "touch" && (
                  <div className="grid gap-5">
                    <div>
                      <div className="text-sm sm:text-base text-slate-200">
                        Touch something small. Get a small reward.
                      </div>
                      <div className="mt-2 text-xs sm:text-sm text-slate-400">
                        These aren’t “features.” They’re signals.
                      </div>
                    </div>

                    <div className="grid md:grid-cols-3 gap-4">
                      <RevealCard
                        title="Less noise"
                        teaser="Most AI tools talk too much, too soon."
                        reveal="CapeControl is built around ‘just enough clarity’ — one next step at a time, so your attention stays intact."
                        isOpen={openClue === "noise"}
                        onToggle={() => setOpenClue((prev) => (prev === "noise" ? null : "noise"))}
                      />
                      <RevealCard
                        title="More trust"
                        teaser="Confidence comes from boundaries, not bravado."
                        reveal="Instead of asking you to believe, it shows you what’s happening—only when you ask for it."
                        isOpen={openClue === "trust"}
                        onToggle={() => setOpenClue((prev) => (prev === "trust" ? null : "trust"))}
                      />
                      <RevealCard
                        title="A gentle guide"
                        teaser="It feels like a guide, not a machine."
                        reveal="You get prompts that make your next decision easier—without pulling you into a big commitment."
                        isOpen={openClue === "guide"}
                        onToggle={() => setOpenClue((prev) => (prev === "guide" ? null : "guide"))}
                      />
                    </div>

                    <div className="flex flex-col sm:flex-row gap-3 sm:items-center">
                      <button
                        type="button"
                        onClick={() => unlockAndGo(2)}
                        disabled={!canAdvance}
                        className={classNames(
                          "inline-flex w-full sm:w-auto min-h-12 items-center justify-center rounded-full px-6 py-3 text-sm font-medium transition",
                          canAdvance
                            ? "bg-slate-100 text-slate-950 hover:bg-white"
                            : "bg-slate-800/60 text-slate-500 cursor-not-allowed"
                        )}
                      >
                        Follow the breadcrumb trail
                      </button>
                      <button
                        type="button"
                        onClick={() => unlockAndGo(0)}
                        className="inline-flex w-full sm:w-auto min-h-12 items-center justify-center rounded-full px-6 py-3 text-sm font-medium border border-slate-800/80 text-slate-200 hover:border-slate-700 hover:text-white transition"
                      >
                        Go back
                      </button>
                    </div>
                  </div>
                )}

                {stageKey === "trail" && (
                  <div className="grid gap-5">
                    <div>
                      <div className="text-sm sm:text-base text-slate-200">
                        Breadcrumbs, not a brochure.
                      </div>
                      <div className="mt-2 text-xs sm:text-sm text-slate-400">
                        Pick one. Let it sharpen your next question.
                      </div>
                    </div>

                    <div className="grid md:grid-cols-3 gap-4">
                      <RevealCard
                        title="Tame AI anxiety?"
                        teaser="What would make AI feel safer to start?"
                        reveal="Not another setup marathon. A guided first step that reduces uncertainty, so you can move without second‑guessing."
                        isOpen={trailStep === "signal"}
                        onToggle={() => setTrailStep((prev) => (prev === "signal" ? null : "signal"))}
                      />
                      <RevealCard
                        title="Query with magic?"
                        teaser="What if the next answer felt obvious?"
                        reveal="A conversational layer that helps you ask better questions—without needing to learn a new language on day one."
                        isOpen={trailStep === "shift"}
                        onToggle={() => setTrailStep((prev) => (prev === "shift" ? null : "shift"))}
                      />
                      <RevealCard
                        title="Agents that delight?"
                        teaser="What if automation felt predictable—and pleasant?"
                        reveal="Small, composable building blocks that do one thing well, so surprises stay useful—not risky."
                        isOpen={trailStep === "control"}
                        onToggle={() => setTrailStep((prev) => (prev === "control" ? null : "control"))}
                      />
                    </div>

                    <div className="flex flex-col sm:flex-row gap-3 sm:items-center">
                      <button
                        type="button"
                        onClick={() => unlockAndGo(3)}
                        disabled={!canAdvance}
                        className={classNames(
                          "inline-flex w-full sm:w-auto min-h-12 items-center justify-center rounded-full px-6 py-3 text-sm font-medium transition",
                          canAdvance
                            ? "bg-slate-100 text-slate-950 hover:bg-white"
                            : "bg-slate-800/60 text-slate-500 cursor-not-allowed"
                        )}
                      >
                        Tell me who this is for
                      </button>
                      <button
                        type="button"
                        onClick={() => setActiveStage(1)}
                        className="inline-flex w-full sm:w-auto min-h-12 items-center justify-center rounded-full px-6 py-3 text-sm font-medium border border-slate-800/80 text-slate-200 hover:border-slate-700 hover:text-white transition"
                      >
                        Go back
                      </button>
                    </div>
                  </div>
                )}

                {stageKey === "forYou" && (
                  <div className="grid gap-5">
                    <div>
                      <div className="text-sm sm:text-base text-slate-200">
                        This is for people who…
                      </div>
                      <div className="mt-2 text-xs sm:text-sm text-slate-400">
                        Pick the closest fit. It doesn’t lock you in.
                      </div>
                    </div>

                    <div className="grid sm:grid-cols-2 gap-3">
                      {(
                        [
                          { key: "leader", label: "Lead a team", sub: "Need clarity without chaos" },
                          { key: "ops", label: "Run operations", sub: "Want fewer surprises and faster decisions" },
                          { key: "builder", label: "Build systems", sub: "Prefer clean boundaries and control" },
                          { key: "risk", label: "Carry responsibility", sub: "Need trust before momentum" },
                          { key: "explorer", label: "Just exploring", sub: "Want a safe way to learn" },
                        ] as const
                      ).map((p) => {
                        const isSelected = persona === p.key;
                        return (
                          <button
                            key={p.key}
                            type="button"
                            onClick={() => setPersona(p.key)}
                            className={classNames(
                              "rounded-2xl border px-5 py-4 sm:px-4 sm:py-3 text-left transition",
                              isSelected
                                ? "border-sky-500/40 bg-slate-900/70"
                                : "border-slate-800/80 bg-slate-900/45 hover:border-slate-700 hover:bg-slate-900/60"
                            )}
                          >
                            <div className="text-sm font-semibold text-slate-50">
                              {p.label}
                            </div>
                            <div className="mt-1 text-xs sm:text-sm text-slate-400">
                              {p.sub}
                            </div>
                          </button>
                        );
                      })}
                    </div>

                    {persona && (
                      <div className="rounded-2xl border border-slate-800/80 bg-slate-950/35 p-4 text-sm text-slate-200">
                        {persona === "leader" && (
                          <>You want a calmer way to align people around decisions—without turning everything into a project.</>
                        )}
                        {persona === "ops" && (
                          <>You want to spot patterns early, reduce thrash, and keep work moving without noise.</>
                        )}
                        {persona === "builder" && (
                          <>You want a tool that respects constraints, keeps things legible, and doesn’t overreach.</>
                        )}
                        {persona === "risk" && (
                          <>You want trust built slowly—through boundaries and clarity, not hype.</>
                        )}
                        {persona === "explorer" && (
                          <>You want to learn at your pace—without needing to “decide” immediately.</>
                        )}
                      </div>
                    )}

                    <div className="flex flex-col sm:flex-row gap-3 sm:items-center">
                      <button
                        type="button"
                        onClick={() => unlockAndGo(4)}
                        disabled={!canAdvance}
                        className={classNames(
                          "inline-flex w-full sm:w-auto min-h-12 items-center justify-center rounded-full px-6 py-3 text-sm font-medium transition",
                          canAdvance
                            ? "bg-slate-100 text-slate-950 hover:bg-white"
                            : "bg-slate-800/60 text-slate-500 cursor-not-allowed"
                        )}
                      >
                        Offer me a safe next step
                      </button>
                      <button
                        type="button"
                        onClick={() => setActiveStage(2)}
                        className="inline-flex w-full sm:w-auto min-h-12 items-center justify-center rounded-full px-6 py-3 text-sm font-medium border border-slate-800/80 text-slate-200 hover:border-slate-700 hover:text-white transition"
                      >
                        Go back
                      </button>
                    </div>
                  </div>
                )}

                {stageKey === "invite" && (
                  <div className="grid gap-5">
                    <div>
                      <div className="text-sm sm:text-base text-slate-200">
                        Want to continue?
                      </div>
                      <div className="mt-2 text-xs sm:text-sm text-slate-400">
                        Choose what feels safe. There’s no wrong answer.
                      </div>
                    </div>

                    <div className="grid md:grid-cols-3 gap-4">
                      <Link
                        to="/explore"
                        className="rounded-3xl sm:rounded-2xl border border-slate-800/80 bg-slate-900/45 hover:bg-slate-900/60 hover:border-slate-700 transition p-6 sm:p-5"
                      >
                        <div className="text-sm font-semibold text-slate-50">Take the quiet tour</div>
                        <div className="mt-1 text-xs sm:text-sm text-slate-400">
                          Read and explore without creating an account.
                        </div>
                      </Link>
                      <Link
                        to="/subscribe"
                        className="rounded-3xl sm:rounded-2xl border border-sky-500/30 bg-gradient-to-br from-slate-900/40 via-slate-900/40 to-sky-900/20 hover:border-sky-500/45 transition p-6 sm:p-5"
                      >
                        <div className="text-sm font-semibold text-slate-50">Join early access</div>
                        <div className="mt-1 text-xs sm:text-sm text-slate-400">
                          If you want updates, opt in. If not, that’s fine.
                        </div>
                      </Link>
                      <Link
                        to="/auth/login"
                        className="rounded-3xl sm:rounded-2xl border border-slate-800/80 bg-slate-900/45 hover:bg-slate-900/60 hover:border-slate-700 transition p-6 sm:p-5"
                      >
                        <div className="text-sm font-semibold text-slate-50">I already have access</div>
                        <div className="mt-1 text-xs sm:text-sm text-slate-400">
                          Log in when you’re ready.
                        </div>
                      </Link>
                    </div>

                    <div className="flex flex-col sm:flex-row gap-3 sm:items-center">
                      <button
                        type="button"
                        onClick={() => setActiveStage(3)}
                        className="inline-flex w-full sm:w-auto min-h-12 items-center justify-center rounded-full px-6 py-3 text-sm font-medium border border-slate-800/80 text-slate-200 hover:border-slate-700 hover:text-white transition"
                      >
                        Go back
                      </button>
                    </div>
                  </div>
                )}
              </div>

              <div className="text-[11px] sm:text-xs text-slate-500">
                Tip: You can click any unlocked breadcrumb above.
              </div>
            </div>
          </section>
        </div>
      </main>

      <footer className="w-full max-w-6xl mx-auto px-4 sm:px-8 py-6 flex flex-col sm:flex-row items-center justify-between gap-2 text-[11px] sm:text-xs text-slate-500">
        <span>© {new Date().getFullYear()} CapeControl. All rights reserved.</span>
        <span>Curiosity first. Commitment later.</span>
      </footer>
    </div>
  );
};

export default LandingPage;
