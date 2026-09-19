# awesome-codex-workflows submission

Target: `shinpr/awesome-codex-workflows`

Suggested issue title:

`Add catterhu1207-ux/codex-desktop-workflow under Codex-Native Workflow Frameworks`

Suggested issue body:

> Repository: https://github.com/catterhu1207-ux/codex-desktop-workflow
>
> Summary: A Windows workflow that builds a verified independent copy of a user-supplied Codex Desktop package, with start-time ordering, attention colors, readable remote project names, and preserved per-task model settings.
>
> Why it is Codex-specific: It consumes exact Codex Desktop ASAR, frontend, protocol, and backend identities; it does not target a generic Electron app.
>
> Workflow evidence: `ACCEPTANCE.md` records two isolated renderer runs with 60 seconds of observation, packaged backend identity, and normal exit. The project refuses unknown versions and hash mismatches.

Suggested data file `data/repos/catterhu1207-ux--codex-desktop-workflow.json`:

```json
{
  "name": "catterhu1207-ux/codex-desktop-workflow",
  "url": "https://github.com/catterhu1207-ux/codex-desktop-workflow",
  "summary": "Builds a verified local Codex Desktop workflow copy with start-time ordering, attention colors, readable remote project names, and preserved per-task model settings.",
  "codex_relation": "primary",
  "category": "Codex-Native Workflow Frameworks",
  "tags": [
    "desktop",
    "windows",
    "multitasking",
    "workflow",
    "quality-gates"
  ],
  "signals": [
    "quality-gates",
    "local-build"
  ],
  "evidence": [
    "README documents exact Codex Desktop version profiles and user-supplied official package inputs.",
    "ACCEPTANCE.md records two isolated 60-second renderer runs and packaged backend identity."
  ],
  "status": "experimental"
}
```
