import React from "react";

export type LandingContent = {
  meta: {
    name: string;
    version: number;
  };
  hero: {
    eyebrow: string;
    headline: string;
    subhead: string;
    primaryCta: {
      label: string;
      href: string;
    };
    secondaryCta?: {
      label: string;
      href: string;
    };
  };
  trustbar: {
    items: string[];
  };
  benefits: {
    headline: string;
    items: Array<{
      title: string;
      description: string;
    }>;
  };
  finalCTA: {
    headline: string;
    subhead: string;
    primaryCta: {
      label: string;
      href: string;
    };
  };
};

export function LandingTemplate({ content }: { content: LandingContent }) {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-50">
      <header className="w-full max-w-6xl mx-auto px-4 sm:px-8 py-6 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-2xl bg-gradient-to-tr from-pink-500 via-purple-500 to-sky-500 flex items-center justify-center text-xs font-bold">
            CC
          </div>
          <span className="font-semibold tracking-tight">CapeControl</span>
        </div>
        <span className="text-[11px] sm:text-xs text-slate-400">{content.meta.name}</span>
      </header>

      <main className="w-full max-w-6xl mx-auto px-4 sm:px-8 py-10 md:py-16">
        {/* Hero */}
        <section className="mb-12">
          <p className="text-[11px] sm:text-xs font-semibold tracking-[0.25em] text-sky-400 uppercase mb-4">
            {content.hero.eyebrow}
          </p>
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-semibold tracking-tight mb-5">
            {content.hero.headline}
          </h1>
          <p className="text-sm sm:text-base text-slate-300 mb-8">{content.hero.subhead}</p>

          <div className="flex flex-col sm:flex-row gap-3 sm:items-center">
            <a
              href={content.hero.primaryCta.href}
              className="inline-flex items-center justify-center rounded-full px-6 py-3 text-sm font-medium bg-gradient-to-r from-fuchsia-500 via-purple-500 to-sky-500 shadow-lg shadow-purple-500/30 hover:shadow-purple-500/50 transition"
            >
              {content.hero.primaryCta.label}
            </a>
            {content.hero.secondaryCta && (
              <a
                href={content.hero.secondaryCta.href}
                className="inline-flex items-center gap-1 text-sm font-medium text-sky-400 hover:text-sky-300"
              >
                <span>{content.hero.secondaryCta.label}</span>
                <span aria-hidden="true">→</span>
              </a>
            )}
          </div>
        </section>

        {/* Trustbar */}
        <section className="mb-12">
          <div className="flex flex-wrap gap-x-6 gap-y-2 text-[11px] sm:text-xs text-slate-400">
            {content.trustbar.items.map((item) => (
              <span key={item}>{item}</span>
            ))}
          </div>
        </section>

        {/* Benefits */}
        <section className="mb-12">
          <h2 className="text-xl sm:text-2xl font-semibold tracking-tight mb-6">
            {content.benefits.headline}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {content.benefits.items.map((benefit) => (
              <div
                key={benefit.title}
                className="rounded-3xl border border-slate-800/80 bg-slate-900/70 backdrop-blur-sm p-6"
              >
                <h3 className="font-semibold mb-2">{benefit.title}</h3>
                <p className="text-sm text-slate-300">{benefit.description}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Final CTA */}
        <section className="rounded-3xl border border-slate-800/80 bg-slate-900/70 backdrop-blur-sm p-6 sm:p-8">
          <h2 className="text-xl sm:text-2xl font-semibold tracking-tight mb-2">
            {content.finalCTA.headline}
          </h2>
          <p className="text-sm sm:text-base text-slate-300 mb-6">{content.finalCTA.subhead}</p>
          <a
            href={content.finalCTA.primaryCta.href}
            className="inline-flex items-center justify-center rounded-full px-6 py-3 text-sm font-medium bg-gradient-to-r from-fuchsia-500 via-purple-500 to-sky-500 shadow-lg shadow-purple-500/30 hover:shadow-purple-500/50 transition"
          >
            {content.finalCTA.primaryCta.label}
          </a>
        </section>
      </main>

      <footer className="w-full max-w-6xl mx-auto px-4 sm:px-8 py-6 text-[11px] sm:text-xs text-slate-500">
        <span>© {new Date().getFullYear()} CapeControl. All rights reserved.</span>
      </footer>
    </div>
  );
}
