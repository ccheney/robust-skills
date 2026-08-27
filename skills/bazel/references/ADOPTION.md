# Adopting and Migrating to Bazel

Use this guide when introducing Bazel to an existing repository, consolidating
several builds into a monorepo, or replacing a legacy WORKSPACE-based Bazel
setup. Adoption is a dependency-modeling program, not a BUILD-file generation
exercise.

## Define the Outcome First

Write down the migration's actual goal before changing the build:

- one correct dependency graph across the monorepo,
- reproducible local and CI builds,
- shared remote cache or remote execution,
- multi-platform builds and releases,
- faster tests through precise invalidation,
- a single policy layer for generated code and tools,
- or retirement of several incompatible build systems.

These goals imply different first slices. For example, remote execution requires
hermetic actions and registered toolchains early; graph consolidation requires
package boundaries and direct dependencies early.

Define measurable success criteria such as clean build time, no-op build time,
remote cache hit rate, affected-test precision, CI reliability, or the number of
projects no longer using the legacy build.

## Inventory Before Modeling

Capture the current repository as a system, not merely as a file tree.

### Languages and Toolchains

For each language or artifact type, record:

- compiler/interpreter/runtime version,
- package manager and lockfile,
- code generation tools,
- test runner and test data conventions,
- linter and formatter,
- packaging and release tooling,
- supported target platforms,
- machines or containers required for execution,
- and any environment or credentials the current build reads.

### Dependency and Artifact Flow

Identify:

- source libraries and applications,
- generated sources,
- schemas and generators,
- runtime resources,
- container images or installers,
- deployable manifests,
- third-party dependency resolution,
- cross-language boundaries,
- and publish/deploy steps.

For every step, ask: what are its declared inputs, tools, outputs, environment,
and consuming targets? Bazel adoption succeeds when those relationships become
explicit.

### Existing Automation

Inventory local scripts and CI jobs. Classify each as:

- graph-aware build/test work that should become a Bazel target,
- workspace orchestration that may remain outside Bazel,
- release or deployment work that consumes Bazel outputs,
- or accidental environment setup that should become a toolchain or declared
  dependency.

Do not translate every shell script line-for-line into a `genrule`. That
preserves the old build's opacity inside a new wrapper.

## Establish the Baseline

Before migrating product targets:

1. Pin Bazel with `.bazelversion` and use Bazelisk locally and in CI.
2. Create a root `MODULE.bazel`; Bazel 9 has no WORKSPACE implementation.
3. Add `.bazelrc` with small, named configs rather than a machine-specific flag
   dump.
4. Add or adopt supported external language rules explicitly.
5. Register hermetic toolchains for the first language and platforms.
6. Commit the generated `MODULE.bazel.lock`.
7. Format `MODULE.bazel`, BUILD files, and `.bzl` files with Buildifier.
8. Decide package visibility defaults and code-ownership boundaries.
9. Create a small CI path that exercises the Bazel skeleton itself.

Keep this baseline intentionally small. Remote execution, aggressive
configuration, and repository-wide code generation can follow once one slice
builds correctly.

## Choose a Vertical Slice

Select a slice with real value but bounded dependencies:

- a leaf library plus its unit tests,
- a standalone CLI,
- a generator and one generated consumer,
- or one service with a small internal dependency cone.

A useful first slice includes source, tests, tools, runtime data, and a final
artifact. It proves more than a library-only demo while avoiding the hardest
shared subsystem.

Avoid starting with:

- the repository root `//...`,
- the most dependency-heavy application,
- a bespoke framework used by every team,
- or a target whose correctness cannot be compared with the existing build.

## Migration Loop

Repeat this loop for each slice.

### 1. Define the Boundary

Choose Bazel package boundaries based on ownership, visibility, and dependency
cohesion. Do not mechanically create one package per directory if that produces
hundreds of meaningless BUILD files, and do not create one giant package that
hides dependency structure.

### 2. Model Direct Dependencies

Give each target only the dependencies its sources use. Avoid copying a
directory-wide dependency list into every target.

Use `bazel query`, `cquery`, and the language rules' strict-dependency tooling to
find missing or accidental edges. See [BUILD-GRAPH.md](BUILD-GRAPH.md).

### 3. Model Tools and Generated Code

Create explicit generator targets. Put generator executables in the execution
configuration, declare generated outputs, and feed those outputs into consumers
through labels.

Never depend on generated files left in the source tree by a previous build.

### 4. Model Runtime Data

Declare resources and test data. Verify binaries and tests through Bazel's
runfiles model, not by running them from a convenient source-tree directory.

### 5. Reproduce Configuration Semantics

Translate meaningful build variants into platforms, toolchains, build settings,
and small `select()` expressions. Do not clone a matrix of legacy environment
variables into `.bazelrc`.

### 6. Establish Parity

Build and test with both systems and compare the contract:

- compiled contents,
- generated source or API output,
- test selection and result,
- runtime resources,
- package/archive/image contents,
- platform compatibility,
- and release metadata.

Byte-for-byte parity is ideal for deterministic artifacts but is not always
required. When output differs intentionally, document why and compare the
semantic contract instead.

### 7. Exercise Clean and Constrained Environments

Run the slice:

- from a clean checkout,
- with sandboxing enabled,
- without preexisting generated artifacts,
- under the intended CI configuration,
- and against remote cache or remote execution when those are part of the goal.

This exposes host dependencies before more targets build on top of them.

### 8. Cut Over One Consumer

Move a real consumer or CI job to the Bazel target. A target that no workflow
uses is not a completed migration slice.

### 9. Remove Dual Ownership

Once the slice is stable, designate one system as authoritative. Remove or
freeze the old build definition for that slice so two implementations cannot
quietly diverge.

### 10. Expand Along Dependency Edges

Migrate the next dependency or consumer, using what the first slice taught about
toolchains, external packages, code generation, and visibility.

## External Dependencies

Choose a source of truth for every ecosystem.

Common strategies include:

- a Bazel ruleset or module extension that resolves the ecosystem lockfile,
- generated Bazel metadata checked into the repository,
- a repository-specific importer that translates an existing lockfile,
- or explicit `bazel_dep()` modules for Bazel-native libraries.

The right choice depends on the supported ruleset. Apply these invariants:

- Keep one authoritative version-resolution source.
- Pin versions and integrity data.
- Preserve licenses and provenance needed by release processes.
- Make dependency updates reviewable and reproducible.
- Avoid resolving the same ecosystem independently in Bazel and another package
  manager.
- Test the ruleset's behavior with the repository's actual package-manager
  features, such as workspaces, optional dependencies, patches, or platform
  variants.

Do not invent generic repository rules for a language when a maintained,
language-aware ruleset already integrates that ecosystem.

## BUILD File Generation

BUILD files can be hand-authored, generated, or maintained by a hybrid policy.
Choose explicitly.

### Hand-Authored

Best when target structure encodes deliberate architecture and changes slowly.
Require Buildifier and review direct dependencies carefully.

### Generated

Best when a supported generator, such as Gazelle or a language-specific tool,
can infer target and dependency structure reliably. Pin the generator, define
its directives centrally, and make generation idempotent in CI.

### Hybrid

Use generated regions or generator-owned target classes with hand-authored
policy targets around them. Clearly separate ownership so a developer and a
generator do not rewrite the same fields.

Generation is not a substitute for modeling decisions. Review package size,
target granularity, visibility, generated target names, and dependencies.

## Parallel Build Systems

Running Bazel beside a legacy build is often necessary, but it needs an exit
policy.

- Declare which system owns each artifact.
- Keep parity checks on migrated boundaries.
- Avoid mutual recursion: Bazel should not call the legacy build which then
  calls Bazel.
- Do not share mutable output directories.
- Prefer consuming stable source or published artifacts across the boundary.
- Track the remaining targets and their blockers.
- Set criteria for deleting the legacy path.

A temporary wrapper around a legacy command may unblock sequencing. Mark it as
non-hermetic, exclude it from remote execution/cache when necessary, assign an
owner, and replace it with modeled actions. Do not present the wrapper as a
completed Bazel migration.

## Consolidating Repositories into a Monorepo

When repository consolidation and Bazel adoption happen together, separate the
decisions:

1. Preserve each project's known-good build while moving source boundaries.
2. Establish ownership and label conventions in the monorepo.
3. Model cross-project dependencies explicitly rather than relying on publish
   and consume steps.
4. Migrate vertical slices to Bazel.
5. Retire package publication that existed only to cross former repository
   boundaries, while retaining publication for real external consumers.

Do not convert every former repository into one monolithic Bazel package. Old
repository boundaries may inform ownership, but Bazel packages should follow
actual visibility and dependency cohesion.

## Migrating a WORKSPACE-Based Repository

For an existing Bazel repository using `WORKSPACE` or `WORKSPACE.bazel`:

1. Pin a Bazel 7 release for the migration work. The official migration tool
   requires Bazel 7 and does not support Bazel 8.
2. Inventory `workspace()` declarations, repository rules, macros, toolchain
   registration, and `bind()` usage.
3. Run the official `migrate_to_bzlmod` helper from the Bazel Central Registry
   repository as a starting point, then inspect its output and migration report.
4. Replace dependency macros with `bazel_dep()`, module extensions, or
   `use_repo_rule()` as appropriate.
5. Replace apparent repository names with canonical/repository-mapped labels.
6. Move toolchain and execution-platform registration into Bzlmod-compatible
   declarations.
7. Resolve root-only overrides explicitly.
8. Commit and verify the lockfile.
9. Test with Bzlmod enabled while the WORKSPACE path still exists.
10. Remove WORKSPACE dependencies and then upgrade to Bazel 9.

Do not jump first to Bazel 9 and expect the old WORKSPACE implementation to
remain as a fallback. See [BZLMOD.md](BZLMOD.md) for the detailed mapping.

## CI Rollout

Introduce CI in stages:

1. Build and test the current migrated slice.
2. Add repository-wide BUILD/Starlark formatting and linting.
3. Add a clean-build lane to catch undeclared dependencies.
4. Add remote cache once actions are deterministic enough to share safely.
5. Add affected-target selection as an optimization, retaining broader safety
   lanes.
6. Add remote execution only after toolchains and sandboxed builds are healthy.
7. Collect BEP and profile data before tuning flags.

Do not make developers debug an unstable build, dependency migration, remote
cache, and remote execution at the same time. Establish a correct local baseline
and add distributed infrastructure deliberately.

## Policy That Scales

Encode a small number of clear repository rules:

- default target visibility,
- allowed dependency directions,
- where public APIs live,
- package ownership,
- how toolchains are selected,
- how external dependencies are updated,
- who owns generated BUILD files,
- which configs CI and developers may rely on,
- and what repository-wide validation the stable branch runs.

Prefer enforcement through Bazel visibility, compatible-with constraints,
linting, and tests over prose alone. Keep exceptions narrow and reviewable.

## Failure Modes

| Failure | Consequence | Better direction |
|---|---|---|
| Generate BUILD files for the whole repository before proving one slice | Large, low-signal diff with unknown semantics | Validate a vertical slice, then expand |
| Wrap legacy builds in `genrule` | Opaque, non-hermetic action with poor caching | Model inputs, tools, outputs, and dependencies directly |
| Depend on every internal library through one umbrella target | Broad invalidation and hidden architecture | Use direct, granular library targets |
| Preserve environment-variable configuration | Machine-dependent analysis and cache fragmentation | Use build settings, platforms, and toolchains |
| Install compilers in CI images without toolchain modeling | Local/CI drift and weak remote execution | Register hermetic toolchains |
| Run two dependency resolvers indefinitely | Version drift and irreproducible graphs | Choose one authoritative lock/resolution path |
| Enable remote execution before sandboxed local builds work | Distributed, expensive failures | Fix hermeticity locally first |
| Use `//...` as every inner-loop command | Slow feedback that obscures target quality | Run precise targets; retain broad validation lanes |
| Leave both builds authoritative | Silent artifact divergence | Cut ownership over slice by slice |
| Tune flags before measuring | Complexity without known benefit | Capture BEP/profile evidence and tune bottlenecks |

## Slice Completion Checklist

- The target graph represents direct source, generated, tool, data, and runtime
  dependencies.
- Toolchains and platforms reproduce the supported build variants.
- The slice builds and tests from a clean checkout.
- Sandboxing does not reveal undeclared host dependencies.
- Bazel and the previous build meet the defined parity contract.
- At least one real local or CI consumer uses the Bazel target.
- External dependencies have one pinned source of truth.
- BUILD ownership and formatting are automated.
- The old build path is removed, frozen, or explicitly time-bounded.
- The next migration slice is chosen along a known dependency edge.

## Program Completion Checklist

- Stable-branch CI builds and tests the intended repository-wide scope.
- Developers have documented, precise inner-loop commands.
- Remote cache/execution, if enabled, is reliable and observable.
- Release artifacts originate from Bazel-owned targets.
- Toolchains are pinned and registered for supported platforms.
- Visibility and dependency policies match team ownership.
- Legacy build definitions and duplicate dependency resolution are retired.
- Upgrade ownership exists for Bazel, rulesets, toolchains, and module
  dependencies.
- Success metrics show the intended correctness, speed, or maintainability gain.

## Authoritative Sources

- [Bazel installation with Bazelisk](https://bazel.build/install/bazelisk)
- [Bazel 9 LTS](https://blog.bazel.build/2026/01/20/bazel-9.html)
- [Bzlmod migration guide](https://bazel.build/external/migration)
- [Bzlmod migration tool](https://bazel.build/external/migration_tool)
- [Bazel best practices](https://bazel.build/configure/best-practices)
- [BUILD style guide](https://bazel.build/build/style-guide)
- [Hermeticity](https://bazel.build/basics/hermeticity)
- [Platforms](https://bazel.build/extending/platforms)
- [Toolchains](https://bazel.build/extending/toolchains)
- [Remote execution overview](https://bazel.build/remote/rbe)
- [Bazel Central Registry](https://registry.bazel.build/)
- [Gazelle](https://github.com/bazel-contrib/bazel-gazelle)
