# FSD Public API Patterns

> **Source:** [Public API Reference](https://feature-sliced.design/docs/reference/public-api)

## What is a Public API?

A public API is a **contract** between a slice and consuming code. It controls which objects are accessible and how they can be imported: modules outside a slice may reference only the public API, never the internal file structure.

**Implementation:** an `index.ts` file with explicit re-exports.

---

## Three Goals of a Quality Public API

1. **Protection from structural changes** — consumers are shielded from internal refactoring
2. **Behavioral transparency** — significant changes to the slice show up as API changes
3. **Selective exposure** — only the necessary parts are exposed

---

## Basic Pattern

```typescript
// entities/user/index.ts
export { UserCard } from './ui/UserCard';
export { UserAvatar } from './ui/UserAvatar';
export { getUser, updateUser } from './api/userApi';
export type { User, UserRole } from './model/types';
export { userSchema } from './model/schema';
```

```typescript
import { UserCard, type User } from '@/entities/user';
```

---

## Avoid Wildcard Exports

```typescript
// ❌ Don't
export * from './ui';
export * from './model';
```

Wildcards hide the contract (you can't see what the slice offers), accidentally expose internals, complicate refactoring, and harm tree-shaking. Always re-export by name.

---

## One Index Per Slice — No Segment Indexes on Sliced Layers

On layers that have slices (`pages`, `widgets`, `features`, `entities`), the slice index is the **only** barrel file. Official guidance: if `features/comments/index.ts` exists, do **not** also create `features/comments/ui/index.ts`.

Why: extra barrels add work for the bundler and dev server, and they are the main source of accidental circular imports (a segment file importing a sibling through the segment index).

```
features/comments/
├── ui/
│   ├── CommentCard.tsx      # no ui/index.ts
│   └── CommentForm.tsx
├── model/
│   └── types.ts             # no model/index.ts
└── index.ts                 # the ONLY public API
```

---

## The Shared Layer Is Different

`shared/` has no slices, so the public API is defined **per segment** — and there is intentionally **no root `shared/index.ts`**:

```typescript
// shared/api/index.ts
export { apiClient } from './client';
```

For `shared/ui` and `shared/lib` — big collections of unrelated things — go one level finer: an index **per component/library**, imported directly:

```
shared/ui/
├── button/
│   ├── Button.tsx
│   └── index.ts
├── date-picker/
│   ├── DatePicker.tsx
│   └── index.ts
```

```typescript
// ✅ Per-component import
import { Button } from '@/shared/ui/button';

// ❌ Monolithic barrel: shared/ui/index.ts re-exporting everything
import { Button } from '@/shared/ui';
```

Why: one root barrel couples unrelated modules — importing `Button` pulls the date-picker's heavy dependency into the module graph, hurting tree-shaking in some bundlers and slowing dev-server cold starts.

---

## Avoiding Circular Imports

**Problem:** a file inside a slice importing from its own slice's index.

```typescript
// features/comments/ui/CommentForm.tsx

// ❌ Circular: index.ts re-exports CommentForm, which imports index.ts
import { commentSchema } from '../index';

// ✅ Relative import with the full path
import { commentSchema } from '../model/schema';
```

**Rule:** within a slice, use relative imports to the concrete file. Between slices, use absolute aliased imports of the public API (`@/entities/user`). Never mix the two directions.

---

## Cross-Imports with @x Notation

> [Official @x Documentation](https://feature-sliced.design/docs/reference/public-api#public-api-for-cross-imports)

Slices on the same layer normally cannot import each other. When two business entities genuinely reference each other (a song has an artist), declare a dedicated public API for that one consumer: `entities/A/@x/B.ts` is importable by code in `entities/B/`.

```
entities/
├── song/
│   ├── @x/
│   │   └── artist.ts      # exports intended ONLY for the artist entity
│   ├── model/
│   │   └── types.ts
│   └── index.ts
└── artist/
    ├── model/
    │   └── types.ts
    └── index.ts
```

```typescript
// entities/song/@x/artist.ts
export type { Song, SongId } from '../model/types';

// entities/artist/model/types.ts
import type { Song } from '@/entities/song/@x/artist';

export interface Artist {
  name: string;
  songs: Song[];
}
```

**Guidelines:**
- Use `@x` **only on the entities layer**, where eliminating cross-references is often unreasonable
- Keep the `@x` file tiny — usually just type re-exports
- The filename names the consumer, making the coupling impossible to miss
- If two entities cross-reference extensively, merge them into one slice

---

## Index File Trade-offs

Be aware of what barrels cost, and mitigate deliberately:

1. **Circular imports** — internal files re-importing via the index → use relative imports inside slices
2. **Tree-shaking failures** — unrelated code bundled together → per-component indexes in `shared/ui`/`shared/lib`
3. **Weak enforcement** — nothing technically stops deep imports → lint with [Steiger](https://github.com/feature-sliced/steiger) (`fsd/public-api` rule) or `@feature-sliced/eslint-config`
4. **Dev-server overhead** — thousands of index files slow cold starts → one index per slice, no segment indexes

For Next.js server/client public API splitting (`index.server.ts`), see [NEXTJS.md](NEXTJS.md#server-vs-client-public-apis-indexserverts).

---

## Complete Example

```typescript
// entities/product/model/types.ts
export interface Product {
  id: string;
  name: string;
  price: number;
  imageUrl: string;
  category: string;
}

export interface ProductFilters {
  category?: string;
  minPrice?: number;
  maxPrice?: number;
}
```

```typescript
// entities/product/model/schema.ts
import { z } from 'zod';

export const productSchema = z.object({
  id: z.string(),
  name: z.string().min(1),
  price: z.number().positive(),
  imageUrl: z.url(),
  category: z.string(),
});
```

```typescript
// entities/product/api/productApi.ts
import { apiClient } from '@/shared/api';
import type { Product, ProductFilters } from '../model/types';

export async function getProducts(filters?: ProductFilters): Promise<Product[]> {
  const { data } = await apiClient.get('/products', { params: filters });
  return data;
}

export async function getProductById(id: string): Promise<Product> {
  const { data } = await apiClient.get(`/products/${id}`);
  return data;
}
```

```tsx
// entities/product/ui/ProductCard.tsx
import type { Product } from '../model/types';

interface ProductCardProps {
  product: Product;
  onSelect?: (product: Product) => void;
}

export function ProductCard({ product, onSelect }: ProductCardProps) {
  return (
    <div onClick={() => onSelect?.(product)}>
      <img src={product.imageUrl} alt={product.name} />
      <h3>{product.name}</h3>
      <p>${product.price}</p>
    </div>
  );
}
```

```typescript
// entities/product/index.ts — the only barrel in this slice
export { ProductCard } from './ui/ProductCard';
export { getProducts, getProductById } from './api/productApi';
export type { Product, ProductFilters } from './model/types';
export { productSchema } from './model/schema';
```
