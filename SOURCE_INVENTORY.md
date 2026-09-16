# Source inventory

| Files | Origin | License basis |
|---|---|---|
| `src/codex_desktop_workflow/` | Original public workflow layer | MIT |
| `src/hotfix_builder.py`, `src/frontend_feature_contracts.py` | Extracted from the author's private Codex desktop maintenance tooling, with private state excluded | MIT, author-owned |
| `src/hotfix_profile_*.py`, `src/composer_selector_contract.py` | Author-owned version-profile chain used by the extracted builder; the public CLI enables only `26.908.9136.0` | MIT, author-owned |
| `src/codex_desktop_workflow/policies/*.json` | Author-generated allowlist for the byte-identical official backend in the one supported package | MIT, metadata only |
| Tests, examples and documentation | Original synthetic material | MIT |

The repository contains byte signatures needed to identify and transform specific locations in a user-supplied official package. It does not contain the package, full extracted frontend files, binaries, credentials, sessions, databases, logs, or private maintenance state.
