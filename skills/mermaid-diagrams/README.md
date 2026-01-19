# mermaid-diagrams

Generate Mermaid diagrams in markdown. Claude will automatically use this skill when you ask for diagrams, charts, visualizations, or system documentation.

## Supported Diagram Types

| Category | Diagrams |
|----------|----------|
| **Flows** | Flowchart, Sequence, State |
| **Data Modeling** | Class, ER |
| **Planning** | Gantt, Timeline, Kanban |
| **Visualization** | Pie, Quadrant, XY Chart, Sankey, Treemap |
| **Architecture** | C4, Architecture, Block |
| **Other** | Mindmap, Git Graph, User Journey, Requirement, Packet |

## Example Usage

```
"Create a sequence diagram showing the OAuth flow"
"Draw an ER diagram for a blog database"
"Make a flowchart of the CI/CD pipeline"
"Show me a Gantt chart for sprint planning"
"Create a C4 context diagram for our system"
```

## Skill Structure

- **[SKILL.md](SKILL.md)** - Main skill file (concise overview)
- **Reference Files:**
  - [FLOWCHARTS.md](references/FLOWCHARTS.md) - Flowchart syntax
  - [SEQUENCE.md](references/SEQUENCE.md) - Sequence diagrams
  - [CLASS-ER.md](references/CLASS-ER.md) - Class & ER diagrams
  - [STATE-JOURNEY.md](references/STATE-JOURNEY.md) - State & user journey
  - [DATA-CHARTS.md](references/DATA-CHARTS.md) - Gantt, Pie, Timeline, Charts
  - [ARCHITECTURE.md](references/ARCHITECTURE.md) - C4, Architecture, Block, Kanban
  - [ADVANCED.md](references/ADVANCED.md) - Configuration & styling
  - [CHEATSHEET.md](references/CHEATSHEET.md) - Quick reference

## Did You Know Mermaid Can Do This?

```mermaid
sankey-beta

Visitors,Signed Up,4200
Visitors,Bounced,8500
Signed Up,Free Trial,3100
Signed Up,Churned,1100
Free Trial,Converted,1800
Free Trial,Churned,1300
Converted,Pro Plan,1200
Converted,Enterprise,600
```

```mermaid
quadrantChart
    title Feature Prioritization
    x-axis Low Effort --> High Effort
    y-axis Low Impact --> High Impact
    quadrant-1 Do First
    quadrant-2 Schedule
    quadrant-3 Delegate
    quadrant-4 Eliminate
    Dark Mode: [0.2, 0.9]
    API v2: [0.7, 0.85]
    Bug Fixes: [0.15, 0.5]
    Refactor Auth: [0.9, 0.4]
    Update Docs: [0.3, 0.3]
```

```mermaid
xychart-beta
    title "Monthly Active Users (2024)"
    x-axis [Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec]
    y-axis "Users (thousands)" 0 --> 150
    bar [23, 34, 45, 52, 67, 78, 89, 95, 108, 120, 135, 142]
    line [23, 34, 45, 52, 67, 78, 89, 95, 108, 120, 135, 142]
```
