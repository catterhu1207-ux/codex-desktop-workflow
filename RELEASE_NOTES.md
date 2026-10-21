# v0.3.9 — Desktop 26.1016.6573.0 and activity ordering

This release adds an independent adapter for the complete official Windows x64 package **26.1016.6573.0**. Supply a matching signed MSIX or official application directory; a Store installation is not required.

Automatic priority and activity lists put recent chat activity first. Merely opening an old chat does not move it ahead after a restart. Manual pin order is preserved. Pending questions and approvals stay orange; plans awaiting implementation stay yellow.

The adapter preserves native first messages, readable SSH projects and routing, Work project selection, file drops, paginated history and per-chat model settings. Update notices follow the interface language and distinguish an announcement, a downloadable official package and a qualified adaptation.

The official backend is the default. The optional compatibility backend is built from pinned public source for 0.163.0-alpha.11.1, with Rust 1.95.0 and all 77 database migration checksums. Existing published desktop profiles retain their identities.

See the [acceptance report](https://github.com/catterhu1207-ux/codex-desktop-workflow/blob/main/ACCEPTANCE.md) for the runtime, installation and download checks.
