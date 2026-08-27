# BUILD Graph and Repository Structure

Use this reference when creating packages and targets, editing BUILD files, tightening dependencies, setting visibility, or deciding how a Bazel monorepo should be organized.

## Contents

- Packages and source ownership
- Target granularity
- Labels and target patterns
- Direct dependency discipline
- BUILD file style
- Visibility and APIs
- Tests and runtime data
- BUILD maintenance tooling
- Review checklist

## Packages Are Graph Boundaries

A Bazel package is a directory containing `BUILD` or `BUILD.bazel`. It owns files in that directory and below it until another BUILD file starts a subpackage.

```text
services/payments/BUILD.bazel       package //services/payments
services/payments/main.go           belongs to //services/payments
services/payments/testdata/a.json   belongs to //services/payments
services/payments/api/BUILD.bazel   starts package //services/payments/api
services/payments/api/types.go      belongs to //services/payments/api
```

The package name is a logical path from the repository root, not a language package-manager name. A file below a subpackage cannot be referenced from the parent package as if the subpackage did not exist.

### When to Add a BUILD File

Prefer a new package when the directory has its own:

- language package/module identity;
- ownership or review boundary;
- public/private dependency boundary;
- platform compatibility;
- build/test lifecycle;
- independently reusable library or executable;
- meaningful opportunity for narrower invalidation.

Avoid creating a package purely because a directory exists when it contains only internal data tightly coupled to its parent's target. Conversely, a BUILD file that reaches deeply through multiple source directories is a warning that the package is too broad.

### Do Not Copy JavaScript Workspace Layouts Blindly

Bazel does not require `apps/` and `packages/`. Those names may be appropriate, but they carry no special Bazel meaning. Prefer structure that reflects domain ownership, deployable units, language conventions, and dependency boundaries:

```text
services/
  billing/
  identity/
libraries/
  money/
  auth/
platforms/
tools/
third_party/
```

This is an example, not a required template. Existing source layout and language rules should drive the decision.

## Target Granularity

Targets are Bazel's units of analysis, scheduling, caching, visibility, and test impact. Choose the smallest cohesive unit whose dependency list and interface make sense.

### Split a Target When

- part of its sources has substantially different dependencies;
- a subset is reused independently;
- visibility differs;
- the sources build for different target platforms;
- the test impact should be isolated;
- the target is owned by different teams;
- a dependency cycle can be broken along a real API boundary.

### Keep a Target Together When

- files implement one indivisible language module;
- every source always changes/builds/tests together;
- splitting would expose implementation details;
- the ruleset or compiler gains little from finer nodes;
- one-file targets would create more graph and maintenance cost than useful incrementality.

### Failure Modes

| Shape | Symptom | Correction |
|---|---|---|
| Monolithic target | Small edit rebuilds a service; deps list contains unrelated systems | Split around cohesive APIs/dependency sets |
| Target per source file | Huge BUILD files and analysis overhead; awkward imports | Group the sources that form one library/module |
| Directory-spanning target | Package boundaries are unclear; recursive globs | Add BUILD packages along real module boundaries |
| Convenience aggregate used everywhere | Consumers gain enormous transitive closures | Depend on the narrow provider target directly |

## Labels

Full conceptual form:

```text
@repository//package/path:target
```

Common forms:

| Form | Meaning |
|---|---|
| `//services/billing:server` | `server` target in the main repo package |
| `//services/billing` | Shorthand for `//services/billing:billing` only |
| `:server` | Target in the current package |
| `@rules_python//python:defs.bzl` | Target/file through an apparent external repo name |
| `@@canonical//pkg:target` | Canonical repo name; diagnostic/tooling form, not a source-code default |

Prefer explicit colons when the shorthand could confuse package and target names. Inside BUILD files, use `:local_target` for same-package dependencies and full `//pkg:target` labels across packages.

### Labels Are Not Paths

`//foo/bar:baz` identifies a target. It does not mean `$REPO/foo/bar/baz` exists. Generated outputs can be configuration-specific and multiple artifacts may come from one target. Obtain outputs through providers, `bazel cquery --output=files`, rule-supported location expansion, or the Build Event Protocol—not string concatenation with `bazel-bin`.

### Target Patterns

Target patterns select sets for commands; they are not dependency declarations.

| Pattern | Selection |
|---|---|
| `//foo:bar` | one target |
| `//foo:all` | rule targets in one package |
| `//foo/...` | rule targets in packages recursively under `foo` |
| `//...` | rule targets in all main-repo packages |
| `-//foo/legacy/...` | subtract a pattern after `--` or where option parsing is unambiguous |

`//...` does not include external repositories. Targets tagged `manual` are skipped by positive wildcard patterns for build/test, but `query` deliberately still sees them. Subtracting a target pattern does not guarantee that target will not build: a remaining top-level target may depend on it.

## Direct Dependency Discipline

The declared target graph should match the dependency graph visible in the source.

```starlark
some_library(
    name = "checkout",
    srcs = ["checkout.ext"],
    deps = [
        "//libraries/money",
        "//services/catalog/api",
    ],
)
```

If `checkout.ext` directly uses symbols from `//libraries/money`, list that target even if `//services/catalog/api` currently depends on it. Otherwise:

- strict-deps checks may fail;
- removal or refactoring of the intermediate edge breaks the build;
- dependency queries lie about architecture;
- affected-target selection may omit the consumer;
- remote/cache correctness can become fragile for permissive rulesets.

Do not list dependencies that sources do not use just because they are “standard.” Unused edges increase analysis, compilation, classpaths/include paths, cache invalidation, and coupling.

### `srcs`, `deps`, `data`, and Tools

These names are common, but the selected ruleset defines the exact contract.

```starlark
some_test(
    name = "invoice_test",
    srcs = ["invoice_test.ext"],
    data = ["//testdata/invoices:cases"],
    deps = [
        ":invoice",
        "//testing/assertions",
    ],
)
```

- `srcs`: files directly processed or source-producing targets.
- `deps`: separately analyzed/compiled providers needed by the source.
- `data`: runtime files placed into runfiles.
- `tools` or executable attributes: programs run during an action in the execution configuration.

Do not put runtime fixtures in `deps` merely to make them appear. Do not put compiler/plugin tools in `data` when the ruleset offers an executable or toolchain attribute.

### Directory Inputs

Avoid directory labels as inputs. Bazel needs to know individual file identities for correct invalidation. Prefer explicit files, a `filegroup`, or a controlled `glob()`:

```starlark
filegroup(
    name = "cases",
    srcs = glob(["*.json"]),
    visibility = ["//services/billing:__subpackages__"],
)
```

## BUILD File Style

Choose `BUILD.bazel` or `BUILD` consistently with the repository. If both exist in one directory, `BUILD.bazel` takes precedence, which is rarely a useful situation.

### Recommended Order

1. `load()` statements
2. `package()` and package metadata
3. exported files/package groups/config settings when applicable
4. library targets
5. binaries
6. tests and suites
7. utility/generation targets

Buildifier is the final authority on formatting and load/dependency ordering for repositories that use it.

### Loads

In Bazel 9, explicitly load external language rules from public entry points:

```starlark
load("@rules_cc//cc:cc_binary.bzl", "cc_binary")
load("@rules_cc//cc:cc_library.bzl", "cc_library")
load("@rules_cc//cc:cc_test.bzl", "cc_test")
```

Do not load from `private/` paths in a ruleset. Avoid wrapper files that simply re-export every external rule; they hide provenance and make upgrades harder unless the wrapper is a deliberate, tested compatibility boundary.

### Globs

Use `glob()` when membership by extension is the stable contract and the repository's generator/tooling supports it:

```starlark
srcs = glob(
    ["*.cc"],
    exclude = ["*_test.cc"],
)
```

Avoid recursive source globs:

```starlark
# Avoid: membership changes when subpackages appear, and review is less explicit.
srcs = glob(["**/*.cc"])
```

Recursive globs skip directories that contain BUILD files. Adding a subpackage can therefore remove files from a parent's target without editing that target. This is correct package semantics but a poor surprise.

### Keep Dependency Lists on Targets

```starlark
# Prefer
some_library(
    name = "a",
    deps = ["//lib:x"],
)

some_library(
    name = "b",
    deps = ["//lib:x"],
)
```

Avoid a shared `COMMON_DEPS` variable for ordinary dependency lists. It obscures which source uses which provider and prevents automated tools from editing targets independently.

### Comments

Comment why a target, dependency, visibility exception, tag, compatibility restriction, or non-obvious option exists. Do not narrate obvious syntax.

## Visibility

Target visibility controls which packages may depend on a target. Load visibility controls which packages may load a `.bzl` file.

### Target Visibility Forms

| Visibility entry | Grants access to |
|---|---|
| `//visibility:private` | declaration location only |
| `//visibility:public` | every package |
| `//foo/bar:__pkg__` | exactly `//foo/bar` |
| `//foo/bar:__subpackages__` | `//foo/bar` and all subpackages |
| `//policy:clients` | packages listed by a `package_group` |

Use a shared policy for repeated boundaries:

```starlark
package_group(
    name = "billing_clients",
    packages = [
        "//services/billing/...",
        "//services/checkout",
    ],
)
```

```starlark
some_library(
    name = "billing_api",
    visibility = ["//visibility/policies:billing_clients"],
)
```

The `packages` syntax inside `package_group` is not label syntax: use `//foo/bar` and `//foo/bar/...`, not `:__pkg__` or `:__subpackages__`.

### Visibility Review Questions

- Is this target an intended API or only an implementation detail?
- Can a narrower subtree/package group express the consumer set?
- Is a test-only friendship better than making the target public?
- Would a small public facade keep several internal targets private?
- Does a `.bzl` file need load visibility as well as target visibility on any `bzl_library`?

Avoid disabling visibility checks. A temporary diagnostic with `--check_visibility=false` does not justify submitted code that bypasses the boundary.

## Tests

Tests are executable targets run by `bazel test`; direct execution is not the authoritative test environment.

### Declare the Environment

- Put fixtures/resources in `data`.
- Use runfiles libraries to resolve runtime files.
- Write temporary files under the test-provided temporary directory.
- Avoid access to developer credentials, user home, local services, uncontrolled network, locale, and wall clock unless the test explicitly models them.
- Use a local hermetic service fixture instead of a shared mutable test environment where practical.

### Size and Timeout

`size` influences local scheduling/resource assumptions and implies a default timeout. `timeout` controls the test target's total time limit, not each framework test case. Choose the smallest truthful values and use `--test_verbose_timeout_warnings` to find over-large declarations.

| `size` | Default timeout label | Limit |
|---|---|---|
| `small` | `short` | 60 s |
| `medium` | `moderate` | 300 s |
| `large` | `long` | 900 s |
| `enormous` | `eternal` | 3600 s |

Use `flaky = True` only when a test is genuinely known to be flaky and the remediation is tracked. It changes retry semantics; it is not a cure. Use `shard_count` only when the test runner implements Bazel sharding correctly.

### Tags and Compatibility

- Use `target_compatible_with` for target-platform impossibility.
- Use `exec_compatible_with` for execution-platform requirements.
- Use descriptive tags for policy/filtering.
- Reserve `manual` for targets wildcard invocations should not select at all.
- Use `test_suite` for a curated semantic suite, not as a replacement for target patterns everywhere.

## BUILD Maintenance Tooling

### Buildifier

Buildifier formats BUILD, `.bzl`, and module-like Starlark files and can emit lint diagnostics:

```bash
buildifier -mode=check -lint=warn path/to/BUILD.bazel path/to/rules.bzl
buildifier -mode=fix path/to/BUILD.bazel path/to/rules.bzl
```

Prefer a repository-pinned Buildifier target or tool version over an unpinned global binary in CI.

### Buildozer

Buildozer performs structured edits. Prefer it for broad mechanical changes—adding/removing deps, renaming attributes, or editing many rules—when commands can express the intended change. Review the resulting diff and run Buildifier/tests.

### Gazelle

Gazelle can generate/update BUILD files for supported languages and extensions. It natively supports Go and protobuf; other language support comes from extensions maintained with those ecosystems. Before adopting it:

- decide whether BUILD files or another manifest are authoritative;
- pin the Gazelle binary and extensions;
- encode repository directives close to their scope;
- run it in CI check mode so generated files do not drift;
- avoid mixing hand-owned and generator-owned attributes without a documented merge contract.

Gazelle is a bazel-contrib project and explicitly not an official Google product. Its own documentation is authoritative for its behavior.

## Review Checklist

- [ ] New files belong to the intended package; no accidental subpackage crossing.
- [ ] Target granularity matches dependencies, ownership, visibility, and test impact.
- [ ] Every direct source dependency has a direct graph edge.
- [ ] Runtime resources are in `data`; build tools are declared executable/toolchain deps.
- [ ] Public visibility is intentional and narrow.
- [ ] Loads use public, version-compatible ruleset entry points.
- [ ] No recursive source glob or directory input hides membership.
- [ ] Tests declare resources, compatibility, size, timeout, and known tags accurately.
- [ ] BUILD/Starlark files pass Buildifier and repository lint policy.
- [ ] Narrow targets and relevant reverse dependents build/test.

## Sources

- Repositories, workspaces, packages, and targets: https://bazel.build/concepts/build-ref
- Labels: https://bazel.build/concepts/labels
- BUILD files: https://bazel.build/concepts/build-files
- Dependencies: https://bazel.build/concepts/dependencies
- Visibility: https://bazel.build/concepts/visibility
- BUILD style guide: https://bazel.build/build/style-guide
- Build target patterns: https://bazel.build/run/build
- Test encyclopedia: https://bazel.build/reference/test-encyclopedia
- Common rule definitions: https://bazel.build/reference/be/common-definitions
- Buildtools (Buildifier/Buildozer): https://github.com/bazelbuild/buildtools
- Gazelle: https://github.com/bazel-contrib/bazel-gazelle
