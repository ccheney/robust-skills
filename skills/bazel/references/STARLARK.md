# Starlark, Macros, Rules, and Repository Logic

Use this guide when the repository needs reusable build declarations, a custom
build rule, a module extension, or other Bazel-specific logic. Keep ordinary
build structure in `BUILD` files until repetition or a missing abstraction
justifies code.

## Choose the Smallest Extension Point

| Need | Prefer | Why |
|---|---|---|
| A few targets with shared defaults | A symbolic macro | Preserves ordinary rules while standardizing their shape |
| A new kind of action or artifact | A custom rule | Gives Bazel a precise analysis-time model of inputs, outputs, tools, and providers |
| Cross-cutting inspection or metadata propagation | An aspect | Traverses an existing dependency graph without rewriting every target |
| External repository generation | A repository rule | Materializes one repository deterministically |
| User-configurable external dependency logic | A module extension | Aggregates tags from the Bzlmod dependency graph and creates repositories |
| Pure reusable calculation | A `.bzl` function | Avoids inventing a graph abstraction when no targets or actions are involved |

Do not start with a custom rule simply because Starlark permits it. Native or
ecosystem rules usually have better toolchain support, interoperability, and
maintenance. Prefer a thin, repository-specific layer over a well-supported
ruleset.

## Starlark Execution Model

Starlark code participates in distinct Bazel phases:

1. **Loading** evaluates `BUILD` and `.bzl` files and constructs declared
   targets.
2. **Analysis** resolves configuration, dependencies, toolchains, providers,
   and actions for configured targets.
3. **Execution** runs the registered actions.

This separation is the source of many Bazel guarantees. Loading and analysis
must not behave like arbitrary build scripts:

- Do not read undeclared files, inspect the current directory, contact the
  network, or run subprocesses from rule implementations.
- Do not make analysis depend on wall-clock time, random values, machine-local
  paths, or ambient environment variables.
- Declare all artifacts and actions during analysis. Let Bazel decide when and
  where actions execute.
- Treat Starlark values as immutable once exposed. Use deterministic ordering
  when converting unordered conceptual data into action arguments or files.
- Use labels to refer to dependencies and tools. Do not construct execution-time
  filesystem paths by concatenating strings.

Repository rules are an intentional exception: they run while Bazel fetches
external repositories and can perform I/O through the repository API. They
still need pinned inputs, integrity checks, declared environment influences,
and deterministic output.

## Organize Starlark Code

A maintainable layout typically separates public entry points from internal
implementation:

```text
tools/
  build_defs/
    BUILD.bazel
    defs.bzl             # small public surface
    private/
      BUILD.bazel
      rules.bzl
      providers.bzl
      transitions.bzl
  extensions/
    BUILD.bazel
    deps.bzl             # module extension entry point
    repositories.bzl
```

Apply these boundaries:

- Give public `.bzl` entry points explicit visibility.
- Keep implementation files private to their package or a narrow subtree.
- Export a small, documented API from `defs.bzl`; avoid asking callers to load
  internals directly.
- Keep providers in a dependency-light file when several rules consume them.
- Keep repository rules and module extensions separate from build rules. They
  run in different contexts and have different responsibilities.
- Prefer one conceptual API per file over a single, ever-growing `defs.bzl`.

Use `load()` statements explicitly. Bazel 9 no longer autoloads externally
maintained language rules on behalf of the repository.

## Symbolic Macros

Use symbolic macros, introduced as the modern macro API in Bazel 8, for new
macro work. Unlike legacy functions that merely call rules, symbolic macros
declare a typed interface and participate in Bazel's macro-aware semantics.

A small example:

```starlark
def _source_bundle_impl(name, visibility, srcs):
    native.filegroup(
        name = name,
        srcs = srcs,
        visibility = visibility,
    )

source_bundle = macro(
    attrs = {
        "srcs": attr.label_list(allow_files = True),
    },
    implementation = _source_bundle_impl,
)
```

The example is intentionally small: callers get a typed `srcs` interface, and
the macro correctly exports its main target by forwarding `visibility`.

### Macro Design Rules

- Keep the public attributes few, typed, and unsurprising.
- Forward `name`, `visibility`, `tags`, `testonly`, and other common semantics
  correctly when they are part of the macro's contract.
- Use `inherit_attrs` when the macro intentionally presents a constrained form
  of another symbolic macro or rule; remove or override inherited attributes
  deliberately.
- Give generated targets stable names derived from the macro's `name`.
- Document every generated target a caller is expected to reference.
- Preserve visibility rather than silently making generated targets public.
- Do not use a macro to hide important dependency edges or generate a large,
  opaque subgraph.
- Do not make callers pass parallel lists whose ordering encodes relationships;
  model those relationships as targets or typed attributes.
- Do not wrap every rule in a repository-specific macro. A wrapper must enforce
  a real policy or remove recurring, meaningful boilerplate.

Prefer a rule when the abstraction needs its own actions, providers,
toolchains, execution requirements, configuration transitions, or queryable
identity.

## Custom Rules

A rule implementation receives a configured `ctx`, declares actions, and
returns providers. It does not execute the build action itself.

```starlark
ReportInfo = provider(
    doc = "Information produced by report_file.",
    fields = {
        "report": "The generated report artifact.",
    },
)

def _report_file_impl(ctx):
    output = ctx.actions.declare_file(ctx.label.name + ".report")

    args = ctx.actions.args()
    args.add("--output", output)
    args.add_all(ctx.files.srcs, before_each = "--source")

    ctx.actions.run(
        executable = ctx.executable._tool,
        arguments = [args],
        inputs = depset(ctx.files.srcs),
        outputs = [output],
        mnemonic = "WriteReport",
        progress_message = "Writing report for %{label}",
    )

    return [
        DefaultInfo(files = depset([output])),
        ReportInfo(report = output),
    ]

report_file = rule(
    implementation = _report_file_impl,
    attrs = {
        "srcs": attr.label_list(allow_files = True),
        "_tool": attr.label(
            default = Label("//tools/report:writer"),
            executable = True,
            cfg = "exec",
        ),
    },
)
```

Treat the example as a minimal shape. Real rules must decide how tool runfiles,
transitive inputs, output groups, platform constraints, and provider contracts
are represented.

### Attributes

- Use the most specific attribute type available.
- Set `allow_files` or allowed file extensions intentionally.
- Use `mandatory = True` when absence has no useful meaning.
- Mark private implicit attributes with a leading underscore.
- Resolve executable tools in the execution configuration with
  `executable = True` and `cfg = "exec"`.
- Prefer toolchains over hard-coded implicit tool labels when the tool varies by
  platform or repository policy.
- Remember that many label attributes are configurable unless explicitly made
  nonconfigurable. Do not promise loading-time behavior for configuration-time
  values.

### Actions

For every action, make the contract exact:

- Declare every input and output artifact.
- Pass tools through executable attributes or toolchains.
- Use `ctx.actions.args()` for potentially large or platform-sensitive argument
  vectors. It can create parameter files without eager string flattening.
- Prefer `ctx.actions.run()` or `run_shell()` over encoding build work in a
  generated script, unless that script is itself a declared artifact.
- Give actions meaningful `mnemonic` and `progress_message` values. These make
  `aquery`, profiles, and failures substantially easier to read.
- Declare relevant environment variables explicitly. Avoid
  `use_default_shell_env = True` unless the rule's contract genuinely requires
  the client environment and the cache implications are understood.
- Keep outputs deterministic and independent of absolute paths, locale, time,
  directory enumeration order, and concurrency.
- Add execution requirements only for concrete scheduler or sandbox needs;
  they are not a substitute for modeling inputs correctly.

Inspect the final action graph with:

```bash
bazel aquery 'mnemonic("WriteReport", //path/to:target)'
bazel aquery --include_param_files 'mnemonic("WriteReport", //path/to:target)'
```

### Providers

Providers are typed contracts between rules.

- Return `DefaultInfo` only for conventional default artifacts, runfiles, and
  executable behavior.
- Define a custom `provider()` for domain-specific information. Do not make
  downstream rules guess meaning from filenames.
- Document fields and keep their types stable.
- Require expected providers on dependency attributes where practical.
- Avoid forwarding an entire dependency object when only a narrow provider is
  part of the contract.
- Use output groups when a rule exposes optional artifact sets that should not
  all build by default.

### `depset`

Use `depset` for transitive collections of artifacts or metadata.

- Construct it from direct items plus transitive child depsets.
- Preserve compatible order semantics across the graph.
- Avoid calling `to_list()` during analysis merely to concatenate or iterate.
  Flattening destroys the sharing that keeps large graphs efficient.
- Do not use depsets as general-purpose mutable sets or for arbitrary nested
  objects.

```starlark
transitive_sources = depset(
    direct = ctx.files.srcs,
    transitive = [dep[SourceInfo].files for dep in ctx.attr.deps],
)
```

### Runfiles and Executables

An executable that succeeds only from the source tree is incomplete.

- Build runfiles from declared data and transitive runfiles.
- Use `ctx.runfiles()` and merge dependency runfiles without flattening them.
- Let consumers resolve runtime data through the runfiles library supported by
  their language or ruleset.
- Do not depend on the current working directory, `bazel-bin` paths, or a
  particular runfiles tree layout.
- Verify with `bazel run` and the repository's test environment, including a
  remote or sandboxed path when those modes matter.

## Toolchains

If a custom rule invokes a compiler, generator, linter, or other platform-aware
tool, model it as a toolchain when more than one implementation or execution
platform can exist.

1. Define or adopt a `toolchain_type`.
2. Define the provider that the toolchain supplies.
3. Create toolchain implementation targets.
4. Wrap them in `toolchain()` targets with constraints.
5. Register them from `MODULE.bazel` or the appropriate module extension.
6. Declare the toolchain type in the consuming rule.
7. Read the resolved provider through `ctx.toolchains`.

Do not use `select()` to reproduce toolchain resolution manually. Toolchains
connect target constraints, execution constraints, and usable tools; `select()`
only chooses an attribute value from configuration conditions.

Use execution groups when one rule has distinct actions that need different
toolchain sets or execution constraints, such as compilation on one platform
and signing on another.

## Aspects

An aspect propagates along selected attributes of an existing target graph.
Appropriate uses include IDE metadata, lint collection, dependency metadata,
and graph-wide reporting.

- Define precisely which attributes the aspect follows.
- Require and return providers rather than inferring target types from names.
- Keep aspect actions hermetic like ordinary rule actions.
- Be mindful of graph multiplication: an aspect can analyze a large configured
  graph even when its implementation looks small.
- Do not use an aspect to silently mutate or replace the behavior of the target
  it visits.

If the result belongs to the target's normal build contract, prefer an ordinary
rule/provider relationship.

## Repository Rules and Module Extensions

### Repository Rules

A repository rule creates one external repository. Use repository APIs for
downloads, archive extraction, template expansion, executable discovery, and
file creation.

Make the result reproducible:

- Pin URLs to immutable versions where possible.
- Require checksums or integrity values for downloads.
- Declare environment variables that affect the result through the repository
  rule's `environ` contract.
- Avoid relying on arbitrary tools installed on the developer machine.
- Generate deterministic `BUILD.bazel` and metadata files.
- Use canonical IDs or equivalent cache controls when the same URL may later
  serve different content.
- Return reproducibility metadata where the API supports it.

Use a regular build rule, not a repository rule, for work that belongs in the
build action graph and should benefit from ordinary sandboxing and remote
execution.

### Module Extensions

A module extension reads tags contributed by modules, resolves their combined
intent, and invokes repository rules to create repositories.

Design extensions as dependency resolvers, not imperative setup scripts:

- Define a small tag-class API with typed attributes.
- Account for tags from every participating module; do not assume only the root
  module contributes configuration.
- Resolve conflicts deterministically and report actionable errors.
- Keep generated repository names stable.
- Document which repositories users must import with `use_repo()`.
- Emit extension metadata so lockfile, reproducibility, and root-module direct
  dependency checks can diagnose drift.
- Avoid reading root-only configuration unless the extension contract clearly
  declares that behavior.

`MODULE.bazel` remains the user-facing composition layer. Keep large resolution
implementations in `.bzl` files rather than growing the module file into a
program.

See [BZLMOD.md](BZLMOD.md) for consumption, lockfile, override, and vendoring
workflows.

## Transitions

Custom transitions are a last-resort configuration tool. They can cause the
configured target graph to multiply and can make command-line behavior hard to
predict.

Before writing one, ask whether the need is better represented by:

- a toolchain and execution platform,
- a target platform,
- a normal build setting selected by the user,
- an execution group,
- or separate explicit targets.

If a transition is necessary:

- Declare exact input and output settings.
- Keep it narrow and deterministic.
- Attach it to the smallest viable edge.
- Explain the resulting configuration split in rule documentation.
- Inspect the edge with `cquery --transitions=lite`.
- Measure analysis memory and configured-target growth.

## Test Starlark APIs

Treat build logic like production code.

### Minimum Test Layers

1. **Loading tests** prove public `.bzl` files load and macros instantiate.
2. **Analysis tests** assert providers, configured attributes, actions, and
   failure conditions without executing the actions.
3. **Execution tests** build representative targets and inspect their outputs.
4. **Runfiles tests** execute binaries/tests outside assumptions about the
   workspace layout.
5. **Platform tests** cover materially different target or execution platforms.
6. **Integration fixtures** exercise Bzlmod or repository logic in a small
   consuming module.

Use supported analysis-test utilities such as `bazel_skylib`'s `analysistest`
when appropriate, but keep the public rule contract—not the helper library's
implementation—as the focus.

For negative cases, assert a precise failure reason. A test that accepts any
analysis failure can hide an unrelated regression.

## Documentation Contract

Every public macro, rule, provider, aspect, repository rule, or module extension
should document:

- its purpose and when not to use it,
- attributes or tags and their defaults,
- returned providers and output groups,
- generated targets and their naming,
- required toolchains and platforms,
- visibility expectations,
- compatibility or migration guarantees,
- and at least one minimal example.

Keep examples buildable. Run Buildifier on Starlark and use repository tests to
catch documentation drift.

## Review Checklist

- Is an ecosystem rule or ordinary BUILD declaration sufficient?
- Is the selected extension point the smallest one that models the need?
- Are loading, analysis, and execution responsibilities kept separate?
- Are all inputs, tools, outputs, environment influences, and runfiles declared?
- Are tools resolved for the execution configuration or through toolchains?
- Do providers form a typed, documented contract?
- Are transitive collections retained as depsets?
- Are actions deterministic, well named, and inspectable with `aquery`?
- Are macro-generated targets predictable and visibility-safe?
- Are repository downloads pinned and verified?
- Are module extension resolution and repository names deterministic?
- Are transitions justified and measured?
- Do analysis, execution, and integration tests cover the public API?

## Authoritative Sources

- [Starlark language](https://bazel.build/rules/language)
- [Rules overview](https://bazel.build/extending/rules)
- [Rule implementation](https://bazel.build/extending/rules#implementation-function)
- [Symbolic macros](https://bazel.build/extending/macros)
- [Attributes](https://bazel.build/rules/lib/toplevel/attr)
- [Actions API](https://bazel.build/rules/lib/builtins/actions)
- [Providers](https://bazel.build/extending/rules#providers)
- [Depsets](https://bazel.build/extending/depsets)
- [Runfiles](https://bazel.build/extending/rules#runfiles)
- [Toolchains](https://bazel.build/extending/toolchains)
- [Execution groups](https://bazel.build/extending/exec-groups)
- [Aspects](https://bazel.build/extending/aspects)
- [Repository rules](https://bazel.build/extending/repo)
- [Module extensions](https://bazel.build/external/extension)
- [Testing rules](https://bazel.build/rules/testing)
- [Starlark style guide](https://bazel.build/rules/bzl-style)
