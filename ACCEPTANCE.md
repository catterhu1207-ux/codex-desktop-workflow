# Acceptance reports

This public report is a redacted summary of the maintainer-side Windows acceptance run. Local paths, process identifiers, ports, logs, credentials, and task data are excluded.

## v0.3.0 qualification

The 26.924.1866.0 public workflow was built from the exact official Windows package and qualified with both backend modes on 2026-09-26.

| Item | Result |
|---|---|
| Official ASAR | `96b6aa6e1ea46dd8a30b3fa5166be12284ba66bd3901241a81a60684f150189d` |
| Official backend | `0122378c15dc0c3c0af0d6addf2dd278125c19676b41fadaa520f89d2c9e0079` |
| Public-source compatibility backend | Profile `0.158.0-alpha.2`, upstream `10382da79a2a2d6e8ae221fa63077215389c1ad2`; immutable compatibility source reference recorded in `backend-source.json` |
| Exact frontend contracts | 24 passed for each backend mode |
| Real renderer feature inventory | All 21 features passed in all four independent launches |
| Official backend launches | Empty data and 400 synthetic tasks; 64.84 and 65.52 seconds observed after proof; matching current app-server; normal exit |
| Compatibility backend launches | Empty data and 400 synthetic tasks; 66.38 and 67.80 seconds observed after proof; matching current app-server; normal exit |
| Desktop executable | Unique embedded ASAR digest updated in the independent copy; all other bytes unchanged |
| Public tests | 68 run, 66 passed; two older official-artifact tests skipped because their exact samples were unavailable |
| Wheel and installer | Installed wheel resources, bundle contents and checksums passed; official, compatibility-manifest and compatibility-source dry-runs passed |
| Publication scan | Source, wheels and bundle passed the sensitive-file and identifier scan |
| History import | Indirect logical parent and physical ancestor chain verified; original bytes and source database preserved; imported copy remained usable after the source directory was moved |
| History rejection tests | Cycles, missing segments, wrong ownership, boundaries, changed dependencies and escaping paths rejected |

The required new-version checks were not skipped. The source-bound qualification record is packaged as `qualification-26.924.1866.0.json`. The compatibility backend's separate acceptance report covers 15 module tests, HTTP and WebSocket image-tool replay, local and remote V2 compaction, cold restoration and all 57 database migration checksums.

## v0.2.4 qualification

The 26.917.9434.0 public workflow was built from the exact official Windows package with its unchanged bundled backend and independently qualified on 2026-09-25.

| Item | Result |
|---|---|
| Official ASAR | `d4234b03eb532fe0f3e9a7d90caad51edb68af45f771cc786d966377e7446f5a` |
| Generated ASAR | `3d49514032ec8ffa9e39566082a5b691ffb1f4595f335811828e18fafc749a58` |
| Unchanged official backend | `9015c47d1714294ecd9033c4b5aefc3076797d867d1c36aa37749fcb76c8942f` |
| Desktop executable | Copied byte-identically; no matching embedded ASAR-header digest record in the official executable |
| Exact frontend contracts | 24 passed; validator `2.4.10` |
| Real renderer feature inventory | 21 passed per isolated launch; artifact `2.6.13-d4234b03eb53` |
| Public tests with the exact current artifact | 32 run, 30 passed, two older-version artifact tests skipped because their local artifacts were unavailable |
| Wheel and installer | Version `0.2.4` wheel contains the profile, scenarios, and official-backend policy; installed-wheel resource loading and local-bundle installer dry-run passed |
| Two isolated renderer launches | Both passed; 90 seconds observed each; matching official backend, fresh renderer proof, and normal close |
| Qualification stage | `isolated_renderer_qualified`; daily-user validation is separate |

The renderer checks covered plan and pinned indicator precedence through the mounted row, task and project ordering, remote project labels and routing, the Work picker, file drop, and history behavior with synthetic data. Existing version profiles and their release identities remain registered.

## v0.2.3 qualification

The 26.917.6896.0 public workflow was built from the exact official Windows package and independently checked with its unchanged bundled backend on 2026-09-23.

| Item | Result |
|---|---|
| Official ASAR | `00b7936388d11a3faede5fc736a8c6264eb66e1907bac4ef72c39b7399175d68` |
| Generated ASAR | `a6ee404ee47a92244d5c2581a792fe9739400c342d7d9690e979f5ebc01e0ab0` |
| Unchanged official backend | `97d4d67419d0ac2f71342f9a5e850f9468aa622618de8ea823223edb9a91926a` |
| Desktop executable | Copied byte-identically; the official executable contained no matching embedded ASAR-header digest record |
| Public tests with explicit current artifact | 31 run, 30 passed, one older-version artifact test skipped because its local artifact was unavailable |
| Two isolated renderer launches | Both passed; 90 seconds observed each; matching official backend; fresh renderer proof; both closed normally |
| Qualification stage | `isolated_renderer_qualified`; daily-user validation remains separate |

The current renderer checks exercised plan and pinned indicator precedence, task and project ordering, remote project labels and routes, the Work picker, file drop, and history behavior with synthetic data. The initial public acceptance attempt exposed an inconsistent synthetic project name in the renderer probe. That fixture was corrected and a new artifact was built before the two passing launches; the failed attempt is not counted as a pass.

## v0.2.2 qualification

The 26.915.4065.0 public workflow was independently built and checked with the unchanged official backend on 2026-09-19.

| Item | Result |
|---|---|
| Official ASAR | `b8aeb817cd1ee6ef50efe8a97985d3be41de89688a5addfe0a444e1e52348096` |
| Generated ASAR | `fa8ce965d63650cf8f67922280f15f053c334a031f0d51e0b8800c1a0ca8641e` |
| Unchanged official backend | `bc45017e8239dc150258f69309ced9df6bbcdf5b8e4f346decf780ac0999e226` |
| Public tests, with explicit local artifact | 38 passed, zero skipped, zero failed |
| Two independent renderer launches | Both passed; 60 seconds observed each; fresh proof for `2.6.11-b8aeb817cd1e`; matching official backend; both closed normally |
| Authentication or real task data in public acceptance | None |
| Qualification stage | `isolated_renderer_qualified`; daily-user validation remains separate |

The first public acceptance attempt exposed a startup navigation race: the harness navigated before Electron completed initial loading, causing `ERR_ABORTED`. The harness now waits for the complete document and renderer bridge, defers navigation, and checks the actual evaluation result. Regression tests cover the not-ready state and unsuccessful evaluation responses. The failed run is not counted as one of the two passing runs.

### Supplemental private-maintenance check (separate scope)

The maintainer's broader suite originally ran 566 checks: 466 passed, 100 skipped, none failed. The skipped task-binding integration check was supplied with an isolated fixture and passed. Combined coverage is therefore 467 passed, 99 skipped, none failed. The remaining skips concern unavailable historical inputs or a superseded patch; they are not counted as passes.

Two additional cold `app-server` resumes exercised the locally patched, version-matched backend through `initialize`, `thread/resume` and `thread/turns/list`: a preserved task binding survived a different global default, and a subsequent explicit binding change in the shadow database survived another cold resume. Neither call supplied a model/provider override. These checks sent no generation request and left the original task history unchanged. The backend appended two settings events only to the shadow history; the original 43-record prefix was preserved.

This supplemental evidence applies to the maintainer's patched backend, not to the official-backend combination distributed here. It does not turn the public `codex-history-compat` integration into a supported combination, or establish daily-user `live_validated` status. Private fixtures and raw logs are excluded.

## v0.2.0 result

`v0.2.1` changes distribution, installer, and documentation only. The launcher artifact hashes and two-run runtime evidence below remain the retained version-bound acceptance record for 26.915.3509.0.

| Item | Result |
|---|---|
| Release target | Windows x64, Codex desktop `26.915.3509.0` |
| Official `app.asar` identity | `8227f6234cf2cc418ec8bbdeedec03f8d777f85520929ff2d9d38e774f681dfd` |
| Official `codex.exe` identity | `ff9bc3ddc08fa52b43ea170be5f628ffad1c1d9c80c5770b8e2a2f817a9ee3c9` |
| Generated `app.asar` identity | `17f443796846f12ec46f505a80a5f7cc3644d56420733e6f35f9f4ddfe7f636f` |
| Package and source gates | Passed |
| Actual bundled JavaScript contracts | Passed |
| Isolated renderer run 1 | Passed; 60 seconds observed; fresh renderer proof; packaged official backend matched by path and file identity; main and backend exited normally |
| Isolated renderer run 2 | Passed; 60 seconds observed; fresh renderer proof; packaged official backend matched by path and file identity; main and backend exited normally |
| Official bundled backend combination | Passed |
| `codex-history-compat` backend combination | Skipped and unsupported in v0.2.x |
| Real task content or credentials used | No |
| Force termination used | No |

### Verified behavior

- Priority recency ordering for ordinary and pinned items, including live refresh.
- Loading spinner, planned yellow, pinned red, and unread blue; planned yellow wins when an item is also pinned.
- A real pending-request object is required for the planned state; a display scalar alone is rejected.
- Remote project names are visible in the relevant pickers while route identity remains unchanged.
- The package contracts for preserving valid per-task model and reasoning settings passed.
- Each run produced a fresh renderer attestation tied to `2.6.10-8227f6234cf2` and closed through the application-owned quit action.

## Retained v0.1.0 result

| Item | Result |
|---|---|
| Release target | Windows x64, Codex desktop `26.908.9136.0` |
| Official `app.asar` identity | `7a46bd6fe162050afbac27d7d5271d19524e887fa0cdd06c0f2d3fa9b606a31d` |
| Generated `app.asar` identity | `304ada38ece9df561a7da99fe81f484b0da08baef127db8cc85705e62a2a2ce1` |
| Two isolated renderer runs | Passed; 60 seconds observed each; fresh renderer proof; normal exit |
| Official bundled backend combination | Passed |

## Scope

The isolated runs used synthetic data and did not copy authentication. The test route mounted the real task renderer long enough to produce the artifact-bound proof; an unauthenticated session may subsequently return to the sign-in screen. This establishes isolated renderer qualification, not validation of a user's daily environment or external services.

Earlier diagnostic attempts exposed shell-folder and normal-exit handling defects. Those attempts were retained locally as failure evidence, and the defects were fixed before the two reported runs. No failed attempt is counted as a pass.
