# 🎨 Figma → React Handoff Template

**Project:** CapeWire / CapeControl  
**Maintainer:** Robert Kleyn  
**Revision:** v1.0 – 2025-11-01  

This guide standardizes how to translate finalized **Figma designs** into **React components** with accuracy and speed.  
It ensures consistent spacing, naming, and integration between UI and backend logic.

---

## 1️⃣ Figma Prep (Designer Side)

Before handing off any frame, confirm the following:

| ✅ Check | Details |
|----------|----------|
| **Frame Naming** | Matches React route (e.g., `LoginPage`, `DashboardPage`, `AgentSettingsPage`). |
| **Components Labeled** | Each reusable element named clearly (e.g., `PrimaryButton`, `CardItem`). |
| **Autolayout + Constraints** | Used correctly for responsive behavior. |
| **Text Styles Defined** | Heading, paragraph, label, etc. all consistent with Tailwind/Theme tokens. |
| **Color Styles Named** | Use global tokens (e.g., `brand-blue`, `neutral-200`, `success-green`). |
| **Interactions Linked** | Clicks and transitions defined in Prototype tab for flow preview. |
| **Developer Notes** | Add a sticky or annotation block with: API endpoint(s), props, state, or dynamic data placeholders. |

📘 *Outcome:* The frame is developer-ready and can be exported as PNG/SVG or inspected directly via Figma’s “Dev Mode.”

---

## 2️⃣ React Implementation (Developer Side)

### Folder Layout

Place each page and its components in the relevant structure:
