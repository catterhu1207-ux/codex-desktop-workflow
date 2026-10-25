# Compatibility

Installer **v0.3.15** supports the independent Desktop 26.1021.3705.0 adapter. Both backend modes passed empty-home and populated synthetic runtime checks, with native first sends and cold restoration. Download availability and installation results are recorded on the [release page](https://github.com/catterhu1207-ux/codex-desktop-workflow/releases).

| Component | Status in v0.3.15 |
|---|---|
| Windows x64 | Supported platform |
| Desktop `26.1021.3705.0` | Independent frontend 2.12.1; official backend by default; optional source-built 0.164.0-alpha.11.1.1; 26 contracts and 23 renderer features |
| Desktop `26.1016.8622.0` | Independent frontend 2.11.0; official backend by default; optional pinned source-built 0.163.0-alpha.11.2.1; 26 contracts and 23 renderer checks |
| Desktop `26.1016.8120.0` | Independent frontend 2.10.1; official backend by default; optional source-built 0.163.0-alpha.11.1.1; 26 contracts and 23 renderer checks |
| Desktop `26.1016.6573.0` | Independent frontend 2.9.2; official backend by default; optional pinned compatibility source for 0.163.0-alpha.11.1; 26 contracts and 23 renderer checks |
| Desktop `26.1007.9446.0` | Official backend by default; optional public-source compatibility backend; both modes passed the source/runtime matrix; the final public download passed three fresh profiles, 26 contracts and 23 renderer features |
| Desktop `26.928.4866.0` | Official backend by default; optional source-built 0.159.2 compatibility profile; 25 contracts and 22 renderer proofs; three isolated launch profiles |
| Desktop `26.1002.7124.0` | Retained exact-source profile; its unavailable historical original was not requalified in this run |
| Complete official x64 MSIX | Accepted by PowerShell `-Source`; exact identity and signature required; no Store installation |
| Desktop `26.924.2738.0` | Official and opt-in source-built compatibility backend; frontend 2.7.3 start-event ordering; independent profile and build identity |
| Desktop `26.924.1866.0` | Official and opt-in source-built compatibility backend |
| Codex desktop `26.917.9434.0`, official ASAR `d4234b03eb532fe0f3e9a7d90caad51edb68af45f771cc786d966377e7446f5a` | Supported; executable copied unchanged after exact source and renderer qualification |
| Codex desktop `26.917.6896.0`, official ASAR `00b7936388d11a3faede5fc736a8c6264eb66e1907bac4ef72c39b7399175d68` | Supported; executable copied unchanged |
| Codex desktop `26.915.4065.0`, official ASAR `b8aeb817cd1ee6ef50efe8a97985d3be41de89688a5addfe0a444e1e52348096` | Supported; independently verified by two isolated launches |
| Codex desktop `26.915.3509.0`, official ASAR `8227f6234cf2cc418ec8bbdeedec03f8d777f85520929ff2d9d38e774f681dfd` | Supported; independently verified by two isolated launches |
| Codex desktop `26.908.9136.0`, official ASAR `7a46bd6fe162050afbac27d7d5271d19524e887fa0cdd06c0f2d3fa9b606a31d` | Supported; retained v0.1.0 isolated-renderer acceptance evidence |
| Desktop `26.1013.4894.0` | Unpublished recovery profile retained as source; unavailable to this installer |
| Any other desktop version or ASAR | Rejected |
| Official bundled `codex.exe` | Default for all supported releases |
| `codex-history-compat` backend | Opt-in profile `desktop-26.1021.3705.0-sqlite-v2` (77 migrations), plus retained `desktop-26.1016.8622.0-sqlite-v2` (77 migrations across six databases), plus retained `desktop-26.1016.8120.0-sqlite-v2` (77 migrations across six databases), plus retained `desktop-26.1016.6573.0-sqlite-v2` (77 migrations across six databases), plus retained `desktop-26.1007.9446.0-sqlite-v2` (75 migrations across six databases), plus retained profiles `desktop-26.928.4866.0-sqlite-v2` (73 migrations across six databases), `desktop-26.924.2738.0-sqlite-v2` (72 migrations across six databases) and `0.158.0-alpha.2` for their respective desktop versions; older desktop profiles remain official-only |
| Existing task data | Explicit snapshot import into a new independent directory |
| Automatic task-data synchronization | Unsupported |

A version number alone is insufficient. `inspect` also checks the complete ASAR, bundled backend, and all required ASAR entry hashes for the selected supported version.


## v0.3.15 prerequisites

Python 3.11 or later and Node.js with WebSocket and internal Acorn support are required (Node.js 24.18 tested). Complete signed MSIX and installed-directory sources are accepted. The optional backend profile `desktop-26.1021.3705.0-sqlite-v2` binds public source commit `fabd73f0370b279be6e57c74a14ec53cd6c3c945`, upstream `6905ecede7816e91373e9eabda3f6b0368fc747b`, Rust 1.99.1 and all 77 migrations across six databases. Old release evidence is retained; missing original samples in this run are skips.
