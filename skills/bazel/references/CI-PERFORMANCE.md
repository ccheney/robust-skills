# CI and Performance

Use this reference for Bazelisk/version pinning, continuous integration, affected-target strategies, remote cache/execution rollout, Build Event Protocol, test parallelism, profiles, workers, memory, or slow builds.

## Contents

- Reproducible CI baseline
- CI target scope
- Affected-target fast paths
- CI structure and caches
- Build Event Protocol
- Performance measurement
- Loading, analysis, and execution tuning
- Tests
- Remote scaling
- Review checklist

## Reproducible CI Baseline

### Pin Bazel with Bazelisk

Check in an exact `.bazelversion`:

```text
9.2.0
```

Install/use Bazelisk as the `bazel` launcher locally and in CI. It selects the checked-in version and downloads it when needed. This makes Bazel upgrades ordinary reviewed changes that include code, ruleset, lockfile, and CI updates atomically.

Do not rely on whatever `bazel` version happens to be preinstalled on an image. Bazel/ruleset/lockfile behavior is version-sensitive.

### Pin the Whole Build Toolchain

Reproducibility also requires:

- committed `MODULE.bazel` and `MODULE.bazel.lock`;
- pinned language rulesets and package-manager lockfiles;
- declared toolchains/SDKs/interpreters;
- versioned Buildifier/Gazelle/Buildozer integration;
- checked-in `.bazelrc` named configs;
- explicit target/execution platforms;
- immutable container/worker definitions where used.

The Bazel binary alone does not pin an undeclared `/usr/bin` compiler or a floating module override.

### Baseline Commands

The Bazel best-practices contract is that stable branches can run:

```bash
bazel build //...
bazel test //... --test_output=errors
```

`bazel test //...` builds selected tests and their dependencies, but it does not guarantee every non-test binary/library target is built. Keep both gates when the repository promises all main-repo targets are healthy.

Targets requiring special platforms, licenses, hardware, or services should express specific compatibility/tags and run in an appropriate matrix. Do not hide ordinary broken targets behind `manual`.

## CI Target Scope

Use layers of confidence:

| Gate | Purpose | Typical cadence |
|---|---|---|
| Changed package/target smoke | immediate developer feedback | local/PR |
| Affected targets + reverse-dependent tests | PR fast path | every PR after validation |
| Full main-repo build/test | correctness backstop | merge queue/default branch |
| Platform/configuration matrix | compatibility | PR for relevant changes + scheduled/default |
| Clean/offline/remote reproducibility | hermeticity | scheduled and dependency/toolchain changes |
| Release/package targets | deliverable validation | release candidates |

Do not make the fastest gate the only gate until its false-negative rate is demonstrated against the full graph.

### Representative Configurations

At minimum, exercise configurations that materially change analysis/actions:

- developer vs optimized/release compilation;
- supported target platforms/architectures;
- local vs remote execution if both are supported;
- sanitizer/instrumentation/coverage modes;
- feature/edition build settings that select different dependencies;
- toolchain versions during an upgrade.

Avoid a Cartesian matrix whose combinations are not supported. Define named platform/config targets and an explicit support policy.

## Affected-Target Fast Paths

Bazel does not natively map an arbitrary Git diff to a universally correct target set. A correct system must understand source targets, BUILD definitions, transitive `.bzl` loads, external modules, repository mappings, platforms, toolchains, configs, generated BUILD files, and deletions.

### Conservative Policy

An affected-target system should:

1. calculate changes against the correct merge base;
2. map changed and deleted files using both pre-change and post-change graphs when needed;
3. include reverse dependents and affected tests;
4. understand BUILD and transitive `.bzl` definition dependencies;
5. widen/fallback for `MODULE.bazel`, lockfiles, `.bazelrc`, platform/toolchain, generator, and CI policy changes;
6. preserve config/platform distinctions;
7. fall back to `//...` when graph information is missing or analysis fails;
8. compare fast-path decisions to full runs over representative history.

### Do Not Equate Directory with Impact

Running only `//changed/directory/...` misses consumers elsewhere. A library change normally requires reverse-dependent tests and possibly binaries across the monorepo.

Diagnostic query:

```bash
bazel query 'tests(rdeps(//..., //libraries/money:money))'
```

This helps understand one target's structural impact; it is not a full Git integration.

### Build Definition Changes

Treat these as broad unless the selected tool proves a narrower closure:

- root/module/lockfile changes;
- shared `.bzl` macros/rules/aspects;
- `.bazelrc` and config fragments;
- platform constraints and toolchain registration;
- package-manager lockfiles consumed by module extensions;
- BUILD generator version/directives;
- remote execution platform definitions.

### Validate the Fast Path

Record for a sample of changes:

- predicted targets/tests;
- full build/test targets that actually rebuilt/failed;
- false negatives and fallbacks;
- analysis cost vs work saved;
- historical changes involving deletes/renames/BUILD edits.

A fast selector that spends more time loading the whole graph than the saved work may still be valuable for expensive tests, but measure the whole critical path.

## CI Structure

### Keep One Configuration Contract

Prefer repository named configs:

```bash
bazel build --config=ci //...
bazel test --config=ci //... --test_output=errors
```

Keep provider endpoints and runner-specific resource paths in imported/environment-specific rc fragments, but avoid CI-only output semantics that developers cannot reproduce.

### Avoid Manual Build Ordering

Do not encode target dependency order with shell chains or CI `needs` when Bazel can express it in the graph:

```bash
# Avoid as a build graph.
bazel build //lib:a && bazel build //service:b && bazel test //service:b_test

# Let Bazel analyze/schedule the graph.
bazel test //service:b_test
```

Separate CI jobs may still serve different policy concerns (lint, test, release, platform matrix). Use remote cache to share artifacts rather than scripts copying `bazel-bin` files between jobs.

### Output Base and Concurrency

Bazel uses a server and output base per workspace identity. Concurrent clients targeting one output base contend on Bazel's command lock. In CI:

- avoid running several Bazel clients concurrently in one checkout/output base;
- run multiple top-level targets in one invocation when they share configuration;
- use separate checkouts/output bases for independent parallel jobs;
- use remote cache/execution for cross-job sharing;
- preserve server/Skyframe state across sequential commands in long-lived runners when safe.

Do not force `--batch` or `bazel shutdown` after every command; it discards in-memory state and increases startup/loading cost. Use `shutdown` when the runner lifecycle or JVM option changes require it.

### Do Not Clean Every Run

`bazel clean --expunge` defeats local incremental state, redownloads/reanalyzes work, and masks dependency bugs. CI isolation should come from clean checkout semantics, pinned inputs, and controlled caches—not routine expunges.

Use explicit clean builds as a separate reproducibility measurement, not the only performance workload.

### Failure Collection

`--keep_going` can report more independent failures in one invocation, but it also performs more work after the first failure. Choose it for feedback quality, not as a universal speed setting.

Use `--test_output=errors` for concise failed-test logs. Persist full logs, XML, profiles, and BEP artifacts for diagnosis.

## Caching in CI

### Prefer Action-Aware Remote Cache

A Bazel remote cache shares action results and the CAS across jobs and developers. It understands Bazel action identity and is usually a better cross-job mechanism than archiving the entire output base.

Avoid generic caching of the whole output base unless the Bazel/provider documentation and runner lifecycle support it. Output bases contain server/install state, symlink forests, absolute-path-sensitive data, and large transient trees.

Reasonable generic cache candidates include:

- Bazelisk downloaded binaries/cache according to its documented location;
- repository/download cache with integrity-pinned artifacts;
- a disk cache directory when scoped safely to compatible builds;
- language package-manager download caches used only by hermetic repository setup.

### Remote Cache CI Policy

- Define compatible instance/namespace boundaries.
- Restrict writes from untrusted contexts according to threat model.
- Use read-only access where a job should consume but not publish.
- Monitor cache error rate and fall back behavior.
- Keep remote cache failure from obscuring actual build correctness unless cache availability is itself required.
- Measure hit latency, download/upload bytes, and critical-path savings.

### Output Download Strategy

Remote builds can avoid downloading every intermediate output. Provider/Bazel flags can request all, top-level, or minimal outputs. Choose based on consumers:

- tests and following Bazel actions can often keep intermediates remote;
- packaging/upload steps need specific top-level artifacts;
- local post-processing outside Bazel forces downloads and weakens graph tracking;
- BEP/BES can identify artifacts without scraping `bazel-bin`.

Keep post-processing inside Bazel targets where practical so remote outputs remain graph-connected.

## Build Event Protocol (BEP)

BEP is the machine interface for an invocation. It reports progress, target completion, test results, configurations, output files, and more.

Write a local artifact:

```bash
bazel test //... \
  --build_event_json_file=/tmp/build-events.json \
  --test_output=errors
```

For robust tooling, prefer binary length-delimited protobuf. JSON/text are useful for inspection but larger/less efficient.

### Build Event Service (BES)

Bazel can stream BEP events to a gRPC Build Event Service:

```text
build:ci --bes_backend=grpcs://bes.example.invalid:443
```

Provider/auth details are environment-specific. A BES may link events to remote-cache artifacts and provide invocation dashboards.

### Use BEP Instead of Terminal Parsing

Use BEP/BES to determine:

- which targets/tests completed or failed;
- test attempts and logs;
- output artifact URIs/files;
- invocation/configuration identifiers;
- timing/progress events.

Do not scrape colored progress output or final “Build completed” lines for automation.

## Performance Measurement

Measure at least these workloads:

1. clean build/test;
2. no-change rebuild;
3. small leaf edit;
4. central-library edit with many reverse dependencies;
5. BUILD/`.bzl`/module/config change;
6. local cache warm/cold;
7. remote cache warm/cold;
8. remote execution representative target;
9. CI checkout with realistic network latency.

Report wall time together with:

- loading and analysis duration;
- critical-path duration/actions;
- action count and concurrency;
- local/remote/cache strategy mix;
- upload/download bytes and latency;
- Bazel and worker CPU/memory;
- test execution/queue time;
- configuration/platform and source revision.

One wall-clock number without workload/config/cache state is not actionable.

### JSON Trace Profiles

Bazel writes recent compressed JSON profiles into the output base by default for build-like commands. Capture an explicit artifact when comparing:

```bash
bazel build //app:binary --profile=/tmp/bazel-profile.json.gz
bazel analyze-profile /tmp/bazel-profile.json.gz
```

Load the trace into a compatible trace viewer or Bazel Invocation Analyzer. Inspect:

- main-thread loading/analysis spans;
- action concurrency;
- critical path;
- local/remote/cache events;
- sandbox setup;
- persistent worker activity;
- garbage collection and CPU utilization;
- long-tail actions.

Do not enable maximum/full profiler detail permanently; high-detail tracing can add overhead and large artifacts.

### Compare Like with Like

When benchmarking a change:

- use the same source revision except for the intended patch;
- same Bazel/rules/toolchains/config/platform;
- same cache read/write state;
- repeated runs with warm-up;
- similar machine/network load;
- preserve profiles and invocation IDs;
- compare medians/distributions, not one lucky run.

## Loading Performance

Loading evaluates packages and `.bzl` files.

Common problems:

- wildcard target patterns loading far more packages than needed;
- recursive globs and filesystem-heavy BUILD logic;
- large legacy macros instantiating many targets eagerly;
- widely loaded `.bzl` files with expensive top-level computation;
- package boundaries too coarse or too numerous for the workload;
- BUILD generation drift causing duplicate/oversized graph structures.

Guidance:

- keep BUILD files declarative and straightforward;
- move reusable functions to focused `.bzl` files;
- use symbolic macros where lazy evaluation support/semantics benefit the version, but do not assume future laziness solves current cost;
- profile before reorganizing package boundaries solely for loading speed;
- scope interactive target patterns while preserving full CI gates.

## Analysis Performance

Analysis constructs configured targets, resolves providers/toolchains, and registers actions.

Common problems:

- large transitive provider values flattened to lists;
- custom transitions multiplying configured variants;
- rules creating too many actions/outputs;
- broad aspects traversing huge graphs;
- excessive toolchain candidates/platforms;
- macros/targets with enormous dependency lists;
- providers carrying redundant per-target metadata.

Rule-authoring guidance:

- use depsets for transitive collections and pass them directly to actions;
- avoid `to_list()` on large transitive depsets during analysis;
- keep providers minimal and immutable;
- bound split transitions and configuration values;
- make aspects selective through provider/attribute propagation;
- use `--nobuild` to isolate analysis cost during diagnostics;
- use Starlark CPU/memory profiling when rule logic is suspected.

## Execution Performance

Optimize the critical path and resource bottlenecks, not total action count in isolation.

### Action Granularity

- Too coarse: weak parallelism, large invalidations, long single actions.
- Too fine: scheduling/sandbox/remote overhead dominates useful work.

Use profiles to identify whether compile, link, code generation, test, download, or sandbox overhead dominates. Change target/action granularity based on measured bottlenecks and ruleset semantics.

### Persistent Workers

Rules/tools supporting Bazel's worker protocol can reuse long-lived processes and reduce JVM/interpreter/tool startup. Verify:

- the ruleset enables workers for the relevant mnemonic;
- worker state does not leak between requests;
- inputs are fully declared and multiplex behavior is safe;
- memory is bounded over a long invocation;
- sandboxed worker settings match hermeticity needs.

Do not force worker strategies for tools that do not implement the protocol correctly.

### Resource Tuning

Flags such as `--jobs` and local CPU/RAM resources affect scheduling. Do not hardcode one developer laptop's values in shared `.bazelrc`. Set CI runner-specific limits based on actual cores/memory and profile whether Bazel is CPU-bound, memory-bound, IO-bound, or remote-latency-bound.

More parallelism can increase contention, GC, swapping, remote queueing, and link/test resource pressure.

## Test Performance

- Give tests accurate `size` and `timeout`; size informs local resource scheduling.
- Split unrelated test suites when independent execution/impact is valuable.
- Use `shard_count` only for runners that implement Bazel sharding.
- Avoid marking flaky tests merely to gain retries; fix and track them.
- Keep fixtures hermetic and local to remove network/service latency.
- Use `--test_verbose_timeout_warnings` to identify over-large timeout/size declarations.
- Analyze test queue time vs actual execution time.
- Use remote execution for tests only when worker startup/data transfer/service constraints justify it.

Target-level caching means a test reruns when its declared inputs/action key change. Incorrect/missing deps can make test selection/caching wrong; performance work cannot compensate for an inaccurate graph.

## Remote Scaling

### Remote Cache Before Remote Execution

Remote cache usually has a smaller adoption surface and exposes reproducibility issues. Establish it before distributing actions.

### Remote Execution Readiness

- sandboxed builds pass;
- tools/SDKs are declared and platform-compatible;
- no local device/service/home/network assumptions;
- deterministic outputs across workers;
- worker images/platform properties are versioned;
- unsupported actions have explicit local routing;
- BEP/profile/remote metrics are available.

### Tune with Data

Classify action mnemonics by:

- local duration;
- remote queue + execution duration;
- input upload/output download size;
- cache hit latency/rate;
- worker resource needs;
- critical-path frequency.

Short actions may be faster locally; highly parallel compiles/tests often benefit remotely; large links can need specialized workers or remain local. Dynamic execution can race local/remote paths, but it spends additional resources and requires measured strategy selection.

## Review Checklist

- [ ] `.bazelversion` is exact and used by CI Bazelisk.
- [ ] Modules, lockfiles, rulesets, toolchains, and generators are pinned.
- [ ] Full build/test remains a correctness backstop.
- [ ] Affected-target logic handles reverse deps, BUILD/`.bzl`, configs, modules, deletes, and broad fallbacks.
- [ ] CI uses graph dependencies rather than manual shell ordering.
- [ ] Output bases are not shared by concurrent Bazel clients.
- [ ] CI does not routinely expunge incremental state.
- [ ] Remote cache is preferred over archiving the full output base.
- [ ] BEP/BES, not terminal text, feeds automation and dashboards.
- [ ] Performance claims include workload, config, cache state, and profiles.
- [ ] Loading, analysis, and execution are diagnosed separately.
- [ ] Remote execution strategy is selected by action characteristics and platform constraints.

## Sources

- Bazel best practices: https://bazel.build/configure/best-practices
- Updating Bazel/Bazelisk: https://bazel.build/versions/updating-bazel
- Bazelisk repository: https://github.com/bazelbuild/bazelisk
- Build Event Protocol and Service: https://bazel.build/remote/bep
- JSON trace profile: https://bazel.build/advanced/performance/json-trace-profile
- Optimizing Starlark/rule performance: https://bazel.build/rules/performance
- Remote caching: https://bazel.build/remote/caching
- Remote execution: https://bazel.build/remote/rbe
- Dynamic execution: https://bazel.build/remote/dynamic
- Test encyclopedia: https://bazel.build/reference/test-encyclopedia
- Commands and options: https://bazel.build/docs/user-manual
- Calling Bazel from scripts: https://bazel.build/run/scripts
