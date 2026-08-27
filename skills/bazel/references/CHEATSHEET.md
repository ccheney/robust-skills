# Bazel Monorepo Field Guide

Use this compact guide during routine work. Follow the linked deep guides when
the correct model or diagnostic is not obvious.

## Mental Model

```text
MODULE.bazel
  -> modules and module extensions
  -> repositories
  -> packages (directories containing BUILD or BUILD.bazel)
  -> targets (rules, source files, generated files, package groups)
  -> configured targets (target + configuration)
  -> actions (declared commands)
  -> artifacts (declared files)
```

The dependency graph is the primary product. BUILD files describe it; Bazel
loads, analyzes, and executes only what the requested targets require.

## Repository Files

| File | Purpose | Commit? |
|---|---|---|
| `.bazelversion` | Bazel release selected by Bazelisk | Yes |
| `MODULE.bazel` | Root module, direct module dependencies, extensions, toolchains | Yes |
| `MODULE.bazel.lock` | Resolved Bzlmod and extension state | Yes |
| `.bazelrc` | Shared command options and named configs | Yes |
| `.bazelignore` | Directories Bazel should not treat as workspace content | Usually |
| `BUILD.bazel` | Package target declarations | Yes |
| `*.bzl` | Reusable Starlark APIs | Yes |
| `bazel-bin`, `bazel-out`, `bazel-testlogs`, workspace symlink | Bazel output conveniences | No |

Prefer `BUILD.bazel` over `BUILD` in new code. Keep personal flags in a separate
user rc file rather than the shared `.bazelrc`.

## Labels

```text
//path/to/package:target       target in the main repository
//path/to/package              shorthand when target equals package basename
:target                       target in the current package
@repo//path/to/package:target target in an apparent external repository
@@canonical//pkg:target       canonical external repository label
```

Inside `BUILD.bazel`, relative target labels are appropriate within the package.
In public docs and scripts, prefer complete, unambiguous labels.

## Target Patterns

```text
//app/service:binary           one target
//app/service:all              all rule targets in one package
//app/service:*                all targets in one package, including files
//app/service/...              all targets recursively below a package
//...                          all targets in the main repository
@repo//...                     all targets in an external repository
-//app/service:slow_test       subtract a target in supported command contexts
```

`//pkg/...` is a target pattern interpreted by commands. It is not one label and
cannot be used wherever an ordinary dependency label is expected.

## Daily Commands

```bash
# Build, test, run
bazel build //app/service:binary
bazel test //app/service:all
bazel run //tools/linter -- --fix src/file.cc

# Fetch without building
bazel fetch //app/service:binary

# Show command help and startup/server information
bazel help build
bazel info
bazel version

# Keep the server, discard build results only when genuinely needed
bazel clean
```

Avoid routine `bazel clean --expunge`. It discards the local cache and server,
often making the next build slower without fixing the underlying graph or
hermeticity problem.

## Query Router

| Question | Command family |
|---|---|
| What targets and declared edges exist? | `query` |
| What survives configuration and `select()`? | `cquery` |
| What action will run, with which inputs/arguments/outputs? | `aquery` |
| Which modules, extensions, and repositories were resolved? | `mod` |
| What happened during an actual invocation? | BEP, execution log, profile |

### Declared Target Graph: `query`

```bash
bazel query //app/service:all
bazel query 'deps(//app/service:binary)'
bazel query 'rdeps(//..., //lib/api:api)'
bazel query 'somepath(//app/service:binary, //lib/api:api)'
bazel query 'kind(".*_test rule", //app/service/...)'
bazel query 'attr(tags, "manual", //...)'
bazel query --noimplicit_deps 'deps(//app/service:binary)'
bazel query --output=graph 'deps(//app/service:binary)'
```

### Configured Graph: `cquery`

```bash
bazel cquery //app/service:binary --config=ci
bazel cquery 'deps(//app/service:binary)' --platforms=//platforms:linux_x86_64
bazel cquery //app/service:binary --output=files
bazel cquery //app/service:binary --transitions=lite
bazel cquery //app/service:binary \
  --output=starlark \
  --starlark:expr='str(target.label) + " " + str(target.files.to_list())'
```

Run `cquery` with the same flags/config as the failing build. A configured target
is identified by both label and configuration.

### Action Graph: `aquery`

```bash
bazel aquery //app/service:binary
bazel aquery 'mnemonic("CppCompile", //app/service:binary)'
bazel aquery 'inputs("config.json", //app/service:binary)'
bazel aquery 'outputs(".*\\.jar", //app/service:binary)'
bazel aquery --include_param_files //app/service:binary
```

### Module Graph: `bazel mod`

```bash
bazel mod graph
bazel mod deps
bazel mod all_paths <module>
bazel mod explain <module>
bazel mod show_repo <apparent-repository-name>
bazel mod show_extension '<extension-label>%<extension-name>'
bazel mod tidy
```

See [QUERIES-DEBUGGING.md](QUERIES-DEBUGGING.md) for expression composition,
affected-target analysis, and phase-based debugging.

## Dependency Hygiene

- Depend on the smallest target that supplies what the consumer uses.
- Declare direct dependencies even when another dependency currently exports
  them transitively.
- Use narrow visibility by default.
- Keep public API targets explicit and stable.
- Split targets when code changes, visibility, ownership, or platform
  compatibility differ materially.
- Avoid umbrella targets that make every consumer depend on an entire subtree.
- Keep tests close to the targets they validate.

Useful checks:

```bash
bazel query 'same_pkg_direct_rdeps(//lib/core:core)'
bazel query 'rdeps(//..., //lib/core:core)'
bazel query 'somepath(//app:binary, //lib/core:core)'
```

## Visibility

```starlark
# Private: omit visibility or write explicitly
visibility = ["//visibility:private"]

# One package
visibility = ["//app/service:__pkg__"]

# One package and descendants
visibility = ["//app/service:__subpackages__"]

# Named policy group
visibility = ["//visibility:service_consumers"]

# Public API only
visibility = ["//visibility:public"]
```

Define a package group in a `BUILD.bazel` file:

```starlark
package_group(
    name = "service_consumers",
    packages = [
        "//app/service/...",
        "//integration/...",
    ],
)
```

Use public visibility intentionally; it is an architectural commitment, not a
quick fix for an error.

## BUILD Style

```starlark
load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "parser",
    srcs = ["parser.cc"],
    hdrs = ["parser.h"],
    deps = [
        "//lib/lexer",
        "@abseil-cpp//absl/status",
    ],
)
```

- Put `load()` statements first, grouped consistently.
- Keep attributes in the style guide's conventional order.
- Prefer one label per line for multi-item lists.
- Use source globs sparingly; explicit sources make graph changes visible.
- Use `package()` only for real package-wide defaults.
- Format and lint with Buildifier.

```bash
buildifier -mode=check -lint=warn -r .
buildifier -mode=fix -lint=fix -r .
```

Use Buildozer for reviewed, mechanical BUILD edits and Gazelle when the
language-specific generator is an established source of truth.

## Bzlmod

Minimal current shape:

```starlark
module(
    name = "example_monorepo",
    version = "0.0.0",
)

bazel_dep(name = "platforms", version = "1.1.0")
bazel_dep(name = "rules_cc", version = "0.2.22")
```

Common directives:

```starlark
bazel_dep(name = "rules_example", version = "1.2.3")

example = use_extension("@rules_example//example:extensions.bzl", "deps")
example.toolchain(version = "4.5.6")
use_repo(example, "example_toolchains")

register_toolchains("@example_toolchains//:all")

# Root-module-only escape hatches; keep narrow and temporary.
single_version_override(module_name = "example", version = "1.2.4")
local_path_override(module_name = "example", path = "third_party/example")
```

Lockfile workflow:

```bash
bazel mod tidy
bazel mod graph
bazel mod deps --lockfile_mode=update
git diff -- MODULE.bazel MODULE.bazel.lock
bazel test //path/to/affected/...
```

Normal CI should use the committed lockfile without rewriting it. Use
`--lockfile_mode=error` in a validation lane when drift must fail explicitly.

See [BZLMOD.md](BZLMOD.md) for module extensions, overrides, repository
mappings, vendoring, offline operation, and WORKSPACE migration.

## Configuration

Named config:

```text
# .bazelrc
build:ci --color=no
build:ci --show_timestamps
test:ci --test_output=errors
```

```bash
bazel test --config=ci //app/service:all
```

Configurable attribute:

```starlark
config_setting(
    name = "linux",
    constraint_values = ["@platforms//os:linux"],
)

cc_library(
    name = "platform_impl",
    srcs = select({
        ":linux": ["linux.cc"],
        "//conditions:default": ["portable.cc"],
    }),
)
```

Use:

- **build settings** for product feature or mode choices,
- **target platforms** for what the output must run on,
- **execution platforms** for where actions may run,
- **toolchains** for compatible tools selected between them,
- **execution groups** when one rule has actions with distinct toolchain needs,
- and **transitions** only when an edge truly must change configuration.

Inspect configuration with:

```bash
bazel cquery //app/service:binary --transitions=lite
bazel build //app/service:binary --toolchain_resolution_debug='.*'
```

See [CONFIGURATION.md](CONFIGURATION.md).

## Hermetic Action Checklist

An action's result must be determined by:

- declared input artifacts,
- declared tools and their runfiles,
- command and arguments,
- explicitly modeled environment,
- execution/target platform and configuration,
- and no undeclared machine state.

Watch for:

- `/usr/bin` or `/usr/local` tools,
- ambient `PATH`, locale, timezone, home-directory config, and credentials,
- absolute source or output paths embedded in artifacts,
- undeclared generated files,
- current-working-directory assumptions,
- network access during build actions,
- nondeterministic timestamps or archive member order,
- and tests sharing mutable state.

Diagnostic sequence:

```bash
bazel build //path/to:target --spawn_strategy=sandboxed --verbose_failures
bazel aquery --include_param_files //path/to:target
bazel build //path/to:target --subcommands
bazel clean
bazel build //path/to:target
```

Use a clean only as a controlled comparison. If it changes the result, find the
undeclared dependency or nondeterminism instead of institutionalizing cleaning.

See [HERMETICITY-CACHING.md](HERMETICITY-CACHING.md).

## Test Commands

```bash
bazel test //app/service:all
bazel test //app/service:test --test_output=errors
bazel test //app/service:test --test_filter='<framework-specific-filter>'
bazel test //app/service:test --runs_per_test=10
bazel test //app/service:test --cache_test_results=no
bazel test //app/service:test --test_timeout=60
```

Tests must declare data, isolate writable state, obey timeout and exit-code
contracts, and avoid network or machine-local dependencies unless the test type
explicitly models them.

## CI Baseline

```bash
bazelisk test --config=ci //...
```

- Pin Bazel and module dependencies.
- Keep output bases stable only within a trusted, compatible runner/cache scope.
- Share a remote cache only after actions are hermetic.
- Use credentials outside shared rc files.
- Retain a repository-wide stable-branch build/test even when PRs use precise
  affected-target fast paths.
- Collect Build Event Protocol data and JSON profiles before tuning.

```bash
bazel test --config=ci //... \
  --build_event_json_file="$PWD/bep.json" \
  --profile="$PWD/profile.json.gz"

bazel analyze-profile "$PWD/profile.json.gz"
```

See [CI-PERFORMANCE.md](CI-PERFORMANCE.md).

## Failure Router

| Symptom | First inspection |
|---|---|
| Target not found | Package boundary, label spelling, `query //pkg:*` |
| Visibility error | Producer's visibility and intended API boundary |
| Missing symbol/header/import | Direct `deps`, ruleset strict-deps diagnostics |
| Wrong `select()` branch | Same flags under `cquery`, inspect build settings |
| Wrong compiler/tool | Toolchain resolution debug and execution platform |
| Action missing a file | `aquery` inputs and sandbox failure |
| Works locally, fails remotely | Host tools, environment, runfiles, platform constraints |
| Rebuilds unexpectedly | `aquery`, execution log, `--explain`, cache miss diagnostics |
| Cache hit produces wrong behavior | Undeclared input/environment or non-hermetic repository rule |
| Test is flaky | Test isolation, data, time, concurrency, randomized repetition |
| External repo missing | `bazel mod graph`, `show_repo`, `use_repo()` imports |
| Dependency version surprising | `bazel mod explain`, `all_paths`, root overrides |
| Analysis is slow or memory-heavy | Configured-target count, transitions, depset flattening, profile |
| Execution is slow | Critical path, action parallelism, local/remote queue and transfer time |

## Before Submitting a Change

```bash
buildifier -mode=check -lint=warn -r .
bazel mod tidy
bazel mod graph
bazel query //path/to/changed/package:all
bazel test //path/to/affected/...
git diff --check
```

Then confirm:

- labels and loads are explicit,
- direct dependencies are correct,
- visibility remains narrow,
- new tools and data are declared,
- generated artifacts and runfiles work outside the source tree,
- configuration changes were tested under relevant platforms/configs,
- `MODULE.bazel.lock` changed only when expected,
- and CI/repository-wide validation covers the change at the appropriate stage.

## Deep Guides

- [BUILD-GRAPH.md](BUILD-GRAPH.md) — packages, labels, target design,
  dependencies, visibility, tests, and BUILD tooling
- [BZLMOD.md](BZLMOD.md) — modules, extensions, repository mappings, lockfiles,
  vendoring, and migration
- [CONFIGURATION.md](CONFIGURATION.md) — rc files, build settings, `select()`,
  platforms, toolchains, execution groups, and transitions
- [QUERIES-DEBUGGING.md](QUERIES-DEBUGGING.md) — query languages, affected
  targets, build phases, and diagnostic playbooks
- [HERMETICITY-CACHING.md](HERMETICITY-CACHING.md) — action contracts,
  sandboxing, runfiles, remote cache/execution, and cache debugging
- [CI-PERFORMANCE.md](CI-PERFORMANCE.md) — CI scope, remote infrastructure,
  BEP, profiles, tests, and performance tuning
- [STARLARK.md](STARLARK.md) — symbolic macros, custom rules, providers,
  actions, repository logic, and testing
- [ADOPTION.md](ADOPTION.md) — migration slices, parallel builds, ecosystem
  dependencies, rollout, and cutover

## Authoritative Sources

- [Bazel command-line reference](https://bazel.build/reference/command-line-reference)
- [Build concepts](https://bazel.build/concepts/build-ref)
- [Query guide](https://bazel.build/query/guide)
- [Bzlmod commands](https://bazel.build/external/mod-command)
- [Bazel best practices](https://bazel.build/configure/best-practices)
- [Buildifier](https://github.com/bazelbuild/buildtools/tree/master/buildifier)
- [Buildozer](https://github.com/bazelbuild/buildtools/tree/master/buildozer)
- [Gazelle](https://github.com/bazel-contrib/bazel-gazelle)
