---
name: bazel
description: Manage, structure, modernize, and troubleshoot Bazel monorepos. Use for MODULE.bazel, BUILD or BUILD.bazel files, Starlark, Bazelisk, Bzlmod dependencies and module extensions, labels and targets, visibility, query/cquery/aquery, .bazelrc configuration, select(), platforms and toolchains, hermetic actions, sandboxing, local or remote caching, remote execution, tests, CI, performance, Gazelle, Buildifier, Buildozer, or migration from WORKSPACE and other build systems. Inspect the repository's pinned Bazel and ruleset versions before applying version-specific guidance.
metadata:
  version: "9.2.0"
---

# Bazel Monorepos

Bazel is a graph-based build and test system for large, multi-language repositories. Treat the target graph—not folders, shell scripts, or CI job order—as the source of truth. A healthy repository has explicit dependency edges, narrow public interfaces, hermetic actions, reproducible external dependencies, and one configuration model from laptop through CI.

This skill is grounded in Bazel 9.2.0 documentation. Bazel 9 changed two fundamentals:

- **Bzlmod fully replaced `WORKSPACE`.** Bazel 9 removed the legacy `WORKSPACE` implementation. New Bazel 9 code must use `MODULE.bazel`, module extensions, and repository rules exposed through Bzlmod.
- **Language rules are external modules.** Previously built-in language rules—including C++—must be declared as modules and explicitly loaded. Do not assume `cc_*`, `java_*`, `py_*`, or other language rules exist natively.

For an existing repository, its checked-in `.bazelversion`, module versions, and compatibility constraints outrank this baseline. Do not silently upgrade them as part of an unrelated change.

## First Inspection

Before proposing or editing Bazel configuration:

1. Read `.bazelversion`, `MODULE.bazel`, `MODULE.bazel.lock`, `.bazelrc`, `.bazelignore`, and any `REPO.bazel` or `VENDOR.bazel` files that exist.
2. Find `BUILD`, `BUILD.bazel`, and `.bzl` files in the affected tree. A nearer `BUILD` file creates a subpackage boundary.
3. Inspect the specific ruleset versions and their own documentation. Bazel core version and language-rules version are independent.
4. Check existing repository conventions: package granularity, visibility groups, macros, platforms, toolchain registration, CI configs, remote execution, code generation, and BUILD-file generation.
5. Use graph tools before guessing. Choose `query`, `cquery`, `aquery`, or `mod` based on the layer being investigated.
6. Make the smallest graph-preserving change, format it, and validate the narrowest affected targets before widening to `//...`.

Useful reconnaissance:

```bash
bazel --version
bazel info workspace
bazel info release
rg --files -g '.bazelversion' -g 'MODULE.bazel' -g 'MODULE.bazel.lock' \
  -g '.bazelrc' -g 'BUILD' -g 'BUILD.bazel' -g '*.bzl'
bazel query //path/to/area/...
bazel mod graph --extension_info=usages
```

Do not run `bazel clean`, especially `bazel clean --expunge`, as routine troubleshooting. It destroys useful incremental state and can conceal an incorrect dependency declaration. Use it only when reclaiming disk space, explicitly reproducing a clean-build issue, or following a diagnostic that truly requires it.

## The Mental Model

```
MODULE.bazel                    external module graph and extension inputs
       │
repositories / workspace       main repo + fetched/generated external repos
       │
packages                       directories rooted by BUILD files
       │
targets                        rules and files named by labels
       │
configured targets             targets after flags/selects/transitions/toolchains
       │
actions                        concrete commands with declared inputs/outputs/tools
       │
artifacts                      files produced or consumed by actions
```

Keep these layers separate:

| Layer | Question | Primary tool |
|---|---|---|
| Modules/repos | Why is this external dependency or repository present? | `bazel mod` |
| Unconfigured target graph | Who depends on this target? Where is a path? | `bazel query` |
| Configured target graph | Which `select()` branch, platform, transition, or toolchain applies? | `bazel cquery` |
| Action graph | What command, inputs, outputs, and environment will actually run? | `bazel aquery` |
| Execution | Why did an action rerun, miss cache, fail in a sandbox, or run slowly? | profiles, execution logs, BEP, sandbox diagnostics |

A **repository** is a source tree. The main repository plus external repositories form the **workspace** visible to an invocation. A **package** is a directory containing a `BUILD` or `BUILD.bazel` file; it owns files below it until another BUILD file creates a subpackage. A **target** is a rule instance or file. A **label** identifies a target:

```text
@apparent_repo//path/to/package:target
```

Inside the main repository, prefer `//path/to/package:target`; inside one package, prefer `:target`. Do not bake canonical `@@repo+version` names into source code or runfile paths. Canonical names are resolution details and may change.

## Governing Rules

### 1. Declare Direct Dependencies Exactly

If a source directly imports, includes, loads, invokes, or reads something, the owning target needs a direct edge to the target that provides it. Do not rely on a transitive dependency merely because the build currently passes.

Use the attribute matching the relationship:

| Relationship | Typical attribute |
|---|---|
| Source compiled or transformed by this rule | `srcs` |
| Separately built code/API needed by the source | `deps` |
| Runtime-only file or executable | `data` |
| Program used while building | `tools`, an executable label, or a ruleset-specific tool attribute |

This accuracy is what makes incremental builds, remote caching, affected-test selection, visibility, and refactoring trustworthy.

### 2. Make Packages and Targets Cohesive

Do not force Bazel into a universal `apps/` and `packages/` layout. Bazel architecture follows source ownership and dependency boundaries. A BUILD file defines a package boundary; target granularity defines the units Bazel can analyze, cache, schedule, test, and invalidate.

- Prefer a BUILD package in each directory with buildable code when that matches the language's package/module structure.
- Split targets when sources have materially different dependencies, visibility, ownership, platforms, or test impact.
- Avoid one giant target per service or directory; it makes every change invalidate too much.
- Avoid one target per file by reflex; excessive graph nodes and boilerplate can outweigh the incrementality benefit.
- Keep the repository root package small. Put meaningful code under descriptive packages.

Read [references/BUILD-GRAPH.md](references/BUILD-GRAPH.md) when shaping packages, targets, labels, dependencies, or BUILD files.

### 3. Default to Private Interfaces

Visibility is architecture enforcement, not decoration.

- Leave targets private unless another package needs them.
- Expose deliberate APIs with narrow `visibility` entries.
- Reuse `package_group` targets for shared policies.
- Use `//foo:__pkg__` for one package and `//foo:__subpackages__` for that subtree.
- Do not set package-wide `default_visibility = ["//visibility:public"]` in a growing monorepo.
- Apply load visibility to `.bzl` entry points so internal Starlark implementation files stay internal.

### 4. Make Actions Hermetic

An action must derive its result from declared inputs, declared tools, its command line, declared environment, and platform/toolchain selection. It must write only declared outputs.

- Never discover tools through the host `PATH` when a toolchain or executable target can declare them.
- Never read undeclared workspace files, user home files, system SDKs, wall-clock time, random state, or network resources during an ordinary build action.
- Put runtime resources in `data` and locate them through the ruleset's runfiles library; do not hardcode `bazel-bin`, execroot, or runfiles-tree paths.
- Use a repository rule or module extension for dependency acquisition, not an ordinary action.
- Treat local success with `--spawn_strategy=local` as weaker evidence than sandboxed success.

Read [references/HERMETICITY-CACHING.md](references/HERMETICITY-CACHING.md) for sandboxing, action inputs, cache correctness, remote execution, and runfiles.

### 5. Use Bzlmod as the Dependency System

For Bazel 9:

- Declare Bazel modules with `bazel_dep` in `MODULE.bazel`.
- Use module extensions for ecosystems such as Maven, npm, pip, or Go when the ruleset provides one.
- Import extension-generated repositories explicitly with `use_repo`.
- Keep `MODULE.bazel.lock` in version control and update it with Bazel, not by hand.
- Use root-module overrides sparingly and document why they are needed.
- Use vendor mode only when offline or source-control requirements justify its size and maintenance cost.

`WORKSPACE`, `http_archive()` in `WORKSPACE`, and legacy `*_deps()` chains are not Bazel 9 solutions. Read [references/BZLMOD.md](references/BZLMOD.md) for module resolution, extensions, overrides, the lockfile, vendor mode, and migration.

### 6. Model Platforms and Toolchains Explicitly

Keep three concepts distinct:

- **Host platform:** where Bazel itself runs.
- **Execution platform:** where a build or test action runs.
- **Target platform:** where the produced artifact will run.

Select toolchains by declared types and constraints. Prefer `--platforms=//platforms:linux_x86_64` and constraint-based `config_setting`s over piles of unrelated CPU/OS flags. Use `target_compatible_with` for targets that cannot build on a platform and `exec_compatible_with` for actions that require a particular execution environment.

Read [references/CONFIGURATION.md](references/CONFIGURATION.md) whenever editing `.bazelrc`, `select()`, build settings, platforms, toolchains, transitions, or execution groups.

## Decision Trees

### “Where should this build logic live?”

```
Build concern
├─ Declares a buildable library/binary/test       → BUILD target
├─ Repeats a small declaration pattern            → symbolic macro
├─ Creates actions or transports providers        → custom rule/aspect
├─ Discovers/downloads an external repository     → repository rule
├─ Aggregates ecosystem dependencies across mods  → module extension
├─ Selects compiler/runtime for platforms         → toolchain
└─ Chooses a project-wide command-line policy     → .bazelrc config
```

Start with a symbolic macro for repeated declarations. Write a rule only when analysis must create actions or providers. Avoid hiding ordinary target structure behind large macros; queryability and explicit BUILD files are valuable.

Read [references/STARLARK.md](references/STARLARK.md) before creating or substantially changing macros, rules, aspects, providers, repository rules, or module extensions.

### “Which query should I use?”

```
Question
├─ What targets/deps/rdeps/path exist?             → query
├─ What survives select()/flags/platforms?         → cquery
├─ What action/argv/input/output/tool is created?  → aquery
├─ Why is an external module/repo present?         → mod
└─ Why did execution/cache/performance differ?     → execution log/profile/BEP
```

Examples:

```bash
# Direct and transitive target dependencies, before configuration.
bazel query 'deps(//app/server:server)'

# Why one target depends on another.
bazel query 'somepath(//app/server:server, //lib/auth:auth)'

# Reverse dependencies within an explicit universe.
bazel query 'rdeps(//..., //lib/auth:auth)'

# Configured dependencies after selects/toolchains/transitions.
bazel cquery 'deps(//app/server:server)' --config=ci

# Concrete compile/link/generation actions.
bazel aquery 'deps(//app/server:server)' --config=ci

# Why a module version was selected.
bazel mod explain rules_python --verbose --include_unused
```

Read [references/QUERIES-DEBUGGING.md](references/QUERIES-DEBUGGING.md) for query operators, output formats, dependency diagnosis, configuration diagnosis, and action diagnosis.

### “Why did this build fail only in CI/remote execution?”

```
CI/remote-only failure
├─ Missing file                    → undeclared srcs/deps/data/tool/runfile
├─ Missing executable             → host PATH leak; declare tool/toolchain
├─ Wrong architecture/OS          → target vs execution platform confusion
├─ Different generated output     → non-determinism or undeclared environment
├─ Cache hit with wrong result     → incomplete action inputs/toolchain identity
├─ Cache miss across machines     → differing flags, env, tools, or platforms
└─ Test reaches network/service    → non-hermetic test or missing test fixture
```

Reproduce with the same config and platform first. Then use `--verbose_failures`, `--sandbox_debug`, `aquery`, and compact execution logs. Do not disable sandboxing as the permanent fix.

### “How much should CI build?”

```
CI scope
├─ Stable/default branch confidence gate  → bazel build //... + bazel test //...
├─ PR fast path                           → proven affected-target system
├─ Build metadata/dashboard               → Build Event Protocol / BES
├─ Team-wide reuse                        → authenticated remote cache
└─ Compute scaling                        → remote execution after hermeticity
```

Bazel itself does not turn a Git diff into a universally correct affected-target set. BUILD, `.bzl`, `MODULE.bazel`, toolchain, platform, and configuration changes can affect targets far beyond the changed source directory. Treat any affected-target tool as a correctness-sensitive system with a conservative fallback. Read [references/CI-PERFORMANCE.md](references/CI-PERFORMANCE.md).

## Repository Baseline

A new Bazel 9 repository usually needs:

```text
.
├── .bazelversion          # exact Bazel version, used by Bazelisk
├── MODULE.bazel           # root module + direct external dependencies
├── MODULE.bazel.lock      # generated resolution/extension state; commit it
├── .bazelrc               # shared, reviewed command configurations
├── BUILD.bazel            # only if the root package owns real targets
├── platforms/             # repository platforms/constraints, if needed
├── tools/                 # shared macros/rules/tooling, with narrow APIs
└── <source trees>/        # BUILD packages follow source/ownership boundaries
```

For Bazel 9.2.0 and current C++ rules at this skill's research baseline:

```starlark
# MODULE.bazel
module(name = "acme_monorepo")

bazel_dep(name = "rules_cc", version = "0.2.22")
bazel_dep(name = "platforms", version = "1.1.0")
```

```starlark
# app/hello/BUILD.bazel
load("@rules_cc//cc:cc_binary.bzl", "cc_binary")
load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "greeting",
    srcs = ["greeting.cc"],
    hdrs = ["greeting.h"],
)

cc_binary(
    name = "hello",
    srcs = ["main.cc"],
    deps = [":greeting"],
)
```

Versions in examples are evidence of the documented baseline, not permission to overwrite an existing repository's pins. For a new dependency, verify the current compatible release in the Bazel Central Registry and the ruleset's release notes.

## BUILD File Discipline

- Prefer `BUILD.bazel` consistently for new packages unless the repository uses `BUILD`.
- Keep `load()` statements at the top and load rules from their public entry points.
- Use explicit source lists for small, stable target APIs. Non-recursive `glob()` is reasonable for homogeneous sources; avoid recursive source globs because new subpackages silently change their meaning.
- Keep direct dependencies inline on the target. Shared dependency-list variables obstruct automated maintenance and can hide unused edges.
- Export rule targets instead of raw source files when possible.
- Give tests their own targets and precise `size`, `timeout`, `tags`, `data`, and platform constraints.
- Use `tags = ["manual"]` only when wildcard commands truly must skip a target. Prefer descriptive restrictions such as platform compatibility when that is the real reason.
- Format and lint Starlark with Buildifier. Use Buildozer for mechanical BUILD edits and a suitable Gazelle extension when the language ecosystem can reliably generate/update BUILD files.

## Common Anti-Patterns

| Anti-pattern | Why it fails | Better model |
|---|---|---|
| `WORKSPACE` dependencies on Bazel 9 | The implementation was removed | `MODULE.bazel`, extensions, `use_repo` |
| Assuming language rules are native | Bazel 9 externalized language rules | `bazel_dep` + explicit `load()` |
| `default_visibility = public` | Turns every new target into API | Private default + narrow exported targets |
| One target for an entire service tree | Coarse invalidation and weak boundaries | Cohesive packages/targets with exact deps |
| Recursive source `glob(["**/*"])` | Package boundaries and membership become surprising | Explicit lists or non-recursive globs |
| Depending on a transitive library | Builds break when intermediates change | Direct `deps` edge |
| Runtime file omitted from `data` | Works locally, fails in tests/remote execution | Declare data and use runfiles library |
| Tool found via `/usr/bin` or `PATH` | Host-dependent action and unsafe cache reuse | Executable target/toolchain |
| Hardcoded `bazel-bin`/execroot/runfiles path | Layout is configuration- and platform-dependent | Providers, `$(location)` where supported, runfiles API |
| `query` to explain a `select()` result | `query` is unconfigured and returns possible branches | `cquery` with the same flags |
| Parsing human terminal output in automation | Output is for people and can change | BEP or proto/JSON query formats |
| Disabling sandboxing to “fix” a build | Preserves hidden inputs | Declare the missing inputs/tools |
| Routine `clean --expunge` | Erases useful state and masks graph bugs | Diagnose the dependency/cache discrepancy |
| Local-only override committed permanently | Other machines cannot resolve it | Temporary `local_path_override`, then a published/pinned dependency |
| Hand-editing `MODULE.bazel.lock` | Format is generated and version-sensitive | `bazel mod deps` / normal resolution |
| Using canonical `@@...` repo names in source | Canonical names are implementation details | Apparent repo names and repo mappings |
| Treating `//...` as including external repos | It covers main-repo packages only | Explicit external target patterns when needed |

## Change Workflow

1. **Preserve the baseline.** Use the pinned Bazel and ruleset versions. If an upgrade is the task, isolate it and read release/migration notes.
2. **Identify package boundaries.** A file may belong to a parent package or a nearer subpackage; never infer from the filesystem alone.
3. **Trace the graph.** Use `query` for structural dependencies, `cquery` for configuration, `aquery` for actions, and `mod` for external resolution.
4. **Edit the correct layer.** BUILD target, macro, rule, module extension, toolchain, platform, or rc configuration each solves a different problem.
5. **Format/lint.** Run the repository's Buildifier target or installed Buildifier in check/fix mode according to local convention.
6. **Validate narrowly.** Build and test the changed targets and their relevant dependents/configurations.
7. **Validate broadly in proportion to risk.** Widen to the affected subtree and then `bazel build //...` / `bazel test //...` for graph-wide or stable-branch changes.
8. **Check reproducibility artifacts.** Review `MODULE.bazel.lock`, generated BUILD changes, query output, and platform-specific effects.
9. **Preserve diagnostics.** For CI/performance/cache work, compare profiles or execution logs rather than relying on wall-clock anecdotes.

Typical checks, adapted to the repository:

```bash
buildifier -mode=check -lint=warn -r .
bazel mod tidy
bazel mod deps --lockfile_mode=error
bazel build //path/to/changed/...
bazel test //path/to/changed/... --test_output=errors
bazel build //...
bazel test //... --test_output=errors
```

Many repositories expose Buildifier as a Bazel target instead; follow the
checked-in convention when one exists.

## Reference Router

Load only the references needed for the task.

| Reference | Use for |
|---|---|
| [BUILD-GRAPH.md](references/BUILD-GRAPH.md) | packages, targets, labels, BUILD style, direct deps, visibility, tests, code organization |
| [BZLMOD.md](references/BZLMOD.md) | `MODULE.bazel`, modules, extensions, overrides, lockfile, vendor/offline mode, Bazel 9 migration |
| [CONFIGURATION.md](references/CONFIGURATION.md) | `.bazelrc`, configs, `select()`, build settings, platforms, toolchains, transitions, execution groups |
| [QUERIES-DEBUGGING.md](references/QUERIES-DEBUGGING.md) | `query`, `cquery`, `aquery`, `mod`, target patterns, dependency paths, build/action diagnosis |
| [HERMETICITY-CACHING.md](references/HERMETICITY-CACHING.md) | declared inputs, sandboxing, runfiles, local/remote caches, remote execution, cache debugging |
| [CI-PERFORMANCE.md](references/CI-PERFORMANCE.md) | Bazelisk, CI gates, affected-target safety, BEP/BES, profiles, workers, remote scaling |
| [STARLARK.md](references/STARLARK.md) | symbolic macros, rules, providers, depsets, actions, aspects, repository rules, module extensions |
| [ADOPTION.md](references/ADOPTION.md) | introducing Bazel to an existing monorepo, migration slices, source-of-truth choices, rollout criteria |
| [CHEATSHEET.md](references/CHEATSHEET.md) | compact command, label, visibility, and diagnosis lookup |

## Authority Order

1. The repository's checked-in Bazel/ruleset versions and tests
2. Version-matched Bazel documentation and Bazel release notes
3. The selected ruleset's official documentation and release notes
4. Bazel Central Registry metadata for published module versions and compatibility
5. Bazel-maintained tooling repositories such as Bazelisk and Buildtools
6. Bazel-contrib projects for their own documented behavior

Official starting points:

- Bazel documentation: https://bazel.build/
- Bazel 9 LTS announcement: https://blog.bazel.build/2026/01/20/bazel-9.html
- Bazel releases: https://github.com/bazelbuild/bazel/releases
- Bazel Central Registry: https://registry.bazel.build/
- Bazelisk: https://github.com/bazelbuild/bazelisk
- Buildifier and Buildozer: https://github.com/bazelbuild/buildtools
- Gazelle: https://github.com/bazel-contrib/bazel-gazelle
