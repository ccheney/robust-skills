# Bzlmod and External Dependencies

Use this reference for `MODULE.bazel`, Bazel Central Registry modules, module extensions, repository rules, overrides, `MODULE.bazel.lock`, vendor/offline builds, repo-name problems, or migration away from `WORKSPACE`.

## Contents

- Bazel 9 boundary
- Modules, repositories, and resolution
- `MODULE.bazel` directives
- Module extensions
- Repository names and mappings
- Overrides
- Lockfile workflow
- Vendor and offline modes
- Dependency diagnostics
- `WORKSPACE` migration
- Review checklist

## Bazel 9 Boundary

Bazel 9 removed the legacy `WORKSPACE` implementation. Bzlmod is not an optional mode on Bazel 9; it is the external dependency system.

For Bazel 9 code:

- root marker and external module manifest: `MODULE.bazel`;
- versioned Bazel modules: `bazel_dep`;
- multi-module ecosystem integration: module extensions;
- repository materialization: repository rules called by Bazel/modules/extensions;
- resolved state: `MODULE.bazel.lock`;
- offline/source-controlled copies: vendor mode where justified.

Do not solve Bazel 9 dependency problems by adding:

- `WORKSPACE` or `WORKSPACE.bazel`;
- `http_archive()` calls in `WORKSPACE`;
- `--enable_workspace`;
- legacy `*_repositories()` / `*_deps()` chains designed for WORKSPACE.

If an existing project still depends on WORKSPACE, migrate it under Bazel 7 before upgrading to Bazel 9. The official migration tool requires Bazel 7 and is not supported with Bazel 8.

## Modules, Repositories, and Resolution

A **module** is a versioned Bazel project with module metadata and dependencies. A **repository** is a concrete source tree visible to the build. A module is normally backed by one repository, and module extensions may generate additional repositories.

Bzlmod resolution broadly does this:

1. Read the root `MODULE.bazel`.
2. Discover transitive module manifests through configured registries, normally the Bazel Central Registry first.
3. Resolve module versions.
4. Materialize repositories for selected modules.
5. Evaluate only the module extensions whose results are needed.
6. Materialize extension-generated repositories imported with `use_repo`.

External repositories are fetched on demand when labels or analyzed targets require them. The external module graph is distinct from the main repository's target graph.

### Minimal Version Selection

Bzlmod uses Minimal Version Selection (MVS): when compatible dependents request several versions of one module, Bazel selects the highest version requested in the graph, not the newest version that happens to exist in a registry.

This makes resolution reproducible but has an important assumption: versions within one compatibility level should be backward compatible. A module author increments `compatibility_level` for an incompatible line. Do not use an override to suppress a compatibility problem without confirming that the selected module/ruleset actually works.

Use:

```bash
bazel mod graph --verbose --include_unused
bazel mod explain <module> --verbose --include_unused
```

to see requested, selected, upgraded, and unused versions.

## `MODULE.bazel`

`MODULE.bazel` is intentionally more constrained than ordinary `.bzl` code. It declares data and extension usages; it is not a general startup script. Do not try to put arbitrary control flow or `load()` calls in it.

```starlark
module(
    name = "acme_monorepo",
    compatibility_level = 1,
)

bazel_dep(name = "rules_cc", version = "0.2.22")
bazel_dep(name = "platforms", version = "1.1.0")
```

For an unpublished application monorepo, a source-tree `version` is often unnecessary and can become misleading when commits move beyond a release tag. Module authors should follow the current Bazel module-versioning FAQ and their release automation.

### Direct Dependencies

Declare modules the root module uses directly. Do not add a `bazel_dep` for every transitive module solely because it appears in `bazel mod graph`. A direct dependency is appropriate when:

- BUILD/`.bzl` files load or reference its apparent repository;
- its rules are part of the repository's public build contract;
- an extension it hosts is used;
- the root intentionally controls that module's version/API.

Use `repo_name` only to preserve or choose an apparent repository name when necessary. Prefer the module's ordinary name for new code; gratuitous renaming makes documentation and debugging harder.

### Language Rules in Bazel 9

Bazel 9 externalized language rules. A module declaration and an explicit rule load are separate steps:

```starlark
# MODULE.bazel
bazel_dep(name = "rules_cc", version = "0.2.22")
```

```starlark
# BUILD.bazel
load("@rules_cc//cc:cc_library.bzl", "cc_library")
```

Follow each ruleset's version-matched setup. Many rulesets also require module extension tags and toolchain registration. Do not infer one ruleset's setup from another.

### Organizing Large Module Files

Bazel 9's module language includes `include()` for splitting root-module declarations when the repository truly benefits. Keep the dependency story searchable: group by ecosystem or ownership and avoid a maze of tiny included fragments. `include()` is not a substitute for a module extension when logic must aggregate or generate repositories.

## Module Extensions

Module extensions let a ruleset read typed tags from modules across the dependency graph and generate repositories. They are the normal bridge to package ecosystems that need more than one Bazel module declaration—for example, Maven artifacts, Python wheels/toolchains, npm packages, or Go modules.

Schematic usage (the extension API and version must come from the ruleset's docs):

```starlark
bazel_dep(name = "rules_example", version = "X.Y.Z")

deps = use_extension("@rules_example//example:extensions.bzl", "deps")
deps.from_lockfile(lockfile = "//:example.lock")

use_repo(
    deps,
    "generated_dependency_a",
    "generated_dependency_b",
)
```

Important behaviors:

- Extension usages across the module graph are evaluated together after module resolution.
- Extension results are repositories, not ordinary build targets.
- Extensions are lazy. `use_repo` tells Bazel which generated repos the current module expects to see and helps determine whether evaluation is needed.
- An extension may provide metadata that lets `bazel mod tidy` add/remove root `use_repo` entries.
- Extension evaluation may depend on OS/architecture. The lockfile can contain separate results for those environments.

### Maintain `use_repo`

Run:

```bash
bazel mod tidy
```

after changing extension inputs when the extension supplies the needed metadata. Review the edit; do not assume every extension can fully maintain its usage automatically.

Use:

```bash
bazel mod show_extension '@rules_example//example:extensions.bzl%deps'
bazel mod graph --extension_info=all
```

to inspect generated repositories and which modules import them. Exact extension identifiers in `mod` output may use canonical repository names.

### Repository Rules from the Root Module

Prefer a published module or a ruleset-provided extension. For a standalone repository rule that genuinely belongs in the root module, `use_repo_rule()` can expose it directly from `MODULE.bazel`:

```starlark
http_file = use_repo_rule(
    "@bazel_tools//tools/build_defs/repo:http.bzl",
    "http_file",
)

http_file(
    name = "checked_tool",
    integrity = "sha256-...",
    urls = ["https://example.invalid/releases/tool"],
)
```

Always supply integrity/checksum information for fetched content. A floating URL without content identity is not reproducible.

## Repository Names and Mappings

Bzlmod distinguishes:

- **apparent name**: `@rules_cc`, meaningful in the current repository's mapping;
- **canonical name**: often a generated `@@...` form, globally unique within the workspace.

Use apparent names in BUILD and `.bzl` source. Canonical names are implementation details appropriate for diagnostics and some `bazel mod` commands.

If `@foo` appears to mean different things from different repositories, inspect mappings instead of string-rewriting labels:

```bash
bazel mod dump_repo_mapping @some_repo
bazel mod show_repo @foo
bazel mod show_repo --base_module=some_module @foo
```

For external tools, use `bazel mod dump_repo_mapping`; do not reverse-engineer canonical-name formats.

Do not hardcode canonical repository names into runfile paths. Use the language-specific runfiles library and apparent repository-relative `rlocation` paths.

## Overrides

Only overrides in the root module take effect. Overrides in dependencies are ignored, so the final application controls exceptional resolution policy.

### `single_version_override`

Use to pin a specific version, registry, or patch set when ordinary MVS is insufficient:

```starlark
single_version_override(
    module_name = "some_module",
    version = "1.4.2",
    patches = ["//third_party/patches:some_module.patch"],
    patch_strip = 1,
)
```

Record why the override exists, upstream issue, owner, and removal condition. A version override can violate another dependent's compatibility assumptions.

### `multiple_version_override`

Allows explicitly listed versions to coexist. Use only when the ecosystem/ruleset supports multiple-version operation. It does not accept an arbitrary version absent from the pre-resolution graph, and Bazel upgrades requests to allowed versions within their compatibility level.

Multiple versions increase repository mappings, testing surface, and cognitive load. Prefer one compatible version where possible.

### Non-Registry Overrides

- `archive_override`: source archive instead of registry metadata;
- `git_override`: Git repository/commit;
- `local_path_override`: local checkout for development.

`local_path_override` is useful for iterating on two modules together but is usually machine-specific. Do not leave it committed as the permanent source of a shared dependency unless the path is an intentional repository-relative contract supported by every environment.

Pin Git/archive sources immutably and include integrity where the API supports it. Branch names and moving tags are not content identity.

### Extension Repo Overrides

Advanced directives such as `override_repo` and `inject_repo` change repositories produced/seen by module extensions. Use them only with the extension's documented contract and add focused tests: they can make the root's graph differ materially from what the extension generated.

## `MODULE.bazel.lock`

The root lockfile records module-resolution inputs and module-extension evaluation results. It is specific to the Bazel version as well as module/extension state.

### Commit It

Commit both:

- `.bazelversion`, pinning Bazel through Bazelisk;
- `MODULE.bazel.lock`, pinning the current resolution/extension state.

Do not hand-edit the lockfile. Its format is generated and can change between even backward-compatible Bazel releases.

### Lockfile Modes

| Mode | Behavior | Typical use |
|---|---|---|
| `update` | Use valid entries and add/update missing state | normal local dependency maintenance |
| `refresh` | Like update, plus refresh mutable information such as yanked status | deliberate refresh/security maintenance |
| `error` | Fail if information is missing/stale; do not update resolution state | CI reproducibility check |
| `off` | Ignore and do not update lockfile | exceptional diagnostics only |

Useful commands:

```bash
# Evaluate/lock all module extensions and update generated state.
bazel mod deps --lockfile_mode=update

# Verify checked-in state in CI.
bazel mod deps --lockfile_mode=error

# Refresh mutable registry information deliberately.
bazel mod deps --lockfile_mode=refresh
```

Normal builds update only extension state reached by that invocation. `bazel mod deps --lockfile_mode=update` is the explicit way to lock down all extensions at once.

An extension declaring itself reproducible may opt out of lockfile result storage and may still perform network work even when module resolution uses `--lockfile_mode=error`; its contract promises deterministic repository definitions for the same inputs.

### Lockfile Diff Review

After dependency changes:

1. Inspect the `MODULE.bazel` diff first.
2. Run `bazel mod tidy` if applicable.
3. Run `bazel mod deps --lockfile_mode=update` with the pinned Bazel.
4. Review selected module versions and extension repos through `bazel mod graph`/`show_extension`.
5. Confirm the lockfile changes correspond to intended module/extension inputs.
6. Build and test representative targets for every affected ruleset/ecosystem.

### Merge Conflicts

The safest general process is:

1. resolve `MODULE.bazel` and extension input-file conflicts;
2. restore a syntactically valid lockfile base rather than combining opaque extension result structures;
3. regenerate with the pinned Bazel using `bazel mod deps`;
4. review the resolved graph.

Bazel documents a `jq`-based Git merge driver. If the repository adopts it, pin/document the setup and still validate the resulting graph.

## Vendor and Offline Modes

Vendor mode copies external repository contents and registry files into a controlled directory. Use it when offline builds, source review, archival, or network policy justify the repository size and update workflow.

### Prefer Target-Scoped Vendoring

```bash
bazel vendor --vendor_dir=vendor_src //services/payments/... //tools/release:package
```

This analyzes those targets under the current configuration and vendors their required repos. Platform/configuration changes can change the required set, so vendor all supported configs/platforms or use a deliberately broad policy.

Vendoring every transitive repository can be slow, large, and fail on repos incompatible with the current host. Start with the target set that must work offline.

### Verify Offline Behavior

```bash
bazel build --vendor_dir=vendor_src --nofetch //services/payments/...
```

For a true offline test, also block network externally; arbitrary repository-rule commands cannot always be prevented from making their own network calls by a Bazel flag alone.

Some Bazel subcommands such as `bazel mod tidy` use implicit tools not reachable from ordinary targets. Vendor them explicitly when needed offline:

```bash
bazel vendor --vendor_dir=vendor_src \
  //... \
  @bazel_tools//tools:tools_for_bazel_subcommands
```

### `VENDOR.bazel`

In the vendor directory:

```starlark
ignore("@@some_configure_repo+")
pin("@@patched_dependency+")
```

- `ignore()` excludes a canonical repository from vendor handling.
- `pin()` keeps and uses the current vendored contents, allowing intentional local maintenance.

Repository rules marked `local` or `configure` are always excluded. Add the generated `<vendor_dir>/bazel-external` symlink to ignore rules; Bazel refreshes it and it should not be committed.

### Lightweight Prefetching

When source-controlled vendoring is unnecessary:

```bash
bazel fetch //services/payments/...
bazel fetch --repo=@rules_cc
bazel build --nofetch //services/payments/...
```

The repository cache can reuse downloads across workspaces when downloads have checksums. `--distdir` can provide verified local archives. Neither automatically makes arbitrary repository-rule logic hermetic.

## Dependency Diagnostics

| Question | Command |
|---|---|
| Full resolved module graph | `bazel mod graph` |
| Include discarded requests and reasons | `bazel mod graph --verbose --include_unused` |
| Why a module is present/selected | `bazel mod explain <module> --verbose --include_unused` |
| All paths to a module | `bazel mod all_paths <module>` |
| Repository rule/attributes behind a repo | `bazel mod show_repo @repo` |
| Extension usages and generated repos | `bazel mod show_extension <extension>` |
| Apparent-to-canonical mapping | `bazel mod dump_repo_mapping @repo` |
| Update `use_repo` where supported | `bazel mod tidy` |
| Lock every extension | `bazel mod deps --lockfile_mode=update` |

Do not use `bazel query //external:...` as the primary Bzlmod dependency inspector. `bazel mod` is designed for the resolved external graph.

## Migrating from `WORKSPACE`

### Version Strategy

Do the dual-system migration with the latest supported Bazel 7 release:

1. Pin Bazel 7 with Bazelisk.
2. Inventory WORKSPACE-created repos and the representative target set.
3. Add `MODULE.bazel` and migrate direct modules, rulesets, extensions, toolchains, and repo rules incrementally.
4. Build/test the same target matrix in legacy and Bzlmod modes while Bazel 7 supports both.
5. Remove legacy repo-name assumptions and explicit built-in-rule assumptions.
6. Commit/validate `MODULE.bazel.lock`.
7. Eliminate WORKSPACE dependency setup.
8. Upgrade to Bazel 8, resolve warnings/incompatible changes, then Bazel 9.

Do not first upgrade a WORKSPACE-dependent repository to Bazel 9: the code needed to evaluate it no longer exists.

### Inventory

Legacy `*_deps()` macros can hide transitive repositories. The official migration guidance uses Bazel 7's resolved-repository output and a representative build target set. Inventory:

- direct `http_archive`, `git_repository`, and local repositories;
- repositories introduced by macros;
- language/package-manager setup;
- registered toolchains/execution platforms;
- `bind()` and legacy aliases;
- patches and repository-name translations;
- repository rules reading local environment or system tools.

The official migration tool is best effort. Review every recommendation and validate repository mappings, versions, toolchains, and extension-generated repos.

### Equivalence Gates

For each migrated slice, compare:

- build and test success for representative targets/configurations/platforms;
- resolved external module/repo graph;
- selected toolchains;
- output/action differences where relevant (`cquery`, `aquery`);
- offline/remote execution behavior;
- developer and CI entry points.

## Review Checklist

- [ ] Bazel/ruleset versions were inspected before editing setup.
- [ ] Bazel 9 changes use Bzlmod, not WORKSPACE compatibility code.
- [ ] Direct module dependencies and extension usages are intentional.
- [ ] Rulesets are explicitly loaded from public entry points.
- [ ] Overrides are root-scoped, pinned, documented, and removable.
- [ ] Apparent names are used in source; canonical names only for diagnostics/vendor policy.
- [ ] `MODULE.bazel.lock` was generated by the pinned Bazel and is committed.
- [ ] `bazel mod tidy` / `bazel mod deps` changes were reviewed.
- [ ] Vendor/offline scope includes all supported targets/configs and implicit subcommand tools when needed.
- [ ] Representative targets across affected ecosystems build and test.

## Sources

- Bazel 9 LTS announcement: https://blog.bazel.build/2026/01/20/bazel-9.html
- External dependencies overview: https://bazel.build/external/overview
- Bazel modules and MVS: https://bazel.build/external/module
- Module extensions: https://bazel.build/external/extension
- `MODULE.bazel` built-ins: https://bazel.build/rules/lib/globals/module
- `mod` command: https://bazel.build/external/mod-command
- Bazel lockfile: https://bazel.build/external/lockfile
- Vendor mode: https://bazel.build/external/vendor
- External dependencies FAQ: https://bazel.build/external/faq
- Repository rules: https://bazel.build/external/repo
- Bzlmod migration guide: https://bazel.build/external/migration
- Bzlmod migration tool: https://bazel.build/external/migration_tool
- Bazel Central Registry: https://registry.bazel.build/
