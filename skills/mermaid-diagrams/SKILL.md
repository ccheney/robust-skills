---
name: mermaid-diagrams
description: Create or fix Mermaid diagrams in Markdown. Use for requested flowcharts, sequence diagrams, ER diagrams, state machines, or system diagrams when Mermaid is the output format; not every visualization or explanation.
---

# Mermaid Diagrams

Turn the supplied process, code, schema, or relationships into the requested Mermaid diagram. The user's explicit instructions take precedence over this skill's guidelines, including their choice of output format.

## Choose the representation

Establish the facts to show and the destination renderer. If the request leaves the format open and a text-based system/process diagram fits, Mermaid is a reasonable choice. Preserve an explicitly requested drawing tool or artifact format.

| Question | Diagram |
|---|---|
| What happens next or which path is taken? | `flowchart` |
| Who calls whom, in what order? | `sequenceDiagram` |
| What tables and cardinalities exist? | `erDiagram` |
| What states and transitions exist? | `stateDiagram-v2` |
| How are types or services related? | `classDiagram` or flowchart with subgraphs |
| What is scheduled or measured? | A matching planning/data type from the references |

Use supplied evidence for nodes, edges, cardinalities, dates, and values. Mark conceptual assumptions; ask for missing facts that determine the diagram rather than inventing a system.

## Produce a renderable result

- Return a fenced `mermaid` block, or the requested `.mmd`/rendered artifact. Use one diagram declaration per block.
- Prefer stable syntax supported by the destination. Examples were checked against Mermaid 11.16; a host can bundle an older version.
- Give nodes stable IDs distinct from display labels and subgraph IDs. Quote labels with punctuation; avoid reserved `end` IDs and use `%%` comments on their own lines.
- Keep ER attributes one per line and alias sequence participants whose names contain spaces.
- Split diagrams when readability suffers, not at a fixed node count.

Validate nontrivial or repaired syntax with the project's renderer or an available Mermaid CLI. Inspect the rendered result when producing an artifact; if rendering is unavailable, state that limitation. A simple syntax answer does not require installing a new toolchain.

## References

Load the diagram type or rendering topic required.

| Task | Reference |
|---|---|
| Flowcharts, subgraphs, shapes, edges | [FLOWCHARTS.md](references/FLOWCHARTS.md) |
| Calls, activation, loops, alternatives | [SEQUENCE.md](references/SEQUENCE.md) |
| Classes, types, database relationships | [CLASS-ER.md](references/CLASS-ER.md) |
| State machines and user journeys | [STATE-JOURNEY.md](references/STATE-JOURNEY.md) |
| Gantt, timeline, pie, XY, sankey, mindmap, gitGraph | [DATA-CHARTS.md](references/DATA-CHARTS.md) |
| C4, architecture, block, kanban, packet, requirements | [ARCHITECTURE.md](references/ARCHITECTURE.md) |
| Configuration, styling, export, troubleshooting | [ADVANCED.md](references/ADVANCED.md) |
| Compact syntax and platform lookup | [CHEATSHEET.md](references/CHEATSHEET.md) |

Check [Mermaid documentation](https://mermaid.js.org/) and the destination's own support notes when a feature is version-sensitive.
