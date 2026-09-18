# v0.2.0

Experimental source release for Windows x64 Codex desktop `26.915.3509.0`, retaining the `26.908.9136.0` profile.

- Adds the exact `26.915.3509.0` frontend, Work picker, resource-route and renderer-attestation profile.
- Builds an independent workflow-mod copy from a matching user-supplied official application directory.
- Pins each launch to the packaged official `codex.exe`, so an inherited `CODEX_CLI_PATH` cannot silently select another backend.
- Verifies Priority recency, planned/pinned/unread/loading indicators, remote-project naming, Work selection, file drop, history detail and preserved per-task settings contracts.
- Supports explicit task-data snapshot import into an independent directory.
- Uses the official bundled backend. The optional cross-provider backend remains unqualified for this release.
- Passed two independent maintainer-side renderer runs on `26.915.3509.0` with 60 seconds of observation each, matching packaged-backend identity and normal main/backend exit; see `ACCEPTANCE.md`.
