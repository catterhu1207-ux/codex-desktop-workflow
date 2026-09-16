# codex-desktop-workflow

**This is the local build entry point for applying the workflow mod to Codex desktop.** Supply your own supported official Codex application directory. The tool creates an independent modified copy, validates the real bundled components, and performs two isolated launches to prove that the result starts and exits cleanly.

[中文说明](README.md)

## Why did I build it?

When I work on many Codex tasks in parallel, the official Priority view does not accurately express what I need to look at next. A task that just started, one waiting for implementation, one I pinned, and an ordinary unread message place different demands on human attention. Internal IDs for remote projects and a global default model replacing an established task setting also break the context of parallel work.

I changed the desktop workflow and turned adaptation after each official update into an evidence-based process. This repository is the usable entry point: it reads the user's own official installation and creates the modified copy locally. It does not provide or download official binaries.

## What does the generated copy change?

| Practical problem | Modified behavior |
|---|---|
| Priority order does not reflect current work | Sort by actual task or process start-time recency, using the same rule for initial loading and live updates. |
| A status dot does not describe the next action | Pending implementation is yellow, pinned attention is red, and ordinary unread state is blue. Yellow wins when planned and pinned; loading keeps its spinner. |
| Remote projects display internal IDs | Sidebar, search, Work picker, prompts, and accessibility text use a recognizable name while routing identity remains unchanged. |
| A global model default changes the context of parallel tasks | Existing tasks retain valid model and reasoning settings; the global default applies to new tasks. |

## Supported first release

- Windows x64.
- Codex desktop `26.908.9136.0`.
- Official `app.asar` SHA-256 `7a46bd6fe162050afbac27d7d5271d19524e887fa0cdd06c0f2d3fa9b606a31d`.
- The official bundled `codex.exe` remains the default backend.

The tool checks the version, whole ASAR, backend, and four relevant entries. A matching version number with different bytes is rejected. See [COMPATIBILITY.md](COMPATIBILITY.md).

The cross-provider backend source patch is available in [codex-history-compat](https://github.com/catterhu1207-ux/codex-history-compat), but that desktop combination has not completed independent qualification and is therefore unsupported in `v0.1.0`.

## Shortest path

Python 3.10+, Git, and a user-supplied official application directory are required.

```powershell
git clone https://github.com/catterhu1207-ux/codex-desktop-workflow.git
cd codex-desktop-workflow
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .

.\.venv\Scripts\codex-desktop-workflow.exe inspect `
  --source C:\official\OpenAI.Codex_26.908.9136.0_x64__2p2nqsd0c76g0

.\.venv\Scripts\codex-desktop-workflow.exe build `
  --source C:\official\OpenAI.Codex_26.908.9136.0_x64__2p2nqsd0c76g0 `
  --target C:\codex-workflow\app

.\.venv\Scripts\codex-desktop-workflow.exe verify `
  --source C:\official\OpenAI.Codex_26.908.9136.0_x64__2p2nqsd0c76g0 `
  --portable C:\codex-workflow\app `
  --runs-root C:\codex-workflow\verification
```

`verify` requires two launches with the matching `codex.exe` descendant, a fresh renderer proof, at least 60 seconds of observation, and a clean normal exit. It never force-terminates user processes.

Isolated acceptance does not copy authentication. In the signed-out environment, the tool briefly mounts the real task renderer to produce proof bound to the current artifact; the UI may then return to sign-in. See the redacted two-run result in [ACCEPTANCE.md](ACCEPTANCE.md).

## Import an independent copy of existing tasks

Exit every Codex/ChatGPT desktop and backend process first, then run:

```powershell
codex-desktop-workflow import-data --source C:\Users\you\.codex --target C:\codex-workflow\data
codex-desktop-workflow launch --portable C:\codex-workflow\app --data C:\codex-workflow\data --runs-root C:\codex-workflow\daily-runs
```

The import uses SQLite backups and copies task-record directories. It excludes `auth.json`, `config.toml`, plugins, skills, and authentication material. Sign in or configure services again inside the independent environment. The official and modified data sets are not automatically synchronized or merged.

Use the returned run directory with `status` and `stop`. Builds always use a new target directory, and unknown versions, hash mismatches, ambiguous transformations, failed contracts, or missing runtime evidence stop the workflow.

`stop` uses the supported app's own quit action through its local debugging port, then checks the registered main and backend processes again. Identity mismatches and timeouts are reported as blocked; processes are not force-terminated.

This is an unofficial experimental community project and is not endorsed by OpenAI. Generic staging and process management are pinned to [electron-update-safety v0.1.3](https://github.com/catterhu1207-ux/electron-update-safety/releases/tag/v0.1.3); lifecycle evidence stages come from [desktop-adaptation-lab v0.1.0](https://github.com/catterhu1207-ux/desktop-adaptation-lab/releases/tag/v0.1.0).
