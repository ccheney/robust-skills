# FSD Implementation Patterns

> Sources:
> - https://feature-sliced.design/docs/get-started/tutorial
> - https://feature-sliced.design/docs/guides/examples

## Project Setup

### Directory Scaffolding

```bash
mkdir -p src/{app,pages,widgets,features,entities,shared}/{ui,api,model,lib}
```

### Recommended Folder Structure

```
src/
├── app/
│   ├── providers/
│   │   ├── QueryProvider.tsx
│   │   ├── ThemeProvider.tsx
│   │   └── index.ts
│   ├── routes/
│   │   └── router.tsx
│   ├── styles/
│   │   └── globals.css
│   └── index.tsx
├── pages/
│   ├── home/
│   │   ├── ui/
│   │   │   └── HomePage.tsx
│   │   ├── api/
│   │   │   └── loader.ts
│   │   └── index.ts
│   └── ...
├── widgets/
│   └── ...
├── features/
│   └── ...
├── entities/
│   └── ...
└── shared/
    ├── ui/
    │   ├── Button/
    │   ├── Input/
    │   └── index.ts
    ├── api/
    │   ├── client.ts
    │   └── index.ts
    ├── lib/
    │   ├── dates.ts
    │   └── index.ts
    └── config/
        ├── env.ts
        └── index.ts
```

---

## Entity Implementation

### Complete Entity Example: User

A full entity implementation includes types, mapper, schema, API functions, and UI components.

**Model Layer:**

- [User types](../examples/entities/user-types.ts) - TypeScript interfaces for User and UserDTO
- [User mapper](../examples/entities/user-mapper.ts) - DTO to domain transformation
- [User schema](../examples/entities/user-schema.ts) - Zod validation schema

**API Layer:**

- [User API](../examples/entities/user-api.ts) - CRUD operations with API client

**UI Layer:**

- [UserAvatar](../examples/entities/user-avatar.tsx) - Avatar component with fallback
- [UserCard](../examples/entities/user-card.tsx) - User display card component

**Public API:**

- [User index](../examples/entities/user-index.ts) - Barrel file exporting public interface

### React Query Integration

For data fetching with React Query:

- [Product queries](../examples/entities/product-queries.ts) - Query keys, hooks, and mutations

---

## Feature Implementation

### Complete Feature Example: Authentication

Features implement user-facing interactions with business value.

**Model Layer:**

- [Auth types](../examples/features/auth-types.ts) - Login/register credentials, tokens
- [Auth schema](../examples/features/auth-schema.ts) - Zod validation for forms
- [Auth store](../examples/features/auth-store.ts) - Zustand store with persistence

**API Layer:**

- [Auth API](../examples/features/auth-api.ts) - Login, register, logout, refresh

**UI Layer:**

- [LoginForm](../examples/features/login-form.tsx) - Form with react-hook-form + zod
- [LogoutButton](../examples/features/logout-button.tsx) - Logout action button

**Public API:**

- [Auth index](../examples/features/auth-index.ts) - Feature public API

### State Management with Zustand

- [Cart store](../examples/features/cart-store.ts) - Shopping cart with persistence

---

## Widget Implementation

### Complete Widget Example: Header

Widgets compose features, entities, and shared components into reusable UI blocks.

- [Header widget](../examples/widgets/header.tsx) - Navigation with auth, search, user menu

---

## Page Implementation

### Complete Page Example: Product Detail

Pages orchestrate widgets, features, and entities for a specific route.

- [Product detail loader](../examples/pages/product-detail-loader.ts) - Data fetching
- [ProductDetailPage](../examples/pages/product-detail-page.tsx) - Page component
- [HomePage](../examples/pages/home-page.tsx) - Home page composition

---

## Shared Layer Patterns

### API Client

- [API client](../examples/shared/api-client.ts) - Axios with interceptors

### UI Components

- [Button](../examples/shared/button.tsx) - Reusable button with variants

---

## App Layer Patterns

### Providers

- [Providers](../examples/app/providers.tsx) - React Query + Theme provider setup
- [Root layout](../examples/app/root-layout.tsx) - Next.js root layout

### Server Actions (Next.js)

- [Server action](../examples/app/server-action.ts) - Login action with cookies

### Middleware

- [Middleware](../examples/app/middleware.ts) - Auth route protection

---

## Configuration

### TypeScript Path Aliases

- [tsconfig paths](../examples/config/tsconfig-paths.json) - Path alias setup
