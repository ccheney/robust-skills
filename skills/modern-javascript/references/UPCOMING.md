# Upcoming JavaScript Features (Stage 4 for ES2027, and Active Proposals)

Temporal API, explicit resource management (`using` / `await using`), Atomics.pause, Iterator.zip, Decorators, Decorator Metadata, import defer — plus withdrawn proposals to avoid (Records & Tuples).

Status snapshot (mid-2026, per https://github.com/tc39/proposals):

| Feature | Status | How to use today |
|---------|--------|------------------|
| Temporal | **Stage 4** (Sept 2025) → ES2027 | Native: Firefox 139+, Chrome 144+, Node 26+. Elsewhere: `temporal-polyfill` / `@js-temporal/polyfill` |
| `using` / `await using` | **Stage 4** (May 2025) → ES2027 | Native: Chrome 134+, Firefox 141+, Node 24+. Safari: flagged. Transpile: TypeScript 5.2+, Babel |
| Atomics.pause | **Stage 4** (Oct 2024) → ES2027 | Chrome 133+, Firefox 137+, Safari 18.4+ |
| Iterator.zip / zipKeyed | **Stage 4** (Nov 2025) → ES2027 | Firefox 148+ only so far |
| Decorators + Metadata | Stage 3 (no engine ships them) | Babel or TypeScript 5.0+ only |
| `import defer` | Stage 3 | TypeScript 5.9+ (syntax), SWC, webpack/Rspack |
| Records & Tuples `#{}` `#[]` | **Withdrawn April 2025** | Never emit this syntax; successor "Composites" is Stage 1 |

## Temporal API (Stage 4 → ES2027)

Modern replacement for the broken `Date` object. Immutable, timezone-aware, and calendar-correct. Reached Stage 4 in September 2025; native in Firefox 139+, Chrome 144+, and Node 26+, still behind a flag in Safari — use a polyfill (`temporal-polyfill`) when you can't pin those baselines.

### Why Temporal over Date?

```javascript
// ❌ Date problems
const legacyDate = new Date('2024-03-10');  // Parsed as UTC? Local? Depends!
legacyDate.setMonth(1);                      // Mutates original
legacyDate.getMonth();                       // 0-indexed (January = 0)

// ✅ Temporal - immutable, explicit, correct
const date = Temporal.PlainDate.from('2024-03-10');
const nextMonth = date.add({ months: 1 });  // Returns new instance
date.month;  // 3 (March, 1-indexed!)
```

### Temporal Types

```javascript
// PlainDate - date only, no time or timezone
const birthday = Temporal.PlainDate.from('1990-05-15');
const today = Temporal.Now.plainDateISO();

// PlainTime - time only
const meeting = Temporal.PlainTime.from('14:30:00');

// PlainDateTime - date + time, no timezone
const appointment = Temporal.PlainDateTime.from('2024-03-15T14:30:00');

// ZonedDateTime - full date/time with timezone (DST-aware!)
const flight = Temporal.ZonedDateTime.from(
  '2024-03-15T14:30:00[America/New_York]'
);

// Instant - exact moment in time (like Unix timestamp)
const now = Temporal.Now.instant();

// Duration - length of time
const duration = Temporal.Duration.from({ hours: 2, minutes: 30 });
```

### Date Arithmetic

```javascript
const date = Temporal.PlainDate.from('2024-01-31');

// Add months correctly (clamps to end of month; leap-year aware)
date.add({ months: 1 });  // 2024-02-29

// Subtract
date.subtract({ days: 15 });

// Compare
date1.equals(date2);
Temporal.PlainDate.compare(date1, date2);  // -1, 0, or 1

// Difference
const diff = date1.until(date2);
diff.days;  // Number of days between
```

### Timezone Handling

```javascript
// Convert between timezones
const nyTime = Temporal.ZonedDateTime.from(
  '2024-03-15T14:30:00[America/New_York]'
);
const londonTime = nyTime.withTimeZone('Europe/London');

// Handle DST transitions correctly
const beforeDST = Temporal.ZonedDateTime.from(
  '2024-03-10T01:30:00[America/New_York]'
);
beforeDST.add({ hours: 2 });  // Correctly handles "spring forward"
```

### Migration Guide

| Use Case | Date | Temporal |
|----------|------|----------|
| Store timestamps | `Date.now()` | `Temporal.Now.instant()` |
| Display dates | `new Date()` | `Temporal.Now.zonedDateTimeISO()` |
| Birthdays, holidays | `new Date(y, m-1, d)` | `Temporal.PlainDate.from()` |
| Meeting times | Manual TZ conversion, DST bugs | `Temporal.ZonedDateTime` |
| Duration math | Manual calculation | `Temporal.Duration` |

---

## Explicit Resource Management — `using` / `await using` (Stage 4 → ES2027)

Automatic cleanup of resources like file handles, connections, and locks. Native in Chrome 134+, Firefox 141+, and Node 24+; Safari still flags it. TypeScript 5.2+ and Babel can transpile for older targets.

```javascript
// Synchronous disposal with `using`
{
  using file = openFile('data.txt');
  // Work with file...
} // file[Symbol.dispose]() called automatically, even on throw

// Asynchronous disposal with `await using` (inside async contexts/modules)
async function run() {
  await using db = await connectDatabase();
  await db.query('SELECT * FROM users');
} // db[Symbol.asyncDispose]() awaited automatically

// Creating disposable resources
class FileHandle {
  #handle;

  constructor(path) {
    this.#handle = fs.openSync(path);
  }

  read() { /* ... */ }

  [Symbol.dispose]() {
    fs.closeSync(this.#handle);
    console.log('File closed');
  }
}

// DisposableStack for multiple resources
{
  using stack = new DisposableStack();
  const file1 = stack.use(openFile('a.txt'));
  const file2 = stack.use(openFile('b.txt'));
  // Both disposed in reverse order when block exits
}

// AsyncDisposableStack for async cleanup
async function runAll() {
  await using stack = new AsyncDisposableStack();
  const conn1 = stack.use(await connect('db1'));
  const conn2 = stack.use(await connect('db2'));
}
```

**Key concepts:**
- `Symbol.dispose` / `Symbol.asyncDispose` — the cleanup methods a resource implements
- Disposal runs in reverse declaration order, even when the block exits via `throw`/`return`
- `DisposableStack` / `AsyncDisposableStack` — aggregate multiple disposables
- `SuppressedError` — thrown when disposal itself errors while another error is in flight
- `using` bindings are block-scoped and cannot be reassigned; the initializer must be an object with the dispose symbol (or `null`/`undefined`)

---

## Decorators (Stage 3 — Requires Transpiler)

Annotate and modify classes/methods with `@decorator` syntax. Still Stage 3 as of mid-2026 with **no engine shipping it unflagged** — usable only via Babel or TypeScript 5.0+ (the standard semantics; legacy `experimentalDecorators: true` is a different, incompatible system).

```javascript
// Requires transpiler (Babel or TypeScript 5.0+)

// Method decorator
function logged(target, context) {
  return function (...args) {
    console.log(`Calling ${context.name} with`, args);
    return target.apply(this, args);
  };
}

class Calculator {
  @logged
  add(a, b) {
    return a + b;
  }
}

// Class decorator
function singleton(Class, context) {
  let instance;
  return function (...args) {
    if (!instance) {
      instance = new Class(...args);
    }
    return instance;
  };
}

@singleton
class Database {
  constructor(url) {
    this.url = url;
  }
}
```

**Key points:**
- `@decorator` syntax before classes, methods, fields, accessors
- Receives `(value, context)` — value being decorated + metadata
- Must return the decorated value (or a replacement of the same kind)
- No parameter decorators (unlike TypeScript legacy decorators)
- TypeScript 5.0+ supports TC39 decorators when `experimentalDecorators` is off (the default)

## Decorator Metadata (Stage 3 — Requires Transpiler)

Store metadata on decorated elements (complements Decorators). Requires Babel or TypeScript 5.2+.

```javascript
function meta(value) {
  return function (target, context) {
    context.metadata[context.name] = value;
    return target;
  };
}

class User {
  @meta('string')
  name;

  @meta('number')
  age;
}

User[Symbol.metadata];
// { name: 'string', age: 'number' }
```

## import defer (Stage 3)

Load a module's code eagerly but defer *evaluation* until first property access — a startup-cost optimization. Syntax only, namespace-import form:

```javascript
import defer * as heavyLib from './heavy-lib.js';

export function rarelyCalled() {
  return heavyLib.process();  // module body executes here, on first access
}
```

Deferred modules cannot use top-level await (evaluation must be synchronous). Supported by TypeScript 5.9+ (syntax), SWC, webpack/Rspack; not yet in stable engines.

---

## Withdrawn: Records & Tuples

The `#{ x: 1 }` / `#[1, 2]` immutable-primitives proposal was **withdrawn at the April 2025 TC39 plenary** (performance expectations couldn't be met, and adding new primitives lost consensus). LLMs and older articles still suggest this syntax — it was never valid JavaScript and never will be.

Use instead:
- `Object.freeze({ ... })` for shallow immutability
- Structural-equality needs: compare manually or use a library (e.g. a keyed Map)
- Watch the successor **Composites** proposal (Stage 1): frozen *objects* with well-defined equality, not new primitives

## Resources

- **TC39 Proposals**: https://github.com/tc39/proposals (authoritative stage tracking)
- **Temporal docs**: https://tc39.es/proposal-temporal/docs/
- **Can I Use**: https://caniuse.com (browser support tables)
