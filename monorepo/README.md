# Monorepo Setup

This monorepo uses `uv` for Python and `pnpm` for JavaScript.

## Structure

```
data-creator-finetune/
├── monorepo/
│   ├── README.md
│   └── setup.sh
├── src/
│   ├── api/          # FastAPI backend
│   └── web/          # Next.js frontend
├── infrastructure/   # Kubernetes manifests
└── docs/             # Documentation
```

## Prerequisites

- Python 3.12+
- Node.js 20+
- pnpm 8+
- uv 0.4+

## Setup

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install pnpm
npm install -g pnpm

# Setup the monorepo
cd monorepo
./setup.sh
```

## Development

```bash
# Install all dependencies
make deps

# Run API
make api

# Run web
make web

# Run all
make dev
```

## CI/CD

```bash
# Build multi-arch images
make build-multiarch

# Run tests
make test

# Lint
make lint
```
