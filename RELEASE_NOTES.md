# v0.3.5 - Pending requests and Desktop 26.928.4866.0

Unanswered questions, choices and approval requests show an orange dot, including when a chat continues working. The dot remains until every outstanding request is resolved. A plan awaiting implementation stays yellow unless another request needs your response. Reading or selecting a chat does not clear its requests or change its order.

Adds Desktop 26.928.4866.0 support and protects a newly opened chat from premature history recovery before its first message creates a saved conversation. Sent messages retain their history and model settings. An unsent blank page is not promised to survive a restart. Existing ordering modes, pinned groups, project names, Work selection, file drop and paginated history are preserved.

The installer also accepts a complete official MSIX through `-Source`, so the supported Store version need not be installed first. It checks and extracts the package into a separate cache. The official backend remains the default; compatibility builds remain optional and version-specific.

Verification uses awake time for its launch and interface checks. Sleep time does not consume those budgets. Test processes and data are isolated from the daily application.

The bundle contains source wheels, the installer, README and license. Supply your own supported official package or installation. Official application binaries and user data are not included. The published bundle passed anonymous download, checksum verification and normal installation, followed by three complete isolated launches. Both backend modes passed their independent runtime checks. See [the acceptance report](https://github.com/catterhu1207-ux/codex-desktop-workflow/blob/main/ACCEPTANCE.md) for the test scope and results.
