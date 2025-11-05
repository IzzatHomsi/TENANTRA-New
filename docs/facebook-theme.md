# Tenantra Frontend — Facebook-Inspired Theme Reference

This document captures the design tokens and layout patterns that drive the Facebook-style experience introduced across the Tenantra UI. Use these references when extending the interface or building new components so the look & feel stays cohesive.

## Color System

| Token | HEX | Usage |
| --- | --- | --- |
| `--tena-primary` | `#1877F2` | Brand actions, header background, active navigation |
| `--tena-secondary` | `#42B72A` | Success affordances, secondary call-to-action |
| `--tena-neutral` | `#F0F2F5` | App background, large surface areas |
| `--tena-surface` | `#FFFFFF` (light) / `#242526` (dark) | Cards, modals, panels |
| `--tena-text` | `#101828` (light) / `#E5E7EB` (dark) | Primary copy |
| `--tena-muted` | `#667085` (light) / `#CBD5E1` (dark) | Secondary text, helper copy |
| `--tena-border` | `#E5E7EB` (light) / `#374151` (dark) | Dividers, control borders |

Tailwind color aliases (`bg-facebook-gray`, `text-facebook-blue`, etc.) map directly to these CSS variables so utility classes and bespoke components stay in sync.

### Elevation & Effects

- Cards and panels use a soft drop shadow (`0 1px 2px rgba(0,0,0,0.08), 0 4px 12px rgba(0,0,0,0.06)`).
- Hover states subtly raise the card (`transform: translateY(-1px)`) to mimic Facebook’s motion.
- Outline buttons use an inset border highlight (`rgba(24,119,242,0.2)`) and a translucent hover fill.

## Typography

- **Font stack**: `-apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, "Noto Sans", Roboto, "Segoe UI", sans-serif`
- **Headers**: `font-weight: 700` / uppercase eyebrow for section titles
- **Body copy**: `font-size: 0.875rem – 1rem`, color `var(--tena-text)`
- **Muted text**: `var(--tena-muted)` for helper/secondary lines
- **Button text**: `font-size: 0.875rem`, `font-weight: 600`, letter spacing normal

## Spacing Scale

The layout relies on an 8 px rhythm exposed as CSS custom properties:

| Token | px |
| --- | --- |
| `--space-1` | 4 |
| `--space-2` | 8 |
| `--space-3` | 12 |
| `--space-4` | 16 |
| `--space-5` | 20 |
| `--space-6` | 24 |
| `--space-7` | 32 |
| `--space-8` | 40 |

Use these for padding/margins on custom layouts to match the sidebar/content rhythm.

## Core Layout Patterns

### Header

- `fb-header` provides a Facebook-style top bar: brand blue background, white icons, rounded search field, pill-shaped logout button.
- Height: 56 px, horizontal padding uses `--space-4`.
- Tenancy selector and user avatar sit on the right cluster.

### Sidebar

- `sidebar` class delivers a dark slate background (`#0F172A`) with light text.
- Active navigation items receive the primary blue background and white text, echoing Facebook’s active tab treatment.
- Sections are grouped with uppercase labels (`tracking-wide`, muted color).

### Card

- `.card` + `.shadow-soft` define rounded, elevated surfaces.
- Padding defaults to `1rem` (`p-4`), override via the `padded` prop on the shared `<Card />` component when building complex layouts.

### Buttons

| Variant | Class | Description |
| --- | --- | --- |
| Primary | `btn-primary` | Solid brand fill, white text, Facebook CTA styling |
| Ghost | `btn-ghost` | Transparent background, subtle border for tertiary actions |
| Outline | `btn-outline` | Facebook outline button – transparent background with blue border & hover tint |
| Danger | `danger` (legacy) | High-contrast destructive action (`bg-red-600`) |

The reusable Button component now supports polymorphic `as` rendering so links and router navigation inherit exact button styling.

## Iconography

SVG glyphs live in `components/ui/Icon.jsx`. The current set covers dashboard metrics (clock, shield, bolt, graph, search, user). Extend this module with 24×24 line icons converted to path data when new status cards are introduced.

## Usage Checklist

- Import `./styles/theme.css` in any entry point (`src/main.jsx`) to ensure CSS variables are registered.
- Prefer the shared UI primitives in `components/ui/` (Button, Card, Input, Table) to keep typography and padding consistent.
- When introducing a new hero CTA or navigation item, verify the color contrast using `var(--tena-primary)` against the white/dark backgrounds to meet WCAG AA (contrast ratio ≥ 4.5:1).
- For dark mode testing, toggle the root `.dark` class or set local storage key `tenat_theme` to `dark` to confirm background/text tokens invert correctly.

## Layout Sketches

While no static mockups are checked in, follow these structural guidelines:

1. **Viewport width ≤ 1024 px**: collapse the sidebar behind the hamburger button, keep header fixed and search input hidden (existing `Shell.jsx` behavior).
2. **Dashboard metrics**: arrange primary KPIs in a three-card grid (`grid-cols-1 sm:grid-cols-2 lg:grid-cols-3`) with hero icon chips aligned left.
3. **Forms**: wrap fields in `space-y-6`, align labels with `text-sm font-medium` and primary buttons at the bottom (`btn-primary`, full width when mobile).

Align future design decisions with this document so the Facebook-inspired theme remains cohesive across modules.
