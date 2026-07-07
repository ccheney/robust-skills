# FSD Layers Reference

> **Source:** [Layers Reference](https://feature-sliced.design/docs/reference/layers) | [Slices & Segments](https://feature-sliced.design/docs/reference/slices-segments) | [FSD Overview](https://feature-sliced.design/docs/get-started/overview)

## Table of Contents

- [Layer Hierarchy](#layer-hierarchy)
- [Import Rule](#import-rule)
- [Shared Layer](#shared-layer)
- [Entities Layer](#entities-layer)
- [Features Layer](#features-layer)
- [Widgets Layer](#widgets-layer)
- [Pages Layer](#pages-layer)
- [App Layer](#app-layer)
- [Layer Selection Flowchart](#layer-selection-flowchart)
- [Common Mistakes](#common-mistakes)

---

## Layer Hierarchy

Arranged from highest to lowest responsibility. A slice can only import slices from layers strictly below it.

| Layer | Purpose | Has Slices | Required |
|-------|---------|------------|----------|
| `app/` | Application initialization, providers, routing | No (segments only) | Yes |
| `pages/` | Route-based screens; the default home for non-reused code | Yes | Yes |
| `widgets/` | Large self-sufficient UI blocks reused across pages | Yes | No |
| `features/` | Reused user interactions with business value | Yes | No |
| `entities/` | Business domain models | Yes | No |
| `shared/` | Reused infrastructure | No (segments only) | Yes |

**Deprecated:** the `processes/` layer. Official guidance: avoid it and move its contents to `features/` and `app/`.

`app/` and `shared/` are each "a layer and a slice at the same time" — they divide directly into segments, which may freely import each other.

---

## Import Rule

```
app/      → can import: pages, widgets, features, entities, shared
pages/    → can import: widgets, features, entities, shared
widgets/  → can import: features, entities, shared
features/ → can import: entities, shared
entities/ → can import: shared (use @x for cross-entity)
shared/   → can import: external packages only
```

Slices on the same layer never import each other (zero coupling between siblings; high cohesion within a slice). The single exception is `@x` notation on the entities layer.

---

## Shared Layer

> [Shared Layer Docs](https://feature-sliced.design/docs/reference/layers#shared)

Foundation layer for external connections and reused infrastructure. Shared has **no knowledge of the slices above it** — no `User` types, no domain rules — but since v2.1 it explicitly *may* contain application-aware infrastructure: your backend's API client and request functions, route path constants, logos.

**Segments:**
```
shared/
├── api/           # Backend client, request functions, DTOs, interceptors
├── ui/            # Business-agnostic UI kit (buttons, inputs, modals)
├── lib/           # Focused internal libraries (dates, colors, validation)
├── config/        # Environment variables, feature flags
├── routes/        # Route path constants
└── i18n/          # Translation setup
```

**Guidelines:**
- Avoid essence-named segments: `components/`, `hooks/`, `utils/`, `types/` — they become junk drawers. Name by purpose.
- Each segment has its own public API; there is no root `shared/index.ts` (see [PUBLIC-API.md](PUBLIC-API.md#the-shared-layer-is-different))
- `shared/lib` is a set of small, documented, focused libraries — not a dumping ground for "helpers"
- No business logic. Litmus test: would this code survive unchanged if the product pivoted to a different domain?

**Where TypeScript types go:**
- Utility types → `shared/lib` (e.g. `shared/lib/utility-types`)
- DTOs of your backend → `shared/api`, next to the request functions
- Domain types (`User`, `Product`) → the entity that owns them, never shared

---

## Entities Layer

> [Entities Layer Docs](https://feature-sliced.design/docs/reference/layers#entities)

Real-world business concepts the application works with — created when the concept is **reused across pages**.

**Structure:**
```
entities/
├── user/
│   ├── ui/           # UserAvatar, UserCard, UserBadge
│   ├── api/          # getUser, updateUser, queries
│   ├── model/        # User types, validation, store
│   ├── lib/          # formatUserName, calculateAge
│   └── index.ts      # Public API (the only barrel)
├── product/
│   ├── ui/
│   ├── api/
│   ├── model/
│   └── index.ts
└── order/
    └── ...
```

**What belongs here:**
- Data models and TypeScript interfaces
- API functions for CRUD operations
- Reusable UI representations (cards, avatars) — display only, no interaction logic
- Validation schemas (Zod, Valibot)
- Entity-specific mappers (DTO → domain model)

**What doesn't belong:**
- User interactions (→ features, or the page if single-use)
- Page layouts (→ pages)
- Composed UI blocks (→ widgets)

**Cross-entity references:** use `@x` notation — see [PUBLIC-API.md](PUBLIC-API.md#cross-imports-with-x-notation).

---

## Features Layer

> [Features Layer Docs](https://feature-sliced.design/docs/reference/layers#features)

User interactions that provide business value **and are reused across pages**.

**Key principle (v2.1): not everything is a feature.** An interaction used on a single page stays in that page's slice. Extracting everything into features forces readers to jump between folders to follow one user flow. Optimize for the newcomer who finds code by page.

**Structure:**
```
features/
├── auth/
│   ├── ui/           # LoginForm, LogoutButton
│   ├── api/          # login, logout, register
│   ├── model/        # session store, schemas
│   └── index.ts
├── add-to-cart/
│   ├── ui/           # AddToCartButton, QuantitySelector
│   ├── api/          # addToCart mutation
│   └── index.ts
└── search-products/
    ├── ui/           # SearchInput, Filters
    ├── api/          # searchProducts
    ├── model/        # search state
    └── index.ts
```

**Feature vs Entity:**

| Entity | Feature |
|--------|---------|
| Represents a THING | Represents an ACTION |
| `user` — user data | `auth` — login/logout |
| `product` — product info | `add-to-cart` — adding |
| `comment` — comment data | `write-comment` — creating |

---

## Widgets Layer

> [Widgets Layer Docs](https://feature-sliced.design/docs/reference/layers#widgets)

Large, self-sufficient chunks of UI that deliver a complete use case and are **reused across pages**.

Since v2.1, widgets are not just compositional shells: a widget **may own its business logic, stores, and API interactions**. If a header fetches the notification count itself, that fetch belongs in `widgets/header/api/`.

**When to create a widget:**
- The block is reused on 2+ pages, or
- It's a self-contained unit in a nested routing system (route-level composition)

**Structure:**
```
widgets/
├── header/
│   ├── ui/           # Header, NavMenu, UserDropdown
│   ├── api/          # e.g. notification count query
│   └── index.ts
├── sidebar/
│   ├── ui/           # Sidebar, SidebarItem
│   └── index.ts
└── product-list/
    ├── ui/           # ProductList, ProductGrid, Filters
    ├── model/        # list state
    └── index.ts
```

**Widget vs Feature:** a widget is a block of the page (structural); a feature is an action the user takes (behavioral). Widgets often compose entities and features:

```tsx
// widgets/header/ui/Header.tsx
import { UserAvatar } from '@/entities/user';
import { LogoutButton } from '@/features/auth';
import { SearchBox } from '@/features/search-products';
```

**Don't create widgets for:**
- Blocks used by a single page — keep them in that page's `ui/`
- Trivial compositions — compose directly in the page

---

## Pages Layer

> [Pages Layer Docs](https://feature-sliced.design/docs/reference/layers#pages)

Individual screens or routes. One slice per route, generally; closely related routes (login/register) can share a slice.

**Pages are the default home for code (v2.1):** large UI blocks, forms, and data logic that are not reused on other pages **stay in the page slice**, organized into segments. Don't pre-extract.

**Structure:**
```
pages/
├── home/
│   ├── ui/           # HomePage, HeroSection (page-local blocks live here)
│   ├── api/          # loader functions
│   └── index.ts
├── product-detail/
│   ├── ui/           # ProductDetailPage
│   ├── api/          # getProduct loader
│   └── index.ts
└── checkout/
    ├── ui/           # CheckoutPage, CheckoutSteps, PaymentForm
    ├── api/          # checkout mutations
    ├── model/        # form state, validation
    └── index.ts
```

**Guidelines:**
- Pages compose widgets, features, entities — plus their own page-local code
- Reused logic gets extracted down only when a second page needs it
- Business *infrastructure* that several pages share goes to shared; page *content* stays in pages

---

## App Layer

> [App Layer Docs](https://feature-sliced.design/docs/reference/layers#app)

Application-wide concerns. No slices — segments only. Custom segment names are most appropriate here.

**Structure:**
```
app/
├── providers/        # React context, store setup, QueryClient
├── routes/           # Router configuration
├── styles/           # Global CSS, theme tokens
├── analytics/        # App-wide analytics init (custom segment)
└── index.tsx         # Entry point
```

**Responsibilities:**
- Initialize application state and providers
- Set up routing
- Global styles and error boundaries
- Anything that applies to the whole app, not one page

---

## Layer Selection Flowchart

```
START: Where does this code go?
│
├─ Used by exactly ONE page (UI block, form, data logic)?
│  └─ YES → that page's slice in pages/ (the v2.1 default)
│
├─ Reusable infrastructure with no domain knowledge?
│  └─ YES → shared/
│
├─ Reused business domain object / data model?
│  └─ YES → entities/
│
├─ Reused user interaction with business value?
│  └─ YES → features/
│
├─ Reused self-sufficient UI block (may own logic/data)?
│  └─ YES → widgets/
│
├─ Route/screen component?
│  └─ YES → pages/
│
└─ App-wide initialization/config?
   └─ YES → app/
```

---

## Common Mistakes

1. **Business logic in shared** — shared must have no knowledge of domain slices; domain rules live in entities/features/pages
2. **Premature extraction** — extracting single-use code into features/entities/widgets; keep it in the page (v2.1)
3. **Features in entities** — entities are data, features are actions
4. **Too many layers in a small app** — start with `app`, `pages`, `shared`; add layers only when reuse appears
5. **Importing upward or sideways** — strictly forbidden; catch with [Steiger](https://github.com/feature-sliced/steiger)
6. **Generic segment names** — `components/`, `hooks/`, `types/` say nothing about purpose; use `ui/`, `model/`, `api/`, `lib/`
7. **Using the deprecated `processes/` layer** — move its contents to features and app
