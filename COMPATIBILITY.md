# Compatibility

| Component | Status in v0.2.1 |
|---|---|
| Windows x64 | Supported |
| Codex desktop `26.915.3509.0`, official ASAR `8227f6234cf2cc418ec8bbdeedec03f8d777f85520929ff2d9d38e774f681dfd` | Supported; independently verified by two isolated launches |
| Codex desktop `26.908.9136.0`, official ASAR `7a46bd6fe162050afbac27d7d5271d19524e887fa0cdd06c0f2d3fa9b606a31d` | Supported; retained v0.1.0 isolated-renderer acceptance evidence |
| Any other desktop version or ASAR | Rejected |
| Official bundled `codex.exe` | Default and required for both supported releases |
| `codex-history-compat` backend | Source patch is public; desktop integration is not qualified in this repository and is reported as unsupported |
| Existing task data | Explicit snapshot import into a new independent directory |
| Automatic task-data synchronization | Unsupported |

A version number alone is insufficient. `inspect` also checks the complete ASAR, bundled backend, and all required ASAR entry hashes for the selected supported version.

