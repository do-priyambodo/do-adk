---
trigger: model_decision
description: When writing React components or fetching data in Next.js
---

## Next.js Idioms and Patterns

This document outlines best practices and patterns for writing Next.js applications.

### Server vs Client Components

Next.js uses Server Components by default. You must explicitly opt-in to Client Components using the `'use client'` directive.

**Rules:**
- **Use Server Components for**: Data fetching, accessing backend resources directly, and keeping large dependencies off the client bundle.
- **Use Client Components for**: Interactivity (useState, useEffect), event listeners (onClick), and using browser-only APIs (localStorage, Web Audio).
- **Move Client Components to the Leaves**: Keep the tree mostly server-side and only use client components for the interactive parts to reduce bundle size.

### Data Fetching

**Rules:**
- **Fetch on the Server**: Prefer fetching data in Server Components using `async/await`.
- **Cache effectively**: Use Next.js's extended `fetch` with caching options or `unstable_cache` where appropriate.
- **Keep it clean**: Don't mix data fetching logic directly with UI components; use separate fetchers or API routes if needed.

### Performance & Optimization

**Rules:**
- **Use next/image**: Always use the `next/image` component for optimized images and layout shift prevention.
- **Font optimization**: Use `next/font` to automatically optimize fonts.
- **Dynamic Imports**: Use `next/dynamic` to lazy load heavy client components.
