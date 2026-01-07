# Design JSON Exchange (Figma ↔ VS Code)

This folder is the **authoritative content exchange** surface between Figma and the repo.

## Scope (content only)

JSON in this folder is strictly **UI content**, not layout/styling.

Allowed:
- Strings (copy)
- Arrays of strings
- Arrays of objects for repeated content blocks (e.g., benefit cards)
- URLs/paths for CTA links

Not allowed:
- Colors, fonts, spacing, radii, shadows
- CSS classes or Tailwind classes
- Pixel sizes, breakpoints
- Component names or code-only concepts

## Landing schema (v1)

Each landing variant file must contain exactly these top-level keys:
- `meta` (name + version)
- `hero`
- `trustbar`
- `benefits`
- `finalCTA`

Files:
- `landing.mobile.json`
- `landing.desktop.json`

The **section order and section names** must be identical between mobile and desktop.

## Figma usage rules

- Use the JSON → Figma plugin **only inside section frames** (not at the page root).
- Import **partial JSON** (one section at a time: `hero`, `trustbar`, `benefits`, `finalCTA`).
- Rename generated frames using:
  - `<Section> — JSON scaffold`

## VS Code usage rules

- React page components import the JSON files and pass content to a template component via props.
- Keep content types in sync with the schema above.
- No backend dependencies.

## Update workflow

1. Update copy in Figma.
2. Export JSON sections into the matching file in this folder.
3. Update React if new fields are added (prefer extending the schema carefully).
