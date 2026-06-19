## Problem Statement

The Planfuge frontend currently only supports a fixed light theme. Engineers and reviewers working in low-light environments — or simply preferring dark UIs — must stare at a bright white interface with no way to change it. This negatively affects comfort during extended review sessions and makes the product feel less polished compared to modern tooling.

## Solution

Add a fully themed dark mode to the React frontend. A toggle button in the header lets the user switch between light and dark themes. The chosen preference is persisted in `localStorage` and auto-detected from the operating system's `prefers-color-scheme` on first visit. All UI surfaces — backgrounds, text, cards, borders, inputs, buttons, and tables — switch seamlessly via a `data-theme` attribute and CSS custom properties, with a smooth `0.3s` transition. Plan images displayed on the canvas are left untouched (they always render as captured).

## User Stories

1. As a reviewer, I want a dark mode toggle in the header, so that I can switch to a dark theme without leaving the current plan view.
2. As a reviewer, I want my theme preference to be remembered across page reloads, so that I do not have to re-select dark mode every session.
3. As a first-time visitor, I want the app to automatically match my operating-system dark/light preference, so that the app feels native from the first load.
4. As a reviewer, I want the transition between themes to be smooth and animated, so that the switch does not feel jarring.
5. As a reviewer, I want all UI elements — sidebar, header, candidate table, modals, overlays, and inputs — to be fully styled in dark mode, so that no surface is left blindingly bright.
6. As a reviewer, I want the plan image (PDF page render) to remain visually accurate in dark mode, so that bounding box colours and page content are not distorted.
7. As a developer, I want theme state managed through a single `ThemeContext` and `useTheme` hook, so that any future component can consume the theme without prop drilling.

## Implementation Decisions

- **CSS custom properties + `data-theme` attribute**: All colour tokens are declared as CSS custom properties on `:root[data-theme="light"]` and `:root[data-theme="dark"]`. Applying or removing the `data-theme="dark"` attribute on the `<html>` element is the only runtime action needed to switch themes. No Tailwind class toggling at runtime.
- **Colour palette**: Dark theme uses Tailwind's `slate` and `zinc` scale as a reference — primary backgrounds at `slate-900`, surface cards at `slate-800`, borders at `slate-700`, and muted text at `slate-400`.
- **Smooth transition**: A global `transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease` rule is applied to all major elements so switching feels fluid.
- **ThemeContext module**: A new `ThemeContext` (React Context + Provider) exposes `{ theme, toggleTheme }`. The provider initialises by reading `localStorage`, falling back to `window.matchMedia('prefers-color-scheme: dark')`, and finally defaulting to `'light'`. It writes back to `localStorage` and updates `document.documentElement.dataset.theme` on every toggle.
- **useTheme hook**: A thin wrapper around `useContext(ThemeContext)` consumed by the toggle button component and any component that needs to conditionally adjust non-CSS behaviour (e.g. canvas background fill).
- **Toggle button component**: A `ThemeToggle` component placed in the top-right of the existing header bar renders a sun/moon icon with a pill-shaped switch. It calls `toggleTheme` on click.
- **Canvas / image area**: The plan image (`<img>` tag sourced from `/api/images/…`) is not filtered or inverted. Only the surrounding UI chrome changes.
- **No feature flag**: The feature ships directly to `main`. There is only one developer on this project.

## Testing Decisions

- A good test checks only observable behaviour from the outside — what the DOM contains and what `localStorage` holds — not how `ThemeContext` is implemented internally.
- **ThemeContext unit tests** (using Vitest + React Testing Library): verify that (a) the initial theme matches a mocked `prefers-color-scheme` media query, (b) `toggleTheme` flips the theme and writes the new value to `localStorage`, and (c) reloading the provider with an existing `localStorage` value restores the correct theme.
- **Prior art**: `sampleMode.test.ts` and `metadata.test.ts` in `client/src/` demonstrate the Vitest + TypeScript pattern already in use for pure-logic unit tests. The new context tests should follow the same file-naming convention (`themeContext.test.ts`).
- Manual smoke test: toggle in both directions, reload the page, and confirm the correct theme is restored on every major view (plan list, plan detail, upload modal).

## Out of Scope

- Per-component overrides or a third "system" option in a dropdown — the toggle is binary (light / dark).
- Dark mode for the PDF/image canvas render itself — images always show their true colours.
- Backend changes of any kind — theme is purely a client-side preference.
- Accessibility contrast audits beyond what the chosen slate/zinc palette already provides.
- Automated end-to-end tests with Cypress or Playwright for the toggle flow.

## Further Notes

- The existing `index.css` already imports Tailwind and defines a `@theme` block with colour tokens. The dark mode tokens should be added alongside those existing definitions to keep the colour system consolidated in one file.
- The `App.tsx` file is currently monolithic (~940 lines). The `ThemeContext` and `ThemeToggle` should be extracted into separate files under `client/src/` to begin reducing that monolith, even if a full refactor is out of scope for this PRD.
