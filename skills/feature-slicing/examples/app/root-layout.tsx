// src/app/layout.tsx
import { Providers } from './providers';
import './styles/globals.css';

/**
 * Props for the RootLayout component.
 */
interface RootLayoutProps {
  /** Page content to render within the layout. */
  children: React.ReactNode;
}

/**
 * Root layout component that wraps all pages in the application.
 *
 * @remarks
 * This is the top-level layout in Next.js App Router. It:
 * - Sets up the HTML document structure
 * - Imports global CSS styles
 * - Wraps content with application providers
 *
 * According to FSD, the app layer handles application-wide concerns
 * like providers, global styles, and routing configuration.
 *
 * @example
 * ```tsx
 * // This is used automatically by Next.js App Router
 * // All pages are rendered as children of this layout
 * ```
 */
export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
