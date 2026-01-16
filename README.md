# cc-plugins

Custom Claude Code plugins for enhanced development workflows.

## Installation

### Using add-skill (Recommended)

```bash
npx add-skill ccheney/cc-plugins
```

This installs skills to your project's `.claude/skills/` directory. Use `-g` for global installation.

### Using Claude Code Plugin Marketplace

```bash
/plugin marketplace add ccheney/cc-plugins
```

### Using Claude CLI

```bash
claude plugin install ccheney/cc-plugins
```

## Skills

| Skill | Description |
|-------|-------------|
| [mermaid-diagrams](skills/mermaid-diagrams/) | Generate Mermaid diagrams in markdown |
| [postgres-drizzle](skills/postgres-drizzle/) | PostgreSQL 18 + Drizzle ORM best practices |
