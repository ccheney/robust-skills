# robust-skills

Production-grade skills that encode battle-tested architectural patterns and best practices directly into your AI-assisted development workflow.

## Overview

**robust-skills** extends AI coding agents with domain-specific expertise for building maintainable, scalable software. Each skill packages comprehensive knowledge—architectural patterns, code examples, anti-patterns to avoid—so your agent can guide you toward robust implementations from the start.

**Why skills matter:**
- **Consistency** — Apply the same proven patterns across your entire codebase
- **Speed** — Skip the research phase; best practices are built-in
- **Quality** — Avoid common pitfalls with anti-pattern awareness
- **Learning** — Each skill includes reference documentation for deeper understanding

## Skills

| Skill | Domain | Description |
|-------|--------|-------------|
| [clean-ddd-hexagonal](skills/clean-ddd-hexagonal/) | Backend | Clean Architecture + DDD + Hexagonal patterns for maintainable services |
| [feature-slicing](skills/feature-slicing/) | Frontend | Feature-Sliced Design (FSD) for scalable React/Next.js/Vue projects |
| [mermaid-diagrams](skills/mermaid-diagrams/) | Documentation | Generate architectural diagrams in markdown |
| [postgres-drizzle](skills/postgres-drizzle/) | Database | PostgreSQL 18 + Drizzle ORM type-safe database patterns |

## Installation

```bash
npx add-skill ccheney/robust-skills
```

### Install a Specific Skill

```bash
npx add-skill ccheney/robust-skills/clean-ddd-hexagonal
npx add-skill ccheney/robust-skills/feature-slicing
npx add-skill ccheney/robust-skills/mermaid-diagrams
npx add-skill ccheney/robust-skills/postgres-drizzle
```

## Usage

Once installed, skills activate automatically based on context. You can also invoke them explicitly:

```
# Architecture skills trigger on relevant tasks
"Set up a new Express API with clean architecture"
"Create a new feature for user authentication using FSD"

# Or reference directly
"Use the postgres-drizzle skill to design my schema"
"Generate a mermaid diagram showing the data flow"
```

## Skill Overview

### clean-ddd-hexagonal

Combines three complementary patterns for building maintainable, testable backend systems:

- **Domain-Driven Design (DDD)** — Strategic and tactical patterns for modeling complex business domains
- **Clean Architecture** — Dependency rules ensuring business logic independence
- **Hexagonal Architecture** — Ports & Adapters for external system isolation

Language-agnostic: works with Go, Rust, Python, TypeScript, Java, and any backend language.

### feature-slicing

Feature-Sliced Design (FSD) is an architectural methodology for scaffolding frontend applications with rules and conventions for organizing code to remain understandable and stable amid changing business requirements.

- **Layers** — 7 standardized horizontal levels (app, pages, widgets, features, entities, shared)
- **Import Rule** — Modules can only import from layers strictly below them
- **Slices** — Business-domain partitions within layers
- **Segments** — Purpose-based groupings (ui, api, model, lib, config)

### mermaid-diagrams

Generate diagrams using Mermaid syntax in markdown code blocks. Diagrams render automatically in GitHub, GitLab, Obsidian, Notion, VS Code, and most documentation platforms.

Supports flowcharts, sequence diagrams, class diagrams, ER diagrams, state machines, user journeys, Gantt charts, pie charts, mindmaps, timelines, git graphs, C4 architecture, and more.

### postgres-drizzle

Type-safe database applications with PostgreSQL 18 and Drizzle ORM.

- **Schema Definition** — Type-safe table definitions with TypeScript
- **Relations** — Declarative relationship mapping
- **Queries** — Type-safe query builder with full SQL power
- **Migrations** — Generated SQL migrations from schema changes
- **PostgreSQL 18** — UUIDv7, async I/O, index skip scan, RETURNING OLD/NEW
