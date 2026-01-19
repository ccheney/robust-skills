# FSD with Next.js Integration

> Source: https://feature-sliced.design/docs/guides/tech/with-nextjs

## The Challenge

FSD conflicts with Next.js's built-in `app/` and `pages/` folders, which expect file structures matching URL routes. FSD uses flat slice architecture incompatible with Next.js file-based routing.

## Solution Overview

> **Note:** Next.js ignores `src/app/` if `app/` exists at root. Therefore, we place the entire App Router inside `src/app/` alongside FSD providers, keeping all code in `src/`.

Place the Next.js App Router in `src/app/` (no root `app/` folder). This directory serves double duty: Next.js routing AND the FSD app layer. Re-export page components from FSD `pages/` layer into route files.

---

## App Router Setup (Next.js 13+)

### Directory Structure

```
project-root/
├── src/
│   ├── app/                  # Next.js App Router + FSD app layer
│   │   ├── layout.tsx        # Root layout with providers
│   │   ├── page.tsx          # Home route → re-exports from pages/
│   │   ├── products/
│   │   │   ├── page.tsx
│   │   │   └── [id]/
│   │   │       └── page.tsx
│   │   ├── login/
│   │   │   └── page.tsx
│   │   ├── api/              # API routes
│   │   │   └── ...
│   │   ├── providers/        # FSD: React context providers
│   │   │   └── index.tsx
│   │   └── styles/           # FSD: Global styles
│   │       └── globals.css
│   ├── pages/                # FSD pages layer
│   │   ├── home/
│   │   ├── products/
│   │   ├── product-detail/
│   │   └── login/
│   ├── widgets/
│   ├── features/
│   ├── entities/
│   └── shared/
├── middleware.ts             # Next.js middleware
└── next.config.js
```

### Page Re-Export Pattern

```typescript
// src/app/page.tsx (Next.js route)
export { HomePage as default } from '@/pages/home';

// src/app/products/page.tsx
export { ProductsPage as default } from '@/pages/products';

// src/app/products/[id]/page.tsx
export { ProductDetailPage as default } from '@/pages/product-detail';
```

### FSD Page Implementation

```typescript
// src/pages/home/ui/HomePage.tsx
import { Header } from '@/widgets/header';
import { FeaturedProducts } from '@/widgets/featured-products';
import { HeroSection } from './HeroSection';

export function HomePage() {
  return (
    <>
      <Header />
      <main>
        <HeroSection />
        <FeaturedProducts />
      </main>
    </>
  );
}

// src/pages/home/index.ts
export { HomePage } from './ui/HomePage';
```

### Root Layout with FSD Providers

```typescript
// src/app/layout.tsx
import { Providers } from './providers';
import './styles/globals.css';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}

// src/app/providers/index.tsx
'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from 'next-themes';

const queryClient = new QueryClient();

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider attribute="class" defaultTheme="system">
        {children}
      </ThemeProvider>
    </QueryClientProvider>
  );
}
```

### Server Components with FSD

```typescript
// src/app/products/[id]/page.tsx
import { ProductDetailPage } from '@/pages/product-detail';
import { getProductById } from '@/entities/product';

interface Props {
  params: { id: string };
}

export default async function Page({ params }: Props) {
  const product = await getProductById(params.id);
  return <ProductDetailPage product={product} />;
}

// Generate static paths
export async function generateStaticParams() {
  const products = await getProducts();
  return products.map((product) => ({ id: product.id }));
}
```

### Server Actions

```typescript
// src/features/auth/api/actions.ts
'use server';

import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';
import { loginSchema } from '../model/schema';

export async function loginAction(formData: FormData) {
  const rawData = {
    email: formData.get('email'),
    password: formData.get('password'),
  };

  const result = loginSchema.safeParse(rawData);
  if (!result.success) {
    return { errors: result.error.flatten().fieldErrors };
  }

  // Call your auth API
  const response = await fetch(`${process.env.API_URL}/auth/login`, {
    method: 'POST',
    body: JSON.stringify(result.data),
  });

  if (!response.ok) {
    return { errors: { form: ['Invalid credentials'] } };
  }

  const { token } = await response.json();
  cookies().set('token', token, { httpOnly: true });
  redirect('/dashboard');
}
```

---

## Pages Router Setup (Next.js 12)

### Directory Structure

```
project-root/
├── pages/                    # Next.js Pages Router
│   ├── _app.tsx              # Custom App
│   ├── _document.tsx
│   ├── index.tsx             # Home → re-exports from src/pages
│   ├── products/
│   │   ├── index.tsx
│   │   └── [id].tsx
│   └── api/
│       └── ...
├── src/
│   ├── app/
│   │   ├── custom-app/       # _app component
│   │   └── providers/
│   ├── pages/
│   │   ├── home/
│   │   └── products/
│   ├── widgets/
│   ├── features/
│   ├── entities/
│   └── shared/
└── next.config.js
```

### Custom App Component

```typescript
// pages/_app.tsx
export { CustomApp as default } from '@/app/custom-app';

// src/app/custom-app/CustomApp.tsx
import type { AppProps } from 'next/app';
import { Providers } from '../providers';
import '../styles/globals.css';

export function CustomApp({ Component, pageProps }: AppProps) {
  return (
    <Providers>
      <Component {...pageProps} />
    </Providers>
  );
}
```

### Page Re-Exports with getServerSideProps

```typescript
// pages/products/[id].tsx
import { ProductDetailPage } from '@/pages/product-detail';
import { getProductById } from '@/entities/product';
import type { GetServerSideProps } from 'next';

export default ProductDetailPage;

export const getServerSideProps: GetServerSideProps = async ({ params }) => {
  const product = await getProductById(params?.id as string);

  if (!product) {
    return { notFound: true };
  }

  return {
    props: { product },
  };
};
```

---

## TypeScript Configuration

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

---

## API Routes Guidance

FSD is frontend-focused. For API routes:

### Option 1: Keep in `src/app/api/`

```
src/app/
├── api/
│   ├── auth/
│   │   └── route.ts
│   └── products/
│       └── route.ts
```

### Option 2: Separate Backend Package (Monorepo)

```
packages/
├── frontend/          # Next.js + FSD
│   └── src/
│       ├── app/       # App Router + FSD app layer
│       ├── pages/     # FSD pages layer
│       └── ...
└── backend/           # Express/Fastify
    └── src/
        └── routes/
```

### Option 3: Re-export API handlers

```typescript
// src/app/api-handlers/auth.ts
import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  // Auth logic
}

// src/app/api/auth/route.ts
export { POST } from '../api-handlers/auth';
```

---

## Database & Data Fetching

### Database Queries in Shared

```typescript
// shared/db/client.ts
import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';

const connectionString = process.env.DATABASE_URL!;
const client = postgres(connectionString);

export const db = drizzle(client);
```

```typescript
// shared/db/queries/products.ts
import { db } from '../client';
import { products } from '../schema';

export async function getAllProducts() {
  return db.select().from(products);
}

export async function getProductById(id: string) {
  return db.select().from(products).where(eq(products.id, id)).limit(1);
}
```

### Entity API Using Shared DB

```typescript
// entities/product/api/productApi.ts
import { getAllProducts, getProductById as dbGetProduct } from '@/shared/db/queries/products';
import { mapProductRow } from '../model/mapper';
import type { Product } from '../model/types';

export async function getProducts(): Promise<Product[]> {
  const rows = await getAllProducts();
  return rows.map(mapProductRow);
}

export async function getProductById(id: string): Promise<Product | null> {
  const [row] = await dbGetProduct(id);
  return row ? mapProductRow(row) : null;
}
```

---

## Middleware Integration

```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('token')?.value;
  const isAuthPage = request.nextUrl.pathname.startsWith('/login');
  const isProtectedRoute = request.nextUrl.pathname.startsWith('/dashboard');

  if (isProtectedRoute && !token) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  if (isAuthPage && token) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*', '/login'],
};
```

---

## Common Patterns

### Loading States

```typescript
// src/app/products/loading.tsx
import { ProductListSkeleton } from '@/widgets/product-list';

export default function Loading() {
  return <ProductListSkeleton />;
}

// widgets/product-list/ui/ProductListSkeleton.tsx
export function ProductListSkeleton() {
  return (
    <div className="grid grid-cols-3 gap-4">
      {Array.from({ length: 6 }).map((_, i) => (
        <div key={i} className="h-64 bg-gray-200 animate-pulse rounded-lg" />
      ))}
    </div>
  );
}
```

### Error Boundaries

```typescript
// src/app/products/error.tsx
'use client';

import { Button } from '@/shared/ui';

export default function Error({
  error,
  reset,
}: {
  error: Error;
  reset: () => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <h2 className="text-xl font-bold mb-4">Something went wrong!</h2>
      <p className="text-gray-600 mb-4">{error.message}</p>
      <Button onClick={reset}>Try again</Button>
    </div>
  );
}
```

---

## Best Practices

1. **Keep Next.js routes thin** - Only re-exports and data fetching
2. **All UI logic in FSD layers** - Components, state, business logic
3. **Use path aliases** - Clean imports across layers
4. **Server Components default** - Add `'use client'` only when needed
5. **Colocate server actions** - In feature's `api/` segment with `'use server'`
6. **Shared DB queries** - Keep database logic in `shared/db/`
