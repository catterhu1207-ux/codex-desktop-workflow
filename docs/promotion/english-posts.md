# English launch copy

## Show HN

Title:

`Show HN: Codex Desktop Workflow – a verified local mod for multitasking`

Body:

> I run many Codex Desktop tasks in parallel and kept losing time deciding which one needed attention next.
>
> `codex-desktop-workflow` is a Windows tool that builds an independent copy from a user-supplied official Codex package. It does not replace or modify the installed app.
>
> The workflow changes three things:
>
> - orders tasks by actual start-time recency, in both initial and live updates;
> - uses yellow for a real pending implementation plan, red for pinned attention, and blue for ordinary unread;
> - exposes human-readable remote project names in the sidebar, search, Work picker, tooltips, and accessibility text.
>
> The installer checks the exact package and hashes, builds a separate copy, and runs two isolated 60-second launches. It compares the official `app.asar` before and after, and the release bundle contains no official binaries.
>
> One command:
>
> `irm https://github.com/catterhu1207-ux/codex-desktop-workflow/releases/latest/download/install.ps1 | iex`
>
> Current support is Windows x64, Codex Desktop `26.915.3509.0`, with `26.908.9136.0` retained. It is an unofficial project and is not affiliated with OpenAI. I would especially value reports from people who run several tasks at once.

## Reddit

Title variants:

- `I built a verified local workflow mod for managing many Codex Desktop tasks`
- `Yellow = waiting for plan approval, red = pinned, blue = unread: a Codex Desktop multitasking mod`

Body:

> After a few tasks, “last updated” stopped answering which task needed me next. I built a small Windows workflow that creates an independent copy of the official Codex Desktop app instead of patching it in place.
>
> It adds start-time ordering, attention colors, and readable remote project names. The existing tasks keep their valid model and reasoning settings.
>
> The installer validates the exact official package, runs two isolated launches with a fresh renderer proof, and never redistributes official binaries. Source and acceptance evidence: `https://github.com/catterhu1207-ux/codex-desktop-workflow`
>
> This is an unofficial community project. Read the subreddit rules before trying it, and let me know which Codex version and Windows build you use.

## X thread

1. `Codex Desktop gets hard to scan when several tasks are running. I built a verified local workflow mod that makes the next action visible.`
2. `Yellow = a real plan is waiting for implementation. Red = pinned attention. Blue = ordinary unread. Loading keeps its spinner.`
3. `Tasks are ordered by actual start-time recency, not by the last message. Initial load and live updates use the same rule.`
4. `The installer builds a separate copy, keeps the official app untouched, checks hashes, and runs two isolated 60-second launches.`
5. `Windows x64, Codex Desktop 26.915.3509.0. One command and source: https://github.com/catterhu1207-ux/codex-desktop-workflow`

## dev.to

Title:

`Making Codex Desktop multitasking readable without replacing the app`

Outline:

1. The problem: task ordering, ambiguous dots, remote project UUIDs, and global model defaults.
2. The design: build a separate copy from a user-supplied official package.
3. The release gate: exact ASAR/backend hashes, two isolated launches, renderer proof, and normal exit.
4. The attention model: plan waiting, pinned, unread, loading, and why yellow wins over pinned red.
5. What is deliberately not included: official binaries, patched backend redistribution, account proxy, or telemetry.
6. How to try it and what feedback is most useful.

## Product Hunt

Tagline:

`Know which Codex Desktop task needs you next.`

Description:

> A verified local workflow mod for Windows Codex Desktop. Start-time ordering, plan-waiting yellow, pinned red, ordinary unread blue, readable remote names, and preserved per-task settings. The official app is not modified, and the release bundle contains no official binaries.

First comment:

> I built this because “last updated” did not answer which one of my many Codex tasks needed attention. The installer keeps the official app untouched and runs two isolated verification launches. I would love feedback from heavy multi-task users, especially on Windows version coverage and first-run setup.
