# Performance — Rendering, Typography, and Accessibility

> Sources: [CSS Containment Level 2](https://www.w3.org/TR/css-contain-2/), [CSS Logical Properties Level 1](https://www.w3.org/TR/css-logical-1/), [CSS Text Level 4](https://www.w3.org/TR/css-text-4/), [MDN Web Docs: CSS](https://developer.mozilla.org/en-US/docs/Web/CSS). All features below are Baseline unless noted otherwise.

## Contents

- [`content-visibility: auto` — Skip Off-Screen Rendering](#content-visibility-auto--skip-off-screen-rendering)
- [CSS Containment — The `contain` Property](#css-containment--the-contain-property)
- [`will-change` — Compositor Hints](#will-change--compositor-hints)
- [Typography](#typography)
- [Logical Properties — Writing-Direction-Aware CSS](#logical-properties--writing-direction-aware-css)
- [Accessibility Media Queries](#accessibility-media-queries)
- [Progressive Enhancement Meta-Pattern](#progressive-enhancement-meta-pattern)
- [Modern Viewport Units](#modern-viewport-units)
- [Performance Checklist](#performance-checklist)

---

## `content-visibility: auto` — Skip Off-Screen Rendering

The single most impactful CSS performance property. When applied to off-screen sections, the browser skips layout, paint, and style computation entirely. Chrome's own documentation reports up to **7x rendering improvement** on long pages. The browser lazily renders content only when it approaches the viewport — CSS-level virtualization without JavaScript.

Use on discrete page sections that start off-screen: article cards below the fold, long lists, tab panels, accordion bodies, comment threads, footer regions.

**CRITICAL: Never apply to above-the-fold content.** The browser delays rendering of `content-visibility: auto` elements, which directly delays Largest Contentful Paint (LCP). If your hero section, primary heading, or first visible card has this property, you have made performance worse.

**Do not apply to tiny elements.** The overhead of containment tracking per element exceeds the rendering savings for small items. Apply to section-level containers, not to each individual child.

**Always measure before and after.** Use Chrome DevTools Performance panel or Lighthouse. If you cannot measure a difference, remove it.

### Required: `contain-intrinsic-size`

When the browser skips rendering, it does not know the element's height. Without a size hint, the scrollbar jumps as elements render. You **must** pair with `contain-intrinsic-size`. The `auto` keyword tells the browser to remember the actual size after first render.

```css
/* ❌ Missing size hint — scrollbar jumps, layout shifts */
.article-section {
  content-visibility: auto;
}

/* ✅ Proper implementation with size estimate */
.article-section {
  content-visibility: auto;
  contain-intrinsic-size: auto 500px;
}
```

### Pattern: Long Article Page

```css
/* Above the fold — NO content-visibility */
.hero,
.article-intro {
  /* Renders immediately */
}

/* Below-fold sections skip rendering until needed */
.article-body,
.comments-section,
.related-articles,
.site-footer {
  content-visibility: auto;
  contain-intrinsic-size: auto 800px;
}
```

Baseline. Feature-detect with `@supports (content-visibility: auto)`.

---

## CSS Containment — The `contain` Property

`contain` tells the browser that an element's internals are independent from the rest of the page. The rendering engine can skip recalculating layout, paint, or style for the entire document when something inside that element changes. `content-visibility: auto` implicitly applies containment — `contain` is the manual, granular version.

| Value | What It Isolates | Effect |
|---|---|---|
| `size` | Element's size from children | Element does not resize based on content. You must set explicit dimensions. |
| `layout` | Internal layout from external | Floats, counters, layout changes inside do not affect outside. |
| `paint` | Painting boundary | Content that overflows is clipped. No visible overflow. |
| `style` | Counter and `content` scoping | CSS counters and `quotes` do not leak out. |
| `strict` | All of the above | `size layout paint style`. Maximum isolation. |
| `content` | Layout + paint + style | Like `strict` but without `size` — element can still auto-size. |

Use `contain: content` on independent UI components — cards, widgets, modals, sidebar panels — especially inside container queries. Use `contain: strict` when you know exact dimensions (ad slots, map containers, iframes).

**Do not use `contain: size` without explicit dimensions** — the element collapses to zero. **Do not use `contain: paint` on elements that intentionally overflow** — tooltips and dropdowns will be clipped.

```css
/* ❌ Size containment without dimensions — collapses to 0x0 */
.widget {
  contain: strict;
}

/* ✅ Size containment with explicit dimensions */
.widget {
  contain: strict;
  inline-size: 300px;
  block-size: 200px;
}

/* ✅ Content containment — auto-sizes but isolates layout/paint */
.card {
  contain: content;
}
```

Container queries require containment. When you declare `container-type: inline-size`, the browser implicitly applies `contain: inline-size layout style`. No need for explicit `contain` on container query containers.

---

## `will-change` — Compositor Hints

`will-change` tells the browser which properties will animate, allowing it to create a GPU layer in advance. It is an optimization hint, not a directive. Ideally, add it dynamically just before animation starts, then remove it after — GPU layers consume memory for the entire time they exist.

**Do not apply to everything.** Every `will-change` creates a GPU compositor layer consuming video memory. A page with `* { will-change: transform; }` can cause the browser to fall back to software rendering.

**Do not use on elements that never animate.** It wastes GPU memory with zero benefit.

**Do not use as a "performance sprinkle."** If animation is janky, profile first. The cause is usually layout thrashing, not missing compositor hints.

```css
/* ❌ Wasteful — GPU layers for everything */
* {
  will-change: transform, opacity;
}

/* ✅ Targeted — only the property that animates */
.modal-overlay {
  will-change: opacity;
  transition: opacity 0.3s ease;
}

/* ✅ Dynamic via CSS — prime layer on parent hover */
.card-list:hover .card {
  will-change: transform;
}

.card:hover {
  transform: translateY(-4px);
}
```

---

## Typography

### `text-wrap: balance` — Equalized Line Lengths

Distributes text across lines so each line is approximately the same width. Eliminates the problem of headings with one or two orphaned words on the last line.

**Use only on headings and short text.** Browsers cap the balancing algorithm at 6 lines (Chrome) to 10 lines (spec). Beyond that, balancing is silently ignored. The algorithm is computationally expensive — it tries multiple line-breaking solutions.

```css
/* ❌ Applying to all text — performance-heavy, ignored on long content */
body {
  text-wrap: balance;
}

/* ✅ Headings only */
:is(h1, h2, h3, h4, h5, h6) {
  text-wrap: balance;
}
```

### `text-wrap: pretty` — Better Paragraph Rag

Adjusts line breaks to avoid orphans and improves the right-edge "rag" of left-aligned text. Designed for paragraphs and long-form content. Progressive enhancement — Firefox does not support it yet. Degrades gracefully.

```css
/* Headings balanced, body text pretty */
:is(h1, h2, h3, h4, h5, h6) {
  text-wrap: balance;
}

:is(p, li, dd, blockquote, figcaption) {
  text-wrap: pretty;
}
```

### Fluid Typography with `clamp()`

Creates font sizes that scale smoothly between a minimum and maximum, eliminating breakpoint-based jumps. Always use `rem` for min/max to respect user font-size preferences.

```css
/* ❌ Breakpoint-based — jumpy */
h1 { font-size: 1.5rem; }
@media (min-width: 768px) { h1 { font-size: 2rem; } }
@media (min-width: 1200px) { h1 { font-size: 3rem; } }

/* ✅ Fluid — smooth scaling */
h1 {
  font-size: clamp(1.5rem, 1rem + 2vw, 3rem);
}
```

#### Common Fluid Scale

```css
:root {
  --text-sm: clamp(0.875rem, 0.8rem + 0.3vw, 1rem);
  --text-base: clamp(1rem, 0.875rem + 0.5vw, 1.25rem);
  --text-2xl: clamp(1.25rem, 1rem + 1vw, 1.75rem);
  --text-3xl: clamp(1.5rem, 1rem + 2vw, 2.5rem);
  --text-4xl: clamp(2rem, 1.2rem + 3.2vw, 3.5rem);
}

body { font-size: var(--text-base); }
h1 { font-size: var(--text-4xl); }
h2 { font-size: var(--text-3xl); }
h3 { font-size: var(--text-2xl); }
```

### `text-box` — Optical Vertical Centering

`text-box` (shorthand for `text-box-trim` and `text-box-edge`) trims extra space above and below text from the font's line-height metrics. This invisible space causes text to appear off-center in buttons, badges, and tight containers.

**Not Baseline as of mid-2026:** Chrome/Edge 133+ and Safari 18.2+ support it; Firefox does not (implementation in progress). Degrades gracefully — untrimmed text just keeps its default metrics. Feature-detect with `@supports (text-box: trim-both cap alphabetic)`.

```css
/* ❌ Padding hacks to compensate for font metrics */
.badge {
  padding: 0.15em 0.5em 0.25em;
}

/* ✅ Trim to cap height and alphabetic baseline */
.badge {
  text-box: trim-both cap alphabetic;
  padding: 0.25em 0.5em;
}
```

| Value | Trims |
|---|---|
| `trim-both` | Above and below |
| `trim-start` / `trim-end` | Above only / below only |
| `cap alphabetic` | To cap height and alphabetic baseline |
| `ex alphabetic` | To x-height and alphabetic baseline |

Use on buttons, badges, pills, tags. Do not apply globally — it changes effective line-height and breaks paragraph spacing.

### Line-Height Units: `lh` and `rlh`

`lh` equals the computed `line-height` of the current element. `rlh` equals the root element's `line-height`. These keep spacing proportional to the text rhythm.

```css
p {
  margin-block-end: 1lh; /* Exactly one line of text */
}

.section-divider {
  block-size: 3rlh; /* Three root line-heights */
}

.drop-cap::first-letter {
  font-size: 3lh;
  float: inline-start;
  line-height: 1;
}
```

---

## Logical Properties — Writing-Direction-Aware CSS

Logical properties replace physical direction properties (`left`, `right`, `top`, `bottom`) with flow-relative equivalents. In LTR, `margin-inline-start` maps to `margin-left`. In RTL, it maps to `margin-right`. In vertical writing modes, the mapping rotates accordingly.

### The Rule

**Always use logical properties in new code.** No downside — identical behavior in LTR horizontal text, automatic RTL and vertical writing mode support. Physical properties are legacy.

### Full Mapping Table

| Physical | Logical |
|---|---|
| `margin-top` / `margin-bottom` | `margin-block-start` / `margin-block-end` |
| `margin-left` / `margin-right` | `margin-inline-start` / `margin-inline-end` |
| `margin-top` + `bottom` / `left` + `right` | `margin-block` / `margin-inline` |
| `padding-top` / `padding-bottom` | `padding-block-start` / `padding-block-end` |
| `padding-left` / `padding-right` | `padding-inline-start` / `padding-inline-end` |
| `padding-top` + `bottom` / `left` + `right` | `padding-block` / `padding-inline` |
| `border-top` / `border-bottom` | `border-block-start` / `border-block-end` |
| `border-left` / `border-right` | `border-inline-start` / `border-inline-end` |
| `border-top-left-radius` | `border-start-start-radius` |
| `border-top-right-radius` | `border-start-end-radius` |
| `border-bottom-left-radius` | `border-end-start-radius` |
| `border-bottom-right-radius` | `border-end-end-radius` |
| `width` / `height` | `inline-size` / `block-size` |
| `min-width` / `min-height` | `min-inline-size` / `min-block-size` |
| `max-width` / `max-height` | `max-inline-size` / `max-block-size` |
| `top` / `bottom` | `inset-block-start` / `inset-block-end` |
| `left` / `right` | `inset-inline-start` / `inset-inline-end` |
| `top` + `bottom` / `left` + `right` | `inset-block` / `inset-inline` |
| `text-align: left` / `right` | `text-align: start` / `end` |
| `float: left` / `right` | `float: inline-start` / `inline-end` |
| `clear: left` / `right` | `clear: inline-start` / `inline-end` |
| `overflow-x` / `overflow-y` | `overflow-inline` / `overflow-block` |
| `resize: horizontal` / `vertical` | `resize: inline` / `block` |

### Before/After

```css
/* ❌ Physical — breaks in RTL */
.sidebar {
  margin-left: 2rem;
  padding-right: 1rem;
  border-bottom: 1px solid oklch(0.85 0 0);
  width: 300px;
  top: 0;
  left: 0;
  text-align: left;
}

/* ✅ Logical — works in LTR, RTL, and vertical */
.sidebar {
  margin-inline-start: 2rem;
  padding-inline-end: 1rem;
  border-block-end: 1px solid oklch(0.85 0 0);
  inline-size: 300px;
  inset-block-start: 0;
  inset-inline-start: 0;
  text-align: start;
}
```

---

## Accessibility Media Queries

These media queries detect user preferences at the OS level. Respecting them is not optional — it is a core accessibility requirement.

### `prefers-reduced-motion: reduce`

The user has requested reduced motion. Affects users with vestibular disorders, motion sensitivity, or those who find animation distracting.

#### Universal Reset Pattern

Apply once, globally. Removes all animations and transitions unless explicitly overridden for essential motion (loading spinners, progress bars).

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

Why `0.01ms` instead of `0s`? Setting `0s` prevents `animationend` and `transitionend` events from firing, breaking JavaScript listeners. Near-zero fires the events while being visually instant.

```css
/* Selective override for essential animation */
@media (prefers-reduced-motion: reduce) {
  .loading-spinner {
    animation-duration: 1.5s !important;
    animation-iteration-count: infinite !important;
  }
}
```

### `prefers-contrast: more` / `less`

The user wants higher or lower contrast. `more` is the common case.

```css
@media (prefers-contrast: more) {
  :root {
    --border-color: oklch(0 0 0);
    --text-secondary: oklch(0.25 0 0);
  }

  button, input, select, textarea {
    border: 2px solid var(--border-color);
  }

  :focus-visible {
    outline-width: 3px;
  }
}
```

### `forced-colors: active` — Windows High Contrast Mode

The OS overrides all colors with a user-defined palette. Most CSS colors are ignored. Use system color keywords to work with the forced palette, not against it.

| System Color | Maps To |
|---|---|
| `CanvasText` / `Canvas` | Text / background |
| `LinkText` | Link color |
| `ButtonText` / `ButtonFace` | Button text / background |
| `Highlight` / `HighlightText` | Selection background / text |

```css
@media (forced-colors: active) {
  .btn {
    border: 2px solid ButtonText;
    background: ButtonFace;
    color: ButtonText;
  }

  .icon-status {
    forced-color-adjust: none;
    border: 2px solid currentColor;
  }

  :focus-visible {
    outline: 2px solid Highlight;
    outline-offset: 2px;
  }
}
```

### `prefers-color-scheme: light` / `dark`

Detects OS-level color scheme preference. Always pair with the `color-scheme` property — without it, browser chrome (scrollbars, form controls) stays light even when your page is dark.

```css
/* ❌ No color-scheme — browser UI stays light */
@media (prefers-color-scheme: dark) {
  body {
    background: oklch(0.15 0 0);
    color: oklch(0.9 0 0);
  }
}

/* ✅ Full dark adaptation */
:root {
  color-scheme: light dark;
}

@media (prefers-color-scheme: dark) {
  :root {
    --surface: oklch(0.15 0 0);
    --text: oklch(0.9 0 0);
  }
}
```

Use `light-dark()` for inline values without repeating media queries:

```css
:root {
  color-scheme: light dark;
  --surface: light-dark(oklch(0.98 0 0), oklch(0.15 0 0));
  --text: light-dark(oklch(0.15 0 0), oklch(0.9 0 0));
  --border: light-dark(oklch(0.85 0 0), oklch(0.3 0 0));
}
```

---

## Progressive Enhancement Meta-Pattern

Build the baseline first, then enhance with `@supports`. Users on older browsers get a functional page, not a broken one.

### Template

```css
/* Baseline — works everywhere */
.component {
  /* Functional styles */
}

/* Enhancement — better where supported */
@supports (feature: value) {
  .component {
    /* Modern feature */
  }
}
```

### Practical Examples

```css
/* Content visibility — baseline renders normally, enhancement skips off-screen */
.article-section {
  margin-block-end: 2rem;
}

@supports (content-visibility: auto) {
  .article-section:not(:first-child) {
    content-visibility: auto;
    contain-intrinsic-size: auto 600px;
  }
}

/* Text wrapping — baseline wraps normally, enhancements improve typography */
@supports (text-wrap: balance) {
  h2 { text-wrap: balance; }
}

@supports (text-wrap: pretty) {
  p { text-wrap: pretty; }
}

/* Layered enhancements — each independent */
.card {
  padding: 1rem;
  border: 1px solid oklch(0.85 0 0);
}

@supports (container-type: inline-size) {
  .card-wrapper { container-type: inline-size; }

  @container (inline-size > 400px) {
    .card { padding: 2rem; }
  }
}

@supports (text-box: trim-both cap alphabetic) {
  .card-title { text-box: trim-both cap alphabetic; }
}
```

---

## Modern Viewport Units

The traditional `vh` is ambiguous on mobile — the viewport height changes when the address bar shows or hides, causing `100vh` to overflow the visible area. Modern units resolve this.

| Unit | Name | Meaning |
|---|---|---|
| `svh` | Small viewport height | Address bar **visible** (smallest viewport) |
| `lvh` | Large viewport height | Address bar **hidden** (largest viewport) |
| `dvh` | Dynamic viewport height | Tracks **current** height as it changes |
| `svw` / `lvw` / `dvw` | Width variants | Rarely differ from `vw` |
| `dvmin` / `dvmax` | Dynamic min/max | Smaller/larger of `dvw` and `dvh` |

Use `dvh` for elements that must fill the visible viewport exactly. Use `svh` for elements that must never overflow. Use `lvh` when you want maximum space and accept brief overflow during address bar transitions.

**Do not use `dvh` with transitions on height** — `dvh` changes continuously as the address bar animates, causing jank. **Do not replace all `vh` with `dvh` blindly** — on desktop they are identical.

```css
/* ❌ Legacy — overflows on mobile */
.hero {
  height: 100vh;
}

/* ✅ Dynamic — fills visible viewport */
.hero {
  height: 100dvh;
}

/* ✅ Safe minimum — never overflows */
.full-screen-modal {
  min-height: 100svh;
}
```

### Pattern: Mobile App Shell

```css
.app-shell {
  display: grid;
  grid-template-rows: auto 1fr auto;
  block-size: 100dvh;
}

.app-header {
  position: sticky;
  inset-block-start: 0;
}

.app-content {
  overflow-y: auto;
}
```

### Fallback

```css
.hero {
  height: 100vh;   /* Fallback */
  height: 100dvh;  /* Override in supporting browsers */
}
```

---

## Performance Checklist

### Rendering
- [ ] Apply `content-visibility: auto` to below-fold sections with `contain-intrinsic-size`
- [ ] Verify `content-visibility` is NOT on above-fold content (check LCP)
- [ ] Use `contain: content` on independent component containers
- [ ] Apply `will-change` only to actively animating elements

### Typography
- [ ] Use `text-wrap: balance` on headings, not paragraphs
- [ ] Use `text-wrap: pretty` on paragraphs as progressive enhancement
- [ ] Use `clamp()` with `rem` min/max for fluid typography
- [ ] Use `text-box: trim-both cap alphabetic` for optical centering in buttons/badges

### Logical Properties
- [ ] Use logical properties in all new code
- [ ] Use `inset-block` / `inset-inline` for positioned elements
- [ ] Use `text-align: start` / `end` instead of `left` / `right`

### Accessibility
- [ ] Include `prefers-reduced-motion: reduce` universal reset
- [ ] Adapt UI for `prefers-contrast: more`
- [ ] Test with `forced-colors: active`
- [ ] Set `color-scheme: light dark` on `:root`
- [ ] Use `light-dark()` for scheme-adaptive colors

### Viewport
- [ ] Use `dvh` for mobile full-viewport layouts instead of `vh`
- [ ] Use `svh` for fixed layouts that must never overflow
- [ ] Provide `vh` fallback before `dvh` for legacy browsers
