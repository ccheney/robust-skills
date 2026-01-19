# FSD Public API Patterns

> Source: https://feature-sliced.design/docs/reference/public-api

## What is a Public API?

A public API is a **contract** between a slice and the code that uses it. It acts as a gateway, controlling which objects are accessible and how they can be imported.

**Implementation:** Typically an `index.ts` barrel file with explicit re-exports.

## Three Goals of Quality Public APIs

1. **Protection from structural changes** - Shield the rest of the application from internal slice refactoring
2. **Behavioral transparency** - Significant behavior changes should reflect in the public API
3. **Selective exposure** - Only necessary components should be exposed

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

**Usage:**

```typescript
// In features/auth/ui/ProfileSection.tsx
import { UserCard, type User } from '@/entities/user';
// NOT: import { UserCard } from '@/entities/user/ui/UserCard';
```

---

## Anti-Pattern: Wildcard Exports

**Avoid this:**

```typescript
// entities/user/index.ts
export * from './ui';
export * from './api';
export * from './model';
```

**Problems:**
- Reduces discoverability of slice interface
- Accidentally exposes internal implementation
- Complicates future refactoring
- Makes tree-shaking less effective

---

## Segment-Level Public APIs

For large slices, define public APIs per segment:

```
entities/user/
├── ui/
│   ├── UserCard.tsx
│   ├── UserAvatar.tsx
│   └── index.ts        # UI segment public API
├── api/
│   ├── userApi.ts
│   └── index.ts        # API segment public API
├── model/
│   ├── types.ts
│   ├── schema.ts
│   └── index.ts        # Model segment public API
└── index.ts            # Slice public API (re-exports from segments)
```

```typescript
// entities/user/ui/index.ts
export { UserCard } from './UserCard';
export { UserAvatar } from './UserAvatar';

// entities/user/index.ts
export * from './ui';
export * from './api';
export * from './model';
```

---

## Cross-Imports with @x Notation

When entities need to reference each other legitimately:

```
entities/
├── song/
│   ├── @x/
│   │   └── artist.ts   # Special API for artist entity
│   ├── model/
│   │   └── types.ts
│   └── index.ts
└── artist/
    ├── model/
    │   └── types.ts    # Imports Song from @x
    └── index.ts
```

```typescript
// entities/song/@x/artist.ts
// Only expose what artist needs
export type { Song, SongId } from '../model/types';

// entities/artist/model/types.ts
import type { Song } from '@/entities/song/@x/artist';

export interface Artist {
  name: string;
  songs: Song[];
}
```

**Guidelines for @x:**
- Keep cross-imports minimal
- Document why the cross-reference exists
- Consider if entities should be merged
- Use only on Entities layer

---

## Avoiding Circular Imports

**Problem:** Within a slice, importing from the index file can cause circular dependencies.

```typescript
// entities/user/model/store.ts
// BAD: Causes circular import
import { UserCard } from '../index';

// GOOD: Use direct relative import
import { UserCard } from '../ui/UserCard';
```

**Rule:** Within a slice, use relative imports. Only external consumers use the public API.

---

## Tree-Shaking Optimization

For large shared UI libraries, split into component-level indices:

```
shared/ui/
├── Button/
│   ├── Button.tsx
│   └── index.ts
├── Input/
│   ├── Input.tsx
│   └── index.ts
├── Modal/
│   ├── Modal.tsx
│   └── index.ts
└── index.ts           # Re-exports all (optional)
```

**Import patterns:**

```typescript
// Full import (may bundle everything)
import { Button, Input } from '@/shared/ui';

// Selective import (better tree-shaking)
import { Button } from '@/shared/ui/Button';
import { Input } from '@/shared/ui/Input';
```

---

## TypeScript Path Aliases

Configure path aliases for clean imports:

```json
// tsconfig.json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

**Usage:**

```typescript
import { UserCard } from '@/entities/user';
import { Button } from '@/shared/ui';
import { AddToCart } from '@/features/add-to-cart';
```

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

// entities/product/model/schema.ts
import { z } from 'zod';

export const productSchema = z.object({
  id: z.string(),
  name: z.string().min(1),
  price: z.number().positive(),
  imageUrl: z.string().url(),
  category: z.string(),
});

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

// entities/product/index.ts (PUBLIC API)
// UI exports
export { ProductCard } from './ui/ProductCard';

// API exports
export { getProducts, getProductById } from './api/productApi';

// Model exports
export type { Product, ProductFilters } from './model/types';
export { productSchema } from './model/schema';
```
