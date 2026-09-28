# v0.3.3 - Start-event ordering repair

A newly started turn moves its task and project forward immediately in automatic sorting. Attention colors remain independent of order. Manual ordering and pinned-group boundaries are preserved, and streaming output, completion and reading keep the order stable.

Supports Desktop 26.924.2738.0 with frontend build 2.7.3. The official backend remains the default; the opt-in compatibility backend stays pinned to codex-history-compat v0.2.2 and its 72 migrations across six databases. Existing desktop profiles and command-line interfaces are retained.

The bundle contains source wheels, the installer, README and license. Build the desktop copy from your own supported official installation. See the repository acceptance report for Windows tests and isolated runtime evidence.
