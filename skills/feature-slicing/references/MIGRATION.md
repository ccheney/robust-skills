# Migrating to Feature-Sliced Design

> **Source:** [Migration from Custom Architecture](https://feature-sliced.design/docs/guides/migration/from-custom) | [Migration from v2.0 to v2.1](https://feature-sliced.design/docs/guides/migration/from-v2-0)

## Table of Contents

- [When to Migrate](#when-to-migrate)
- [Migration Strategy](#migration-strategy)
- [Phase 1: Setup](#phase-1-setup)
- [Phase 2: Divide Code by Pages](#phase-2-divide-code-by-pages)
- [Phase 3: Build the Shared Layer](#phase-3-build-the-shared-layer)
- [Phase 4: Eliminate Cross-Page Dependencies](#phase-4-eliminate-cross-page-dependencies)
- [Phase 5: Organize Segments](#phase-5-organize-segments)
- [Phase 6 (Optional): Extract Entities, Features, Widgets](#phase-6-optional-extract-entities-features-widgets)
- [Common Migration Patterns](#common-migration-patterns)
- [Migration Checklist](#migration-checklist)
- [Rollback Strategy](#rollback-strategy)

---

## When to Migrate

Consider migrating to FSD if:
- The project has grown too large and interconnected
- Implementing new features takes longer than expected
- Onboarding new developers is difficult
- Circular dependencies are common
- Code ownership is unclear

**Don't migrate if** the current architecture works well for your team — and don't switch to FSD against the will of your teammates. Migration succeeds as a team decision.

---

## Migration Strategy

FSD supports incremental adoption — migration "will not halt the development of new features." The official order is **pages first** (matching the v2.1 philosophy), not entities first:

```
Phase 1: Set up structure, aliases, linting
Phase 2: Divide code by pages
Phase 3: Build the shared layer
Phase 4: Eliminate cross-page dependencies
Phase 5: Organize segments within slices
Phase 6: (Optional) Extract entities/features/widgets where reuse is real
```

Run [Steiger](https://github.com/feature-sliced/steiger) in watch mode throughout: `npx steiger ./src --watch`.

---

## Phase 1: Setup

### Create the minimal structure

Only the three required layers to start — resist scaffolding all six:

```bash
mkdir -p src/app src/pages src/shared
```

### Configure path aliases (keep legacy aliases during migration)

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"],
      "@components/*": ["./src/components/*"],
      "@hooks/*": ["./src/hooks/*"]
    }
  }
}
```

Legacy aliases keep old imports compiling while you move code; delete them in the final cleanup.

---

## Phase 2: Divide Code by Pages

The first structural move: every route gets a page slice, and code used by only that route moves into it — components, hooks, state, all of it. Don't classify anything as entity/feature yet; "split by pages" is natural and requires no business-domain debate.

### Before

```
src/
├── pages/
│   ├── Home.tsx
│   ├── ProductList.tsx
│   └── ProductDetail.tsx
├── components/
│   ├── HeroSection.tsx        # used only by Home
│   └── ProductGallery.tsx     # used only by ProductDetail
└── hooks/
    └── useCheckoutSteps.ts    # used only by Checkout
```

### After

```
src/pages/
├── home/
│   ├── ui/
│   │   ├── HomePage.tsx
│   │   └── HeroSection.tsx        # page-local: lives here now
│   └── index.ts
├── products/
│   ├── ui/ProductsPage.tsx
│   └── index.ts
└── product-detail/
    ├── ui/
    │   ├── ProductDetailPage.tsx
    │   └── ProductGallery.tsx
    └── index.ts
```

Give each page slice an `index.ts` public API immediately — it makes later refactors invisible to the router.

---

## Phase 3: Build the Shared Layer

Move genuinely page-independent code into `shared/`, renaming junk-drawer folders to purpose-named segments:

### Before

```
src/
├── utils/
│   ├── api.ts
│   ├── dates.ts
│   └── constants.ts
├── hooks/
│   ├── useLocalStorage.ts
│   └── useDebounce.ts
└── components/
    ├── Button.tsx
    └── Input.tsx
```

### After

```
src/shared/
├── api/
│   ├── client.ts          # from utils/api.ts
│   └── index.ts
├── lib/
│   ├── dates.ts           # from utils/dates.ts
│   ├── use-local-storage.ts
│   └── use-debounce.ts
├── config/
│   └── constants.ts       # from utils/constants.ts
└── ui/
    ├── button/
    │   ├── Button.tsx     # from components/
    │   └── index.ts
    └── input/
        ├── Input.tsx
        └── index.ts
```

Two tests for what belongs in shared:
1. It doesn't import from any page/entity/feature
2. It has no business-domain knowledge (an API *client* qualifies; a `calculateShippingCost` does not)

```typescript
// Before
import { formatDate } from '@/utils/dates';
import { Button } from '@/components/Button';

// After
import { formatDate } from '@/shared/lib/dates';
import { Button } from '@/shared/ui/button';
```

---

## Phase 4: Eliminate Cross-Page Dependencies

Pages must not import each other. For each cross-page import, either:

- **Move it down** to `shared/` (if infrastructure) — or later to entities/features/widgets, or
- **Duplicate it.** Official guidance: "copy-pasting isn't architecturally wrong" — a small duplication is cheaper than a wrong abstraction between pages.

```typescript
// ❌ Before: pages/checkout imports from pages/cart
import { CartSummary } from '@/pages/cart';

// ✅ After: CartSummary is reused by 2 pages → it's now a widget
import { CartSummary } from '@/widgets/cart-summary';
```

---

## Phase 5: Organize Segments

Within each slice, arrange code by technical purpose: `ui/`, `api/`, `model/`, `lib/`, `config/`. Kill essence-named folders (`components/`, `hooks/`, `types/`) as you go.

```
pages/checkout/
├── ui/
│   ├── CheckoutPage.tsx
│   ├── CheckoutSteps.tsx
│   └── PaymentForm.tsx
├── api/
│   └── submitOrder.ts
├── model/
│   └── checkout-store.ts
└── index.ts
```

---

## Phase 6 (Optional): Extract Entities, Features, Widgets

Only now — with pages clean and reuse visible — extract lower layers. Extract when (and only when) 2+ pages need the same thing:

- **Entities:** domain types + CRUD + display components reused across pages (from scattered `types/user.ts`, `api/userApi.ts`, `components/UserCard.tsx`)
- **Features:** interactions reused across pages (auth, add-to-cart, search)
- **Widgets:** large reused blocks (header, cart summary)

```
src/entities/user/
├── ui/
│   ├── UserAvatar.tsx
│   └── UserCard.tsx
├── api/
│   └── userApi.ts
├── model/
│   ├── types.ts
│   └── store.ts
└── index.ts
```

```typescript
// entities/user/index.ts
export { UserAvatar } from './ui/UserAvatar';
export { UserCard } from './ui/UserCard';
export { getUser, updateUser } from './api/userApi';
export type { User, UserRole } from './model/types';
```

Steiger's `fsd/insignificant-slice` rule flags slices referenced by only one page — merge those back into the page.

---

## Common Migration Patterns

### Handling Circular Dependencies

**Problem:** existing code has circular imports.

**Solution:** break the cycle by moving shared parts down and composing above.

```typescript
// Before: components/UserCard.tsx ↔ hooks/useAuth.ts import each other

// After:
// entities/user/ui/UserCard.tsx      — no auth dependency
// features/auth/model/store.ts       — no UserCard dependency
// pages/profile/ui/ProfilePage.tsx   — composes both
```

### Handling Global State

**Problem:** one monolithic store accessed everywhere.

**Solution:** split the store by domain into slice-local models.

```typescript
// Before: monolithic store
export const store = configureStore({
  reducer: {
    user: userReducer,
    products: productsReducer,
    cart: cartReducer,
    auth: authReducer,
  },
});

// After: distributed stores (Zustand example)
// entities/user/model/store.ts     — user data
// entities/product/model/store.ts  — product data
// features/cart/model/store.ts     — cart state
// features/auth/model/store.ts     — auth state
```

### Shared Components with Business Logic

**Problem:** a display component has interaction logic baked in.

**Solution:** split display (entity) from interaction (feature); compose in the page/widget via a render slot.

```tsx
// Before: ProductCard with add-to-cart logic inside

// After — entities/product/ui/ProductCard.tsx (display only):
export function ProductCard({ product, actions }: ProductCardProps) {
  return (
    <div>
      <img src={product.imageUrl} alt={product.name} />
      <h3>{product.name}</h3>
      {actions}
    </div>
  );
}

// features/add-to-cart/ui/AddToCartButton.tsx (interaction):
export function AddToCartButton({ product }: { product: Product }) {
  const addToCart = useCartStore((s) => s.addItem);
  return <button onClick={() => addToCart(product)}>Add to Cart</button>;
}

// Composed in a page or widget:
<ProductCard product={product} actions={<AddToCartButton product={product} />} />
```

---

## Migration Checklist

- [ ] Team agrees to migrate
- [ ] Create `app/`, `pages/`, `shared/` structure
- [ ] Configure path aliases (keep legacy aliases temporarily)
- [ ] Install Steiger, run in watch mode
- [ ] Move every route into a page slice with a public API
- [ ] Move page-local components/hooks/state into their page slices
- [ ] Migrate utilities/API client/UI kit into `shared/` segments
- [ ] Remove all cross-page imports (move down or duplicate)
- [ ] Organize slices into `ui/api/model/lib/config` segments
- [ ] Extract entities/features/widgets only where 2+ pages share code
- [ ] Set up `app/` providers and router
- [ ] Delete legacy folders and legacy path aliases
- [ ] Steiger passes clean

---

## Rollback Strategy

Keep the old structure working during migration via dual aliases:

```json
{
  "paths": {
    "@/*": ["./src/*"],
    "@components/*": ["./src/components/*"],
    "@hooks/*": ["./src/hooks/*"]
  }
}
```

Use a switch to flip between implementations gradually:

```typescript
import { UserCard as LegacyUserCard } from '@components/UserCard';
import { UserCard as FSDUserCard } from '@/entities/user';

export const UserCard = import.meta.env.VITE_USE_FSD ? FSDUserCard : LegacyUserCard;
```

---

## Resources

| Resource | Link |
|----------|------|
| Migration guide | https://feature-sliced.design/docs/guides/migration/from-custom |
| v2.0 → v2.1 guide | https://feature-sliced.design/docs/guides/migration/from-v2-0 |
| v2.1 release notes ("Pages first") | https://github.com/feature-sliced/documentation/releases/tag/v2.1 |
