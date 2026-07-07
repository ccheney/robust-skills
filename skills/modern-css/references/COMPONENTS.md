# Components — Interactive UI Without JavaScript

> Sources: [Open UI](https://open-ui.org/), [Popover API](https://html.spec.whatwg.org/multipage/popover.html), [CSS Anchor Positioning](https://www.w3.org/TR/css-anchor-position-1/), [Invoker Commands](https://open-ui.org/components/invokers.explainer/), [Interop 2025](https://webkit.org/blog/17808/interop-2025-review/). These APIs eliminate entire categories of JavaScript — tooltips, dropdowns, modals, popovers, auto-sizing inputs — with declarative HTML attributes and CSS properties.

## Contents

- [Customizable `<select>` — `appearance: base-select`](#customizable-select--appearance-base-select)
- [Popover API](#popover-api)
- [Invoker Commands — Declarative Button Actions](#invoker-commands--declarative-button-actions)
- [Dialog Light Dismiss — `closedby` Attribute](#dialog-light-dismiss--closedby-attribute)
- [Interest Invokers — Hover/Focus-Triggered UI](#interest-invokers--hoverfocus-triggered-ui)
- [Anchor Positioning](#anchor-positioning)
- [`field-sizing: content` — Auto-Sizing Form Fields](#field-sizing-content--auto-sizing-form-fields)
- [Decision Guide](#decision-guide)

---

## Customizable `<select>` — `appearance: base-select`

Before this, styling a dropdown with images or icons meant rebuilding the widget in JavaScript — destroying native accessibility, keyboard navigation, and form integration. Opt in with CSS; unsupported browsers render a standard `<select>` as fallback.

**Support (mid-2026): not Baseline.** Chrome/Edge 135+ ship it; Safari announced support for Safari 27 (WWDC 2026); Firefox is prototyping behind a flag. Safe to adopt now because the fallback is a fully functional native `<select>`.

### Opt-In and Pseudo-Elements

```css
select,
::picker(select) {
  appearance: base-select;
}
```

| Pseudo-Element | Targets | Purpose |
|---|---|---|
| `::picker(select)` | Dropdown popover on open | Style dropdown container |
| `::picker-icon` | Arrow/chevron indicator | Replace or animate the arrow |
| `option::checkmark` | Selected-item indicator | Style or hide the checkmark |
| `<selectedcontent>` | Reflected chosen option | Display rich content in collapsed state |

Use when options need rich content — flags, avatars, color swatches. Do NOT use for plain text lists.

### Complete Example

```html
<select>
  <option value="us">
    <img src="flags/us.svg" alt="" width="20" height="15"> United States
  </option>
  <option value="gb">
    <img src="flags/gb.svg" alt="" width="20" height="15"> United Kingdom
  </option>
  <selectedcontent></selectedcontent>
</select>
```

```css
/* ❌ JavaScript approach — custom dropdown widget */
```
```javascript
// 200+ lines: keyboard handling, ARIA roles, click-outside,
// scroll locking, focus trapping...
class CustomSelect extends HTMLElement { /* ... */ }
```
```css
/* ✅ Pure CSS — native <select> with full styling */
select,
::picker(select) {
  appearance: base-select;
}

select {
  font: inherit;
  border: 1px solid oklch(0.75 0 0);
  border-radius: 0.5rem;
  padding: 0.5rem 0.75rem;
  min-inline-size: 200px;
  background: oklch(1 0 0);
  cursor: pointer;
}

select::picker(select) {
  background: oklch(0.99 0 0);
  border: 1px solid oklch(0.8 0 0);
  border-radius: 0.75rem;
  padding: 0.25rem;
  box-shadow: 0 8px 24px oklch(0 0 0 / 0.12);
}

select::picker-icon {
  transition: rotate 0.2s ease;
}

select:open::picker-icon {
  rotate: 180deg;
}

option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border-radius: 0.5rem;
}

option:hover {
  background: oklch(0.95 0.02 260);
}

option::checkmark {
  color: oklch(0.55 0.2 145);
}

selectedcontent {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
}
```

Unsupported browsers ignore `base-select` and show a standard `<select>`. Feature-detect with `@supports (appearance: base-select)`.

---

## Popover API

Replaces custom JavaScript tooltip/dropdown/notification implementations. Popovers get automatic top-layer promotion, focus management, and light dismiss. `auto` and `manual` are Baseline (since April 2024); `hint` is Chromium-only (Chrome/Edge 133+) as of mid-2026 — unsupported browsers treat it as `auto`.

### Three Types

| Type | Attribute | Light Dismiss | Closes Others | Use When |
|---|---|---|---|---|
| `auto` | `popover` or `popover="auto"` | Yes (click outside, ESC) | Yes | Menus, dropdowns, action sheets |
| `manual` | `popover="manual"` | No | No | Notifications, toasts, persistent panels |
| `hint` | `popover="hint"` (Chromium-only) | Yes | Only other hints | Tooltips, ephemeral help text |

### Basic Usage

```html
<button popovertarget="my-menu">Open Menu</button>
<div id="my-menu" popover>
  <p>Menu content here</p>
</div>
```

### Styling

```css
/* ❌ JavaScript approach — manually toggling visibility */
```
```javascript
const btn = document.querySelector('#toggle');
const menu = document.querySelector('#menu');
btn.addEventListener('click', () => menu.classList.toggle('open'));
document.addEventListener('click', (e) => {
  if (!menu.contains(e.target) && e.target !== btn)
    menu.classList.remove('open');
});
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') menu.classList.remove('open');
});
```
```css
/* ✅ Pure CSS — popover with enter/exit transitions */
[popover] {
  opacity: 0;
  scale: 0.95;
  transition: opacity 0.2s, scale 0.2s,
    display 0.2s allow-discrete,
    overlay 0.2s allow-discrete;
}

[popover]:popover-open {
  opacity: 1;
  scale: 1;
}

@starting-style {
  [popover]:popover-open {
    opacity: 0;
    scale: 0.95;
  }
}

[popover]::backdrop {
  background: oklch(0 0 0 / 0.25);
  backdrop-filter: blur(2px);
}
```

### `hint` Type — Ephemeral Tooltips

Unlike `auto`, opening a `hint` does not close other open `auto` popovers. A user can have a dropdown open and still see a tooltip on a menu item.

```html
<button popovertarget="settings-menu">Settings</button>
<div id="settings-menu" popover>
  <button popovertarget="tip-1">Dark Mode</button>
  <div id="tip-1" popover="hint">Switches to dark theme</div>
</div>
```

---

## Invoker Commands — Declarative Button Actions

Replace JavaScript event listeners with `commandfor` and `command` attributes. **Baseline Newly Available since December 2025** (Chrome/Edge 135+, Firefox 144+, Safari 26.2+).

Gotcha: always add `type="button"` to invoker buttons inside a `<form>` — buttons default to `type="submit"` and will submit the form.

### Built-In Commands

| Command | Action | Target |
|---|---|---|
| `toggle-popover` | Toggle popover open/closed | `[popover]` |
| `show-popover` | Show popover | `[popover]` |
| `hide-popover` | Hide popover | `[popover]` |
| `show-modal` | Open dialog as modal | `<dialog>` |
| `close` | Close dialog | `<dialog>` |

```html
<!-- ❌ JavaScript approach -->
<button id="open-btn">Open Dialog</button>
<dialog id="my-dialog">
  <p>Dialog content</p>
  <button id="close-btn">Close</button>
</dialog>
<script>
  document.getElementById('open-btn').addEventListener('click', () => {
    document.getElementById('my-dialog').showModal();
  });
  document.getElementById('close-btn').addEventListener('click', () => {
    document.getElementById('my-dialog').close();
  });
</script>
```

```html
<!-- ✅ Invoker commands — no JS -->
<button commandfor="my-dialog" command="show-modal">Open Dialog</button>
<dialog id="my-dialog">
  <p>Dialog content</p>
  <button commandfor="my-dialog" command="close">Close</button>
</dialog>
```

### Custom Commands

Prefix with `--` for application-specific actions. Custom commands fire a `command` event on the target.

```html
<button commandfor="player" command="--play">Play</button>
<button commandfor="player" command="--pause">Pause</button>
<div id="player">...</div>

<script>
  document.getElementById('player').addEventListener('command', (e) => {
    if (e.command === '--play') video.play();
    if (e.command === '--pause') video.pause();
  });
</script>
```

Use invokers whenever a button's sole purpose is to trigger an action on another element.

---

## Dialog Light Dismiss — `closedby` Attribute

Controls how a `<dialog>` can be dismissed — click-outside-to-close previously required JavaScript.

**Support (mid-2026): not Baseline.** Chrome/Edge 134+ and Firefox 141+ support it; Safari does not yet (an Interop 2026 focus area). Unsupported browsers keep default dialog behavior (ESC closes modals) — keep a JS click-outside fallback if light dismiss is essential.

| Value | ESC Key | Click Outside | Programmatic `.close()` |
|---|---|---|---|
| `none` | No | No | Yes |
| `closerequest` (modal default) | Yes | No | Yes |
| `any` | Yes | Yes | Yes |

```html
<!-- ❌ JavaScript approach for click-outside-to-close -->
<dialog id="dlg"><p>Content</p></dialog>
<script>
  const dlg = document.getElementById('dlg');
  dlg.addEventListener('click', (e) => {
    const rect = dlg.getBoundingClientRect();
    if (e.clientX < rect.left || e.clientX > rect.right ||
        e.clientY < rect.top  || e.clientY > rect.bottom)
      dlg.close();
  });
</script>
```

```html
<!-- ✅ Declarative — closedby="any" handles ESC + click outside -->
<dialog closedby="any" id="dlg">
  <p>Content</p>
  <button commandfor="dlg" command="close">Close</button>
</dialog>
<button commandfor="dlg" command="show-modal">Open</button>
```

```css
dialog {
  border: none;
  border-radius: 1rem;
  padding: 2rem;
  max-inline-size: min(90vw, 500px);
  box-shadow: 0 12px 40px oklch(0 0 0 / 0.2);
}

dialog::backdrop {
  background: oklch(0 0 0 / 0.4);
  backdrop-filter: blur(4px);
}
```

---

## Interest Invokers — Hover/Focus-Triggered UI

The `interestfor` attribute triggers popovers on hover or focus rather than click. Default delay: 0.5s show/hide. Works on buttons and links.

**Support (mid-2026): Chromium-only (Chrome/Edge 142+), still experimental** — the attribute was renamed from `interesttarget` to `interestfor` during standardization, and the touch-device interaction model is still in flux. Provide a `title` attribute fallback on the trigger for other browsers.

```html
<button interestfor="tooltip-1">Hover me</button>
<div id="tooltip-1" popover="hint">This appears on hover/focus</div>
```

```css
/* ❌ JavaScript approach — hover intent detection */
```
```javascript
let timer;
trigger.addEventListener('mouseenter', () => {
  timer = setTimeout(() => tooltip.showPopover(), 300);
});
trigger.addEventListener('mouseleave', () => {
  clearTimeout(timer);
  setTimeout(() => tooltip.hidePopover(), 200);
});
```
```css
/* ✅ CSS interest-delay — declarative timing */
[interestfor] {
  interest-delay: 300ms;
}
```

Replaces `mouseenter`/`mouseleave`/`focusin`/`focusout` JavaScript. Keyboard focus triggers the popover automatically.

---

## Anchor Positioning

Replaces Floating UI, Popper.js, and Tether. An element declares itself as an anchor; another positions relative to it. The browser handles viewport collision, auto-flipping, and scroll-aware repositioning.

**Support: Baseline Newly Available since January 2026** (Chrome/Edge 125+, Safari 26+, Firefox 147+). Coverage of older browsers is still limited (Safari 26 requires recent OS versions) — use the [OddBird polyfill](https://github.com/oddbird/css-anchor-positioning) or a JS fallback where positioning is critical. Note the property renames: `inset-area` → `position-area` and `position-try-options` → `position-try-fallbacks` (old names are dead — never emit them).

### Core Properties

| Property | Purpose | Example |
|---|---|---|
| `anchor-name` | Declare an anchor | `anchor-name: --trigger` |
| `position-anchor` | Connect to an anchor | `position-anchor: --trigger` |
| `position-area` | Place relative to anchor | `position-area: block-end` |
| `position-try-fallbacks` | Fallbacks on overflow | `position-try-fallbacks: flip-block` |

### Basic Positioning

```css
/* ❌ JavaScript approach — Floating UI / Popper.js */
```
```javascript
import { computePosition, flip, offset } from '@floating-ui/dom';
computePosition(trigger, tooltip, {
  placement: 'bottom',
  middleware: [offset(8), flip()],
}).then(({ x, y }) => {
  tooltip.style.left = `${x}px`;
  tooltip.style.top = `${y}px`;
});
```
```css
/* ✅ Pure CSS — anchor positioning */
.trigger {
  anchor-name: --trigger;
}

.tooltip {
  position: fixed;
  position-anchor: --trigger;
  position-area: block-end;
  margin-block-start: 8px;
}
```

### Auto-Flip on Overflow

```css
.tooltip {
  position: fixed;
  position-anchor: --trigger;
  position-area: block-end;
  position-try-fallbacks: flip-block, flip-inline;
}
```

| Keyword | Behavior |
|---|---|
| `flip-block` | Flip bottom to top (or top to bottom) |
| `flip-inline` | Flip right to left (or left to right) |
| `flip-block flip-inline` | Flip both axes |

### Custom Fallback Positions

```css
.dropdown-menu {
  position: fixed;
  position-anchor: --menu-trigger;
  position-area: block-end span-inline-end;
  position-try-fallbacks: --above, --left;
}

@position-try --above {
  position-area: block-start span-inline-end;
}

@position-try --left {
  position-area: inline-start;
}
```

### Anchored Container Queries — Arrow Direction

When a tooltip flips, the arrow must point the other way. Detect which fallback was applied (`container-type: anchored` is Chromium-only and experimental as of mid-2026):

```css
.tooltip-wrapper {
  container-type: anchored;
}

.tooltip-arrow {
  rotate: 0deg; /* default: arrow up, tooltip below */
}

@container anchored(fallback: flip-block) {
  .tooltip-arrow {
    rotate: 180deg; /* flipped: arrow down, tooltip above */
  }
}
```

### Complete Tooltip — Zero JavaScript

Combines anchor positioning, popover `hint`, and interest invokers into a fully declarative tooltip:

```html
<button interestfor="tip" style="anchor-name: --btn">Hover me</button>
<div id="tip" popover="hint" style="position-anchor: --btn">
  Tooltip content
</div>
```

```css
[popover="hint"] {
  position: fixed;
  position-area: block-start;
  margin-block-end: 6px;
  position-try-fallbacks: flip-block;

  background: oklch(0.2 0 0);
  color: oklch(0.95 0 0);
  padding: 0.375rem 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  border: none;

  opacity: 0;
  transition: opacity 0.15s;
}

[popover="hint"]:popover-open {
  opacity: 1;
}

@starting-style {
  [popover="hint"]:popover-open {
    opacity: 0;
  }
}
```

---

## `field-sizing: content` — Auto-Sizing Form Fields

Auto-resizes inputs, textareas, and selects to fit content. **Baseline Newly Available since June 2026** (Chrome/Edge 123+, Safari 26.2+, Firefox 152+). Unsupported browsers keep fixed-size fields — safe progressive enhancement.

```css
/* ❌ JavaScript approach — auto-expanding textarea */
```
```javascript
const textarea = document.querySelector('textarea');
textarea.addEventListener('input', () => {
  textarea.style.height = 'auto';
  textarea.style.height = textarea.scrollHeight + 'px';
});
// Bugs: flickers on fast typing, breaks on box-sizing changes
```
```css
/* ✅ Pure CSS — auto-sizing */
textarea {
  field-sizing: content;
}
```

### Constraints and Progressive Enhancement

Always set bounds — without them, the element grows infinitely. Works on `input[type="text"]`, `textarea`, and `select`.

```css
textarea {
  min-block-size: 100px;
  resize: vertical;
}

@supports (field-sizing: content) {
  textarea {
    field-sizing: content;
    min-block-size: 3lh;
    max-block-size: 50vh;
    resize: none;
  }
}
```

---

## Decision Guide

| Need | Solution | JS Required | Cross-Browser (mid-2026) |
|---|---|---|---|
| Styled dropdown with images | `appearance: base-select` | No | Chromium only (native fallback) |
| Tooltip on hover | `interestfor` + `popover="hint"` + anchor positioning | No | Chromium only (`title` fallback) |
| Dropdown menu on click | `popovertarget` + `popover` + anchor positioning | No | Yes (anchor: newly Baseline) |
| Modal (ESC + click outside) | `<dialog closedby="any">` + `command="show-modal"` | No | `closedby`: not in Safari |
| Toast / notification | `popover="manual"` + `command="show-popover"` | Minimal (timer) | Yes |
| Auto-expanding textarea | `field-sizing: content` | No | Yes (newly Baseline) |
| Positioned element that flips | `position-try-fallbacks: flip-block` | No | Yes (newly Baseline) |
| Button opens/closes a panel | `commandfor` + `command="toggle-popover"` | No | Yes (newly Baseline) |

> For non-Baseline features, always feature-detect with `@supports` or use progressive enhancement. Check [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS) or [Baseline](https://web.dev/baseline) for current browser support.
