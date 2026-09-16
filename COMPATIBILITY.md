# Compatibility

| Component | Status in v0.1.0 |
|---|---|
| Windows x64 | Supported |
| OpenAI Codex desktop `26.908.9136.0` with official ASAR SHA-256 `7a46bd6fe162050afbac27d7d5271d19524e887fa0cdd06c0f2d3fa9b606a31d` | Supported |
| Any other desktop version or ASAR | Rejected |
| Official bundled `codex.exe` | Default and required for the supported release |
| `codex-history-compat` backend | Source patch is public; desktop integration is not yet qualified and is reported as unsupported |
| Existing task data | Explicit snapshot import into a new independent directory |
| Automatic task-data synchronization | Unsupported |

A version number alone is insufficient. `inspect` also checks the complete ASAR, bundled backend, and four relevant ASAR entries.

