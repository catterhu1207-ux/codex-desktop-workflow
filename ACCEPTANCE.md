# Acceptance reports

This public report is a redacted summary of the maintainer-side Windows acceptance run. Local paths, process identifiers, ports, logs, credentials, and task data are excluded.

## v0.2.0 result

| Item | Result |
|---|---|
| Release target | Windows x64, Codex desktop `26.915.3509.0` |
| Official `app.asar` SHA-256 | `8227f6234cf2cc418ec8bbdeedec03f8d777f85520929ff2d9d38e774f681dfd` |
| Official `codex.exe` SHA-256 | `ff9bc3ddc08fa52b43ea170be5f628ffad1c1d9c80c5770b8e2a2f817a9ee3c9` |
| Generated `app.asar` SHA-256 | `17f443796846f12ec46f505a80a5f7cc3644d56420733e6f35f9f4ddfe7f636f` |
| Package and source gates | Passed |
| Actual bundled JavaScript contracts | Passed |
| Isolated renderer run 1 | Passed; 60 seconds observed; fresh renderer proof; packaged official backend matched by path and SHA-256; main and backend exited normally |
| Isolated renderer run 2 | Passed; 60 seconds observed; fresh renderer proof; packaged official backend matched by path and SHA-256; main and backend exited normally |
| Official bundled backend combination | Passed |
| `codex-history-compat` backend combination | Skipped and unsupported in v0.2.0 |
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
| Official `app.asar` SHA-256 | `7a46bd6fe162050afbac27d7d5271d19524e887fa0cdd06c0f2d3fa9b606a31d` |
| Generated `app.asar` SHA-256 | `304ada38ece9df561a7da99fe81f484b0da08baef127db8cc85705e62a2a2ce1` |
| Two isolated renderer runs | Passed; 60 seconds observed each; fresh renderer proof; normal exit |
| Official bundled backend combination | Passed |

## Scope

The isolated runs used synthetic data and did not copy authentication. The test route mounted the real task renderer long enough to produce the artifact-bound proof; an unauthenticated session may subsequently return to the sign-in screen. This establishes isolated renderer qualification, not validation of a user's daily environment or external services.

Earlier diagnostic attempts exposed shell-folder and normal-exit handling defects. Those attempts were retained locally as failure evidence, and the defects were fixed before the two reported runs. No failed attempt is counted as a pass.
