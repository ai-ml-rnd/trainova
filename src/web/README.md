# Next.js Web Application Skeleton

This directory contains the Next.js application skeleton for the Forge platform.

## Structure

```
src/web/
├── app/
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Home page
│   ├── (auth)/              # Auth pages (login, register)
│   ├── (app)/               # App pages (protected)
│   ├── api/                 # API routes (BFF)
│   └── lib/                 # Utilities
├── components/              # Reusable components
│   ├── ui/                  # shadcn/ui components
│   └── layout/              # Layout components
├── public/                  # Static assets
├── styles/                  # Global styles
├── types/                   # TypeScript types
├── middleware.ts            # Middleware
├── next.config.ts           # Next.js config
├── tailwind.config.ts       # Tailwind config
└── tsconfig.json            # TypeScript config
```

## Quick Start

```bash
# Install dependencies
pnpm install

# Run dev server
pnpm dev

# Build for production
pnpm build
pnpm start
```

## App Router Structure

- `(auth)/`: Public routes (login, register, etc.)
- `(app)/`: Protected routes (requires auth)
- `api/`: BFF API routes (server-side only)

## Features

- Server-side rendering
- Streaming
- Server actions
- Client-side routing
