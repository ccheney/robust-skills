---
name: clean-ddd-hexagonal
description: Design or review backend domain and dependency boundaries using DDD, Clean Architecture, and ports/adapters. Use for aggregate modeling, bounded contexts, use-case isolation, or architecture refactoring; not routine CRUD changes.
---

# Clean Architecture, DDD, and Hexagonal Architecture

Use these related patterns to solve a concrete domain or dependency problem. This is an opinionated synthesis, not a mandatory folder layout. The user's explicit instructions take precedence over this skill's guidelines.

## Choose the scope

Start from the requested behavior, existing domain model, and current dependencies. Preserve the project's language and architecture unless changing them is part of the task. Simple CRUD can remain simple; team size, entity count, and file length do not determine whether DDD is appropriate.

| Design question | Relevant pattern |
|---|---|
| What language and consistency rules describe the business? | DDD, bounded contexts, aggregates |
| Which way should source dependencies point? | Clean/Onion Architecture |
| How can the application use different interfaces or infrastructure? | Hexagonal ports and adapters |
| Do reads and writes need different models? | CQRS |
| Must state be reconstructed from an event history? | Event Sourcing |

If a business invariant is unknown, identify the specific missing rule and continue work that does not depend on it. Do not invent business behavior or require a discovery workshop for a local fix.

## Preserve the boundaries that matter

- Keep domain behavior independent of HTTP, persistence, and messaging implementations. Put orchestration in application use cases and external I/O in adapters.
- Model entity identity separately from value-object equality. Choose aggregate boundaries from transactional invariants and contention.
- Prefer transactions contained within an aggregate. When a requirement needs cross-aggregate atomicity, make that tradeoff explicit rather than silently replacing it with eventual consistency.
- Use an outbox when a committed database change and external event delivery must be reliable together.
- Treat CQRS, Event Sourcing, repository interfaces, and separate presentation folders as choices justified by the task. Adapt example naming and directories to the project.

Deliver the requested model, patch, or review with affected boundaries and the tradeoffs that explain them. Validate changed invariants and adapter contracts at the appropriate level; an architecture question does not require implementing every pattern.

## References

Load the reference for the decision being made, not the whole collection.

| Task | Reference |
|---|---|
| Layer placement, dependency direction, composition root | [LAYERS.md](references/LAYERS.md) |
| Bounded contexts, ubiquitous language, context mapping | [DDD-STRATEGIC.md](references/DDD-STRATEGIC.md) |
| Entities, value objects, aggregates, repositories | [DDD-TACTICAL.md](references/DDD-TACTICAL.md) |
| Ports, driver/driven adapters, alternative layouts | [HEXAGONAL.md](references/HEXAGONAL.md) |
| CQRS, events, outbox, sagas, Event Sourcing | [CQRS-EVENTS.md](references/CQRS-EVENTS.md) |
| Domain, integration, or architecture test design | [TESTING.md](references/TESTING.md) |
| Compact pattern and placement lookup | [CHEATSHEET.md](references/CHEATSHEET.md) |

Primary foundations: [DDD](https://www.domainlanguage.com/ddd/blue-book/), [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/), and [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html).
