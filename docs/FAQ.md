# FAQ

## Does this replace the official Codex Desktop app?

No. The workflow builds an independent copy from a user-supplied official package. The official app directory is not modified, and the installer compares the official `app.asar` before and after.

## Does it work with a Store installation?

Yes. On Windows, the installer asks Windows for the installed `OpenAI.Codex` package and uses that directory as the source. It does not write to `WindowsApps`.

## Why does verification take about two minutes?

The release gate starts two isolated copies, observes each for 60 seconds, requires a fresh renderer proof, and closes the copy through the app's own quit action. One successful launch is not enough to claim runtime verification.

## Will I have to sign in again?

Yes. `-MigrateData` copies task data with SQLite-consistent backups but deliberately excludes `auth.json`, `config.toml`, plugins, and skills. Sign in and configure services inside the independent copy.

## Does the release bundle contain Codex binaries?

No. The bundle contains wheels, the installer, documentation, and checksums. It never contains `app.asar`, `codex.exe`, a patched backend, user data, or credentials.

## What happens after a Codex Desktop update?

The exact version and hashes stop matching. Run `inspect` to see the detected version, then wait for a version-matched profile or open an adaptation issue. The tool does not silently patch an unknown build.

## Is this affiliated with OpenAI?

No. It is an unofficial community project. It does not distribute official binaries, proxy accounts, or replace official support.
