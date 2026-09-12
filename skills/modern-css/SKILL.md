---
name: modern-css
description: Implement or debug CSS layouts, responsive styles, themes, and motion. Use when choosing native CSS features or replacing legacy styling with browser-compatible CSS; not for unrelated frontend logic.
---

# Modern CSS

Choose native CSS features that fit the requested behavior and supported browsers. The user's explicit instructions take precedence over this skill's guidelines. Preserve the project's framework, preprocessor, tokens, and styling conventions unless changing them is part of the request.

## Resolve the styling problem

Use the affected markup/styles, desired appearance or interaction, and browser targets as input. Infer targets from project configuration when available. If missing support information changes the implementation, ask for it or state a conservative fallback.

Bundled support tables are dated research snapshots, not a current compatibility guarantee. Check [MDN compatibility data](https://developer.mozilla.org/en-US/docs/Web/CSS) or [Web Platform Status](https://webstatus.dev/) for the particular feature when support matters.

| Need | Starting point |
|---|---|
| Rows and columns, or aligned nested tracks | Grid / Subgrid |
| One-dimensional arrangement | Flexbox |
| Layout based on a component's available space | Container queries |
| Cascading overrides or specificity conflict | Layers, scope, selector specificity |
| Themes and derived colors | Custom properties, color functions, color-scheme |
| Motion, popovers, or scroll effects | Feature-specific reference and fallback |

## Keep the result usable

- Preserve layout and interaction in supported browsers. Use progressive enhancement or feature detection where a feature is unavailable.
- Match cascade changes to the existing origin, importance, and layer ordering; adding a layer can change precedence.
- Respect reduced-motion preferences and preserve focus/keyboard behavior when changing interactive components.
- Use modern CSS as an option, not a mandate to remove JavaScript or rebuild working controls. Support and equivalent behavior determine whether a replacement fits.
- Scope resets and stylesheet reorganization to the task; a component edit does not require a global reset.

Deliver the requested style change or explanation and verify affected layout/states when implementing. State unverified browser limitations rather than treating an example as proof of support.

## References

Load only the relevant area, using its contents to find specific features.

| Task | Reference |
|---|---|
| Layers, scope, nesting, specificity | [CASCADE.md](references/CASCADE.md) |
| Grid, Flexbox, containers, intrinsic sizing | [LAYOUT.md](references/LAYOUT.md) |
| Relational selectors, focus, pseudo-elements | [SELECTORS.md](references/SELECTORS.md) |
| Color spaces, palettes, dark mode | [COLOR.md](references/COLOR.md) |
| Custom properties, functions, design tokens | [TOKENS.md](references/TOKENS.md) |
| Transitions, keyframes, entry/exit, view transitions | [ANIMATION.md](references/ANIMATION.md) |
| Scroll timelines, sticky states, carousels | [SCROLL.md](references/SCROLL.md) |
| Dialogs, popovers, anchors, selects, field sizing | [COMPONENTS.md](references/COMPONENTS.md) |
| Rendering performance, typography, writing modes | [PERFORMANCE.md](references/PERFORMANCE.md) |
| Compact syntax or feature-detection lookup | [CHEATSHEET.md](references/CHEATSHEET.md) |
