# Configuration, Platforms, and Toolchains

Use this reference for `.bazelrc`, named configs, `select()`, `config_setting`, Starlark build settings, platforms, toolchains, compatibility, transitions, or execution groups.

## Contents

- Configuration layers
- `.bazelrc` design
- Named configs
- `select()` and build settings
- Platforms and compatibility
- Toolchains
- Transitions and configuration growth
- Execution groups
- Diagnostics and review checklist

## Configuration Layers

A Bazel target is not fully defined by its label. Command flags, rc expansion, build settings, platforms, toolchains, and transitions produce a **configured target**. The same label may be analyzed more than once in one invocation under different configurations.

Keep these sources distinct:

| Source | Role |
|---|---|
| `.bazelversion` | exact Bazel binary selected by Bazelisk |
| `MODULE.bazel` | external modules, extensions, toolchain/execution-platform registration |
| `.bazelrc` | shared command flags and named user workflows |
| command line | invocation-specific choices |
| `config_setting` / constraint values | conditions consumed by `select()` |
| Starlark build settings | typed project-specific configuration values |
| platform targets | named collections of constraints |
| toolchains | tools/providers selected for target + execution platform |
| transitions | rules intentionally changing configuration for dependencies/outputs |

Do not use one layer to imitate another. For example, an environment variable is not a substitute for a declared build setting, and a hardcoded compiler path is not a substitute for a toolchain.

## `.bazelrc` Design

`.bazelrc` is a line-oriented option file, not Starlark. Keep checked-in configuration understandable and reproducible.

```text
# Shared repository defaults.
common --color=yes

# Build/test behavior.
build --show_timestamps
test --test_output=errors

# Named workflow.
build:ci --lockfile_mode=error
test:ci --test_output=errors

# Optional per-user overrides; user.bazelrc is ignored by Git.
try-import %workspace%/user.bazelrc
```

This is illustrative. Preserve existing repository behavior and verify every flag against the pinned Bazel version.

### Scope Flags Narrowly

- `startup` lines: JVM/client/server startup options. These appear before the command on the CLI.
- `common` lines: options accepted across commands.
- `build`, `test`, `run`, `query`, `cquery`, `aquery`, and other command sections: command-specific policy.
- `command:name`: named configuration expanded by `--config=name` for that command and its inheritance rules.

Do not place a flag under `common` just because many commands happen to accept it. Global scope magnifies cache keys, user surprise, and compatibility constraints.

### Debug RC Expansion

When the command line behaves differently across machines or CI:

```bash
bazel --announce_rc build //app:target
bazel --ignore_all_rc_files build //app:target
```

`--ignore_all_rc_files` is a startup option and therefore appears before the command. Compare the announced rc files and expanded options before blaming the target graph.

### Per-User Configuration

Use a checked-in `try-import %workspace%/user.bazelrc` plus an ignored file for local UI/resource preferences. A user file should not be required for correctness. If a flag changes outputs, dependency resolution, target platform, or toolchain selection, encode the supported choice in shared configuration and CI rather than relying on undocumented local setup.

### Do Not Normalize Every Flag

Some values must remain environment-specific: remote endpoints, resource limits, local output roots, or credentials. Expose stable named configs and documented integration points without assuming one literal value works on every host.

## Named Configs

Named configs make supported workflows explicit:

```text
build:dev --compilation_mode=fastbuild

build:release --compilation_mode=opt
build:release --platforms=//platforms:linux_x86_64

build:ci --lockfile_mode=error
test:ci --test_output=errors
```

Use:

```bash
bazel build --config=release //app:binary
bazel test --config=ci //...
```

### Config Principles

- Name workflows by intent (`ci`, `release`, `asan`, `linux_arm64`), not by a long list of flags.
- Keep expansion shallow. Nested/recursive `--config` chains are difficult to debug.
- Avoid two configs that silently contradict each other; document whether combinations are supported.
- Ensure a config means the same thing in local and CI usage.
- Put frequently varied user choices in named configs or build settings, not by editing `.bazelrc`.
- Use `--announce_rc` in diagnostics to see the actual expansion.

## `select()`

`select()` configures an attribute based on conditions. Each key is a `config_setting` or `constraint_value` label.

```starlark
config_setting(
    name = "linux_x86_64",
    constraint_values = [
        "@platforms//cpu:x86_64",
        "@platforms//os:linux",
    ],
    visibility = ["//visibility:public"],
)

some_library(
    name = "runtime",
    srcs = select(
        {
            ":linux_x86_64": ["runtime_linux_x86_64.ext"],
            "//conditions:default": ["runtime_portable.ext"],
        },
        no_match_error = "runtime requires a supported target platform",
    ),
)
```

### Matching Rules

Exactly one effective value must be selected:

- if one condition matches, use it;
- if multiple conditions match and one is a strict specialization of the others, use the specialization;
- if multiple incomparable conditions match different values, analysis fails as ambiguous;
- if none matches, `//conditions:default` is used if present;
- otherwise analysis fails, optionally with `no_match_error`.

Do not add `//conditions:default` mechanically. For unsupported platforms or required choices, an explicit no-match failure can be safer than silently using a generic branch.

### Prefer Constraint Semantics

For OS/CPU/environment capability, match constraint values rather than the exact label passed to `--platforms`. Different platform targets can legitimately represent the same relevant constraints.

```starlark
# Prefer: semantic constraint match.
config_setting(
    name = "is_linux",
    constraint_values = ["@platforms//os:linux"],
)
```

Avoid matching the literal `--platforms` label unless identity, not capability, is the real requirement. Exact platform identity over-constrains consumers and makes compatible custom platforms unexpectedly miss.

### Keep Selects Local and Legible

- Select the smallest attribute that differs, not an entire duplicated target.
- Reuse well-named public `config_setting`s for stable repository concepts.
- Do not build an unbounded matrix of boolean selects; define a platform or typed build setting that captures the supported states.
- Use `selects.with_or`/Skylib helpers only when they clarify repeated combinations; ordinary `select()` should remain the default.
- Test every supported branch with an explicit CI configuration.

Traditional `bazel query` cannot tell which branch is selected; it sees possible edges. Use `cquery` with the same flags/config.

## Starlark Build Settings

Use typed Starlark build settings for project-specific flags instead of legacy `--define` strings. A build setting is a target, which makes its identity and visibility explicit and lets rules read it through providers.

Typical invocation:

```bash
bazel build //app:binary --//config:edition=enterprise
```

For ergonomics, define a flag alias in the root module or `.bazelrc` where supported by the pinned Bazel:

```text
common --flag_alias=edition=//config:edition
```

Then:

```bash
bazel build //app:binary --edition=enterprise
```

### Build-Setting Rules

- Give settings a typed contract and validate values during analysis.
- Keep labels stable; they are public configuration API.
- Give externally selectable settings intentional visibility.
- Avoid reading arbitrary environment variables in rule analysis as hidden configuration.
- Use a label-typed setting when the choice is naturally a provider-bearing target/tool rather than a string.
- Prefer an ordinary attribute when the choice belongs to one target, not the entire transitive configuration.

## Platforms

A platform is a named set of constraint values:

```starlark
platform(
    name = "linux_x86_64",
    constraint_values = [
        "@platforms//cpu:x86_64",
        "@platforms//os:linux",
    ],
)
```

Build for it with:

```bash
bazel build //app:binary --platforms=//platforms:linux_x86_64
```

### Three Platforms

| Concept | Meaning |
|---|---|
| Host platform | machine running Bazel itself |
| Execution platform | machine/environment running a particular action |
| Target platform | machine/environment where final output will run |

Host and execution platforms are often the same locally, which hides mistakes. Remote execution and cross-compilation reveal them.

Example: Bazel runs on macOS; compilation executes on remote Linux; the output targets Linux ARM64. A code generator must execute on remote Linux, while generated code is compiled for Linux ARM64.

### Constraint Design

- Reuse generic constraints from `@platforms` for OS and CPU.
- Add repository/ruleset constraints only for stable capabilities that affect compatibility/toolchain selection.
- Do not encode every feature flag as a platform constraint.
- Avoid mutually contradictory values from the same constraint setting.
- Consider whether a constraint describes target capability, execution capability, or toolchain compatibility.

### Target Compatibility

```starlark
some_binary(
    name = "mac_helper",
    target_compatible_with = ["@platforms//os:macos"],
)
```

An incompatible target is skipped/treated as incompatible in wildcard expansion according to command semantics, rather than failing deep inside a compiler action. Use compatibility attributes when unsupported platforms are structural, not as an arbitrary filtering system.

### Execution Compatibility

```starlark
some_rule(
    name = "sign_bundle",
    exec_compatible_with = ["@platforms//os:macos"],
)
```

This constrains where actions for that target may execute. It does not say the output itself targets macOS.

## Toolchains

Toolchains separate **what tool capability a rule needs** from **which concrete compiler/interpreter/SDK provides it** for a target and execution platform.

Resolution inputs include:

- toolchain types required by the rule;
- target platform constraints;
- available execution platforms;
- registered toolchains;
- `target_compatible_with` and `exec_compatible_with` restrictions;
- registration order/preferences.

### Use Ruleset Toolchains First

Language rulesets normally provide module extensions and registration helpers. Follow their version-matched documentation. Do not write a custom toolchain because a binary exists on disk.

For Bazel 9, toolchain registration may occur through `MODULE.bazel`, a module extension, or ruleset-specific setup. Inspect:

```bash
bazel cquery //app:binary --toolchain_resolution_debug='.*'
```

The exact debug flag syntax/availability is version-sensitive; confirm against `bazel help` for the pinned version.

### Custom Toolchain Shape

A custom toolchain generally needs:

1. a `toolchain_type` target;
2. a provider describing the tool/files/options;
3. a rule that returns `platform_common.ToolchainInfo`;
4. concrete toolchain implementation targets;
5. `toolchain()` declarations with target and execution constraints;
6. registration;
7. consuming rules declaring the toolchain type and using `ctx.toolchains`.

Do not put host paths in `ToolchainInfo`. Tools and support files should be Bazel artifacts/runfiles so action keys and remote execution remain correct.

## Transitions and Configuration Growth

A transition changes build settings for a dependency or output. Tool/exec transitions are fundamental to cross-compilation, but custom transitions are advanced and can multiply configured targets.

Use a custom transition only when the dependency genuinely must be analyzed under a different configuration and a normal attribute, toolchain, platform, or top-level flag cannot express it.

### Risks

- the same target is analyzed under many configurations;
- memory and analysis time grow;
- query/debug output becomes harder to interpret;
- allowlists and transition APIs add maintenance;
- rules can accidentally split configuration on high-cardinality values;
- users cannot reason about command-line flags by looking only at top-level config.

Before adding a transition:

1. state the configuration invariant it enforces;
2. inspect existing ruleset/toolchain capabilities;
3. estimate how many configured-target variants it creates;
4. use `cquery --transitions`/configuration output to verify behavior;
5. test multiple top-level configurations and platforms;
6. profile analysis memory/time on representative graphs.

## Execution Groups

Execution groups allow different action groups from one target to use different toolchains and execution platforms. They are appropriate when a rule performs stages with genuinely different execution requirements, for example compiling on remote Linux and code-signing on macOS.

Rule authors declare named groups with toolchain types and execution constraints, then assign each action to the correct group. Target authors can refine group-specific execution constraints and properties.

```starlark
my_rule(
    name = "bundle",
    exec_properties = {
        "mem": "8g",
        "link.mem": "24g",
    },
    exec_group_compatible_with = {
        "sign": ["@platforms//os:macos"],
    },
)
```

The rule definition must actually define the named groups. Do not treat arbitrary action mnemonics as stable execution-group names.

If an action consumes a toolchain from an execution group, declare that same execution group on the action. A mismatch can remain latent until platform resolution changes.

## Configuration Diagnostics

| Problem | Tool |
|---|---|
| Unexpected rc flag | `--announce_rc`; compare `--ignore_all_rc_files` |
| Wrong `select()` branch | `cquery` with identical flags/config |
| Target appears multiple times | `cquery` configuration IDs/output |
| Unexpected transition | `cquery --output=transitions` and transition flags supported by version |
| No matching condition | inspect platform constraints/build settings and `config_setting` visibility |
| Ambiguous `select()` | find simultaneously matching incomparable settings |
| No matching toolchain | toolchain-resolution debug + registered types/platform constraints |
| Wrong machine runs action | distinguish target vs execution compatibility; inspect `aquery`/execution platform |
| Analysis memory growth | count configured variants; inspect transitions and profile analysis |

Re-run `cquery`/`aquery` with the exact `.bazelrc` config, platform, and user flags from the failing invocation. A query under default flags cannot explain a `--config=ci` build.

## Review Checklist

- [ ] Flag placement matches startup/common/command scope.
- [ ] Checked-in rc files are sufficient for correctness; user rc is optional.
- [ ] Named configs express intent, remain shallow, and are exercised in CI.
- [ ] `select()` conditions are semantic, visible to consumers, unambiguous, and tested.
- [ ] Project flags use typed build settings rather than hidden environment or `--define`.
- [ ] Host, execution, and target platforms are not conflated.
- [ ] Platform constraints model stable capabilities.
- [ ] Toolchains declare tools/files; no host `PATH` or absolute SDK dependency leaks in.
- [ ] Custom transitions are necessary, bounded, and measured.
- [ ] Execution-group actions use the matching group's toolchains/platform.

## Sources

- Bazelrc files: https://bazel.build/run/bazelrc
- Commands and options: https://bazel.build/docs/user-manual
- Configurable attributes (`select()`): https://bazel.build/docs/configurable-attributes
- Starlark configurations/build settings: https://bazel.build/extending/config
- Platforms: https://bazel.build/extending/platforms
- Platforms migration/target vs execution: https://bazel.build/concepts/platforms
- Platforms and toolchains rules: https://bazel.build/reference/be/platforms-and-toolchains
- Toolchains: https://bazel.build/extending/toolchains
- Execution groups: https://bazel.build/extending/exec-groups
- `MODULE.bazel` directives: https://bazel.build/rules/lib/globals/module
