---
name: modern-css
description: Proactively apply when creating design systems, component libraries, or any frontend application. Triggers on CSS Grid, Subgrid, Flexbox, Container Queries, :has(), @layer, @scope, CSS nesting, @property, @function, if(), oklch, color-mix, light-dark, relative color, @starting-style, scroll-driven animations, view transitions, anchor positioning, popover, customizable select, content-visibility, logical properties, text-wrap, interpolate-size, clamp, field-sizing, modern CSS, CSS architecture, responsive design, dark mode, theming, design tokens, cascade layers. Use when writing CSS for any web project, choosing layout approaches, building responsive components, implementing dark mode or theming, creating animations or transitions, styling form elements, or modernizing legacy stylesheets. Modern CSS features and best practices for building interfaces with pure native CSS.
---

# Modern CSS

Pure native CSS for building interfaces — no preprocessors, no frameworks.

## When to Use (and When NOT to)

Support statuses below are as of mid-2026. "Newly Baseline (date)" means all three engines ship it, but users on older browsers won't have it — keep graceful degradation. Verify anything critical on [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS) or [webstatus.dev](https://webstatus.dev/).

| Use Freely (Baseline) | Feature-Detect / Progressive Enhancement |
|---|---|
| CSS Grid, Subgrid, Flexbox | Scroll-driven animations (Firefox: behind flag) |
| Container queries — size; style (newly Baseline May 2026) | Scroll-state queries (Chromium-only) |
| `:has()`, `:is()`, `:where()` | `::scroll-button()`, `::scroll-marker` (Chromium-only) |
| CSS Nesting, `@layer` | Customizable `<select>` (Chromium; Safari 27 announced) |
| `@scope` (newly Baseline Dec 2025) | `@function`, `if()` (Chromium-only) |
| `@property` (typed custom props) | `sibling-index()`, `sibling-count()` (no Firefox) |
| `oklch()`, `color-mix()`, `light-dark()`, relative color | Typed `attr()` beyond `content` (Chromium-only) |
| `@starting-style`, `transition-behavior: allow-discrete` | Cross-document view transitions (no Firefox) |
| View transitions — same-document (newly Baseline Oct 2025) | `interpolate-size`, `calc-size()` (Chromium-only) |
| Anchor positioning (newly Baseline Jan 2026) | `popover="hint"`, `interestfor` (Chromium-only) |
| Popover API, `<dialog>`, invoker commands (newly Baseline Dec 2025) | `text-wrap: pretty`, `text-box` (no Firefox) |
| `field-sizing: content` (newly Baseline Jun 2026) | `reading-flow` (Chromium-only) |
| `text-wrap: balance`, `linear()` easing | `closedby` on `<dialog>` (no Safari) |
| Logical properties, `::details-content` | Grid Lanes / masonry (Safari 26.4 only; flags elsewhere) |
| | `random()` (Safari 26.2+ only), `@mixin` (no browser yet) |

## CRITICAL: The Modern Cascade

Understanding how styles resolve is the single most important concept in CSS. The additions of `@layer` and `@scope` fundamentally changed the cascade algorithm.

```
Style Resolution Order (highest priority wins):
┌─────────────────────────────────────────────────┐
│ 1. Transitions (active transition wins)         │
│ 2. !important (user-agent > user > author;      │
│    layer order INVERTS under !important)        │
│ 3. Unlayered author styles (beat ALL layers)    │
│ 4. @layer order (later layer > earlier layer)   │
│ 5. Specificity (ID > class > element)           │
│ 6. @scope proximity (closer root wins)          │
│ 7. Source order (later > earlier)               │
└─────────────────────────────────────────────────┘

Unlayered > Last layer > ... > First layer
           (utilities)        (reset)
```

Cascade layers (`@layer`) and scope proximity (`@scope`) are now more powerful than selector specificity. Define your layer order once (`@layer reset, base, components, utilities;`) and specificity wars disappear. Unlayered styles always beat layered styles — use this for overrides.

## Quick Decision Trees

### "How do I lay this out?"

```
Layout approach?
├─ 2D grid (rows + columns)         → CSS Grid
│  ├─ Children must align across    → Grid + Subgrid
│  └─ Waterfall / masonry           → display: grid-lanes (not yet cross-browser)
├─ 1D row OR column                 → Flexbox
├─ Component adapts to container    → Container Query + Grid/Flex
├─ Viewport-based responsiveness    → @media range syntax
└─ Element sized to content         → fit-content / min-content / stretch
```

### "How do I style this state?"

```
Style based on what?
├─ Child/descendant presence        → :has()
├─ Container size                   → @container (inline-size)
├─ Container custom property        → @container style()
├─ Scroll position (stuck/snapped)  → scroll-state() query
├─ Element's own custom property    → if(style(...))
├─ Browser feature support          → @supports
├─ User preference (motion/color)   → @media (prefers-*)
└─ Multiple selectors efficiently   → :is() / :where()
```

### "How do I animate this?"

```
Animation type?
├─ Enter/appear on DOM              → @starting-style + transition
├─ Exit/disappear (display:none)    → transition-behavior: allow-discrete
├─ Animate to/from auto height      → interpolate-size: allow-keywords
├─ Scroll-linked (parallax/reveal)  → animation-timeline: scroll()/view()
├─ Page/view navigation             → View Transitions API
├─ Custom easing (bounce/spring)    → linear() function
└─ Always: respect user preference  → @media (prefers-reduced-motion)
```

## What CSS Replaced JavaScript For

| JavaScript Pattern | CSS Replacement |
|---|---|
| Scroll position listeners | Scroll-driven animations |
| IntersectionObserver for reveal | `animation-timeline: view()` |
| Sticky header shadow toggle | `scroll-state(stuck: top)` |
| Floating UI / Popper.js | Anchor positioning |
| Carousel prev/next/dots | `::scroll-button()`, `::scroll-marker` |
| Auto-expanding textarea | `field-sizing: content` |
| Staggered animation delays | `sibling-index()` |
| `max-height: 9999px` hack | `interpolate-size: allow-keywords` |
| Parent element selection | `:has()` |
| Theme toggle logic | `light-dark()` + `color-scheme` |
| Tooltip/popover show/hide | Popover API + invoker commands |
| Color manipulation functions | `color-mix()`, relative color syntax |

> For non-Baseline features, always feature-detect with `@supports` or use progressive enhancement. Check [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS) or [Baseline](https://web.dev/baseline) for current browser support.

## Anti-Patterns (CRITICAL)

| Anti-Pattern | Problem | Fix |
|---|---|---|
| Overusing `!important` | Specificity arms race | Use `@layer` for cascade control |
| Deep nesting (`.a .b .c .d`) | Fragile, DOM-coupled | Flat selectors, `@scope` |
| IDs for styling (`#header`) | Too specific to override | Classes (`.header`) |
| `@media` for component layout | Viewport-coupled, not reusable | Container queries |
| JS scroll listeners for effects | Janky, expensive | Scroll-driven animations |
| JS for tooltip positioning | Floating UI dependency | Anchor positioning |
| JS for carousel controls | Fragile, a11y issues | `::scroll-button`, `::scroll-marker` |
| JS for auto-expanding textarea | Unnecessary complexity | `field-sizing: content` |
| `max-height: 9999px` for animation | Wrong duration, janky | `interpolate-size: allow-keywords` |
| `margin-left` / `padding-right` | Breaks in RTL/vertical | Logical properties (`margin-inline-start`) |
| `rgba()` with commas | Legacy syntax | `rgb(r g b / a)` space-separated |
| `appearance: none` on selects | Removes ALL functionality | `appearance: base-select` |
| Preprocessor-only variables | Can't change at runtime | CSS custom properties |
| Preprocessor-only nesting | Extra build step dependency | Native CSS nesting |
| Preprocessor color functions | Can't respond to context | `color-mix()`, relative colors |
| `text-wrap: balance` on paragraphs | Performance-heavy | Only headings/short text |
| `content-visibility` above fold | Delays LCP rendering | Only off-screen sections |
| Overusing `will-change` | Wastes GPU memory | Apply only to animating elements |

## Reference Documentation

Open the reference file BEFORE writing code in its area — each contains the sharp edges and support caveats that are easy to get wrong.

| Read this | Before doing |
|------|---------|
| [references/CASCADE.md](references/CASCADE.md) | Setting up stylesheet architecture, `@layer` ordering, `@scope`, nesting, resolving specificity conflicts |
| [references/LAYOUT.md](references/LAYOUT.md) | Any Grid/Subgrid/Flexbox layout, container queries, masonry, intrinsic sizing |
| [references/SELECTORS.md](references/SELECTORS.md) | Using `:has()`, `:is()`/`:where()`, `:focus-visible`, or modern pseudo-elements |
| [references/COLOR.md](references/COLOR.md) | Defining palettes, dark mode with `light-dark()`, `color-mix()`, relative color, OKLCH |
| [references/TOKENS.md](references/TOKENS.md) | Building design tokens, animating custom properties (`@property`), `@function`, `if()`, math functions |
| [references/ANIMATION.md](references/ANIMATION.md) | Entry/exit animations, `@starting-style`, animating to `auto`, view transitions, custom easing |
| [references/SCROLL.md](references/SCROLL.md) | Scroll-linked effects, sticky-header states, carousels — anything replacing scroll listeners |
| [references/COMPONENTS.md](references/COMPONENTS.md) | Tooltips, dropdowns, dialogs, popovers, anchor positioning, styled `<select>`, form field sizing |
| [references/PERFORMANCE.md](references/PERFORMANCE.md) | `content-visibility`, typography tuning, logical properties, accessibility media queries, viewport units |
| [references/CHEATSHEET.md](references/CHEATSHEET.md) | Quick lookups: legacy→modern upgrades, `@supports` tests, units, syntax tables |

## Sources

### Official Specifications
- [CSS Snapshot 2025](https://www.w3.org/TR/css-2025/) — W3C
- [CSS Values and Units Level 5](https://www.w3.org/TR/css-values-5/) — `if()`, `random()`, `sibling-index/count()`
- [CSS Functions and Mixins Level 1](https://www.w3.org/TR/css-mixins-1/) — `@function`, `@mixin`
- [CSS Conditional Rules Level 5](https://www.w3.org/TR/css-conditional-5/) — Scroll-state queries
- [CSS Anchor Positioning](https://www.w3.org/TR/css-anchor-position-1/)
- [CSS Overflow Level 5](https://www.w3.org/TR/css-overflow-5/) — Scroll markers/buttons

### Browser Vendor Blogs
- [CSS Wrapped 2025](https://chrome.dev/css-wrapped-2025/) — Chrome DevRel
- [Interop 2025 Review](https://webkit.org/blog/17808/interop-2025-review/) — WebKit
- [What's New in Web UI (I/O 2025)](https://developer.chrome.com/blog/new-in-web-ui-io-2025-recap)

### Support Status (check these — support claims go stale fast)
- [MDN Web Docs: CSS](https://developer.mozilla.org/en-US/docs/Web/CSS)
- [Baseline / webstatus.dev](https://webstatus.dev/)
- [Can I use](https://caniuse.com/)
