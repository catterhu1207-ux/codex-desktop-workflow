# Development and advanced use

[Back to installation](../README.md)

## Optional compatibility backend

The official backend is the installation default. To select history-request compatibility, download the releases `install.ps1` and run:

```powershell
.\install.ps1 -BackendMode compat
```

Source builds require Python 3.11 or later, Git, Rust 1.99.1 for Desktop 26.1016.8120.0 and 26.1016.8622.0 (Rust 1.95.0 for the retained earlier profiles), x64 MSVC and the Windows SDK. Run from the x64 developer environment. Use `-BackendManifest` for an existing matched build or `-DryRun` to inspect mode selection and prerequisites. Supported source profiles are documented in [codex-history-compat](https://github.com/catterhu1207-ux/codex-history-compat).

The directory commands below use supported `26.924.2738.0` as an example; use your actual supported source.

## Manual install and development

Requirements:

- Python 3.11+
- Git
- Your own supported official Codex application directory

Assume the official package is located at:

```text
C:\official\OpenAI.Codex_26.924.2738.0_x64__2p2nqsd0c76g0
```

Install:

```powershell
git clone https://github.com/catterhu1207-ux/codex-desktop-workflow.git
cd codex-desktop-workflow
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
```

### 1. Inspect the official package

```powershell
.\.venv\Scripts\codex-desktop-workflow.exe inspect `
  --source C:\official\OpenAI.Codex_26.924.2738.0_x64__2p2nqsd0c76g0
```

### 2. Build an independent modified copy

The target directory must not already exist:

```powershell
.\.venv\Scripts\codex-desktop-workflow.exe build `
  --source C:\official\OpenAI.Codex_26.924.2738.0_x64__2p2nqsd0c76g0 `
  --target C:\codex-workflow\app
```

### 3. Verify real components and startup behavior

```powershell
.\.venv\Scripts\codex-desktop-workflow.exe verify `
  --source C:\official\OpenAI.Codex_26.924.2738.0_x64__2p2nqsd0c76g0 `
  --portable C:\codex-workflow\app `
  --runs-root C:\codex-workflow\verification
```

The same commands work with the retained `26.908.9136.0` profile when that exact package is supplied.

`verify` requires two launches with the matching packaged `codex.exe` backend, a fresh renderer proof, at least 60 seconds of observation, and a clean normal exit. It never force-terminates user processes.

Isolated acceptance does not copy authentication. In the signed-out environment, the tool briefly mounts the real task renderer to produce proof bound to the current artifact; the UI may then return to sign-in.

See the redacted two-run result in [ACCEPTANCE.md](../ACCEPTANCE.md).

## Import your own task copy

Exit every Codex / ChatGPT desktop and backend process first, then create a separate task-data copy:

```powershell
codex-desktop-workflow import-data `
  --source C:\Users\you\.codex `
  --target C:\codex-workflow\data

codex-desktop-workflow launch `
  --portable C:\codex-workflow\app `
  --data C:\codex-workflow\data `
  --runs-root C:\codex-workflow\daily-runs
```

The import uses SQLite-consistent backups and copies task-record directories.

It excludes:

- `auth.json`
- `config.toml`
- plugins
- skills
- authentication material

Sign in or configure services again inside the independent environment. The official and modified data sets are not automatically synchronized or merged.

Use the returned run directory with `status` and `stop`:

```powershell
codex-desktop-workflow status --run C:\codex-workflow\daily-runs\run-<id>
codex-desktop-workflow stop --run C:\codex-workflow\daily-runs\run-<id>
```

`stop` uses the supported app's own quit action through its local debugging port, then checks the registered main and backend processes again. Identity mismatches and timeouts are reported as blocked; processes are not force-terminated.

## Safety boundaries

- Every build writes to a new target directory; source/target nesting and repeat patching are rejected.
- Unknown versions, hash mismatches, ambiguous transformations, failed contracts, or missing runtime evidence stop the workflow.
- Generated reports contain user-selected local paths; inspect them before sharing.
- Reports do not record task bodies, credentials, or tokens.
- The project does not provide, download, or redistribute official Codex binaries.
- This is an unofficial experimental community project. It is not endorsed by OpenAI and does not replace official updates or support.

## Reusing verified backend build inputs

The optional `CODEX_COMPAT_BUILD_CACHE` points to an existing build-result directory. `CODEX_COMPAT_SOURCE_CACHE` can select its already patched upstream checkout; it requires the build cache. `CODEX_COMPAT_TARGET_CACHE`, `CODEX_COMPAT_RELEASE_TARGET_CACHE` and `CODEX_COMPAT_TOOLCHAIN_ROOT` select existing test, release and Rust directories. The pinned public recipe checks the upstream commit, permitted modifications, dependency lock, compiler and migration bytes before reuse. The 8120 and 8622 recipes can reuse completed module tests only when the full input binding and test-log digest still match; release compilation remains a separate stage. With no cache variables, the installer builds into a new directory using the fixed public revision.

## Run the complete Windows checks

Set `CODEX_WORKFLOW_TEST_SOURCE_8622` to the verified official `resources/app.asar` and `CODEX_WORKFLOW_TEST_APP_8622` to the independent candidate's app directory, then run `python tools/run_tests.py`. The four current native-source checks fail if either input is missing. Supply the corresponding `6573` variables to exercise that retained profile as well. Historical samples that are unavailable are reported as skips.

GitHub uses `python tools/run_tests.py --source-only` to run unit tests and verify the sealed native acceptance record without redistributing official application binaries. That CI selection does not perform fresh native launches. A release also requires the full Windows run, both backend modes, the final installer and downloaded-asset checks.

For 8622, the Windows recipe tests the unchanged compatibility module with real upstream types and locked dependencies. The complete CLI build and runtime replay are separate gates. Linux CI retains the full core test route. Project Pages deploys the Latest published stable tag, so drafts do not advance its download instructions. The first complete CLI build can take hours; cache reuse checks the source, patch, lockfile, toolchain and compiler flags, with runtime acceptance performed separately.
