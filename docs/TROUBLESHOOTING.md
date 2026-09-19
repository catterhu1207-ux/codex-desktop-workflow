# Troubleshooting

## `inspect` reports `unsupported_version`

The installed Codex Desktop build does not have an exact supported profile. Record the detected version from the JSON output and open an adaptation issue. Do not bypass the hash gate.

## `official_asar_sha256_mismatch`

The package version looks supported, but the bytes are different. Reinstall or update the official package from the official source, then run `inspect` again.

## Python is missing

Run the installer with `-InstallPython`, or install Python 3.10+ and run the same command again. The installer never installs anything silently.

## The target directory already exists

Choose a new `-Target`, or remove the old independent copy explicitly after confirming which directory it is. The installer refuses to overwrite a build.

## Verification fails

Read the verification JSON written inside the portable artifact. A timeout, missing renderer proof, or backend identity mismatch is a real release blocker. Keep the failed evidence and open an issue with the redacted error code.

## `-MigrateData` is blocked

Close every ChatGPT and codex process first. The migration uses a separate target and never writes into the live `.codex` directory.

## I need a clean reinstall

Keep the official app untouched. Choose a new `-InstallRoot` and run the installer again; the old independent copy remains available for inspection until you remove it deliberately.
