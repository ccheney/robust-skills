# FSD Quick Reference Cheatsheet

## Layer Hierarchy (Top → Bottom)

```mermaid
flowchart TB
    subgraph LAYERS[" "]
        direction TB
        APP[app/<br/>Global: routing, providers, styles]:::app
        PAGES[pages/<br/>Routes: one slice per screen]:::pages
        WIDGETS[widgets/<br/>Composed: reusable UI blocks]:::widgets
        FEATURES[features/<br/>Actions: user interactions]:::features
        ENTITIES[entities/<br/>Data: business domain models]:::entities
        SHARED[shared/<br/>Utils: project-agnostic code]:::shared
    end

    APP --> PAGES --> WIDGETS --> FEATURES --> ENTITIES --> SHARED

    classDef app fill:#ef4444,stroke:#b91c1c,color:white
    classDef pages fill:#f97316,stroke:#c2410c,color:white
    classDef widgets fill:#eab308,stroke:#a16207,color:white
    classDef features fill:#22c55e,stroke:#15803d,color:white
    classDef entities fill:#3b82f6,stroke:#1d4ed8,color:white
    classDef shared fill:#8b5cf6,stroke:#6d28d9,color:white
```

**Rule:** Import only from layers BELOW. Never sideways or up.

---

## Quick Decision Tree

### "Where does this code go?"

```mermaid
flowchart LR
    Q1[Reusable without<br/>business logic?] --> SHARED[shared/]:::shared
    Q2[Data model?<br/>user, product] --> ENTITIES[entities/]:::entities
    Q3[User action?<br/>login, add-to-cart] --> FEATURES[features/]:::features
    Q4[Complex reusable<br/>UI block?] --> WIDGETS[widgets/]:::widgets
    Q5[Route/screen?] --> PAGES[pages/]:::pages
    Q6[App init/config?] --> APP[app/]:::app

    classDef app fill:#ef4444,stroke:#b91c1c,color:white
    classDef pages fill:#f97316,stroke:#c2410c,color:white
    classDef widgets fill:#eab308,stroke:#a16207,color:white
    classDef features fill:#22c55e,stroke:#15803d,color:white
    classDef entities fill:#3b82f6,stroke:#1d4ed8,color:white
    classDef shared fill:#8b5cf6,stroke:#6d28d9,color:white
```

### "Entity or Feature?"

| Entity (noun) | Feature (verb) |
|---------------|----------------|
| `user` | `auth` (login/logout) |
| `product` | `add-to-cart` |
| `comment` | `write-comment` |
| `order` | `checkout` |

---

## Segment Cheatsheet

| Segment | Purpose | Examples |
|---------|---------|----------|
| `ui/` | Components, styles | `UserCard.tsx`, `Button.tsx` |
| `api/` | Backend calls | `getUser()`, `createOrder()` |
| `model/` | Types, schemas, stores | `User`, `userSchema`, `useUserStore` |
| `lib/` | Slice utilities | `formatUserName()` |
| `config/` | Configuration | Feature flags, constants |

---

## File Structure Templates

### Entity

```
entities/{name}/
├── ui/
│   ├── {Name}Card.tsx
│   ├── {Name}Avatar.tsx
│   └── index.ts
├── api/
│   ├── {name}Api.ts
│   └── index.ts
├── model/
│   ├── types.ts
│   ├── schema.ts
│   ├── store.ts
│   └── index.ts
└── index.ts
```

### Feature

```
features/{name}/
├── ui/
│   ├── {Name}Form.tsx
│   ├── {Name}Button.tsx
│   └── index.ts
├── api/
│   ├── {name}Api.ts
│   └── index.ts
├── model/
│   ├── types.ts
│   ├── schema.ts
│   ├── store.ts
│   └── index.ts
└── index.ts
```

### Page

```
pages/{name}/
├── ui/
│   ├── {Name}Page.tsx
│   └── index.ts
├── api/
│   └── loader.ts       # Optional: data fetching
└── index.ts
```

---

## Public API Pattern

```typescript
// entities/user/index.ts
// UI exports
export { UserCard } from './ui/UserCard';
export { UserAvatar } from './ui/UserAvatar';

// API exports
export { getUser, updateUser } from './api/userApi';

// Model exports
export type { User, UserRole } from './model/types';
export { userSchema } from './model/schema';
export { useUserStore } from './model/store';
```

**Import from public API only:**
```typescript
// ✅ Correct
import { UserCard, type User } from '@/entities/user';

// ❌ Wrong - bypasses public API
import { UserCard } from '@/entities/user/ui/UserCard';
```

---

## TypeScript Path Aliases

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

---

## Cross-Entity References (@x)

When entities must reference each other:

```
entities/product/@x/order.ts  → API for order to import
```

```typescript
// entities/product/@x/order.ts
export type { ProductId } from '../model/types';

// entities/order/model/types.ts
import type { ProductId } from '@/entities/product/@x/order';
```

---

## Common Anti-Patterns

| ❌ Don't | ✅ Do |
|----------|-------|
| Import from higher layer | Import from lower layers only |
| Cross-slice imports at same layer | Use lower layer or @x notation |
| Generic segments: `components/`, `hooks/` | Purpose segments: `ui/`, `lib/` |
| Wildcard exports: `export *` | Explicit exports |
| Business logic in `shared/` | Keep shared domain-agnostic |
| Single-use widgets | Keep in page slice |

---

## Layer Import Matrix

|  | app | pages | widgets | features | entities | shared |
|--|-----|-------|---------|----------|----------|--------|
| **app** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **pages** | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| **widgets** | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| **features** | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| **entities** | ❌ | ❌ | ❌ | ❌ | ❌* | ✅ |
| **shared** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

*Use @x notation for cross-entity references

---

## Minimal FSD Setup

For smaller projects, start with:

```
src/
├── app/          # Required
├── pages/        # Required
└── shared/       # Required
```

Add `entities/`, `features/`, `widgets/` as needed.

---

## Resources

- **Official Docs:** https://feature-sliced.design
- **GitHub:** https://github.com/feature-sliced
- **Examples:** https://github.com/feature-sliced/examples
- **Discord:** https://discord.gg/S8MzWTUsmp
