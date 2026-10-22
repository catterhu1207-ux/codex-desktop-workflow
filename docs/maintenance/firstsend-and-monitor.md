# First-send and runtime-monitor repair lessons

Use when a chat is created but its first message fails, an application opens while the launcher reports failure, or a new artifact revision fails an existing consumer. These are observed 26.1013.4894.0 cases, not fixed names, counts or deadlines for later versions.

## Native first-send lifecycle

The injected first-turn guard called `_z` as a function. In this package `_z` was an atom; `Ub` was the native last-turn helper. Finding a minified identifier in the new bundle did not establish that its role was unchanged. Resolve the declaration, callers and canonical-history reader in the exact source before reusing a predecessor's binding.

Preserve the unsent-draft guard until an accepted turn ID exists. An optimistic turn can exist with a null ID. Exercise the actual conversation-manager subscription through empty draft, optimistic turn, accepted first turn and completion, for both canonical and retained legacy history shapes. Include eviction, model and reasoning-setting preservation. Put this behavior into the startup renderer proof so a later binding regression is caught before ordinary use.

In isolated UI acceptance, require the acknowledged turn ID, completed status and visible user/assistant content; reopen in a fresh renderer and verify history and settings again. Test ordinary and project chats and the default approval setting. Use a local model simulator for these mechanics. Such a simulator does not prove paid-service connectivity or encrypted SSH transport.

A request may have created the chat before failing to send. Read back that chat and any accepted turn before retrying; do not automatically create a replacement or resend. Absence from one local database is not proof of absence from a remote host or another store.

Debugger-paused diagnostic attempts timed out while later unpaused native UI sends passed. Preserve both outcomes. Check breakpoints, paused state and diagnostic wrappers before another expensive run; do not attribute the original timeout to the debugger without sufficient evidence or weaken application behavior to satisfy a stale fixture.

## App liveness and monitor health

An application can remain open even when the runtime monitor exits before its first heartbeat. Diagnose the monitor's own stderr, native host, path policy and process identity separately from application startup. An open window does not retroactively complete the failed launch transaction.

For isolated acceptance, run the actual monitor against the owned app PID and registered artifact, with a separate manager-state directory. Check the first heartbeat within the launcher's real startup budget, a fresh sample before closing, and normal final classification. Use the producer's actual sample interval and the consumer's bounded wait for the next sample. A test must not impose a shorter tick and misclassify the interval between valid samples as a failure.

The monitor must recognize the registered external artifact root. When advancing the next-launch pointer, retain a validated immutable registration for the still-running prior artifact. Check exact path, revision, executable and archive identity; do not accept arbitrary adjacent manifests or broadly allow an entire drive. Test tampered prior registrations and modified executables.

Repair a monitor in place only within authorized ownership and preserve the running app. Record the original failed transaction, fresh monitor heartbeat and observation separately. Do not synthesize a successful genuine launch from repaired infrastructure alone.

## Revision changes reach every consumer

A corrected candidate passed its frontend tests but the SSH label validator still accepted only the prior revision. Inventory every actual consumer before registration: builder, manifest verifier, renderer parser, SSH validator, runtime path guard, acceptance commit and Prepare. Dispatch supported revisions to their own exact source, artifact and proof contracts; keep historical identities immutable and reject mixed revision tuples.

Run the native shortcut-host consumer and actual Prepare after registration. Preserve pending genuine-launch status and the required later restart. Prepare may refresh shortcut metadata without changing its routing; verify target and arguments, and distinguish route preservation from byte-for-byte shortcut equality.

## Records and closeout

Read persisted receipts after uncertain writes before replaying registration, sending or deletion. Bind evidence to effective source/recipe/fixture/parser identities. New revision records must point to current evidence while retaining prior matrices explicitly as historical.

Retain failed regression output. A version assertion can be stale, but a source-profile mismatch can reveal a real unupdated consumer. Repair the consumer rather than simply loosening the test. Report unittest's run and skip counts separately: class-setup skips may not increment `testsRun`, so subtracting all skips can misstate the number of passing test methods.

Reusing a populated fixture adds synthetic chats. Preserve an explicit supplement inventory; do not reset its database blindly to restore an old exact-count assertion. Retire only closed, proven regenerable caches; preserve compact evidence and all current launch/build dependencies.

Source publication, a tagged installable release, genuine local launch and cleanup are distinct deliverables. A sanitized maintenance guide or source profile can be published with an explicit support boundary; it does not qualify a new installer. A required public build or runtime failure blocks that installer release, not unrelated qualified source publication or cleanup.

## Cold history and visible-page observations

Pinned upstreams can append a `thread_settings_applied` checkpoint when a chat resumes even if no new turn starts. Check the exact upstream branch before treating a changed whole-file digest as history corruption. Preserve the original failed observation. Require every original history byte to remain an identical prefix, and independently verify the appended records, owning thread, saved model, provider and reasoning effort. Reject altered prefixes, foreign checkpoints, global-default replacement and unexpected messages. Never rewrite history to satisfy a test.

A cold-open check must distinguish saved settings from the defaults for a new draft. Test both in a fresh renderer. Merely reopening a chat must preserve activity order; a completed new reply must change recency, including after another restart. Keep manual pin order independent of activity grouping.

Native interfaces can keep hidden pages mounted. Scope active-row and composer observations to the visible page and exact routing identity. A hidden duplicate is not a second active chat. Before testing project-list pagination, leave activity view through its native control, then reach the oldest known synthetic chat with actual Show more clicks. Record the starting view and transitions so a stale test precondition cannot become a claimed application failure.
