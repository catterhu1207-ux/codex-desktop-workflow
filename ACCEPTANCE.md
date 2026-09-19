# Acceptance reports

This public report is a redacted summary of the maintainer-side Windows acceptance run. Local paths, process identifiers, ports, logs, credentials, and task data are excluded.

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
