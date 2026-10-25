# Changelog

## v0.3.15

Correct the Windows CI fixture writer to record canonical owner paths. The Desktop 26.1021.3705.0 application, frontend 2.12.1 and compatibility backend retain their qualified bytes; package metadata and distribution checks advance independently. The occupied v0.3.14 tag remains unchanged.


## v0.3.14

Adds the independent Desktop **26.1021.3705.0** adapter, frontend 2.12.1 and optional source-built compatibility backend 0.164.0-alpha.11.1.1. The default remains the official backend.

The new UI retains recent-activity ordering in Priority and activity lists, manual pins, pending-request colors, local and SSH project routes, Work selection, file drops, paginated history and saved chat settings. Native tests covered six first-send cases and six cold reopens for each backend mode, with 400 synthetic tasks, all 26 contracts, 23 renderer features, at least 60 awake seconds of observation and normal closure. Shared browser registration stayed unchanged.

Optional local background predictions and temporary analyses now skip histories larger than 1 GiB, avoiding a complete-history copy for those operations. Normal chat and stored history remain available. Native metadata-reader checks and 64 MiB/512 MiB synthetic compaction replays passed on both backends. The recovery message can also describe unrelated failures; this change addresses the unnecessary background-copy path.

The compatibility backend is pinned to public source commit `fabd73f0370b279be6e57c74a14ec53cd6c3c945`, upstream `6905ecede7816e91373e9eabda3f6b0368fc747b`, Rust 1.99.1 and all 77 migration identities. Earlier adapter and backend profiles retain their build identities. Historical originals unavailable for this run are recorded as skips; the current-version native checks are mandatory.


## v0.3.13

- Correct a Windows CI test to compare the backend's file identity when temporary paths use short names. Application behavior and the existing browser isolation remain unchanged.
- Retain the four qualified v0.3.12 source launches and validate the v0.3.13 wheel separately.
- Keep the v0.3.12 tag, whose CI failed before release assets were built, and the unpublished v0.3.11 draft.

## v0.3.12 (CI failed before release assets)

- Isolate installation checks from the signed-in user's Chrome registration. Four source launches passed in fresh test profiles; regular app launches retain browser integration.
- Retain the 26.1016.8622.0 / frontend 2.11.0 adapter, fixed compatibility-backend source and all earlier profiles.
- Keep v0.3.11 as an unpublished draft with its original tag and evidence.

## v0.3.11 (unpublished draft)

- Add the independent Desktop 26.1016.8622.0 / frontend 2.11.0 profile and adapt its dynamic resource map while preserving existing behavior and older identities.
- Retain activity ordering, manual pins, pending-state colors, project/SSH/Work routes, file drops, history pagination and per-chat settings; qualify both backend modes with current native cases.
- Pin the optional 0.163.0-alpha.11.2.1 source build to Rust 1.99.1, real-type module tests, the full CLI build and all 77 official migration identities.
- Preserve hash-bound resource bytes for current and future Windows checkouts, and deploy project Pages only from a published stable release.


## v0.3.10

- Add an independent Desktop 26.1016.8120.0 profile with frontend 2.10.1. Earlier profiles retain their source and build identities.
- Preserve activity ordering, pending attention, remote routes, Work selection, file drop and per-chat settings across the updated interface.
- Deliver completed renderer proofs again when a minimized window is restored, while still requiring the actual visible primary renderer.
- Check Windows executable integrity before launch and report a blocked candidate without changing system security settings.
- Pin the optional compatibility build to Rust 1.99.1 and its exact public source. Installer dry-run shows the matching toolchain and rejects a backend from a different official package.


## v0.3.9

- Add an independent Desktop 26.1016.6573.0 profile and frontend identity 2.9.2.
- Sort automatic priority/activity lists by current chat activity, including after cold restart; preserve manual pin order.
- Carry pending questions, approvals and implementation plans through the full native row pipeline.
- Preserve native first-send, real SSH project routing, Work selection, file drops, paginated history and per-chat settings.
- Bind optional compatibility builds to upstream 0.163.0-alpha.11, a fixed public source revision and all 77 migrations.
- Run installation smoke tests with the supported unelevated sandbox in disposable homes, avoiding system setup prompts.
- Keep prior published profiles and exact source identities. The unpublished 4894 recovery profile remains unavailable to the installer.

## v0.3.8

- Default new 9446 installations and persistent update notices to English.
- Preserve running task tools while the native qualification sidebar mounts.
- Derive every feature record from the current artifact identity.
- Retain descending update-time sorting, orange unanswered requests, yellow plans, SSH and Work routing, and per-chat models.

## v0.3.7 (unpublished draft)

- Default new 9446 public data and renderer language to English.
- Translate persistent update status labels and explanations.
- Preserve existing language choices and user content.
- Bind the changed frontend to its own exact artifact and fresh acceptance evidence.

## v0.3.6

- Add exact Desktop 26.1007.9446.0 and source-built 0.162.0-alpha.17.2 compatibility profile.
- Use descending update time in current automatic lists, preserving manual and pinned order.
- Propagate native intermediate question and approval state ahead of the spinner.
- Distinguish announcement, verified complete package availability and qualified adaptation with separate update icons; hide update-check terminals.
- Exercise real setting scope, first-send lifecycle, native cold history, SSH and Work routing.
- Use isolated test scheduling, unelevated fixtures and exact-resource elevation checks.
- Bind full MSIX installation checks to the installed wheel and both backend modes.

## v0.3.5

- Add an exact Desktop 26.928.4866.0 profile while retaining earlier profiles.
- Show orange for outstanding questions, choices and approval requests; preserve yellow for plans awaiting implementation and existing ordering rules.
- Preserve the native first-send path for newly opened chats that do not yet have saved history.
- Accept a verified complete official MSIX as installer input without installing the Store package.
- Exercise the native sidebar with persisted settings, synthetic history and project groups.
- Use awake-time probe deadlines and owned process cleanup during isolated acceptance.
- Bind optional compatibility builds to the matching 0.159.2 source and all 73 migrations across six databases.

## v0.3.3

- Move tasks and projects on actual turn starts in automatic sorting; separate attention colors from time order.
- Preserve server ordering in manual pinned mode and use start-time ordering in automatic pinned mode.
- Ignore mutable update timestamps when an older entry lacks a start time; use its creation time.
- Package the start reducer, selector and project-consumer regression scenario with the wheel.
- Retain the v0.2.2 compatibility source profile, all 72 migrations and previous desktop profiles.
- Add a real composer-to-sidebar demonstration using fictional tasks.


## v0.3.2 - 2026-09-27

- Bind Desktop 26.924.2738.0 compatibility builds to the immutable sqlite-v2 source profile and all 72 migrations across six databases.
- Preserve memories_1.sqlite during independent import.
- Use frontend build identity 2.7.2 while retaining previous desktop identities.
- Exercise all six synthetic databases and visible, native-readable task metadata during acceptance.
- Replace drawn demo rows with reproducible real-renderer screenshots, bilingual comparisons, animations and a Pages preview.

## v0.3.1 - 2026-09-27

- Add exact Desktop 26.924.2738.0 support with an independent frontend profile and build identity.
- Rebase sorting, attention indicators, remote names, Work selection, file drop, history and renderer proof to the new interface entries.
- Pin the matching optional compatibility backend to its own immutable public source reference, while retaining the official backend default.
- Preserve earlier profile identities and qualification records; recheck the 26.924.1866.0 contracts against its exact sample.
- Isolate Windows user folders and runtime caches during verification so a test launch cannot replace the daily application's cached runtime.

## v0.3.0 - 2026-09-26

- Add Desktop 26.924.1866.0 support and the optional source-built compatibility backend.
- Verify logical-parent and physical-ancestor history chains during import and before launch.

## v0.2.4 - 2026-09-25

- Add exact Windows desktop 26.917.9434.0 support with the unchanged official backend.
- Rebase the full frontend contracts, including mounted plan and pinned row behavior, Priority ordering, remote project names, Work picker, file drop, and history.
- Keep all previously supported package profiles and their release identities unchanged.
- Bind the new official ASAR, backend, and critical entry hashes; ship only the source workflow and installer.


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

The v0.3.4 tag is retained as an unpublished attempt: its CI concurrency check depended on timer throughput. v0.3.5 checks completed reads and distinct clock updates instead. Application patches and runtime behavior are unchanged.
