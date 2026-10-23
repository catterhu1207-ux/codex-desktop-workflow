# FAQ

[Back to installation](../README.md)

## Is my official version supported?

Published v0.3.11 supports the exact official package `26.1016.8622.0` and the retained profiles listed in the compatibility matrix. See the [release compatibility matrix](https://github.com/catterhu1207-ux/codex-desktop-workflow/blob/main/COMPATIBILITY.md) for the supported package numbers. Both version and file identity must match; a newer official package needs its own adapted release.

## Must I install my downloaded MSIX first?

No. Download the release's `install.ps1` and pass a supported complete x64 MSIX with `-Source`. The tool verifies and extracts it independently, without a Store installation. Identical filenames can contain different versions.

## Will this replace my official app or existing chats?

Your official app stays in place. The modified app and its data are independent. Continuing existing chats requires an explicit task-data import; originals remain in place and the two apps subsequently keep separate data, without automatic synchronization or merging. See [data import](DEVELOPMENT.md#import-your-own-task-copy).

## Why do I sign in again?

Task import excludes authentication, service configuration, plugins and skills. Sign in and configure services inside the independent app. Release and acceptance materials use synthetic data; accounts and real chats remain on your machine.

## How long does installation verification take?

Normal installation for the current `26.1016.8622.0` profile runs two isolated launches, each observed for at least 60 seconds of effective awake time. Older profiles retain their version-specific launch matrices. Copying, building, startup and validation take additional time, so total installation exceeds the observation periods. Optional compatibility-source compilation usually takes longer and depends on the machine and cache.

Each run requires real renderer proof, the matching backend and full observation. Suspension is excluded from the effective runtime deadline. Wait for the installer to report completion before using the generated launcher.

## What do orange and yellow mean?

Orange means a question, option picker or permission request needs your input. Yellow means a plan awaits implementation. Orange takes priority when both exist; yellow takes priority over pinned attention. Reading a chat keeps pending requests, and handling them recalculates the indicator.

## Will an unsent blank page survive a restart?

Persistence across restarts is not guaranteed before the first message. Sent chats, identities and valid model settings restore according to their version's contract; large histories load on demand.

## What should I do after an official update?

Compare the new package number with the support matrix. Unknown versions are blocked from activation. Wait for a matching release or [request an adaptation](https://github.com/catterhu1207-ux/codex-desktop-workflow/issues). Include the version and error; keep official binaries out of the report.

## Is the compatibility backend required?

The official backend is the default. Optional compatibility mode is for users who need its specific history-request behavior and requires an independent source build and toolchain. See [advanced use](DEVELOPMENT.md).

## Is this an official OpenAI project?

This is an unaffiliated community project providing build and verification tools. Users supply their own official app package.
