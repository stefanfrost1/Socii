# CLAUDE.md

This file provides guidance for AI assistants (Claude and others) working in this repository.

## Project Overview

**Socii** is a project currently in its initial state. This repository was initialized with a single README and is ready for development.

- **Repository**: stefanfrost1/Socii
- **Default branch**: `main`

## Repository Structure

```
/
└── README.md      # Project title placeholder
```

As the project grows, update this section to reflect new directories and files.

## Git Workflow

### Branch Naming

- Feature branches from Claude agents: `claude/<short-description>-<session-id>`
- Feature branches from humans: `feat/<short-description>`
- Bug fixes: `fix/<short-description>`

### Development Flow

1. Always develop on the designated branch (never push directly to `main`).
2. Create the branch locally if it does not exist, then push with tracking:
   ```bash
   git checkout -b <branch-name>
   git push -u origin <branch-name>
   ```
3. Write clear, descriptive commit messages in the imperative mood (e.g., `Add user authentication module`).
4. Open a pull request targeting `main` when work is complete.

### Push Instructions

```bash
git push -u origin <branch-name>
```

- Retry on network failure with exponential backoff: 2s, 4s, 8s, 16s.
- Never force-push to `main`.

## Development Guidelines

### General Conventions

- Keep commits atomic — one logical change per commit.
- Do not commit secrets, credentials, or environment-specific configuration.
- Write code that is readable and self-documenting; add comments only where logic is non-obvious.
- Prefer editing existing files over creating new ones unless a new file is clearly warranted.
- Avoid over-engineering; build only what is needed for the current task.

### Adding Technology Stack

When a technology stack is chosen, update this file with:

- **Language / runtime** and version requirements
- **Framework** and key libraries
- **Package manager** commands (install, build, test, lint)
- **Environment variables** required and how to configure them
- **Database / external services** and how to run them locally

## Testing

No test suite has been configured yet. When tests are added, document:

- How to run the full test suite
- How to run a single test file
- Required environment setup before running tests

## Build & Deployment

No build pipeline exists yet. When CI/CD is configured, document:

- Build commands
- Environment variable requirements
- Deployment targets and process

## Common Tasks for AI Assistants

| Task | Notes |
|------|-------|
| Explore the codebase | Read key files before suggesting changes |
| Make changes | Edit existing files where possible; keep diffs minimal |
| Commit work | Use descriptive imperative-mood messages |
| Push changes | Use `git push -u origin <branch>` targeting the designated branch |
| Open a PR | Target `main`; summarize changes and include a test plan |

## Updating This File

Keep CLAUDE.md current as the project evolves:
- Add new top-level directories to the structure section when they are introduced.
- Document new commands (build, test, lint) as tooling is added.
- Record architecture decisions and key conventions as patterns emerge.
