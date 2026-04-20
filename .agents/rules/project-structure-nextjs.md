---
trigger: on_init
description: When setting up or organizing a Next.js (App Router) project
---

## Project Structure — Next.js (App Router)

This document outlines the standard project structure for Next.js applications using the App Router.

### Directory Layout

```text
my-app/
├── public/                 # Static assets (images, fonts, etc.)
├── src/
│   ├── app/                # App Router directory
│   │   ├── favicon.ico
│   │   ├── globals.css    # Global styles (Tailwind)
│   │   ├── layout.tsx     # Root layout
│   │   └── page.tsx       # Main page
│   ├── components/        # Reusable UI components
│   │   ├── ui/            # Shared primitives (buttons, inputs)
│   │   └── ...
│   └── lib/               # Utility functions and shared logic
│       ├── utils.ts
│       └── ...
├── .gcloudignore          # Cloud Build ignores
├── .gitignore
├── next.config.ts         # Next.js configuration
├── package.json
├── tailwind.config.ts     # Tailwind configuration
└── tsconfig.json          # TypeScript configuration
```

### Key Principles

1.  **Colocation**: Keep files close to where they are used. If a component is only used in one page, consider placing it in that page's directory.
2.  **Src Directory**: Always use the `src/` directory for source code to keep the project root clean.
3.  **App Router**: Prefer the App Router over the Pages Router for new projects.
4.  **Standalone Output**: Always enable `output: 'standalone'` in `next.config.ts` for optimized Docker builds.
