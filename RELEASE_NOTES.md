# v0.3.13 — Desktop 26.1016.8622.0

v0.3.13 corrects a Windows CI test that compared equivalent short and long paths as strings. It retains the four browser-isolated source launches recorded for v0.3.12 and the same application bytes. Native frontend behavior retains the earlier results for those identical bytes.

The new v0.3.13 wheel passed its separate resource and contract checks. The exact downloaded v0.3.13 bundle passed normal installation with the official backend and the optional backend built from pinned public source. Each mode passed independent empty-home and 400-chat synthetic launches: four new installation runs with 23 renderer proofs, at least 60 awake seconds of observation, the expected backend and normal closure. Shared Chrome registration remained unchanged throughout all four runs. Three installer dry-run selections and downloaded asset checksums passed.

The complete Windows suite passed 223 tests, with seven historical sample groups skipped; current 8622 and retained 6573 checks passed. The CI-style source-only suite passed 215 tests with seven sample-dependent groups skipped. All 464 tracked files passed the privacy scan.

This version retains the independent adapter for the complete official Windows x64 package **26.1016.8622.0**, frontend 2.11.0 and its existing behavior: recent-activity ordering, stable cold opens, manual pins, local and SSH project routes, Work selection, file drops, paginated history and saved chat settings.

The official backend remains the default. The optional compatibility backend builds from pinned public source for `0.163.0-alpha.11.2.1`, using Rust 1.99.1 and all 77 official migration identities. Earlier profiles retain their identities.

The v0.3.12 tag remains at its original commit; CI stopped before release assets were built. The v0.3.11 draft and original tag remain unpublished and unchanged. See the [acceptance report](https://github.com/catterhu1207-ux/codex-desktop-workflow/blob/main/ACCEPTANCE.md) for source and installation results.

## Project-page automation

After publication, a main-branch deployment successfully refreshed the project page for v0.3.13. The website workflow now sends stable-release notifications to the same protected main-branch deployment, which selects the latest published stable tag. This follow-up changes the website workflow and acceptance documentation; the published application tag and installation assets remain unchanged.
