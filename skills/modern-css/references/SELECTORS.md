# Selectors — Targeting Elements Precisely

> Sources: [CSS Selectors Level 4](https://www.w3.org/TR/selectors-4/), [MDN CSS Selectors](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_selectors), [CSS Wrapped 2025](https://chrome.dev/css-wrapped-2025/). All selectors below are Baseline unless noted.

## Contents

- [`:has()` — The Parent Selector](#has--the-parent-selector)
- [`:is()` vs `:where()` — Selector List Matching](#is-vs-where--selector-list-matching)
- [`:not()` Enhanced — Complex Negation](#not-enhanced--complex-negation)
- [`:focus-visible` — Accessible Focus Styling](#focus-visible--accessible-focus-styling)
- [Scroll-Driven State: `:target` and Scroll-State Queries](#scroll-driven-state-target-and-scroll-state-queries)
- [Modern Pseudo-Elements Reference](#modern-pseudo-elements-reference)
- [Combining Modern Selectors](#combining-modern-selectors)

---

## `:has()` — The Parent Selector

The most impactful CSS selector ever added. `:has()` selects an element based on what it **contains** or what **follows** it. Before `:has()`, styling a parent based on its children required JavaScript. That era is over. Baseline in all modern browsers. The #1 most-loved CSS feature in developer surveys since its release.

`:has()` does not select the argument — it selects the element the `:has()` is attached to, if the argument matches somewhere inside (or after) it.

### Card With vs Without Image

```css
/* ❌ JavaScript approach — classList toggling */
```
```javascript
document.querySelectorAll('.card').forEach(card => {
  if (card.querySelector('img')) card.classList.add('card--has-image');
});
```
```css
/* ✅ Pure CSS — no JS, no extra classes */
.card:has(img) { grid-template-rows: 200px 1fr; }
.card:not(:has(img)) { grid-template-rows: 1fr; padding-block-start: 2rem; }
```

### Form Validation Styling

```css
/* ❌ JavaScript approach */
```
```javascript
form.addEventListener('input', () => {
  form.classList.toggle('form--error', !!form.querySelector(':invalid'));
});
```
```css
/* ✅ Pure CSS — reacts instantly, no event listeners */
form:has(:invalid) { border-color: oklch(0.65 0.25 25); }
form:has(:invalid) .submit-btn { opacity: 0.5; pointer-events: none; }
form:not(:has(:invalid)) .submit-btn { background: oklch(0.65 0.2 145); }
```

### Label Reacting to Sibling Input State

Use the adjacent sibling combinator inside `:has()` to select a label based on its neighboring input.

```css
label:has(+ input:focus) { color: oklch(0.55 0.2 260); font-weight: 700; }
label:has(+ input:placeholder-shown) { opacity: 0.6; }
label:has(+ input:not(:placeholder-shown):invalid) { color: oklch(0.65 0.25 25); }
```

### Quantity Queries

Style containers differently based on how many children they contain.

```css
/* 5+ items — compact layout */
ul:has(li:nth-child(5)) { font-size: 0.875rem; gap: 0.25rem; }

/* 10+ items — multi-column */
ul:has(li:nth-child(10)) { columns: 2; }

/* Exactly 1 item */
ul:has(> li:only-child) { list-style: none; padding: 0; }

/* 4+ cards — switch to grid */
.card-grid:has(.card:nth-child(4)) {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
}
```

### Global Page State

```css
body:has(dialog[open]) { overflow: hidden; }

/* Dark mode toggle without JS (checkbox hack + :has) */
html:has(#dark-mode-toggle:checked) { color-scheme: dark; }

.sidebar:has(nav li:nth-child(8)) { overflow-y: auto; max-block-size: 100dvh; }
```

### Feature Detection and Performance

`:has()` is Baseline, but for defensive coding: `@supports selector(:has(*)) { ... }`.

Scope `:has()` to specific elements. `.card:has(img)` is fast. `*:has(*)` is not. Avoid overly broad `:has()` in high-frequency selectors.

---

## `:is()` vs `:where()` — Selector List Matching

Both accept a forgiving selector list and match if **any** selector in the list matches. Same purpose: reducing repetition. The difference is specificity.

| Selector | Specificity | Use When |
|----------|-------------|----------|
| `:is()` | Takes the **highest** specificity in its list | Normal component styling |
| `:where()` | Always **zero** specificity | Resets, defaults, layers that should be easy to override |

```css
/* :is() — specificity of its most specific argument */
:is(#header, .nav, footer) a {
  /* Specificity: (1,0,1) — takes #header's ID specificity */
  color: oklch(0.55 0.2 260);
}

/* :where() — zero specificity regardless of arguments */
:where(#header, .nav, footer) a {
  /* Specificity: (0,0,1) — only the `a` counts */
  color: oklch(0.55 0.2 260);
}
```

### Use `:is()` for Normal Styling

```css
/* ❌ Repetitive */
header a:hover, nav a:hover, footer a:hover { text-decoration: underline; }

/* ✅ Grouped with :is() */
:is(header, nav, footer) a:hover { text-decoration: underline; }

.btn:is(:hover, :focus-visible) { background: oklch(0.5 0.2 260); }
:is(h1, h2, h3, h4):is(:first-child) { margin-block-start: 0; }
```

### Use `:where()` for Overridable Defaults

```css
/* Reset — any author style should win without specificity fights */
:where(ul, ol) { list-style: none; padding: 0; margin: 0; }
:where(a) { color: inherit; text-decoration: none; }

/* Base layer defaults */
:where(.prose) :where(h1, h2, h3) { font-weight: 700; line-height: 1.2; }

/* Override with zero effort — any class selector wins over :where() */
.custom-heading { font-weight: 400; }
```

Pairs well with `@layer`:

```css
@layer reset {
  :where(*) { margin: 0; padding: 0; box-sizing: border-box; }
}
```

### Forgiving Selector Lists

Both use **forgiving** parsing. If one selector in the list is invalid, the rest still work.

```css
/* Regular list: if :unknown-pseudo is invalid, ENTIRE rule fails */
.a, :unknown-pseudo, .b { color: red; }

/* :is() / :where(): invalid selectors skipped, .a and .b still match */
:is(.a, :unknown-pseudo, .b) { color: red; }
```

---

## `:not()` Enhanced — Complex Negation

`:not()` now accepts complex selector lists (Selectors Level 4). Previously limited to a single simple selector.

```css
/* ❌ Old: chained single :not() calls */
li:not(:first-child):not(:last-child) { border-block-start: 1px solid oklch(0.8 0 0); }

/* ✅ New: selector list in one :not() */
li:not(:first-child, :last-child) { border-block-start: 1px solid oklch(0.8 0 0); }
```

### Practical Patterns

```css
form :not([type="submit"], [type="hidden"]) { margin-block-end: 1rem; }
:not(nav, footer) > a { text-decoration: underline; }
:is(button, input, select, textarea):not(:disabled) { cursor: pointer; }
.card:not(:has(img), .featured) { background: oklch(0.97 0 0); }
```

Specificity of `:not()` is taken from its most specific argument, same as `:is()`.

---

## `:focus-visible` — Accessible Focus Styling

Use `:focus-visible` instead of `:focus` for visible focus indicators. The browser shows `:focus-visible` styles only on **keyboard** navigation (Tab, arrow keys) or assistive technology — not on mouse clicks. This is the accessibility-correct approach.

`:focus` applies on **every** focus event including clicks, causing unwanted focus rings that lead developers to remove outlines entirely — breaking keyboard accessibility.

```css
/* ❌ Anti-pattern: removing all outlines */
*:focus { outline: none; }

/* ❌ Shows focus ring on mouse click */
.btn:focus { outline: 3px solid oklch(0.55 0.2 260); }

/* ✅ Shows focus ring only on keyboard navigation */
.btn:focus-visible {
  outline: 3px solid oklch(0.55 0.2 260);
  outline-offset: 2px;
}
```

### Standard Pattern

```css
:focus { outline: none; }
:focus-visible { outline: 2px solid oklch(0.55 0.2 260); outline-offset: 2px; }
```

### Combining with Other Selectors

```css
.btn:hover { background: oklch(0.45 0.2 260); }
.btn:focus-visible { outline: 3px solid oklch(0.7 0.2 260); outline-offset: 2px; }

/* Highlight parent on keyboard focus */
.input-group:has(:focus-visible) {
  box-shadow: 0 0 0 3px oklch(0.7 0.15 260 / 0.3);
}

/* Only show ring when internal focus is from keyboard */
.dropdown:focus-within:has(:focus-visible) {
  outline: 2px solid oklch(0.55 0.2 260);
}
```

---

## Scroll-Driven State: `:target` and Scroll-State Queries

### `:target` — Fragment-Based Styling

Matches the element whose `id` matches the URL fragment (`#hash`). Use for scroll-to-section highlighting and in-page navigation.

```css
section:target {
  background: oklch(0.95 0.05 80);
  border-inline-start: 4px solid oklch(0.55 0.2 260);
}

html { scroll-behavior: smooth; }
section:target { animation: flash 1s ease-out; }

@keyframes flash {
  from { background: oklch(0.9 0.1 80); }
  to { background: transparent; }
}
```

### Scroll-State Container Queries

For true scroll-spy behavior (styling based on scroll position), use scroll-state container queries. These track stuck (sticky) and snapped (scroll-snap) states.

As with all container queries, rules inside `@container` can only style **descendants** of the container — never the container itself. Put the visual styles on an inner wrapper element. See [SCROLL.md](SCROLL.md#scroll-state-container-queries) for the full pattern.

```css
/* Stuck state — detect when sticky element is stuck.
   Styles apply to .sticky-header-inner, a child of the container. */
.sticky-header {
  position: sticky;
  top: 0;
  container-type: scroll-state;
}

@container scroll-state(stuck: top) {
  .sticky-header-inner {
    box-shadow: 0 2px 8px oklch(0 0 0 / 0.15);
    border-block-end: 1px solid oklch(0.85 0 0);
  }
}

/* Snapped state — detect when element is snapped */
.carousel-item {
  scroll-snap-align: center;
  container-type: scroll-state;
}

@container scroll-state(snapped: x) {
  .carousel-item-content { scale: 1.05; opacity: 1; }
}
```

**Support:** Chromium-only (Chrome/Edge 133+) as of mid-2026. Feature-detect: `@supports (container-type: scroll-state) { ... }`

---

## Modern Pseudo-Elements Reference

### Baseline (Use Freely)

| Pseudo-Element | What It Targets | Use When |
|---|---|---|
| `::marker` | Bullet/number of list items | Custom list styling (color, size, content) |
| `::backdrop` | Overlay behind `<dialog>` or fullscreen | Dimming/blurring behind modals |
| `::placeholder` | Placeholder text in inputs | Styling hint text (color, font, opacity) |
| `::selection` | User-highlighted text | Brand-colored text selection |
| `::details-content` | Content area of `<details>` | Animating accordions (Baseline since Sep 2025: Chrome 131+, Firefox 143+, Safari 18.4+) |

```css
/* Animate <details> open/close — no JS accordion needed */
details::details-content {
  block-size: 0;
  overflow: clip;
  interpolate-size: allow-keywords; /* Chromium-only: enables 0 → auto interpolation */
  transition: block-size 0.3s ease, content-visibility 0.3s ease allow-discrete;
}
details[open]::details-content {
  block-size: auto;
}
```

```css
li::marker { color: oklch(0.55 0.2 260); font-size: 1.2em; }
li::marker { content: '-- '; }

dialog::backdrop { background: oklch(0.15 0 0 / 0.6); backdrop-filter: blur(4px); }
input::placeholder { color: oklch(0.6 0 0); font-style: italic; }
::selection { background: oklch(0.55 0.2 260 / 0.3); color: oklch(0.2 0 0); }
```

### View Transition Pseudo-Elements (Baseline Newly Available Oct 2025)

Exist only during a same-document view transition (Baseline since Firefox 144, October 2025). Customize animation between old and new states.

| Pseudo-Element | What It Targets |
|---|---|
| `::view-transition` | Root overlay for the entire transition |
| `::view-transition-group(name)` | Container animating between old/new |
| `::view-transition-old(name)` | Snapshot of the outgoing state |
| `::view-transition-new(name)` | Snapshot of the incoming state |
| `::view-transition-image-pair(name)` | Container holding old and new snapshots |

```css
.hero-image { view-transition-name: hero; }
::view-transition-old(hero) { animation: fade-out 0.3s ease-out; }
::view-transition-new(hero) { animation: fade-in 0.3s ease-in; }
::view-transition-old(root) { animation-duration: 0.2s; }
```

### Chromium-Only / Emerging (Feature-Detect Required)

As of mid-2026 these ship only in Chromium (Safari 27 has announced customizable `<select>` support). Treat as progressive enhancement.

| Pseudo-Element | What It Targets | Replaces |
|---|---|---|
| `::picker(select)` | Dropdown of customizable `<select>` | Custom dropdown widgets |
| `::picker-icon` | Dropdown arrow on `<select>` | CSS hacks for arrow styling |
| `::checkmark` | Checkmark in `<option>` | Custom checkmark styling |
| `::selectedcontent` | Displayed selected value in `<select>` | JS-based display sync |
| `::scroll-button(*)` | Prev/next buttons for overflow containers | JS carousel controls |
| `::scroll-marker` | Individual scroll indicator (dot) | JS scroll indicator dots |
| `::scroll-marker-group` | Container for scroll markers | JS carousel dot container |

```css
/* Native carousel controls */
.carousel { overflow-x: auto; scroll-snap-type: x mandatory; }
.carousel::scroll-button(inline-start) { content: '<'; }
.carousel::scroll-button(inline-end) { content: '>'; }

.carousel::scroll-marker-group {
  display: flex; gap: 0.5rem; justify-content: center; padding-block: 0.5rem;
}
.carousel > *::scroll-marker {
  content: ''; inline-size: 12px; block-size: 12px;
  border-radius: 50%; background: oklch(0.75 0 0);
}
.carousel > *::scroll-marker:target-current { background: oklch(0.45 0.2 260); }
```

### Customizable `<select>` Pseudo-Elements

Opt in with `appearance: base-select`, then style sub-parts:

```css
select { appearance: base-select; }
select::picker(select) {
  background: oklch(0.98 0 0); border: 1px solid oklch(0.8 0 0);
  border-radius: 0.5rem; padding: 0.25rem;
}
select::picker-icon { transition: rotate 0.2s; }
select:open::picker-icon { rotate: 180deg; }
option::checkmark { color: oklch(0.55 0.2 145); }
selectedcontent { font-weight: 600; }
```

---

## Combining Modern Selectors

The real power emerges from combining selectors. Each example replaces JavaScript.

```css
/* Auto-hide sections with no content beyond a heading */
section:not(:has(*:not(h2))) { display: none; }

/* Dim inactive nav items when one is active */
nav:has(.active) :is(a, button):not(.active) { opacity: 0.6; }

/* Highlight fieldset on keyboard focus */
fieldset:has(:is(input, select, textarea):focus-visible) {
  background: oklch(0.97 0.02 260);
}

/* Grid columns based on item count */
.grid:has(:nth-child(7)) { grid-template-columns: repeat(3, 1fr); }
.grid:not(:has(:nth-child(4))) {
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
}

/* Skip-link visible only on keyboard focus */
.skip-link:focus-visible {
  position: fixed; inset-block-start: 1rem; inset-inline-start: 1rem; z-index: 9999;
}
```

> For non-Baseline features, always feature-detect with `@supports` or use progressive enhancement. Check [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS) or [Baseline](https://web.dev/baseline) for current browser support.
