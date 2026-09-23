# Changelog

## v0.2.3 - 2026-09-23

- Add exact Windows desktop 26.917.6896.0 support with the unchanged official backend.
- Rebase renderer contracts for Priority ordering, plan and pinned indicators, remote project names, Work picker, file drop, and history display.
- Check the exact official executable for an embedded ASAR integrity record; this release's executable has no matching record and remains byte-identical in the independent copy.
- Retain all previously supported profile identities and versions.

## v0.2.2 - 2026-09-19

- Add exact Windows desktop 26.915.4065.0 support and its unchanged official backend policy.
- Adapt renderer routes, attention states, remote project labels, live ordering, file drop and exact attestation route.
- Preserve prior profile identities and add 12 opt-in real-bundle regression checks.
- Wait for initial page completion and a successful renderer response before navigating to the acceptance route, avoiding a startup-abort race.
- Record supplemental task-resume evidence separately from the public official-backend release.

## v0.2.1

- Added a one-command Windows installer and verified release bundle.
- Added GitHub Pages landing page, bilingual demo assets, FAQ, troubleshooting, and roadmap.
- Added issue templates and community feedback surfaces.
- Kept official binaries, patched backends, and user data out of release assets.

## v0.2.0

- Added Codex Desktop `26.915.3509.0` support while retaining `26.908.9136.0`.
- Made English the default README and added `README.zh-CN.md`.
- Pinned verification to the packaged official backend.

## v0.1.0

- Initial experimental source release for `26.908.9136.0`.
