# Contributing to Forge

Thank you for your interest in contributing to Forge! This document describes how to contribute to this platform for building LLM/VLM training datasets.

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/0/code_of_conduct/).

## Getting Started

1. Read the [Architecture](docs/architecture.md) document to understand the system design
2. Review the [Tasks](docs/tasks.md) document to understand the implementation plan
3. Check out the [Monorepo Setup](monorepo/README.md) for development environment setup

## Contribution Guidelines

### Reporting Bugs

- Use the GitHub issue tracker
- Include steps to reproduce the issue
- Include expected vs actual behavior
- Include environment details (OS, Python version, etc.)
- Include relevant logs or error messages

### Suggesting Enhancements

- Open an issue with the `enhancement` label
- Describe the problem and proposed solution
- Explain why this enhancement would be useful to most users

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`make test`)
5. Run linting (`make lint`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to your branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Development Workflow

#### Setting Up

```bash
# Install dependencies
make deps

# Run tests
make test

# Run linting
make lint

# Start development servers
make dev
```

#### Code Style

- Python: Follow PEP 8 with 100 char line length (configured in `pyproject.toml`)
- TypeScript/JavaScript: Follow ESLint rules (configured in `tsconfig.json`)
- All code must pass type checking

#### Testing

- Write unit tests for new functionality
- Write integration tests for API endpoints
- Run tests before submitting PR: `make test`

#### Documentation

- Update documentation for new features
- Add docstrings to all public functions
- Update README.md if needed

### Architecture Principles

1. **Tenant isolation**: Never trust tenant ID from request body/path; always use token
2. **Intent-named endpoints**: No generic CRUD passthrough APIs
3. **ARM64-first**: All images must be multi-arch; no privileged containers
4. **Data integrity**: Every export must be reproducible from a version ID
5. **Security by default**: Deny by default, explicit allow-lists

### Review Process

1. At least one reviewer must approve
2. All tests must pass
3. Code must be linted and typed
4. Documentation must be updated
5. Architecture decisions must follow ADRs

### Questions?

Open an issue with the `question` label or reach out to the maintainers.
