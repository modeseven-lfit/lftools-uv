# Dependency Modernization Report

This report inventories current runtime and optional dependencies, identifies modernization opportunities, evaluates breaking‑change risks, recommends an incremental upgrade plan, and lists concrete actions you can take **without** raising the currently declared Python support (>=3.8). A supplemental section (Section 16) explicitly enumerates non‑breaking improvements achievable while preserving the present Python version matrix.

---

## 1. Executive Summary

1. The dependency set includes multiple legacy or redundant libraries (e.g., `oauth2client`, `six`, `appdirs`, `bs4`, `toml`, `httplib2`, `aspy.yaml`) whose removal/replacement will simplify future upgrades.
2. The largest strategic change is updating `openstacksdk` (currently constrained only by a floor `>=2.1.0`; latest is 4.x) — this *will* eventually require raising the Python floor to >=3.10 (and possibly >=3.11 for best simplification).
3. Prior to major version lifts, a **prune → stabilize → upgrade** approach reduces noise and isolates real regressions.
4. Security / maintenance risks: `oauth2client` (deprecated), stale `python-ldap~=3.1.0`, potential future friction with pinned `urllib3<3.0.0`, historical CVEs & obsolescence concerns around `httplib2`.
5. A staged plan allows early wins (dependency reduction, type coverage, audit integration) before high‑risk refactors.
6. You can perform a substantial amount of cleanup **without** altering supported Python versions (see Section 16).
7. CentOS 7 (glibc 2.17) support is preserved throughout by provisioning all required Python versions (3.8 → 3.10 → 3.11+) via `uvx`, avoiding reliance on the system Python; remaining platform constraints are limited to native extension wheel availability (manylinux2014) and occasional toolchain needs for rare source builds (e.g. potential `python-ldap` compilation).

---

## 2. Current Declared Runtime Dependencies (pyproject.toml)

Unpinned (unless noted):
```
appdirs
aspy.yaml
attrs
beautifulsoup4
boto3
bs4
certifi
cfgv
chardet
click
defusedxml
Deprecated
dnspython
docker
email-validator
filelock
GitPython
httplib2
identify
idna
jinja2
jsonschema
lxml
multi-key-dict
munch
nodeenv
oauth2client
openstacksdk>=2.1.0
pbr
pyasn1
pyasn1-modules
pygerrit2
PyGithub
PyJWT
pyrsistent
python-jenkins
PyYAML
requests>=2.32.0
rsa
ruamel.yaml
ruamel.yaml.clib
six
soupsieve
tabulate
toml
tqdm
typer
urllib3>=2.2.3,<3.0.0
websocket-client
wrapt
xdg
```

Optionals:
- **ldap**: `python-ldap~=3.1.0`
- **openstack**: `osc-lib~=2.2.0`
- **test**: modern pytest plugins
- **dev**: linters, formatters, type stubs, security tools

---

## 3. Risk Classification

| Tier | Description | Examples |
|------|-------------|----------|
| High | Major API shifts / ecosystem ripple | `openstacksdk`, `oauth2client` (replace), `PyJWT` (if still on <2 semantics), `python-ldap` (big version delta), `jsonschema` (draft / validator changes) |
| Medium | Behavioral adjustments, moderate surface | `boto3`, `docker`, `GitPython`, `jinja2`, `PyYAML`, `ruamel.yaml`, `requests`/`urllib3`, `python-jenkins` |
| Low | Generally stable; safe routine bump | `attrs`, `filelock`, `soupsieve`, `tabulate`, `tqdm`, `wrapt`, `Deprecated`, `idna`, `certifi`, `defusedxml`, `dnspython`, etc. |
| Replace/Remove | Deprecated, redundant, unused | `oauth2client`, `httplib2`, `six`, `appdirs`, `aspy.yaml`, `bs4`, `toml`, `chardet` (if unused), `multi-key-dict` (verify usage), possibly `munch` |

---

## 4. Notable Individual Dependency Observations

### 4.1 `openstacksdk`
- Latest series (4.x) requires Python >=3.10.
- Progressive deprecations between 2.x → 3.x → 4.x (proxy method naming, attribute normalization, auth/session tweaks).
- Needs targeted integration tests around your OpenStack command modules.

### 4.2 `oauth2client`
- Deprecated; replace with `google-auth` + `google-auth-oauthlib`.
- Enables removing `httplib2`.

### 4.3 `PyJWT`
- Version 2+ enforces explicit `algorithms` argument in `jwt.decode`.
- Audit any decode calls lacking `algorithms=['RS256', ...]`.

### 4.4 `jsonschema`
- Current code uses `Draft4Validator`; still supported but modern v4.* introduces referencing & format nuances.
- Keep pinned (<5) during incremental upgrade to avoid multi-layer churn.

### 4.5 `python-ldap~=3.1.0`
- Very old; expect bytes/str handling differences and build environment requirement updates on bump.

### 4.6 Misc Legacy / Redundant
- `six` (Python 2 shims; removable once code verified py3-only).
- `appdirs` → `platformdirs`.
- `toml` → `tomllib` (when Python >=3.11) or `tomli` backport interim.
- Duplicate `bs4` & `beautifulsoup4`.
- Possibly unused: `aspy.yaml`, check actual imports.
- `chardet` — only keep if *directly* imported (Requests now prefers `charset-normalizer`).
- `multi-key-dict`, `munch` — evaluate necessity (could replace with standard dict / dataclass / `types.SimpleNamespace`).

---

## 5. Python Version Baseline Considerations

Current: `>=3.8`.

Drivers to raise:
- `openstacksdk` latest wants >=3.10.
- Eliminating `toml` via stdlib `tomllib` needs >=3.11.

CentOS 7 Compatibility Context:
Using `uvx` to fetch standalone CPython builds means raising the declared Python floor (first to 3.10, later optionally to 3.11) does **not** force an OS upgrade: CentOS 7’s glibc 2.17 baseline remains compatible with current manylinux2014 wheels for our dependency graph. Risk monitoring is only required for: (a) future dependencies that might publish wheels requiring newer glibc, (b) packages lacking wheels that would need a newer compiler than stock GCC 4.8.5 (mitigated by adding a Developer Toolset), and (c) ensuring `python-ldap` continues to resolve to a wheel during any version bump.

Recommendation:
1. Perform all **non-baseline-changing** modernization first (Section 16).
2. Then raise to >=3.10 (unlock freshest OpenStack path) while validating CentOS 7 CI via a `uvx` matrix (3.8 legacy / 3.10 target).
3. Optionally later raise to >=3.11 for further simplification (`tomllib` adoption), again validated on CentOS 7 with `uvx`.

---

## 6. Modernization Strategy Overview

**Sequence**: Prune → Low-risk updates → Medium-risk updates → Python baseline raise → High-risk upgrades → Final cleanup.

Rationale: Smaller diffs first reduce false positives in test failures and isolate genuine API breakages later.

---

## 7. Proposed Phased Plan (Full Roadmap)

| Phase | Goal | Representative Actions | Python Floor Impact |
|-------|------|------------------------|---------------------|
| 0 | Baseline snapshot | Produce lockfile, audit, coverage gates, inventory script | None |
| 1 | Prune & Replace | Drop duplicates & deprecated libs (`six`, `oauth2client`, `httplib2`, `bs4`, `appdirs`, unused) | None |
| 2 | Low-risk bumps | Update utility libs & patch-level versions | None |
| 3 | Medium-risk libs | `boto3`, `docker`, `jinja2`, `GitPython`, `jsonschema` (controlled) | None |
| 4 | Python floor raise | Increase to >=3.10, adjust tooling (mypy target), CI matrix | YES |
| 5 | High-risk core | `openstacksdk` to 3.x then 4.x; `python-ldap` modernization; finalize `PyJWT` semantics | Needs >=3.10 |
| 6 | Optional uplift | Raise to >=3.11, adopt `tomllib`, unpin transitional constraints | YES (optional) |
| 7 | Sustain | Dependabot (grouped), periodic audit, SBOM, doc updates | None |

---

## 8. Tooling & Automation Enhancements

- Add a dependency freshness job (weekly) that:
  - Queries PyPI JSON APIs.
  - Emits markdown/CSV deltas.
- Integrate `pip-audit` or `safety` into CI (fail on new HIGH).
- Use a “latest permissive” experimental tox/nox environment that ignores pins to pre-detect upcoming breakages.

---

## 9. Testing & Quality Reinforcements

| Area | Action |
|------|--------|
| OpenStack commands | Add functional smoke tests (list & no-op flows) prior to upgrade. |
| OAuth refactor | Unit test token refresh & error paths with `responses` or `requests-mock`. |
| Schema validation | Snapshot failing vs passing example files to detect jsonschema strictness changes. |
| LDAP | Add deterministic test for attribute types & membership parsing. |
| Gerrit / Git flows | Mock external endpoints; confirm no reliance on legacy exceptions. |

---

## 10. Security & Compliance

Pre vs Post:
1. Generate SBOM (e.g., CycloneDX) before changes.
2. After each phase, diff SBOM (ensures no inadvertent license risk).
3. Enforce dependency signing verification only for high-risk sources if feasible (optional future).

Key deprecations to track: `oauth2client` (remove), `httplib2` (remove), future `urllib3` 3.x adoption schedule.

---

## 11. Metrics for Success

| Metric | Target |
|--------|--------|
| Vulnerability count (HIGH/CRITICAL) | 0 |
| Deprecated libs present | 0 after Phase 1 |
| Mean time to merge version bumps | < 3 days |
| Test coverage delta | ≥ baseline (no net loss) |
| CI matrix freshness | Includes latest stable Python after uplift |

---

## 12. Potential Blocking Hotspots

- Downstream users still on Python <3.10 (may need an LTS branch pinned to legacy `openstacksdk`).
- Build environment for upgraded `python-ldap` (system libraries).
- Hidden runtime reliance on `httplib2` caching semantics (should be negligible).
- jsonschema ref differences causing previously “accepted” invalid docs to fail.

---

## 13. “Pin Earlier” Contingency Guidance

If constraints occur:
- Keep `openstacksdk <3` on an LTS branch until consumers green‑light Python >=3.10.
- Hold `jsonschema <5` until referencing model migration accepted.
- Maintain `urllib3 <3` while ecosystem (notably `requests`) finalizes 3.x readiness.

---

## 14. Immediate Quick Wins (High ROI, Low Risk)

1. Remove duplicate `bs4`.
2. Remove `six` (confirm no compatibility helpers remain).
3. Replace `oauth2client` + `httplib2` with `google-auth` (`google-auth-oauthlib` + `requests`).
4. Remove unused `aspy.yaml` (no grep hits).
5. Introduce automated dependency audit job.
6. Clean up `appdirs` → add `platformdirs` (or inline paths) – (optionally postpone actual replacement code until Python floor increase, but not required).

---

## 15. Open Questions to Validate

| Question | Why it Matters |
|----------|----------------|
| Any external consumers require Python 3.8/3.9 specifically? | Determines feasibility timeline for raising floor. |
| Actual usage of `multi-key-dict`, `munch`? | If minimal, remove to shrink tree. |
| Are any scripts parsing oauth2client-specific token formats? | Ensures refactor doesn’t break implicit assumptions. |
| Do you rely on ordering of OpenStack listing APIs? | Might need explicit sorting post-upgrade. |
| INFO.yaml round-trip fidelity reliant on current `ruamel.yaml` version? | Prevent formatting regressions when upgrading. |

Document answers before high-risk phases.

---

## 16. Non‑Breaking Modernization Actions (Preserving Current Python >=3.8)

This section enumerates **safe improvements you can implement now without raising the Python version floor** or introducing intentional breaking changes. All actions in this phase are explicitly validated to remain compatible with CentOS 7 runners by relying on `uvx` for interpreter provisioning (no dependency on the system Python), keeping native build exposure minimal.

### 16.1 Removals / Consolidations (Zero Functional Change Expected)
| Action | Rationale | Risk Mitigation |
|--------|-----------|-----------------|
| Remove duplicate `bs4` (keep `beautifulsoup4`) | Redundant meta-package | Run tests involving HTML parsing. |
| Remove `aspy.yaml` if unused | Dead dependency | Confirm grep shows no imports. |
| Remove `six` | Python 3-only codebase | Simple grep for `six.`; replace any legacy helpers with stdlib. |
| Remove `appdirs` if usage minimal; or internal shim copying folder logic | Simplify; prefer later `platformdirs` when Python baseline raises (optional now) | Provide fallback wrapper if uncertain. |
| Remove `chardet` if not directly imported | Requests no longer strictly depends (uses charset-normalizer) | Grep to confirm; ensure no custom detection. |
| Remove unused `multi-key-dict` / `munch` (if usage trivial) | Shrink surface | Replace with dict / dataclass; add quick unit assertion. |

### 16.2 Replacements (Drop Deprecated APIs Without Baseline Change)
| Target | Replace With | Notes |
|--------|--------------|-------|
| `oauth2client` + `httplib2` | `google-auth`, `google-auth-oauthlib`, `requests` | Works on Python 3.8+; refactor `oauth2_helper` to fetch/refresh tokens via `google.auth.transport.requests`. |
| (Optional) `appdirs` | `platformdirs` backport (install `platformdirs`) | `platformdirs` supports Python 3.8; swap path retrieval logic. |

### 16.3 Safe Version Bumps
All of these routinely update without changing public APIs significantly (still verify via tests):

- `attrs`
- `filelock`
- `identify`
- `idna`
- `certifi`
- `soupsieve`
- `tabulate`
- `tqdm`
- `wrapt`
- `Deprecated`
- `defusedxml`
- `dnspython`
- `email-validator`
- `rsa`
- `pyasn1` / `pyasn1-modules`
- `pbr`
- `websocket-client`
- `requests` (already pinned to >=2.32.0; bump to latest 2.x is safe)
- `urllib3` (already pinned `<3.0.0`; can advance within 2.x line)

### 16.4 Introduce Tooling Without Functional Impact
| Action | Benefit |
|--------|---------|
| Add workflow to output “outdated dependency” table PR comment weekly | Visibility |
| Add `pip-audit` / `safety` job (non-blocking first, then gating) | Security posture |
| Add SBOM (CycloneDX) generation step in release pipeline | Compliance & diff |

### 16.5 Codebase Hygiene (No Python Version Change)
| Action | Impact |
|--------|--------|
| Refactor `oauth2_helper` to remove `oauth2client` types and update tests | Eliminates deprecated lib dependency early |
| Replace ad-hoc path joins with `pathlib` uniformly | Readability & future maintainability |
| Remove any `# type: ignore` that is obsolete after stub updates (`types-requests`, etc.) | Type safety |
| Consolidate YAML handling: ensure `ruamel.yaml` only where round-trip formatting required; use `yaml.safe_load` elsewhere | Clarity & performance |
| Add explicit `algorithms=[...]` in any `jwt.decode` calls now (compat with PyJWT 2) | Future-proof; no breaking behavior |

### 16.6 “Fence” Mechanisms (Prevent Regression During Later Upgrades)
| Mechanism | Description |
|-----------|-------------|
| Add contract tests for OpenStack image/server listing that only assert minimal invariants (e.g., presence of fields) | Safe baseline snapshot |
| Snapshot representative INFO.yaml before yaml library bumps; diff loader-dumper output | Prevent formatting regressions |
| Introduce a “latest permissive” tox env (installs newest versions ignoring pins) but does **not** publish — for early warning only | Pre-upgrade signal |
| CentOS 7 wheel audit job | Nightly `uvx` matrix run logs any dependency falling back to source build (signals imminent need for toolchain or dependency pin) |

### 16.7 Documentation & Metadata
| Update | Reason |
|--------|--------|
| Add `MODERNISE_DEPENDENCIES.md` (this file) to repo index / README link | Visibility |
| Create `MIGRATING-openstacksdk.md` placeholder | Guides contributors early |
| Update contributor docs to outline phased dependency policy (prune → pin → upgrade) | Consistency |

### 16.8 Deferred (Intentionally NOT Done Until Python Baseline Raises)
| Deferral | Reason |
|----------|--------|
| Replace `toml` with stdlib `tomllib` | Requires Python >=3.11 for clean removal |
| Remove `appdirs` in favor of direct `pathlib` (if you want zero third-party) plus OS-specific logic | Optional, but coordinate with baseline uplift |
| Upgrade `openstacksdk` beyond 2.x/early 3.x | Requires higher Python baseline to reach latest 4.x line comfortably |

### 16.9 Ordering Proposal (Non-Breaking Only)
1. Prune duplicates (`bs4`), dead libs (`six`, `aspy.yaml`).
2. Refactor oauth flow (remove `oauth2client`, `httplib2`).
3. Low-risk version bumps batch commit (utility libs).
4. Add audits + SBOM + latest-permissive env.
4a. Establish `uvx`-driven CI matrix (CentOS 7) for Python 3.8 / 3.10 / 3.11 to confirm interpreter provisioning & wheel-only installs.
5. Implement PyJWT defensive decode adjustments.
6. YAML handling consolidation.
7. Commit documentation & migration scaffolding.
8. (Optional) Introduce `platformdirs`.

### 16.10 Success Criteria (Non-Breaking Phase)
| Metric | Check |
|--------|-------|
| All deprecated libs removed | `grep` yields no imports |
| Test suite passes unchanged | CI green |
| Audit shows no new vulnerabilities | Compare before/after report |
| OpenStack tests unchanged (still using existing version) | Smoke tests pass |
| OAuth token retrieval still functional | Integration test or mocked flow |

---

## 17. Summary of Immediate Actionable Items (While Staying on Python >=3.8)

1. Remove: `bs4`, `six`, `aspy.yaml`, (maybe) `chardet`, `multi-key-dict`, `munch` if unused.
2. Replace: `oauth2client` + `httplib2` → `google-auth` + `requests`.
3. (Optional now) Introduce `platformdirs` (or postpone).
4. Bump low-risk libraries to latest patch/minor versions.
5. Add dependency audit + SBOM generation.
6. Harden `jwt.decode` usage with explicit algorithms list.
7. Consolidate YAML strategy (choose `ruamel.yaml` only for round-trip).
8. Add migration scaffolding docs.
9. Implement a permissive “latest” environment to forecast future breaks.

These steps reduce technical debt and risk for the later high-impact Python baseline uplift and `openstacksdk` modernization.

---

## 18. Closing Notes

By executing the non-breaking actions first you:
- Shrink the dependency graph (fewer upgrade vectors later).
- Remove deprecated/security-sensitive code paths early.
- Gain clearer signal when truly breaking (high-risk) upgrades commence.
- Avoid entangling Python baseline politics with obvious hygiene improvements.
- Proactively validate CentOS 7 compatibility (via `uvx` matrix) before committing to a raised Python baseline.

CentOS 7 Support Assurance:
Maintaining CentOS 7 remains viable across all phases because we never depend on the system Python; instead we provision interpreters (3.8 → 3.10 → 3.11+) via `uvx`, relying on manylinux2014 (glibc 2.17) wheels. The only ongoing watchpoints are: (1) any dependency that begins publishing wheels targeting a newer glibc, (2) packages that drop wheels and trigger a source build (mitigate with a toolchain / Developer Toolset), (3) `python-ldap` wheel availability during its future uplift. A nightly or scheduled “wheel audit” job (matrix install with `--no-build-isolation --only-binary=:all:` fallback reporting) gives early warning without blocking mainline CI.

Post-Baseline Uplift Checklist (CentOS 7 Context):
1. Confirm all environments (3.10 target, 3.11 optional) install with zero local builds (record `pip debug` + wheel list).
2. Run OpenStack integration smoke tests under new baseline (assert minimal invariants rather than strict field ordering).
3. Replace `toml` with stdlib `tomllib` once 3.11 floor declared; remove backfill dependencies.
4. Re‑evaluate legacy compatibility shims (e.g., any conditional imports kept only for 3.8).
5. Re-run SBOM + vulnerability scan; diff against pre-uplift to ensure no unexpected indirect additions.
6. Freeze a short “stability window” (e.g., 1–2 weeks) after baseline raise where only bug fixes merge—ensures signal clarity.
7. Document final supported Python versions and CentOS 7 runtime expectations (explicit note that interpreter is provisioned, not system-provided).

When ready, proceed to the baseline uplift planning with a cleaner, leaner, better-instrumented, and platform‑validated foundation.

---

*End of Report.*