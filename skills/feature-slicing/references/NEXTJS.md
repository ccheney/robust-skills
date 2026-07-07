# FSD with Next.js Integration

> **Source:** [Official Next.js Guide](https://feature-sliced.design/docs/guides/tech/with-nextjs)

## Table of Contents

- [The Conflict and the Official Fix](#the-conflict-and-the-official-fix)
- [App Router Setup](#app-router-setup)
- [Server vs Client Public APIs (index.server.ts)](#server-vs-client-public-apis-indexserverts)
- [Server Actions in Features](#server-actions-in-features)
- [Route Handlers (API Routes)](#route-handlers-api-routes)
- [Proxy / Middleware](#proxy--middleware)
- [Loading, Error, Not-Found Conventions](#loading-error-not-found-conventions)
- [Pages Router Setup (Legacy)](#pages-router-setup-legacy)
- [Best Practices](#best-practices)

---

## The Conflict and the Official Fix

Next.js reserves the folder names `app/` (App Router) and `pages/` (Pages Router) — the same names as two FSD layers. If FSD's `pages/` sits where Next.js can see it, Next.js tries to route it.

**Official recommendation:** keep the Next.js routing folders at the **project root**, put all FSD layers in `src/`, and rename the FSD `app` and `pages` layers to **`_app`** and **`_pages`** — regardless of which router you use. The underscore prefix removes any ambiguity about which folder belongs to the framework and which to your architecture.

```
├── app/                     # Next.js App Router — routing ONLY
│   ├── layout.tsx
│   ├── page.tsx
│   ├── api/
│   └── products/
│       └── [id]/
│           └── page.tsx
├── proxy.ts                 # Next.js 16+ (middleware.ts before 16)
├── next.config.ts
└── src/
    ├── _app/                # FSD app layer (renamed)
    │   ├── providers/
    │   ├── api-routes/      # Route Handler implementations
    │   └── styles/
    ├── _pages/              # FSD pages layer (renamed)
    │   ├── home/
    │   └── product-detail/
    ├── widgets/
    ├── features/
    ├── entities/
    └── shared/
```

Some codebases use `views/` instead of `_pages/` — any non-conflicting name works, but pick one convention and keep it; this guide uses the official `_app`/`_pages`.

**Path alias** stays the usual:

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": { "@/*": ["./src/*"] }
  }
}
```

---

## App Router Setup

### Keep Next.js routes thin: re-export from `_pages`

Every `page.tsx` in the root `app/` folder is a one-line re-export. All real UI, state, and composition live in the FSD page slice.

```typescript
// app/page.tsx
export { HomePage as default } from '@/_pages/home';

// app/products/[id]/page.tsx
export { ProductDetailPage as default, generateMetadata } from '@/_pages/product-detail';
```

### FSD page implementation

Since Next.js 15, `params` and `searchParams` are **Promises** — type them as such and `await` them (in Client Components, unwrap with `React.use()`).

```tsx
// src/_pages/product-detail/ui/ProductDetailPage.tsx  (Server Component)
import { getProductById } from '@/entities/product';
import { AddToCart } from '@/features/add-to-cart';

export async function ProductDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const product = await getProductById(id);

  return (
    <main>
      <h1>{product.name}</h1>
      <AddToCart productId={product.id} />
    </main>
  );
}
```

```typescript
// src/_pages/product-detail/index.ts
export { ProductDetailPage } from './ui/ProductDetailPage';
export { generateMetadata } from './api/metadata';
```

### Root layout with providers

```tsx
// app/layout.tsx
import { Providers } from '@/_app/providers';
import '@/_app/styles/globals.css';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
```

```tsx
// src/_app/providers/index.tsx
'use client';

import { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from 'next-themes';

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient());

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider attribute="class" defaultTheme="system">
        {children}
      </ThemeProvider>
    </QueryClientProvider>
  );
}
```

---

## Server vs Client Public APIs (index.server.ts)

A slice's `index.ts` barrel mixes everything it exports. If a server-only module (Server Component, data-access function importing `server-only`, DB client) is exported from `index.ts`, its server-only side effects propagate into the client module graph the moment a Client Component imports *anything* from that slice — and the build fails.

**Official fix:** split the public API. Client-safe exports stay in `index.ts`; server-only exports go in `index.server.ts`.

```typescript
// entities/product/index.ts        — safe to import anywhere
export { ProductCard } from './ui/ProductCard';
export type { Product } from './model/types';

// entities/product/index.server.ts — server-only public API
export { getProductById, getProducts } from './api/queries';
```

```typescript
// Server Component / Route Handler / Server Action:
import { getProductById } from '@/entities/product/index.server';

// Client Component:
import { ProductCard } from '@/entities/product';
```

Enforce the boundary by putting `import 'server-only';` at the top of the server-only modules (`npm i server-only`).

---

## Server Actions in Features

Server actions belong in the `api/` segment of the feature (or page) that owns the interaction. Note `cookies()` is async since Next.js 15 — `await` it.

```typescript
// src/features/auth/api/actions.ts
'use server';

import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';
import { loginSchema } from '../model/schema';

export async function loginAction(_prevState: unknown, formData: FormData) {
  const result = loginSchema.safeParse({
    email: formData.get('email'),
    password: formData.get('password'),
  });
  if (!result.success) {
    return { errors: result.error.flatten().fieldErrors };
  }

  const response = await fetch(`${process.env.API_URL}/auth/login`, {
    method: 'POST',
    body: JSON.stringify(result.data),
    headers: { 'Content-Type': 'application/json' },
  });
  if (!response.ok) {
    return { errors: { form: ['Invalid credentials'] } };
  }

  const { token } = await response.json();
  const cookieStore = await cookies();
  cookieStore.set('token', token, { httpOnly: true, secure: true });
  redirect('/dashboard');
}
```

---

## Route Handlers (API Routes)

Next.js requires `route.ts` files to live inside the root `app/` folder. Keep them as thin re-exports; implement handlers in an `api-routes` segment of the FSD `_app` layer:

```typescript
// app/api/products/route.ts
export { GET, POST } from '@/_app/api-routes/products';
```

```typescript
// src/_app/api-routes/products.ts
import { NextResponse, type NextRequest } from 'next/server';
import { getProducts } from '@/entities/product/index.server';

export async function GET(request: NextRequest) {
  const category = request.nextUrl.searchParams.get('category') ?? undefined;
  const products = await getProducts({ category });
  return NextResponse.json(products);
}

export async function POST(request: NextRequest) {
  const body = await request.json();
  // ...
  return NextResponse.json({ ok: true }, { status: 201 });
}
```

FSD is a frontend methodology — that's what readers expect to find in the tree. If backend code grows beyond a handful of handlers, move it to a separate package/app in a monorepo rather than growing it inside FSD layers.

---

## Proxy / Middleware

Next.js 16 renamed `middleware.ts` to `proxy.ts` (exported function `proxy`, Node.js runtime; `middleware.ts` still works but is deprecated and Edge-only). It lives at the project root (or in `src/`), outside FSD layers.

```typescript
// proxy.ts  (Next.js 16+; for Next.js 15, name it middleware.ts / export middleware)
import { NextResponse, type NextRequest } from 'next/server';

export function proxy(request: NextRequest) {
  const token = request.cookies.get('token')?.value;
  const isProtected = request.nextUrl.pathname.startsWith('/dashboard');

  if (isProtected && !token) {
    return NextResponse.redirect(new URL('/login', request.url));
  }
  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*'],
};
```

Don't keep both `middleware.ts` and `proxy.ts` — behavior becomes undefined.

---

## Loading, Error, Not-Found Conventions

These are Next.js file conventions, so they stay in the root `app/` folder — but import their UI from FSD layers:

```tsx
// app/products/loading.tsx
export { ProductListSkeleton as default } from '@/widgets/product-list';
```

```tsx
// app/products/error.tsx
'use client';

import { Button } from '@/shared/ui/button';

export default function Error({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <div>
      <h2>Something went wrong</h2>
      <p>{error.message}</p>
      <Button onClick={reset}>Try again</Button>
    </div>
  );
}
```

---

## Pages Router Setup (Legacy)

Same principle for older projects: root `pages/` holds thin re-exports, FSD layers live in `src/` as `_app`/`_pages`.

```
├── pages/                    # Next.js Pages Router — routing only
│   ├── _app.tsx
│   ├── index.tsx
│   └── products/
│       └── [id].tsx
└── src/
    ├── _app/
    ├── _pages/
    ├── widgets/ features/ entities/ shared/
```

```tsx
// pages/_app.tsx
export { App as default } from '@/_app/app';

// pages/products/[id].tsx
import { ProductDetailPage } from '@/_pages/product-detail';
import { getProductById } from '@/entities/product';
import type { GetServerSideProps } from 'next';

export default ProductDetailPage;

export const getServerSideProps: GetServerSideProps = async ({ params }) => {
  const product = await getProductById(params?.id as string);
  if (!product) return { notFound: true };
  return { props: { product } };
};
```

---

## Best Practices

1. **Root `app/` contains routing only** — every `page.tsx`, `layout.tsx`, `route.ts` is a re-export or a few lines of glue.
2. **Rename FSD layers to `_app`/`_pages`** — never fight the framework over folder names.
3. **Split public APIs by runtime** — `index.ts` client-safe, `index.server.ts` server-only, `import 'server-only'` to enforce.
4. **Server Components by default** — add `'use client'` at the leaves (interactive components), not on whole slices.
5. **`await` dynamic APIs** — `params`, `searchParams`, `cookies()`, `headers()` are Promises since Next.js 15.
6. **Server actions live in the owning slice's `api/` segment** — a page-local form's action belongs in that page slice (pages-first).
7. **Backend code beyond a few handlers → separate monorepo package**, not FSD layers.

---

## Resources

| Resource | Link |
|----------|------|
| Official FSD + Next.js guide | https://feature-sliced.design/docs/guides/tech/with-nextjs |
| Next.js async dynamic APIs | https://nextjs.org/docs/messages/sync-dynamic-apis |
| Next.js middleware → proxy | https://nextjs.org/docs/messages/middleware-to-proxy |
