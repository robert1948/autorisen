import { useEffect, useMemo, useState } from "react";
import ReactMarkdown from "react-markdown";
import { Link, Navigate, useParams } from "react-router-dom";

import { DOCS_TRAIL, getDocBySlug, getPrevNext } from "../../content/docs";

function TrailLink({ slug, title, isActive }: { slug: string; title: string; isActive: boolean }) {
  return (
    <Link
      to={`/docs/${slug}`}
      className={
        "block rounded-xl border px-4 py-3 text-sm transition " +
        (isActive
          ? "border-sky-500/40 bg-slate-900/70 text-slate-50"
          : "border-slate-800/80 bg-slate-900/35 text-slate-200 hover:bg-slate-900/55")
      }
    >
      {title}
    </Link>
  );
}

export default function DocReaderPage() {
  const { slug } = useParams();

  const doc = useMemo(() => getDocBySlug(slug), [slug]);
  const { prev, next } = useMemo(() => getPrevNext(slug), [slug]);

  const [markdown, setMarkdown] = useState<string>("");
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  useEffect(() => {
    setIsMenuOpen(false);
  }, [slug]);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      if (!doc) return;
      const md = await doc.load();
      if (!cancelled) setMarkdown(md);
    }

    setMarkdown("");
    load();

    return () => {
      cancelled = true;
    };
  }, [doc]);

  if (!slug) return <Navigate to="/docs/start-here" replace />;

  if (!doc) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100">
        <div className="mx-auto max-w-5xl px-6 py-16">
          <div className="rounded-3xl border border-slate-800/80 bg-slate-900/40 p-8">
            <div className="text-lg font-semibold">Not found</div>
            <p className="mt-2 text-sm text-slate-300">
              That page doesn’t exist. Try the start page.
            </p>
            <div className="mt-6">
              <Link
                to="/docs/start-here"
                className="inline-flex rounded-xl border border-slate-700 px-4 py-2 text-sm text-slate-200 hover:bg-slate-900"
              >
                Go to Start here
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 py-10">
        <div className="mb-6 flex items-center justify-between gap-4">
          <Link to="/" className="text-sm text-slate-300 hover:text-white transition">
            Home
          </Link>

          <button
            type="button"
            className="lg:hidden inline-flex min-h-11 items-center justify-center rounded-xl border border-slate-800/80 bg-slate-900/40 px-4 text-sm text-slate-200 hover:bg-slate-900/55 transition"
            onClick={() => setIsMenuOpen((v) => !v)}
            aria-expanded={isMenuOpen}
            aria-label={isMenuOpen ? "Close Docs Trail" : "Open Docs Trail"}
          >
            Docs Trail
          </button>
        </div>

        <div className="grid gap-6 lg:grid-cols-[280px_1fr]">
          {/* Desktop sidebar */}
          <aside className="hidden lg:block">
            <div className="sticky top-8 rounded-3xl border border-slate-800/80 bg-slate-900/30 p-4">
              <div className="px-2 pb-3 text-xs font-semibold tracking-[0.22em] text-slate-400 uppercase">
                Docs Trail
              </div>
              <div className="grid gap-2">
                {DOCS_TRAIL.map((d) => (
                  <TrailLink key={d.slug} slug={d.slug} title={d.title} isActive={d.slug === slug} />
                ))}
              </div>
            </div>
          </aside>

          {/* Mobile collapsible list */}
          {isMenuOpen && (
            <div className="lg:hidden fixed inset-0 z-50">
              <button
                type="button"
                className="absolute inset-0 bg-slate-950/75 backdrop-blur-sm"
                aria-label="Close Docs Trail"
                onClick={() => setIsMenuOpen(false)}
              />
              <div className="absolute left-4 right-4 top-24 rounded-3xl border border-slate-800/80 bg-slate-950/90 p-4">
                <div className="flex items-center justify-between">
                  <div className="text-sm font-semibold">Docs Trail</div>
                  <button
                    type="button"
                    className="inline-flex h-11 w-11 items-center justify-center rounded-xl border border-slate-800/80 bg-slate-900/40 hover:bg-slate-900/55 transition"
                    aria-label="Close"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    <span className="text-xl leading-none">×</span>
                  </button>
                </div>
                <div className="mt-4 grid gap-2">
                  {DOCS_TRAIL.map((d) => (
                    <TrailLink key={d.slug} slug={d.slug} title={d.title} isActive={d.slug === slug} />
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Content */}
          <main>
            <div className="rounded-3xl border border-slate-800/80 bg-slate-900/40 p-6 sm:p-8">
              <article className="prose prose-invert prose-slate max-w-none">
                <ReactMarkdown>{markdown}</ReactMarkdown>
              </article>

              <div className="mt-10 flex items-center justify-between gap-3">
                {prev ? (
                  <Link
                    to={`/docs/${prev.slug}`}
                    className="inline-flex rounded-xl border border-slate-800 px-4 py-2 text-sm text-slate-200 hover:bg-slate-900 transition"
                  >
                    ← {prev.title}
                  </Link>
                ) : (
                  <span />
                )}

                {next ? (
                  <Link
                    to={`/docs/${next.slug}`}
                    className="inline-flex rounded-xl border border-slate-800 px-4 py-2 text-sm text-slate-200 hover:bg-slate-900 transition"
                  >
                    {next.title} →
                  </Link>
                ) : (
                  <span />
                )}
              </div>
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}
