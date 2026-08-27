# Queries and Debugging

Use this reference to inspect targets, dependencies, configurations, actions, external modules, output files, toolchain selection, or build failures.

## Contents

- Choose the graph layer
- Target patterns
- `query`
- `cquery`
- `aquery`
- `mod`
- Affected-target analysis
- Failure-phase diagnostics
- Output and automation
- Debugging playbooks

## Choose the Graph Layer

| Tool | Graph/state | Best questions |
|---|---|---|
| `query` | post-loading, unconfigured target graph | What targets exist? deps/rdeps/path/kind/attribute? |
| `cquery` | post-analysis configured target graph | Which select/transition/platform/toolchain result? Which providers/outputs? |
| `aquery` | action graph | What command, inputs, outputs, mnemonic, action key? |
| `mod` | external module/repository graph | Why was a module/repo/version/extension selected? |
| execution log | executed action records | Why did cache/execution differ across invocations? |
| profile | timing/resource events | Where did loading/analysis/execution spend time? |
| BEP/BES | invocation events/results | What completed, failed, produced artifacts/tests? |

Use the same top-level flags, named config, platform, aspects, and toolchain settings as the failing build. `cquery` and `aquery` under the default configuration do not explain `bazel build --config=ci --platforms=...`.

## Target Patterns

Patterns are command-line selectors, not labels stored in `deps`.

```bash
bazel build //app/server:server
bazel test //app/server:all
bazel test //services/...
bazel build //...
```

| Pattern | Meaning |
|---|---|
| `//foo/bar:baz` | exact target |
| `//foo/bar` | shorthand for target named `bar` in package `//foo/bar` |
| `//foo/bar:all` | rule targets in one package |
| `//foo/...` | rule targets in all packages below `foo` |
| `//...` | rule targets in all packages in the main repository |
| `@repo//foo/...` | targets in a named external repository |

Negative patterns subtract from the top-level selection:

```bash
bazel test -- //... -//experimental/...
```

Use `--` so a following `-//...` is not parsed as an option. A subtracted target may still be built as a dependency of a retained target. `manual` targets are excluded from positive wildcard build/test patterns but are still visible to `query`.

## `bazel query`

`query` loads packages and evaluates BUILD/macro declarations, but it does not apply configurations. It has no single selected `select()` branch and can show all possible edges.

### Core Operators

```bash
# Transitive dependencies.
bazel query 'deps(//app/server:server)'

# Reverse dependencies, bounded by an explicit universe.
bazel query 'rdeps(//..., //libraries/auth:auth)'

# One path explaining a dependency.
bazel query 'somepath(//app/server:server, //libraries/auth:auth)'

# All dependency paths (can be very large).
bazel query 'allpaths(//app/server:server, //libraries/auth:auth)'

# Rule kind filtering.
bazel query 'kind(".*_test rule", //services/...)'

# Attribute filtering. Regex is matched against the attribute's rendered value.
bazel query 'attr(tags, "manual", //...)'

# Expand test suites and select test rules from an expression.
bazel query 'tests(//services/payments:all)'

# Set algebra.
bazel query 'deps(//app:a) intersect deps(//app:b)'
bazel query '//services/... except //services/legacy/...'
```

Other useful operators include `filter`, `labels`, `siblings`, `same_pkg_direct_rdeps`, `visible`, and `buildfiles`. Confirm exact semantics against the pinned version's query reference before putting a complex expression in automation.

### Direct Dependencies

Limit depth to inspect one graph step:

```bash
bazel query 'deps(//app/server:server, 1)' --noimplicit_deps
```

Implicit dependencies may include toolchains and rule-internal edges. Removing them can make architectural views clearer, but do not assume `--noimplicit_deps` represents every input needed to build.

### Reverse Dependencies

`rdeps(universe, targets)` requires a universe because reverse edges are meaningful only among loaded targets:

```bash
bazel query 'rdeps(//services/..., //libraries/money:money)'
```

Make the universe broad enough to include all possible consumers. `//services/...` intentionally omits tools, tests, or other repository areas outside that subtree.

For large graphs, Sky Query's `allrdeps` can avoid writing an explicit universe but has output/ordering restrictions. Use it deliberately and verify the version's flags.

### Paths

Use `somepath` first. `allpaths` can explode on a large monorepo.

```bash
bazel query \
  'somepath(//services/checkout:server, //third_party/logging:logging)' \
  --output=graph > /tmp/dependency.dot
dot -Tsvg /tmp/dependency.dot > /tmp/dependency.svg
```

Use `--nograph:factored` only when merged equivalent nodes obscure the needed detail; unfactored graphs can become enormous.

### BUILD and `.bzl` Dependencies

`deps()` follows target/file edges, not every Starlark file used to define them. When asking which packages/files are needed to define a build, include `buildfiles`:

```bash
bazel query 'buildfiles(deps(//app/server:server))' --output=package
```

This matters for affected-target calculations: a change to a loaded `.bzl` file may affect targets even when that `.bzl` file is not a normal target dependency.

`buildfiles()` synthesizes target-like values for loaded `.bzl` files and does not compose cleanly with every structured output/operator. Treat it as a specialized definition-dependency tool.

### Useful Output Formats

| Output | Use |
|---|---|
| `label` | labels for people/shell pipelines |
| `label_kind` | distinguish rules, source files, generated files |
| `location` | BUILD/source location, grep/editor friendly |
| `package` | unique packages |
| `build` | expanded rule declarations for inspection, not reusable BUILD source |
| `graph` | Graphviz dot |
| `proto` / `streamed_proto` | machine consumption |
| `streamed_jsonproto` | line-delimited structured machine consumption |

For large machine-readable results, prefer streamed formats. Use `--output_file=...` when supported instead of shell redirection for better performance.

Do not assume query ordering unless the chosen `--order_output` contract provides it. When deterministic ordering matters, request it and accept the cost.

## `bazel cquery`

`cquery` analyzes configured targets. It resolves `select()` values, applies transitions, and includes platform/toolchain effects. One label can appear with multiple configuration IDs.

```bash
bazel cquery 'deps(//app/server:server)' --config=ci
```

### Use It For

- why a configured dependency exists or is absent;
- which target is compatible under a platform;
- which configuration a tool dependency uses;
- output files/providers/output groups;
- transition-induced configuration changes;
- toolchain dependencies selected during analysis.

### Selected Dependencies

Compare structural and configured views:

```bash
bazel query 'deps(//app:binary, 1)'
bazel cquery 'deps(//app:binary, 1)' --platforms=//platforms:linux_x86_64
```

If `query` shows both `select()` possibilities but `cquery` shows one, the graph is behaving as designed.

### Output Files

```bash
bazel cquery //app:binary --output=files --config=release
```

Paths are relative to the execution root. The result can include files for every configuration of a label occurring in the analyzed build. Use `config()` when a specific configured instance matters.

Do not hardcode these paths into BUILD logic. `cquery --output=files` is for inspection/tool integration.

### Providers and Build Options

Starlark output can inspect configured providers/options:

```bash
bazel cquery //app:binary \
  --output=starlark \
  --starlark:expr="[f.path for f in providers(target)['DefaultInfo'].files.to_list()]"
```

The cquery Starlark dialect is a formatter environment, not ordinary `.bzl` Starlark: it has special helpers, does not support `load()`, and should not be copied into build extensions.

Use a checked-in formatter file for complex/reused automation rather than an unreadable shell-quoted expression.

### Transitions

```bash
bazel cquery //app:binary --transitions=lite
bazel cquery //app:binary --transitions=full
```

Full transition output can be large. Start with lite, identify the relevant edge, then inspect detailed option diffs.

### Universe Scope

`cquery` needs top-level targets to determine configurations. When a query references a broad or indirect graph, set `--universe_scope` to the build targets whose configured graph matters:

```bash
bazel cquery 'deps(//lib:shared)' --universe_scope=//app:binary --config=release
```

An incorrect universe can omit configured instances or analyze a configuration that is not the failing build's context.

## `bazel aquery`

`aquery` exposes actions and artifacts after analysis. It inherits build flags.

```bash
# All actions under a target's configured dependency graph.
bazel aquery 'deps(//app/server:server)' --config=ci

# Compile actions only.
bazel aquery 'mnemonic(".*Compile", deps(//app/server:server))' --config=ci

# Actions reading a matching input path.
bazel aquery 'inputs(".*schema.*", deps(//app/server:server))' --config=ci

# Actions producing a matching output.
bazel aquery 'outputs(".*server.*", deps(//app/server:server))' --config=ci
```

### Use It For

- the actual executable and argument vector;
- response/parameter files;
- declared action inputs and tools;
- output files/directories;
- environment represented in the action;
- action mnemonic and configuration;
- whether an aspect created the action;
- comparing local/CI configuration before execution.

### Filters

`inputs()`, `outputs()`, and `mnemonic()` return actions. They can wrap configured-target expressions, but their result cannot be passed back into `deps()` or another target-graph function:

```bash
# Correct
bazel aquery 'mnemonic("CppCompile", deps(//app:binary))'

# Invalid shape: inputs(...) returns actions, not configured targets.
# bazel aquery 'deps(inputs(".*cc", //app:binary))'
```

### Output

Use human text for exploration and proto/JSON proto for tooling. `--output=commands` emits one command per line but may omit the structure needed for robust interpretation. `--include_param_files` reveals response-file contents and can make output very large.

Do not infer cache hits from `aquery`; it describes the action graph, not whether the action executed or was restored. Use execution/BEP data for that.

## `bazel mod`

Use `mod` for external resolution, not `query //external:...`.

```bash
bazel mod graph
bazel mod graph --verbose --include_unused
bazel mod deps rules_python
bazel mod explain rules_python --verbose --include_unused
bazel mod all_paths rules_python
bazel mod show_repo @rules_python
bazel mod show_extension '@rules_python//python/extensions:python.bzl%python'
bazel mod dump_repo_mapping @rules_python
```

The exact extension label/name comes from the ruleset and may differ from the schematic example. Obtain it from `MODULE.bazel`, `bazel mod graph --extension_info=all`, or the ruleset docs.

Use `--base_module` when interpreting an apparent repo name from another module's context.

## Affected-Target Analysis

Bazel knows the target/action graph. Git knows changed paths. Correctly mapping Git changes to affected build/test targets is a separate, high-stakes integration.

### Source Target Reverse Dependencies

For an ordinary source file already known to Bazel:

```bash
bazel query 'rdeps(//..., //libraries/money:money.ext)'
bazel query 'tests(rdeps(//..., //libraries/money:money.ext))'
```

This is a useful diagnostic, not a complete CI algorithm.

### Why Naive Git-to-Query Is Incomplete

Special changes include:

- `BUILD` / `BUILD.bazel`: may change any target declared in the package;
- `.bzl`: may affect every package that loads it, including transitively loaded files;
- `MODULE.bazel` / lockfiles: may change external repos, rule implementations, toolchains;
- `.bazelrc`: may change configurations/action keys globally;
- platforms/toolchains: may affect configured targets far from the file location;
- generators/manifests: may change generated BUILD targets/edges;
- deleted/renamed files: the pre-change graph may be needed to map them;
- implicit/aspect edges: ordinary source rdeps may not capture the policy's intended closure.

### Safe CI Pattern

- Keep `bazel build //...` and `bazel test //...` as stable-branch or periodic truth gates.
- Use a graph-aware affected-target tool only after validating it against full builds over representative history.
- Make global/configuration/ruleset files trigger a conservative broad fallback.
- Include reverse dependents and tests, not only targets in changed directories.
- Keep before/after graph data when deletions and BUILD rewrites matter.
- Monitor false negatives by comparing fast-path and full-path outcomes.

Do not advertise a short `git diff | bazel query` pipeline as universally correct.

## Failure Phases

Classify the failure before changing code.

| Phase | Typical symptoms | Inspect |
|---|---|---|
| Startup/rc | unknown option, server/JVM issue, wrong Bazel | `.bazelversion`, `--announce_rc`, `bazel info release` |
| Module/repository | module not found, repo fetch, mapping, checksum | `bazel mod`, lockfile, extension/repo rule output |
| Loading | package/label/load syntax, missing BUILD, macro error | BUILD boundary, loads, Buildifier, `query` |
| Analysis | visibility, provider, select, compatibility, toolchain | `cquery`, configuration, toolchain debug |
| Execution | compiler/test/action failure, missing input/tool | `aquery`, `--verbose_failures`, sandbox debug |
| Cache/remote | result mismatch, miss, remote-only failure | execution logs, BEP, platform/env/tool identity |
| Performance | slow loading/analysis/action/critical path | JSON profile, action graph, worker/remote metrics |

### Loading Errors

Check:

- whether the label names a real package and target;
- whether a subdirectory gained a BUILD file and changed ownership;
- whether a `.bzl` load uses a public entry point and correct repository mapping;
- whether the external ruleset is declared and version-compatible;
- whether macro arguments match its current API;
- Buildifier syntax/lint diagnostics.

### Analysis Errors

Check:

- direct dependency providers and attribute types;
- visibility of targets/config settings and load visibility;
- `select()` ambiguity/no-match under the exact config;
- target compatibility;
- selected toolchains and execution platforms;
- custom transitions and multiple configured variants;
- whether the error is from the rule implementation rather than an action.

### Execution Errors

Start with:

```bash
bazel build //app:target --verbose_failures --subcommands
```

Then inspect the relevant action:

```bash
bazel aquery 'mnemonic("RelevantMnemonic", deps(//app:target))' \
  --include_param_files
```

For sandbox failures:

```bash
bazel build //app:target --verbose_failures --sandbox_debug
```

`--sandbox_debug` preserves sandbox directories and can consume significant disk. Disable it after the diagnostic.

Do not make `--spawn_strategy=local` the fix. It is a comparison that can prove the action depends on undeclared host state.

## Output and Automation

- Use query proto/streamed JSON proto for graph tooling.
- Use cquery proto/Starlark output for configured providers/options.
- Use aquery proto/JSON proto for actions.
- Use Build Event Protocol for invocation/test/artifact results.
- Use execution logs for executed spawn comparisons.
- Do not parse colored progress lines or assume human-output ordering.
- Add `--output_file` where supported for large outputs.
- Record the invocation ID/config/platform alongside diagnostics.

## Debugging Playbooks

### “Why does A depend on B?”

1. `query somepath(A, B)` for structural path.
2. If configuration matters, repeat with `cquery somepath(A, B)` under exact flags.
3. Inspect BUILD targets along the path for direct vs aggregate/implicit edges.
4. Use `aquery` only if the question is why an action consumes an artifact/tool.

### “Why is the wrong source selected?”

1. Capture `--announce_rc` and exact platform/build settings.
2. `cquery` the target and direct deps.
3. Inspect matching `config_setting`s and constraint values.
4. Check transitions below the top-level target.
5. Test the intended and unintended configs explicitly.

### “Why is the wrong compiler/interpreter used?”

1. Confirm target and execution platform.
2. Inspect registered toolchains/module extension setup.
3. Use toolchain-resolution debug for the pinned Bazel.
4. Use `cquery` for selected toolchain deps.
5. Use `aquery` to confirm the executable and action environment.

### “Why did this action rerun?”

1. Confirm both invocations use identical Bazel/ruleset version, rc expansion, flags, and platforms.
2. Compare compact execution logs.
3. Inspect changed inputs, argv, environment, tool artifacts, execution properties.
4. Check whether one build destroyed incremental state or used a different output base.
5. Fix the action/config identity; do not normalize away a meaningful difference.

### “Why does a target build but `bazel test` fail?”

1. Distinguish compile/link success from test execution.
2. Inspect `data` and runfiles resolution.
3. Check test size/timeout/sharding/flaky policy.
4. Reproduce with `--test_output=errors` and same platform/config.
5. Inspect undeclared network/service/home/temp-file dependencies.

## Sources

- Query language: https://bazel.build/query/language
- Query guide: https://bazel.build/query/guide
- Configurable query: https://bazel.build/query/cquery
- Action graph query: https://bazel.build/query/aquery
- Bzlmod `mod` command: https://bazel.build/external/mod-command
- Build target patterns: https://bazel.build/run/build
- Command-line reference: https://bazel.build/reference/command-line-reference
- Sandboxing diagnostics: https://bazel.build/docs/sandboxing
- Build Event Protocol: https://bazel.build/remote/bep
- JSON trace profile: https://bazel.build/advanced/performance/json-trace-profile
