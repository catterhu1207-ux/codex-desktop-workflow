# Source inventory

| Files | Origin | License basis |
|---|---|---|
| `src/codex_desktop_workflow/` | Original public workflow layer | MIT |
| `src/hotfix_builder.py`, `src/frontend_feature_contracts.py` | Extracted from the author's private Codex desktop maintenance tooling, with private state excluded | MIT, author-owned |
| `src/hotfix_profile_*.py`, `src/frontend_contract_26915.py`, `src/frontend_work_contract_26915.py`, `src/composer_selector_contract.py` | Author-owned version-profile chain used by the extracted builder; the public CLI enables `26.908.9136.0` and `26.915.3509.0` | MIT, author-owned |
| `src/codex_desktop_workflow/data/frontend_scenarios_26915.js` | Synthetic renderer scenarios for the 26.915 profile; no task content or user identifiers | MIT, author-owned |
| `src/codex_desktop_workflow/policies/*.json` | Author-generated allowlists for the byte-identical official backend in each supported package | MIT, metadata only |
| `install.ps1`, release and Pages workflows | Original distribution tooling for the public workflow | MIT |
| `docs/assets/demo-*.gif`, `docs/assets/before-after-*.png`, `docs/assets/social-preview.png` | Generated illustrative UI with synthetic task labels | MIT |
| `docs/`, `docs/promotion/` | Original public documentation and launch copy | MIT |
| Tests, examples and documentation | Original synthetic material | MIT |

The repository contains byte signatures needed to identify and transform specific locations in a user-supplied official package. It does not contain the package, full extracted frontend files, binaries, credentials, sessions, databases, logs, or private maintenance state.
