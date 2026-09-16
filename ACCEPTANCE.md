# v0.1.0 acceptance report

This public report is a redacted summary of the maintainer-side Windows acceptance run. Local paths, process identifiers, ports, logs, credentials, and task data are excluded.

## Result

| Item | Result |
|---|---|
| Release target | Windows x64, Codex desktop `26.908.9136.0` |
| Official `app.asar` SHA-256 | `7a46bd6fe162050afbac27d7d5271d19524e887fa0cdd06c0f2d3fa9b606a31d` |
| Generated `app.asar` SHA-256 | `304ada38ece9df561a7da99fe81f484b0da08baef127db8cc85705e62a2a2ce1` |
| Package and source gates | Passed |
| Actual bundled JavaScript contracts | Passed |
| Isolated renderer run 1 | Passed; 60 seconds observed; fresh renderer proof; main and backend exited normally |
| Isolated renderer run 2 | Passed; 60 seconds observed; fresh renderer proof; main and backend exited normally |
| Official bundled backend combination | Passed |
| `codex-history-compat` backend combination | Skipped and unsupported in v0.1.0 |
| Real task content or credentials used | No |
| Force termination used | No |

## Verified behavior

- Priority recency ordering for ordinary and pinned items, including live refresh.
- Loading spinner, planned yellow, pinned red, and unread blue; planned yellow wins when an item is also pinned.
- A real pending-request object is required for the planned state; a display scalar alone is rejected.
- Remote project names are visible in the relevant pickers while route identity remains unchanged.
- The package contracts for preserving valid per-task model and reasoning settings passed.
- Each run produced a fresh renderer attestation tied to the generated artifact and closed through the application-owned quit action.

## Scope

The isolated runs used synthetic data and did not copy authentication. The test route mounted the real task renderer long enough to produce the artifact-bound proof; an unauthenticated session may subsequently return to the sign-in screen. This establishes isolated renderer qualification, not validation of a user's daily environment or external services.

Earlier diagnostic attempts exposed shell-folder and normal-exit handling defects. Those attempts were retained locally as failure evidence, and the defects were fixed before the two reported runs. No failed attempt is counted as a pass.
