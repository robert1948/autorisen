export type DocMeta = {
  slug: string;
  title: string;
  file: string;
  load: () => Promise<string>;
};

export const DOCS_TRAIL: DocMeta[] = [
  {
    slug: "start-here",
    title: "Start here",
    file: "00-start-here.md",
    load: async () => (await import("./00-start-here.md?raw")).default,
  },
  {
    slug: "curiosity-trail",
    title: "The Curiosity Trail",
    file: "01-curiosity-trail.md",
    load: async () => (await import("./01-curiosity-trail.md?raw")).default,
  },
  {
    slug: "trust-and-safety",
    title: "Trust & safety",
    file: "02-trust-and-safety.md",
    load: async () => (await import("./02-trust-and-safety.md?raw")).default,
  },
  {
    slug: "agents-101",
    title: "Agents, simply explained",
    file: "03-agents-101.md",
    load: async () => (await import("./03-agents-101.md?raw")).default,
  },
  {
    slug: "marketplace-preview",
    title: "The marketplace (preview)",
    file: "04-marketplace-preview.md",
    load: async () => (await import("./04-marketplace-preview.md?raw")).default,
  },
  {
    slug: "roadmap",
    title: "What’s coming (and what isn’t)",
    file: "05-roadmap.md",
    load: async () => (await import("./05-roadmap.md?raw")).default,
  },
];

export function getDocBySlug(slug: string | undefined) {
  if (!slug) return undefined;
  return DOCS_TRAIL.find((d) => d.slug === slug);
}

export function getPrevNext(slug: string | undefined) {
  if (!slug) return { prev: undefined, next: undefined };
  const index = DOCS_TRAIL.findIndex((d) => d.slug === slug);
  if (index < 0) return { prev: undefined, next: undefined };
  return {
    prev: DOCS_TRAIL[index - 1],
    next: DOCS_TRAIL[index + 1],
  };
}
