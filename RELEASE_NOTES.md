# v0.3.14 — Desktop 26.1021.3705.0

Adds the independent Desktop **26.1021.3705.0** adapter, frontend 2.12.1 and optional source-built compatibility backend 0.164.0-alpha.11.1.1. The default remains the official backend.

The new UI retains recent-activity ordering in Priority and activity lists, manual pins, pending-request colors, local and SSH project routes, Work selection, file drops, paginated history and saved chat settings. Native tests covered six first-send cases and six cold reopens for each backend mode, with 400 synthetic tasks, all 26 contracts, 23 renderer features, at least 60 awake seconds of observation and normal closure. Shared browser registration stayed unchanged.

Optional local background predictions and temporary analyses now skip histories larger than 1 GiB, avoiding a complete-history copy for those operations. Normal chat and stored history remain available. Native metadata-reader checks and 64 MiB/512 MiB synthetic compaction replays passed on both backends. The recovery message can also describe unrelated failures; this change addresses the unnecessary background-copy path.

The compatibility backend is pinned to public source commit `fabd73f0370b279be6e57c74a14ec53cd6c3c945`, upstream `6905ecede7816e91373e9eabda3f6b0368fc747b`, Rust 1.99.1 and all 77 migration identities. Earlier adapter and backend profiles retain their build identities. Historical originals unavailable for this run are recorded as skips; the current-version native checks are mandatory.
