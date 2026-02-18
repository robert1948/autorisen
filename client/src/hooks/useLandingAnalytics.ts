/**
 * Landing page analytics hook.
 *
 * Automatically tracks:
 *  - CTA button clicks via `data-analytics-cta` attributes
 *  - Section visibility via `data-analytics-section` attributes (IntersectionObserver)
 *  - Block visibility via `data-analytics-block` attributes
 *
 * All events are forwarded to the server-side analytics endpoint through
 * `trackAnalyticsEvent` from `authApi`.
 *
 * Usage: call `useLandingAnalytics()` once inside the landing page component.
 */

import { useEffect, useRef } from "react";
import { trackAnalyticsEvent } from "../lib/authApi";

const SEEN_SECTIONS = new Set<string>();

function trackCta(ctaName: string) {
  trackAnalyticsEvent({
    event_type: "landing_cta_click",
    step: ctaName,
    details: {
      page: "landing",
      url: window.location.href,
      timestamp: new Date().toISOString(),
    },
  });
}

function trackSectionView(sectionName: string) {
  if (SEEN_SECTIONS.has(sectionName)) return;
  SEEN_SECTIONS.add(sectionName);

  trackAnalyticsEvent({
    event_type: "landing_section_view",
    step: sectionName,
    details: {
      page: "landing",
      url: window.location.href,
      timestamp: new Date().toISOString(),
    },
  });
}

/**
 * Attach click listeners to all `[data-analytics-cta]` elements and
 * IntersectionObservers to all `[data-analytics-section]` and
 * `[data-analytics-block]` elements.
 */
export function useLandingAnalytics() {
  const observerRef = useRef<IntersectionObserver | null>(null);

  useEffect(() => {
    // ── CTA click tracking ──
    const handleClick = (e: MouseEvent) => {
      const target = (e.target as HTMLElement).closest<HTMLElement>(
        "[data-analytics-cta]",
      );
      if (target) {
        const ctaName = target.getAttribute("data-analytics-cta");
        if (ctaName) trackCta(ctaName);
      }
    };

    document.addEventListener("click", handleClick, { passive: true });

    // ── Section / block visibility tracking ──
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (!entry.isIntersecting) continue;
          const el = entry.target as HTMLElement;
          const section =
            el.getAttribute("data-analytics-section") ??
            el.getAttribute("data-analytics-block");
          if (section) trackSectionView(section);
        }
      },
      { threshold: 0.35 },
    );
    observerRef.current = observer;

    const targets = document.querySelectorAll(
      "[data-analytics-section], [data-analytics-block]",
    );
    targets.forEach((el) => observer.observe(el));

    return () => {
      document.removeEventListener("click", handleClick);
      observer.disconnect();
    };
  }, []);
}
