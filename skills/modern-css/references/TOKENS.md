# Tokens — Design System Primitives and CSS Logic

> Sources: [CSS Custom Properties for Cascading Variables Level 2](https://www.w3.org/TR/css-variables-1/), [CSS Properties and Values API (`@property`)](https://www.w3.org/TR/css-properties-values-api-1/), [CSS Values and Units Level 5 (`if()`, `sibling-index()`, `attr()`)](https://www.w3.org/TR/css-values-5/), [CSS Functions and Mixins Level 1 (`@function`)](https://www.w3.org/TR/css-mixins-1/), [CSS Values and Units Level 4 (math functions)](https://www.w3.org/TR/css-values-4/).

This reference covers the primitives that power design systems in pure CSS: custom properties, typed registration, custom functions, conditional values, math, positional functions, and typed attribute access. Every section explains WHEN and WHY to reach for each feature.

Custom properties, `@property`, and all math functions are Baseline. `@function`, `if()`, `sibling-index()`/`sibling-count()`, and typed `attr()` are NOT Baseline as of mid-2026 — each section notes current support.

## Contents

- [Custom Properties (`--*`)](#custom-properties---)
- [`@property` — Typed Custom Properties](#property--typed-custom-properties)
- [`@function` — Custom CSS Functions](#function--custom-css-functions)
- [`if()` — Conditional Values](#if--conditional-values)
- [CSS Math Functions](#css-math-functions)
- [`sibling-index()` / `sibling-count()`](#sibling-index--sibling-count)
- [Typed `attr()`](#typed-attr)
- [Token Architecture Pattern](#token-architecture-pattern)

---

## Custom Properties (`--*`)

Custom properties are the foundational design token mechanism. They cascade, inherit, respond to media queries, and JavaScript can read and write them at runtime. Use them for every design token: colors, spacing, typography scales, component variants, animation parameters.

### Scoping — Any Selector, Not Just `:root`

Scope properties to the narrowest context that makes sense.

```css
/* ❌ Everything on :root — flat, no encapsulation */
:root {
  --card-padding: 1.5rem;
  --card-bg: #fff;
  --button-padding: 0.5rem 1rem;
  --button-bg: blue;
}

/* ✅ Scoped to the component that uses them */
.card {
  --_padding: 1.5rem;
  --_bg: #fff;
  padding: var(--_padding);
  background: var(--_bg);
}
```

Convention: prefix private/internal properties with `--_`. Public properties (the ones consumers override) use the component name: `--card-bg`.

### Cascade and Theming

Properties set on a parent are inherited by all descendants unless overridden. This is how theming works — override semantic tokens in a context, and all components within adapt.

```css
:root {
  --color-primary: oklch(0.6 0.2 260);
  --color-surface: oklch(0.98 0 0);
  --space-md: 1rem;
}

.dark-section {
  --color-primary: oklch(0.8 0.15 260);
  --color-surface: oklch(0.15 0 0);
}

/* Component uses tokens without knowing the theme */
.card {
  background: var(--color-surface);
  padding: var(--space-md);
}
```

### Fallback Values

`var()` accepts a fallback as the second argument. Used only when the property is not set (guaranteed invalid) — not when set to an invalid value.

```css
.element {
  color: var(--text-color, black);
  padding: var(--component-padding, var(--space-md, 1rem));
  width: var(--custom-width, calc(100% - 2rem));
}
```

### Component Variants

Define the public API of a component with custom properties. Consumers change the properties, not the internals.

```css
.button {
  --button-bg: var(--color-primary);
  --button-color: white;
  --button-size: var(--space-md);

  background: var(--button-bg);
  color: var(--button-color);
  padding: var(--button-size) calc(var(--button-size) * 2);
}

.button.danger { --button-bg: var(--color-danger); }
.button.ghost  { --button-bg: transparent; --button-color: var(--color-primary); }
.button.small  { --button-size: var(--space-sm); }
```

### Runtime Manipulation via JavaScript

```javascript
const root = document.documentElement;

// Read
getComputedStyle(root).getPropertyValue('--color-primary').trim();

// Write (affects all descendants)
root.style.setProperty('--color-primary', 'oklch(0.7 0.25 300)');

// Scoped override
card.style.setProperty('--card-bg', 'oklch(0.95 0.02 200)');

// Remove override (revert to inherited)
card.style.removeProperty('--card-bg');

// Dynamic values (mouse position, scroll, etc.)
document.addEventListener('pointermove', (e) => {
  root.style.setProperty('--mouse-x', `${e.clientX}px`);
  root.style.setProperty('--mouse-y', `${e.clientY}px`);
});
```

---

## `@property` — Typed Custom Properties

Unregistered custom properties are strings. The browser cannot interpolate them during transitions — values snap instantly. Register with `@property` to give a type, initial value, and inheritance behavior.

### WHEN to Use

1. **Animate a custom property** — the primary use case. Without registration, `--hue: 0` to `--hue: 360` snaps. With `syntax: "<number>"`, it interpolates smoothly.
2. **Enforce a type** — prevent invalid values from propagating silently.
3. **Set a guaranteed initial value** — applies even when no ancestor sets the property.
4. **Control inheritance** — `inherits: false` prevents a token from leaking into children.

### Syntax

```css
@property --hue {
  syntax: "<number>";
  inherits: false;
  initial-value: 0;
}

.element {
  --hue: 0;
  background: oklch(0.7 0.2 var(--hue));
  transition: --hue 0.5s ease;
}
.element:hover { --hue: 120; }
```

### Supported Syntax Types

| Syntax | Accepts | Example initial-value |
|---|---|---|
| `<color>` | Any CSS color | `oklch(0.5 0.2 260)` |
| `<length>` | Length with units | `0px` |
| `<number>` | Unitless number | `0` |
| `<percentage>` | Percentage value | `0%` |
| `<length-percentage>` | Length or percentage | `0px` |
| `<angle>` | Angle value | `0deg` |
| `<time>` | Time value | `0s` |
| `<integer>` | Whole number | `0` |
| `<resolution>` | Resolution value | `1dppx` |
| `<transform-function>` | Single transform | `rotate(0deg)` |
| `<transform-list>` | Multiple transforms | `rotate(0deg) scale(1)` |
| `<custom-ident>` | Custom identifier | `none` |
| `<image>` | Image value | n/a (cannot set initial-value) |
| `<url>` | URL value | n/a (cannot set initial-value) |
| `*` | Any value (universal) | (no animation benefit) |

Combine with `|` for union types: `syntax: "<length> | <percentage>"`. Append `+` for space-separated lists: `syntax: "<length>+"`. Append `#` for comma-separated lists: `syntax: "<color>#"`.

### Limitation: `initial-value` Must Be Computationally Independent

The initial value cannot use relative units or depend on context.

```css
/* ❌ REJECTED — relative units depend on context */
@property --spacing {
  syntax: "<length>";
  inherits: false;
  initial-value: 2em;      /* depends on font-size */
}

/* ✅ Valid — absolute units only */
@property --spacing {
  syntax: "<length>";
  inherits: false;
  initial-value: 16px;
}
```

### Animating Gradients (Classic Use Case)

Gradients cannot be animated directly. Register the individual values and animate those.

```css
@property --gradient-angle {
  syntax: "<angle>";
  inherits: false;
  initial-value: 0deg;
}

@property --gradient-color {
  syntax: "<color>";
  inherits: false;
  initial-value: oklch(0.6 0.25 260);
}

.gradient-bg {
  background: linear-gradient(var(--gradient-angle), var(--gradient-color), transparent);
  transition: --gradient-angle 1s ease, --gradient-color 0.5s ease;
}
.gradient-bg:hover {
  --gradient-angle: 180deg;
  --gradient-color: oklch(0.8 0.15 140);
}
```

### Non-Inheriting Properties for Component Isolation

```css
@property --variant {
  syntax: "<custom-ident>";
  inherits: false;
  initial-value: default;
}

.alert { --variant: warning; }
.alert .button {
  /* --variant is "default" here, not "warning" — isolation works */
}
```

---

## `@function` — Custom CSS Functions

> **Chromium-only (Chrome/Edge 139+) as of mid-2026. Not Baseline.** Unsupported browsers ignore the `@function` rule AND any declaration calling a `--fn()` — so always provide a fallback declaration before the one using the function.

Define reusable computations that return a value. They accept parameters, support defaults, and are cascade-aware (last definition in the same layer wins).

### WHEN to Use

Use when a computation is used in multiple places and needs to stay consistent: fluid typography, spacing scales, opacity variants, contrast-aware colors.

### Basic Syntax

```css
@function --double(--value) {
  result: calc(var(--value) * 2);
}

.element {
  padding: --double(1rem);   /* 2rem */
  gap: --double(0.5rem);     /* 1rem */
}
```

### Parameters with Types and Defaults

```css
@function --fluid-size(
  --min type(<length>),
  --max type(<length>),
  --min-vw type(<length>): 20rem,
  --max-vw type(<length>): 80rem
) {
  result: clamp(
    var(--min),
    var(--min) + (var(--max) - var(--min)) *
      (100vw - var(--min-vw)) / (var(--max-vw) - var(--min-vw)),
    var(--max)
  );
}

h1 { font-size: --fluid-size(1.5rem, 3rem); }
h2 { font-size: --fluid-size(1.25rem, 2rem); }
```

### Opacity Helper

```css
@function --opacity(--color type(<color>), --alpha type(<percentage>): 100%) {
  result: color-mix(in oklch, var(--color) var(--alpha), transparent);
}

.overlay { background: --opacity(var(--color-primary), 50%); }
.subtle-border { border: 1px solid --opacity(var(--color-text), 20%); }
```

### Conditional Logic Inside Functions

Functions can contain `@media` and other at-rules.

```css
@function --theme-value(--light type(<color>), --dark type(<color>)) {
  result: var(--light);

  @media (prefers-color-scheme: dark) {
    result: var(--dark);
  }
}

.card {
  background: --theme-value(#ffffff, #1a1a2e);
  color: --theme-value(#1a1a2e, #e0e0e0);
}
```

### Cascade Awareness

Override a function in a later layer or later in the source.

```css
@layer base {
  @function --spacing(--n type(<number>)) {
    result: calc(var(--n) * 0.25rem);    /* 4px base */
  }
}

@layer theme {
  @function --spacing(--n type(<number>)) {
    result: calc(var(--n) * 0.5rem);     /* 8px base — overrides */
  }
}

.element { padding: --spacing(4); }  /* 2rem (uses theme layer) */
```

---

## `if()` — Conditional Values

> **Chromium-only (Chrome/Edge 137+) as of mid-2026. Not Baseline.** Feature-detect against a real property, e.g. `@supports (color: if(style(--x): red; blue))`. Do NOT test with a custom property (`@supports (--x: if(...))`) — custom properties accept any value, so that test is always true.

Evaluates conditions inline and returns the matching value. Reduces the need for multiple `@media` or `@container` blocks when varying a single property.

### Condition Types

| Condition | Tests | Example |
|---|---|---|
| `media()` | Media query | `media(width >= 768px)` |
| `supports()` | Feature support | `supports(display: grid)` |
| `style()` | Custom property value | `style(--variant: compact)` |

### CRITICAL: `style()` Checks the SAME Element

Container style queries require the condition on an ancestor container. `if(style(...))` checks the property on the element itself.

```css
/* ❌ Container style query — needs an ancestor with the property */
.card-wrapper { --variant: compact; }
@container style(--variant: compact) {
  .card { padding: 0.5rem; }
}

/* ✅ if() — checks the element's own property */
.card {
  --variant: default;
  padding: if(style(--variant: compact): 0.5rem; 1.5rem);
}
.card.compact { --variant: compact; /* padding becomes 0.5rem */ }
```

### Syntax Rules

**No space** between `if` and `(`. Condition followed by `:`, truthy value, `;`, falsy value.

```css
.element {
  display: if(media(width < 640px): none; block);
  gap:     if(media(width >= 1024px): 2rem; 1rem);
}
```

### Chained Conditions

```css
.heading {
  font-size: if(
    media(width >= 1200px): 3rem;
    media(width >= 768px): 2rem;
    1.25rem
  );
}
```

### Boolean Custom Property Pattern

```css
.accordion-panel {
  --expanded: false;
  max-height: if(style(--expanded: true): 500px; 0);
  overflow: hidden;
  transition: max-height 0.3s ease;
}
.accordion-panel[open] { --expanded: true; }
```

---

## CSS Math Functions

Math functions eliminate preprocessor arithmetic and enable computations that respond to runtime values. They nest freely inside each other.

### Core: `calc()`, `min()`, `max()`, `clamp()`

Baseline — use freely everywhere.

```css
.sidebar { width: calc(100% - var(--sidebar-width)); }

/* min() = ceiling, max() = floor */
.container { width: min(90%, 1200px); }
.element   { font-size: max(1rem, 2vw); }

/* clamp(minimum, preferred, maximum) */
.fluid-text {
  font-size: clamp(1rem, 2.5vw, 2rem);
}
.container {
  width: clamp(320px, 90%, 1200px);
  padding-inline: clamp(1rem, 5vw, 3rem);
}
```

**WHEN:** `clamp()` for fluid typography/spacing. `min()` to cap a maximum. `max()` to enforce a minimum. `calc()` for mixed-unit arithmetic.

### Stepped: `round()`, `mod()`, `rem()`

> Baseline. Snap values to grids or extract remainders.

```css
/* round(strategy, value, interval) */
.element {
  width: round(nearest, 100vw, 100px);
  height: round(up, var(--content-height), 8px);
  padding: round(down, 2.7rem, 0.25rem);   /* 2.5rem */
}

/* mod() for cyclic patterns */
.grid-item { --offset: mod(var(--index), 3); }
```

**WHEN:** `round()` to align to a spacing grid (4px, 8px baseline). `mod()` for repeating patterns.

### Sign: `abs()`, `sign()`

> Baseline.

```css
.element {
  --distance: abs(var(--position) - 50%);
  transform: scaleX(sign(var(--velocity)));
}
```

**WHEN:** `abs()` for magnitude regardless of direction. `sign()` to extract direction for transforms.

### Trigonometric: `sin()`, `cos()`, `tan()`, `asin()`, `acos()`, `atan()`, `atan2()`

> Baseline. Accept angles, return unitless numbers.

```css
/* Circular layout */
.circular-menu > * {
  --angle: calc(360deg / var(--items) * var(--index));
  position: absolute;
  left: calc(50% + var(--radius) * cos(var(--angle)));
  top: calc(50% + var(--radius) * sin(var(--angle)));
  translate: -50% -50%;
}

/* Wave effect */
.wave-item {
  transform: translateY(calc(sin(var(--index) * 45deg) * 20px));
}
```

**WHEN:** Circular/radial layouts, wave animations, polar coordinate systems.

### Exponential: `pow()`, `sqrt()`, `hypot()`, `log()`, `exp()`

> Baseline.

```css
/* Modular type scale */
.heading {
  --ratio: 1.25;
  --level: 3;
  font-size: calc(1rem * pow(var(--ratio), var(--level)));
}

/* Distance calculation */
.element {
  --distance: hypot(var(--dx), var(--dy));
}
```

**WHEN:** `pow()` for exponential type/spacing scales. `hypot()` for distance. These replace Sass functions or JavaScript.

---

## `sibling-index()` / `sibling-count()`

> **Not Baseline as of mid-2026:** Chrome/Edge 138+ and Safari 26.2+; no Firefox. Feature-detect against a real property: `@supports (transition-delay: calc(sibling-index() * 1ms))`. (Testing via a custom property is always true — see the `if()` note above.)

Return the 1-based index and total count of siblings as integers usable in `calc()` — unlike `counter()` which returns strings only for `content`.

### WHEN to Use

Use when you need positional styling that would otherwise require inline `style="--i: N"` attributes, `:nth-child()` rules for every position, or JavaScript.

### Staggered Animations

```css
/* ❌ Before: manually set index via HTML or nth-child */
.list-item:nth-child(1) { transition-delay: 0ms; }
.list-item:nth-child(2) { transition-delay: 50ms; }
.list-item:nth-child(3) { transition-delay: 100ms; }

/* ✅ After: single rule, any number of items */
.list-item {
  transition: opacity 0.3s ease, transform 0.3s ease;
  transition-delay: calc((sibling-index() - 1) * 50ms);
}
```

### Dynamic Spacing and Opacity

```css
.thread-reply {
  padding-inline-start: calc(sibling-index() * 1rem);
}

.notification {
  opacity: calc(1 - (sibling-index() - 1) / sibling-count());
}
```

### Positional Color Shifts

```css
.color-strip > * {
  --hue: calc(360 / sibling-count() * (sibling-index() - 1));
  background: oklch(0.7 0.2 var(--hue));
}
```

### Circular Layout (Combined with Trig)

```css
.radial-menu > * {
  --angle: calc(360deg / sibling-count() * (sibling-index() - 1));
  position: absolute;
  left: calc(50% + 100px * cos(var(--angle)));
  top: calc(50% + 100px * sin(var(--angle)));
  translate: -50% -50%;
}
```

---

## Typed `attr()`

> **Chromium-only (Chrome/Edge 133+) as of mid-2026. Not Baseline.** Feature-detect against a real property: `@supports (width: attr(data-x type(<length>), 0px))`.

Standard `attr()` only works in `content` and returns strings. Typed `attr()` parses HTML attributes as real CSS values — colors, numbers, lengths — usable in any property.

### Syntax

```
attr(<attribute-name> type(<syntax>), <fallback>)
```

### WHEN to Use

Use when data-driven styling makes more sense than classes: star ratings, progress bars, dynamic counts, view-transition-names from data attributes, or avoiding generated CSS for every possible value.

### Data-Driven Grid Columns

```css
/* ❌ Before: a class for every possible column count */
.grid.cols-1 { grid-template-columns: repeat(1, 1fr); }
.grid.cols-2 { grid-template-columns: repeat(2, 1fr); }
.grid.cols-3 { grid-template-columns: repeat(3, 1fr); }

/* ✅ After: one rule, driven by the attribute */
.grid {
  grid-template-columns: repeat(attr(data-cols type(<number>), 1), 1fr);
}
```

```html
<div class="grid" data-cols="3">...</div>
```

### Star Ratings

```css
.star-rating {
  --rating: attr(data-rating type(<number>), 0);
  background: linear-gradient(
    to right,
    gold calc(var(--rating) / 5 * 100%),
    #ddd calc(var(--rating) / 5 * 100%)
  );
  mask-image: url('stars.svg');
}
```

```html
<div class="star-rating" data-rating="3.5"></div>
```

### Progress Bar

```css
.progress-bar {
  --pct: attr(data-value type(<number>), 0);
  background: linear-gradient(
    to right,
    var(--color-primary) calc(var(--pct) * 1%),
    var(--color-surface) calc(var(--pct) * 1%)
  );
}
```

### Dynamic View Transition Names

```css
.product-card {
  view-transition-name: attr(data-product-id type(<custom-ident>), none);
}
```

```html
<div class="product-card" data-product-id="shoe-42">...</div>
```

### Color and Spacing from Attributes

```css
.swatch {
  background: attr(data-color type(<color>), gray);
}

.spacer {
  height: attr(data-size type(<length>), 1rem);
}
```

```html
<span class="swatch" data-color="oklch(0.7 0.25 150)"></span>
<div class="spacer" data-size="2rem"></div>
```

---

## Token Architecture Pattern

How these primitives compose into a design system — no frameworks, no build steps.

```css
/* Layer 1: Primitive tokens (raw values) */
:root {
  --blue-50: oklch(0.97 0.01 250);
  --blue-500: oklch(0.6 0.2 250);
  --blue-900: oklch(0.25 0.08 250);
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-4: 1rem;
  --space-8: 2rem;
}

/* Layer 2: Semantic tokens (meaning aliases) */
:root {
  --color-primary: var(--blue-500);
  --color-bg: var(--blue-50);
  --color-text: var(--blue-900);
  --space-sm: var(--space-2);
  --space-md: var(--space-4);
  --space-lg: var(--space-8);
}

/* Layer 3: Component tokens (scoped) */
.card {
  --_padding: var(--space-md);
  --_bg: var(--color-bg);
  padding: var(--_padding);
  background: var(--_bg);
}

/* Dark theme — override semantic tokens only */
@media (prefers-color-scheme: dark) {
  :root {
    --color-primary: var(--blue-50);
    --color-bg: var(--blue-900);
    --color-text: var(--blue-50);
  }
}
```

Animate an entire palette by registering a hue token with `@property`:

```css
@property --theme-hue {
  syntax: "<number>";
  inherits: true;
  initial-value: 250;
}

:root {
  --theme-hue: 250;
  --color-primary: oklch(0.6 0.2 var(--theme-hue));
  transition: --theme-hue 0.6s ease;
}

[data-mood="warm"]   { --theme-hue: 30; }
[data-mood="nature"] { --theme-hue: 150; }
```

> For non-Baseline features, always feature-detect with `@supports` or use progressive enhancement. Check [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS) or [Baseline](https://web.dev/baseline) for current browser support.
