# v0.3.13 — Desktop 26.1016.8622.0

v0.3.13 corrects a Windows CI test that compared equivalent short and long paths as strings. It retains the four browser-isolated source launches recorded for v0.3.12 and the same application bytes. Native frontend behavior retains the earlier results for those identical bytes.

The new v0.3.13 wheel passed its separate resource and contract checks. Downloadable-installer validation is pending.

This version retains the independent adapter for the complete official Windows x64 package **26.1016.8622.0**, frontend 2.11.0 and its existing behavior: recent-activity ordering, stable cold opens, manual pins, local and SSH project routes, Work selection, file drops, paginated history and saved chat settings.

The official backend remains the default. The optional compatibility backend builds from pinned public source for `0.163.0-alpha.11.2.1`, using Rust 1.99.1 and all 77 official migration identities. Earlier profiles retain their identities.

The v0.3.12 tag remains at its original commit; CI stopped before release assets were built. The v0.3.11 draft and original tag remain unpublished and unchanged. See the [acceptance report](https://github.com/catterhu1207-ux/codex-desktop-workflow/blob/main/ACCEPTANCE.md) for source and installation results.
