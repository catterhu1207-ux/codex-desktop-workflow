# v0.3.7 — English UI for Desktop 26.1007.9446.0

The public Windows installation now defaults to English. Its persistent update labels and explanations are English in all three states: New version announced, Official package available, and Adaptation ready. Each state keeps its distinct icon.

Existing language preferences, chat content and project names are preserved. The exact new frontend artifact is 2.7.20-356c13dc7158. Source-package identity, renderer proofs, history checks and backend identity remain required.

The official backend remains the default. The optional compatibility backend retains its public source and reproducible build recipe. Supply the matching official x64 MSIX or extracted application directory; the bundle contains the installer and source wheels.

Sorting by descending update time, orange pending questions and approvals, yellow pending implementation, lazy history, per-chat models, SSH project identity, Work selection and file drops are retained.

See [acceptance results](https://github.com/catterhu1207-ux/codex-desktop-workflow/blob/main/ACCEPTANCE.md) for the completed release checks and unavailable historical-source inputs.

Current-source and installed-wheel checks passed all 131 tests, with six unavailable historical-source skips. Both backend modes passed three profiles; a normal wheel installation passed three more. The three English update states were checked in the actual mounted component. Final anonymous distribution readback is tracked separately.
