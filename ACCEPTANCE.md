# Acceptance reports

This public report is a redacted summary of the maintainer-side Windows acceptance run. Local paths, process identifiers, ports, logs, credentials, and task data are excluded.


## v0.3.13 release qualification

v0.3.13 corrects the Windows CI test's comparison of short and long paths and updates package version metadata. The application files and browser isolation behavior retain the four qualified v0.3.12 source launches described below. The new v0.3.13 installed wheel passed its separate resource and contract checks.

The complete Windows suite passed 223 tests, including all four current 8622 checks and four checks using the retained official 6573 sample. Seven historical sample groups were skipped because their required inputs were unavailable: 26.915.4065.0, 26.917.6896.0, 26.917.9434.0, 26.924.1866.0, 26.924.2738.0, 26.928.4866.0 and 26.1016.8120.0. The CI-style source-only suite separately passed 215 tests with seven sample-dependent groups skipped; the complete suite supplied the 6573 checks omitted by that selection. The privacy scan covered 464 tracked files and found no issues.

The exact downloaded v0.3.13 bundle passed normal installation with the official backend and the optional backend built from pinned public source. Each mode passed independent empty-home and 400-chat synthetic launches: four new installation runs with 23 renderer proofs, at least 60 awake seconds of observation, the expected backend and normal closure. Shared Chrome registration remained unchanged throughout all four runs. Three installer dry-run selections and downloaded asset checksums passed.


### Project-page publication

The initial Pages job was rejected because release events use a tag reference while the deployment environment permits the main branch. A manual main-branch dispatch then deployed the published v0.3.13 site successfully. Anonymous downloads, checksums, Latest and the project page passed readback.

The website workflow now routes stable-release notifications to a main-branch dispatch. Only that branch's deployment job uses the protected environment; it still selects the latest published stable tag for the site content. The published application tag and installation assets remain unchanged.

## v0.3.12 source and browser isolation qualification

The v0.3.12 source revision keeps the existing Desktop 26.1016.8622.0 frontend and backend identities. The prior 26-contract and 23-feature results remain feature evidence for those unchanged application bytes.

Both backend modes passed new empty-home and 400-chat synthetic launches, four independent source runs in total. Each run produced 23 renderer proofs, preserved the shared Chrome registration throughout startup, observation and closure, ran for at least 60 awake seconds and closed normally. The 26 frontend contracts passed. Empty-home checks covered signed-out onboarding; populated checks covered synthetic history. Existing native first-message, SSH, Work, ordering and settings results remain attributed to the unchanged application bytes tested for the unpublished v0.3.11 draft.

The v0.3.12 tag is retained. Its three required CI runs failed on a test comparing equivalent Windows short and long paths as strings; packaging and asset upload did not run. No v0.3.12 release assets were created.

## v0.3.11 unpublished draft: retained feature evidence

The original tag and draft assets are retained. A later installation check found that an isolated Codex launch could change the signed-in user's Chrome native-host registration. The results below record feature behavior; v0.3.11 did not complete isolated-installation acceptance and was not published.

Desktop 26.1016.8622.0 uses independent frontend 2.11.0. Both the official and newly built compatibility backend passed separate signed-out onboarding and authenticated 400-chat fixture launches. Each qualified launch produced all 23 same-run renderer proofs, matched its actual backend path and ancestry, ran for at least 60 awake seconds, closed normally and left no owned processes. All 26 frontend contracts passed.

Each backend passed six native first-message scenarios, cold reopening with saved task settings, activity ordering and manual pins, 400-chat pagination, fourteen row states with computed-style checks, twelve update-component cases and proof recovery after actual window hiding/restoration. Invalid proof and state variants were rejected. Model-service requests used synthetic loopback fixtures; SSH cases used an isolated synthetic project over encrypted transport.

The compatibility backend passed all 15 unchanged module tests against real upstream types, the complete CLI build and seven runtime groups. The same seven groups passed against the official backend: HTTP, real WebSocket, cold settings, local and remote V2 compaction, 77 migration identities across six database families and 105-turn pagination. Persistent synthetic histories and per-chat settings were preserved.

The v0.3.11 prequalification wheel passed 293 runtime-resource byte checks, all 26 contracts and fourteen packaged row cases. A clean-source reproduction preserved the exact previously accepted official-mode application bytes and retained the original run lineage. Windows checkout tests cover raw resource preservation for current and future versions. The complete Windows suite ran 189 tests without failure; all four mandatory current-source checks and the four available 6573 source checks passed. 7 unavailable historical source samples were reported as skips. Three installer dry-run selections passed. Final downloaded assets and normal installation are verified separately before publication.

## v0.3.10 source and runtime qualification

Desktop 26.1016.8120.0 uses independent frontend 2.10.1. The official backend and the new public-source compatibility backend each passed signed-out onboarding and an authenticated 400-chat fixture in separate launches. All four qualified launches produced 23 same-run renderer proofs, passed 26 frontend contracts, matched the current app-server path and ancestry, remained running for at least 60 awake seconds, closed normally and left no owned processes.

Six actual first-message scenarios passed with each backend: two local projects, a projectless chat, a Work file drop, SSH and Work over SSH. Cold reopening restored all six replies and their saved model, provider and reasoning settings; changed global defaults applied to a new draft. Priority/activity ordering, reply recency across restart and manual pin order passed. Native acceptance also covered 400-chat pagination, fourteen row states with computed styles and negative controls, twelve update-component cases and recovery of all 23 proofs after hiding and restoring the actual window.

The compatibility backend passed 15 Rust module tests, 28 profile/packaging tests and all seven runtime groups. The same seven groups passed against the official backend: HTTP, real WebSocket, cold settings, local and remote V2 compaction, all 77 migration identities across six databases and 105-turn pagination. Tests used synthetic data and loopback model services. SSH interface checks used an isolated synthetic project over encrypted transport.

One initial cold-open checker rejected an upstream settings checkpoint because it compared the entire append-only file. Diagnosis verified the original history bytes and exact pinned upstream resume branch. The corrected check preserves every original byte, validates each appended checkpoint's owner and saved settings, and rejects altered prefixes, foreign owners, changed models and unrequested messages. A fresh cold run passed. The initial failure remains outside the qualified launch matrix. A separate receiver check was corrected to exclude hidden mounted pages from the current visible selection.

Closed logs were read back through the production receiver. Earlier live log copies were retained before the closed snapshots were refreshed; the original logs were unchanged. Fourteen parser cases accepted only the valid same-run proof and rejected thirteen invalid variants. The prequalification wheel preserved all 279 packaged runtime resources and passed actual packaged native-function checks. Three installer dry runs passed.

The complete Windows suite ran 181 tests with no failures. Six unavailable older official samples were explicitly skipped; all four required current-version source checks and all four available previous-version source checks passed.

The exact downloaded v0.3.10 bundle passed normal installation with the official backend and the optional backend built from pinned public source. Each installation passed separate empty and 400-chat launches, all 23 same-run renderer proofs, at least 60 awake seconds of observation, current backend identity and normal closure. The compatibility installation used a byte-verified published Git cache during an HTTPS outage; after its source build completed, the unchanged installer verification and finalization stages resumed following a space-guard stop. Three downloaded-installer dry runs, asset checksums, anonymous downloads, the Latest entry and the project page passed. See [the distribution readback](acceptance/v0.3.10-distribution.json).

## v0.3.9 source and runtime qualification

Desktop 26.1016.6573.0 uses the independent frontend 2.9.2. Both the official backend and the newly built compatibility backend passed two serial isolated launches: signed-out onboarding and an authenticated fixture with 400 synthetic chats. Each launch produced all 23 renderer proofs, matched its actual backend, remained running for at least 60 awake seconds, exited normally and left an empty owned process group. All 26 frontend contracts passed.

Native acceptance covered priority/activity ordering, manual pins, unread and pending-input indicators, Work project selection, file drops, paginated history and distinct update notices. Reading an older chat did not promote it after restart; a completed new reply moved it forward. Fourteen actual row states and three negative controls passed. Six first-message scenarios passed with each backend mode, including Codex and Work over real encrypted SSH to an isolated synthetic project. Cold reopening preserved the six chats and their settings; changing local defaults did not overwrite saved local settings. New drafts used the changed default.

The optional backend was compiled from fixed public inputs at `7cf7c00b0b7ce435e2264c04f5b88e0068e41ae2` and upstream `5425d3e625daa58eea3ad1de27c087eb3b2ffbd3`, using Rust 1.95.0. Its 15 compatibility tests and seven runtime groups passed: ordinary requests, real WebSocket, cold setting recovery, local compaction, remote compaction V2, 77 migrations across six database families, and 105-turn pagination. The official binary provided the request and migration controls. Model responses came from synthetic loopback services.

Test interruptions remain in the private audit trail. A pagination check initially counted a plugin's JSONL fixture as a session; the corrected read resumed the existing 105 completed turns without sending them again. A bounded SSH loopback service expired during one UI turn; restoring that same fixture allowed the existing turn to finish, and independent history/UI readback confirmed completion without another send. Neither event changed application code or real chat data.

The complete signed MSIX, three installer dry-run selections, installed-wheel resources, native resource routes, 14 proof-rejection cases and source privacy checks passed. Six unavailable older official samples are explicitly skipped; their configurations and interfaces remain in regression coverage. Source qualification is bound in [the current record](src/codex_desktop_workflow/policies/qualification-26.1016.6573.0.json). Final normal installation and downloaded-asset results are recorded separately below before publication.

## v0.3.9 normal installation

Normal installation from the complete signed MSIX passed separately with the default official backend and the explicit public-source compatibility backend. Each installed package completed an empty-home run and a 400-chat synthetic run, with 23 fresh renderer proofs, at least 60 awake seconds, matching backend identity, normal exit and no pending elevation request. Native cold history remained byte-identical. The public compatibility build entry validated its fixed inputs and reused the qualified warm build cache. All 164 unit/regression checks completed without failure; six unavailable historical source samples remain explicit skips.

The initial installer fixture omitted the upstream unelevated setting and left a system setup request. That failed attempt remains in the audit trail. The correction is confined to disposable test homes and separately bound in the source qualification; original native artifact evidence is preserved. Fresh normal installations passed after the correction. See [the local installation record](acceptance/v0.3.9-local-install.json). Downloaded draft assets must pass the separate distribution check before publication.

## v0.3.9 downloaded distribution

The actual GitHub draft bundle passed both normal installation paths before publication: default official backend and explicit compatibility backend built from the pinned public source. Each mode passed a signed-out onboarding run and a 400-chat synthetic run with all 23 fresh renderer proofs, at least 60 awake seconds, matching backend identity, normal exit and no pending elevation request. The installed runtime independently read back its qualification, and cold synthetic history remained unchanged.

The compatibility installation continued in two phases: its public-source build completed, then the disk guard paused the application copy before any runtime test. After verified disposable copies were removed, the same installation resumed using its own completed, identity-checked build manifest. Both subsequent runtime checks were fresh; the interrupted copy is not counted as a successful installation.

All three downloaded-installer dry runs passed. The bundle's 295 packaged files, dependency resources, checksums and sensitive-content scan passed. After publication, anonymous downloads of the bundle, installer and checksum file matched the accepted draft, Latest resolved to v0.3.9, and the project page displayed the current version and installer link. The backend v0.2.5 release passed its separate anonymous readback. See [the distribution record](acceptance/v0.3.9-distribution.json).

## v0.3.8 source and installed-wheel qualification

Six isolated native runs passed with artifact 2.7.21: three with the official backend and three with the public-source compatibility backend. Every run mounted the native sidebar, produced 23 same-run interface proofs and observed at least 60 awake seconds. The actual English update component, six-chat cold recovery, 13 production-parser cases and four directory/MSIX dry runs passed.

A stale per-feature identity annotation was caught before publication. The actual producer rebuilt it from the current profile; executable, ASAR, backend and protocol bytes remained identical. The production parser accepted all six unchanged original run logs against the corrected metadata. Original receipts are preserved. This annotation reconciliation does not claim additional runtime runs.

Normal installation from the rebuilt wheel then passed all three profiles again and created its launch command. The installed package ran independently of the source checkout. Across the nine runs, all 26 feature contracts and 23 interface proofs were checked against the exact current artifact.

The compatibility backend is unchanged from the public-source v0.3.6 build. Its recorded transport and migration tests are reused after identity readback; current runtime identity was verified again. External SSH bindings were synthetic; encrypted SSH transport and real-account migration were not tested. All 132 unit/regression tests completed without failure, including six explicitly skipped historical-original inputs. The published assets passed anonymous download and checksum verification. Normal installation from that download passed the three complete profiles again, each with 23 fresh interface proofs, a mounted native sidebar, at least 60 awake seconds, matching backend identity and normal closure. See [the distribution readback](acceptance/v0.3.8-distribution.json).

## v0.3.7 source and installed-wheel qualification (unpublished draft)

Desktop 26.1007.9446.0 uses frontend artifact 2.7.20. New independent data defaults to English while existing preferences are preserved. The actual native update component passed announcement, available-package and adaptation-ready cases, including English labels, descriptions, accessibility labels and three distinct collapsed icons.

The frozen public executable sources passed three complete profiles with the official backend and three with the unchanged public-source compatibility backend. A normal offline wheel installation with `-NoShortcut` then passed all three profiles again and created its launch command. Each matrix covered empty data, at least 400 conversations created and sent through the actual backend, and native project/settings fixtures. Every round produced 23 fresh same-run interface proofs, mounted the native sidebar, observed at least 60 awake seconds, rechecked the backend and closed normally. The 26 feature contracts, six local/Work/simulated-SSH first sends, cold per-chat model recovery and production-parser rejection cases passed.

The compatibility binary and its source, recipe, dependency and migration identities are unchanged from v0.3.6. Its HTTP, WebSocket, compaction and 75-migration/six-database evidence is reused with explicit provenance; those transport tests were not rerun for this UI-only change. Current backend identity and migration checks were repeated. SSH service bindings remained synthetic; encrypted SSH transport and real-account migration were not tested.

All 131 source tests completed without failure, with six unavailable historical-original inputs recorded as skips. Directory and signed full-MSIX installer dry runs passed for both backend modes without Store installation or full extraction. The unchanged full-MSIX extraction/installation path retains its separately recorded v0.3.6 evidence; this release's fresh normal installation used the identical verified extracted source.

One outer supervision run found a signed, owned Windows console auxiliary after the inner compatibility matrix had closed successfully. The supervisor stopped its own group; the original failed terminal was preserved. Process absence, the exact OS image, unchanged candidate/code bindings and all three closed proofs were independently read back before reusing the functional results. The task monitor subsequently passed real Job tests for bounded natural child teardown and rejection of persistent descendants.

Final release download and fresh installation are recorded separately after publication.


## v0.3.6 source qualification

The Windows x64 Desktop 26.1007.9446.0 source was rebuilt independently with the official backend and the public-source compatibility backend. Both modes passed normal complete-MSIX installation with the installed wheel and three isolated launch profiles: empty data, at least 400 conversations actually created and sent through the backend, and persisted project/settings fixtures. Each profile mounted the native sidebar, produced all 23 same-run interface proofs, observed at least 60 awake seconds, rechecked backend identity and closed its owned process group. Exact-resource checks found no pending sandbox elevation requests.

The 26 contracts cover descending update-time sorting, manual and pinned behavior, native pending questions and approvals, yellow plans, SSH names and routing, Work selection, file drop, paginated history, per-chat models and distinct persistent update states. Local, Work and simulated SSH first sends use the actual native execution and canonical history consumers. External SSH service bindings are synthetic; encrypted SSH transport is not qualified by these checks.

The optional backend was independently built from public commit `a47c618b5b2b9e4438a8208decdada12935fd78f`, with Rust 1.95.0. HTTP, WebSocket, cold model restoration, local and remote compaction, tool-output pairing, notification folding and 75 migration identities across six databases passed. A verified warm-cache build through the public command produced the identical binary.

The unit/regression run completed 122 checks without failure, with six missing-original-sample skips recorded separately. Two additional actual-expression awake-clock checks and both source-qualification checks passed, for 126 checks in total. The final distribution download/install readback is tracked separately. Older runtime acceptance records below remain historical evidence; they are not reruns of this candidate.

The published v0.3.6 assets passed anonymous download and checksum verification. Normal installation from that download into a fresh directory then passed all three profiles with 23 fresh interface proofs, at least 60 awake seconds, matching backend identity, normal application exit and empty owned groups. Removing the isolated application and Python environment preserved all 26 files in its synthetic data-retention fixture. Real account migration was not exercised. See [the distribution readback](acceptance/v0.3.6-distribution.json).

## v0.3.5 qualification

Desktop 26.928.4866.0 was independently built with both official and compatibility backends. The qualified source record binds the runtime results to the product and acceptance tools. Final distribution and installation from the public download are checked separately.

The Windows process-ancestry and awake-clock repairs passed their regression checks. A complete MSIX installation then passed all three launch profiles using the installed package. Compatibility-backend qualification also passed. The published v0.3.5 bundle passed anonymous download, checksum matching and installation into a fresh directory, followed by three complete launches.

| Check | Current result |
|---|---|
| Windows test suite | 110 tests ran successfully, including three skipped older-sample checks; exact 26.924.1866.0, 26.924.2738.0 and 26.928.4866.0 checks ran |
| Exact frontend contracts | 25 passed, including pending-user orange and existing feature regressions |
| Official-backend full launches | Empty data, 400 synthetic tasks, and synthetic projects/settings passed with 22 fresh renderer features and at least 60 seconds of observation each |
| Native sidebar | Actual sidebar and persisted setting reads exercised; the previous wrong-scope setting read is rejected |
| New-chat lifecycle | Six synthetic local, Work and SSH-host chats passed first send, cold backend recovery and native interface reopening; matching backend identity and normal exit were checked |
| SSH boundary | Native host selection, names, paths and conversation identity exercised with local service bindings; encrypted SSH transport was not tested |
| Proof parser | Three actual logs accepted; 15 mutated or stale proofs rejected |
| Awake-time checks | Paused-clock, invalid-clock, output-drain, concurrent clock reading/writing and incomplete-sample tests passed; full launches repeated after the clock repair |
| Test cleanup | Official-mode launch, reopen and complete installer groups exited without retained test descendants; a naturally exiting process is accepted only after a fresh ownership check |
| Previous release regression | Both official and compatibility backends for 26.924.2738.0 passed two full launches each; exact 26.924.1866.0 and 26.924.2738.0 contract checks passed |
| MSIX input | Signature, identity, archive boundaries, cache reuse and changed-source rejection checked; complete MSIX installation passed three launch profiles and installed source/resource matching |
| New compatibility backend | Independent source build, HTTP, WebSocket, cold restoration, local and remote compaction, and 73 migration checks across six databases passed; 17 profile regression tests passed |
| Compatibility full launches | Empty data, 400 synthetic tasks and synthetic projects/settings passed with 22 fresh renderer features, at least 60 seconds of observation, matching backend identity and normal exit each |
| Distribution | Published v0.3.5 assets and checksums verified without authentication; product and dependency modules matched the qualified bundle; installation from the downloaded bundle passed three full launch profiles |

The new-chat repair addresses premature history recovery before the first message creates a saved conversation. A separate placement-format response was examined using recorded errors and the original resolver functions. That comparison does not establish a cloud-service repair. Unsent blank-page persistence is outside the restart guarantee; sent conversation history and model settings are covered.

The distribution readback is recorded in [v0.3.5-distribution.json](acceptance/v0.3.5-distribution.json). The v0.3.4 tag remains as an unpublished attempt after its timer-throughput test failed on a slower CI runner. The replacement test checks actual concurrent reads and distinct clock updates at both fast and slow timer intervals. Application patches are unchanged.

## v0.3.3 qualification

Desktop 26.924.2738.0 was independently built from the verified official source with frontend 2.7.3 and both backend modes on 2026-09-28.

| Check | Result |
|---|---|
| Exact frontend contracts | All 24 passed in both builds |
| Fresh real renderer proof | All 21 features passed in four independent launches |
| Windows tests | 78 passed; two older-sample test classes skipped; required 2738 and previous 1866 checks ran |
| Older artifact regression | Exact 26.917.9434.0 checks also passed |
| Official backend | Empty and 400-task launches, 67.30 and 69.11 seconds after proof; matching current app-server and normal exit |
| Compatibility backend | Empty and 400-task launches, 73.44 and 69.95 seconds after proof; matching current app-server and normal exit |
| Real composer to sidebar | Official 281.4 ms; compatibility 166.3 ms; each followed by more than 70 seconds of stable observation |
| Native ordering matrix | Real starts passed within a project, across projects, in the flat list and in pinned automatic/manual modes; each change within two seconds |
| Attention regression | Synthetic protocol plan/completion events exercised the real rows, including yellow plans after reading and pinning, pinned attention and ordinary unread |
| New-chat identity | Additional compatibility-mode native new chat retained a stable sidebar alias, mapped to the physical task and passed native pin readback |
| Cold recovery | Both modes retained project order, task settings and start times after normal exit; the compatibility cold-resume fixture kept its loopback provider available |
| Backend source | Existing immutable v0.2.2 reference retained; all 72 migration digests across six databases validated |
| Source isolation | Independent Windows user folders and runtime caches; daily instance and real data excluded |
| Executable | Only the unique embedded ASAR digest changed in the independent copy |
| Wheel and installer | Installed-wheel source binding and all 24 contracts passed in both modes; official, compatibility-manifest and compatibility-source dry-runs passed |
| Publication scan | Source and three wheels passed sensitive-content checks |
| Illustrations | Preserved native before/after screenshots; two frames per caption language; unchanged native crop and external captions |

The source-bound qualification record includes the real-start measurements and native matrix. Historical v0.3.2 evidence remains in this directory and at its original release.

## Historical v0.3.2 qualification

The 26.924.2738.0 workflow was independently built from the complete signed official Windows x64 package and qualified with both backend modes on 2026-09-27.

| Item | Result |
|---|---|
| Official ASAR | `89fba67324ffb8dd54ccf13b6f097172e697549eeb1f26396f86f972c10c5b0c` |
| Official backend | `8f0554ede25bbc5450921897c468b2e84635aa513c5017457997af0954581f49` |
| Compatibility source | Profile `desktop-26.924.2738.0-sqlite-v2`, upstream `0d9c7cbfa6cf1489f55a8a9542b75ddd2c061807`; immutable public source reference in `backend-source-26.924.2738.0.json` |
| Frontend contracts | All 24 passed in each mode |
| Real renderer proof | All 21 features passed in all four independent launches |
| Official mode | Empty data and 400 synthetic tasks; 64.95 and 64.53 seconds after proof; matching current app-server; normal exit |
| Compatibility mode | Empty data and 400 synthetic tasks; 65.19 and 66.69 seconds after proof; matching current app-server; normal exit |
| Test isolation | Windows user folders and the primary-runtime cache were isolated in all four runs; the actual runtime-selection logs confirmed each cache path |
| Desktop executable | Unique embedded ASAR digest synchronized in the copy; every other executable byte unchanged |
| Public tests | 77 tests passed; two additional older-artifact test classes skipped because their exact samples were unavailable |
| Previous-version regression | Exact 26.924.1866.0 contracts and protocol patch output passed; old profiles and source pins unchanged |
| Database fixture | All six databases included; 400 visible tasks with native-readable metadata; additional native full-history reads passed for 400 tasks in each backend |
| Wheel and installer | Installed-wheel source binding and all 24 contracts passed in both modes; official, compatibility-manifest and compatibility-source dry-runs passed |
| Publication scan | Source and three wheels passed sensitive-content checks |
| Illustrations | Eleven real, preserved screenshots; English five-frame and Chinese four-frame animations; native pin/read/plan/running states, pixel-preservation checks and mobile-sized single-sidebar frames passed |
| Historical data | Logical-parent and physical-ancestor chains, ownership, byte boundaries, dependency changes and path escape checks passed; source preservation and independent imported copy passed |
| Wheel and installer | Resource loading, bundle checksums, official dry-run, compatibility-manifest dry-run and compatibility-source dry-run passed |
| Publication scan | Public source, wheel, release notes and bundle passed sensitive-content checks |

New-version checks were not skipped. `qualification-26.924.2738.0.json` binds the current shipped source to these runtime results. Earlier qualification records remain attached to their original releases. The backend acceptance report covers 15 module tests, ordinary HTTP and real WebSocket replay, local compaction, remote compaction V2, cold task restoration and all 72 migration checksums across six databases.

## Historical v0.3.1 qualification

The 26.924.2738.0 workflow was independently built from the complete signed official Windows x64 package and qualified with both backend modes on 2026-09-27.

| Item | Result |
|---|---|
| Official ASAR | `89fba67324ffb8dd54ccf13b6f097172e697549eeb1f26396f86f972c10c5b0c` |
| Official backend | `8f0554ede25bbc5450921897c468b2e84635aa513c5017457997af0954581f49` |
| Compatibility source | Profile `desktop-26.924.2738.0`, upstream `0d9c7cbfa6cf1489f55a8a9542b75ddd2c061807`; immutable public source reference in `backend-source-26.924.2738.0.json` |
| Frontend contracts | All 24 passed in each mode |
| Real renderer proof | All 21 features passed in all four independent launches |
| Official mode | Empty data and 400 synthetic tasks; 66.36 and 66.00 seconds after proof; matching current app-server; normal exit |
| Compatibility mode | Empty data and 400 synthetic tasks; 66.22 and 63.50 seconds after proof; matching current app-server; normal exit |
| Test isolation | Windows user folders and the primary-runtime cache were isolated in all four runs; the actual runtime-selection logs confirmed each cache path |
| Desktop executable | Unique embedded ASAR digest synchronized in the copy; every other executable byte unchanged |
| Public tests | 74 tests passed; two additional older-artifact test classes skipped because their exact samples were unavailable |
| Previous-version regression | Exact 26.924.1866.0 contracts and protocol patch output passed; old profiles and source pins unchanged |
| Historical data | Logical-parent and physical-ancestor chains, ownership, byte boundaries, dependency changes and path escape checks passed; source preservation and independent imported copy passed |
| Wheel and installer | Resource loading, bundle checksums, official dry-run, compatibility-manifest dry-run and compatibility-source dry-run passed |
| Publication scan | Public source, wheel, release notes and bundle passed sensitive-content checks |

New-version checks were not skipped. `qualification-26.924.2738.0.json` binds the current shipped source to these runtime results. Earlier qualification records remain attached to their original releases. The backend acceptance report covers 15 module tests, ordinary HTTP and real WebSocket replay, local compaction, remote compaction V2, cold task restoration and all 57 migration checksums.

## v0.3.0 qualification

The 26.924.1866.0 public workflow was built from the exact official Windows package and qualified with both backend modes on 2026-09-26.

| Item | Result |
|---|---|
| Official ASAR | `96b6aa6e1ea46dd8a30b3fa5166be12284ba66bd3901241a81a60684f150189d` |
| Official backend | `0122378c15dc0c3c0af0d6addf2dd278125c19676b41fadaa520f89d2c9e0079` |
| Public-source compatibility backend | Profile `0.158.0-alpha.2`, upstream `10382da79a2a2d6e8ae221fa63077215389c1ad2`; immutable compatibility source reference recorded in `backend-source.json` |
| Exact frontend contracts | 24 passed for each backend mode |
| Real renderer feature inventory | All 21 features passed in all four independent launches |
| Official backend launches | Empty data and 400 synthetic tasks; 64.84 and 65.52 seconds observed after proof; matching current app-server; normal exit |
| Compatibility backend launches | Empty data and 400 synthetic tasks; 66.38 and 67.80 seconds observed after proof; matching current app-server; normal exit |
| Desktop executable | Unique embedded ASAR digest updated in the independent copy; all other bytes unchanged |
| Public tests | 68 run, 66 passed; two older official-artifact tests skipped because their exact samples were unavailable |
| Wheel and installer | Installed wheel resources, bundle contents and checksums passed; official, compatibility-manifest and compatibility-source dry-runs passed |
| Publication scan | Source, wheels and bundle passed the sensitive-file and identifier scan |
| History import | Indirect logical parent and physical ancestor chain verified; original bytes and source database preserved; imported copy remained usable after the source directory was moved |
| History rejection tests | Cycles, missing segments, wrong ownership, boundaries, changed dependencies and escaping paths rejected |

The required new-version checks were not skipped. The source-bound qualification record is packaged as `qualification-26.924.1866.0.json`. The compatibility backend's separate acceptance report covers 15 module tests, HTTP and WebSocket image-tool replay, local and remote V2 compaction, cold restoration and all 57 database migration checksums.

## v0.2.4 qualification

The 26.917.9434.0 public workflow was built from the exact official Windows package with its unchanged bundled backend and independently qualified on 2026-09-25.

| Item | Result |
|---|---|
| Official ASAR | `d4234b03eb532fe0f3e9a7d90caad51edb68af45f771cc786d966377e7446f5a` |
| Generated ASAR | `3d49514032ec8ffa9e39566082a5b691ffb1f4595f335811828e18fafc749a58` |
| Unchanged official backend | `9015c47d1714294ecd9033c4b5aefc3076797d867d1c36aa37749fcb76c8942f` |
| Desktop executable | Copied byte-identically; no matching embedded ASAR-header digest record in the official executable |
| Exact frontend contracts | 24 passed; validator `2.4.10` |
| Real renderer feature inventory | 21 passed per isolated launch; artifact `2.6.13-d4234b03eb53` |
| Public tests with the exact current artifact | 32 run, 30 passed, two older-version artifact tests skipped because their local artifacts were unavailable |
| Wheel and installer | Version `0.2.4` wheel contains the profile, scenarios, and official-backend policy; installed-wheel resource loading and local-bundle installer dry-run passed |
| Two isolated renderer launches | Both passed; 90 seconds observed each; matching official backend, fresh renderer proof, and normal close |
| Qualification stage | `isolated_renderer_qualified`; daily-user validation is separate |

The renderer checks covered plan and pinned indicator precedence through the mounted row, task and project ordering, remote project labels and routing, the Work picker, file drop, and history behavior with synthetic data. Existing version profiles and their release identities remain registered.

## v0.2.3 qualification

The 26.917.6896.0 public workflow was built from the exact official Windows package and independently checked with its unchanged bundled backend on 2026-09-23.

| Item | Result |
|---|---|
| Official ASAR | `00b7936388d11a3faede5fc736a8c6264eb66e1907bac4ef72c39b7399175d68` |
| Generated ASAR | `a6ee404ee47a92244d5c2581a792fe9739400c342d7d9690e979f5ebc01e0ab0` |
| Unchanged official backend | `97d4d67419d0ac2f71342f9a5e850f9468aa622618de8ea823223edb9a91926a` |
| Desktop executable | Copied byte-identically; the official executable contained no matching embedded ASAR-header digest record |
| Public tests with explicit current artifact | 31 run, 30 passed, one older-version artifact test skipped because its local artifact was unavailable |
| Two isolated renderer launches | Both passed; 90 seconds observed each; matching official backend; fresh renderer proof; both closed normally |
| Qualification stage | `isolated_renderer_qualified`; daily-user validation remains separate |

The current renderer checks exercised plan and pinned indicator precedence, task and project ordering, remote project labels and routes, the Work picker, file drop, and history behavior with synthetic data. The initial public acceptance attempt exposed an inconsistent synthetic project name in the renderer probe. That fixture was corrected and a new artifact was built before the two passing launches; the failed attempt is not counted as a pass.

## v0.2.2 qualification

The 26.915.4065.0 public workflow was independently built and checked with the unchanged official backend on 2026-09-19.

| Item | Result |
|---|---|
| Official ASAR | `b8aeb817cd1ee6ef50efe8a97985d3be41de89688a5addfe0a444e1e52348096` |
| Generated ASAR | `fa8ce965d63650cf8f67922280f15f053c334a031f0d51e0b8800c1a0ca8641e` |
| Unchanged official backend | `bc45017e8239dc150258f69309ced9df6bbcdf5b8e4f346decf780ac0999e226` |
| Public tests, with explicit local artifact | 38 passed, zero skipped, zero failed |
| Two independent renderer launches | Both passed; 60 seconds observed each; fresh proof for `2.6.11-b8aeb817cd1e`; matching official backend; both closed normally |
| Authentication or real task data in public acceptance | None |
| Qualification stage | `isolated_renderer_qualified`; daily-user validation remains separate |

The first public acceptance attempt exposed a startup navigation race: the harness navigated before Electron completed initial loading, causing `ERR_ABORTED`. The harness now waits for the complete document and renderer bridge, defers navigation, and checks the actual evaluation result. Regression tests cover the not-ready state and unsuccessful evaluation responses. The failed run is not counted as one of the two passing runs.

### Supplemental private-maintenance check (separate scope)

The maintainer's broader suite originally ran 566 checks: 466 passed, 100 skipped, none failed. The skipped task-binding integration check was supplied with an isolated fixture and passed. Combined coverage is therefore 467 passed, 99 skipped, none failed. The remaining skips concern unavailable historical inputs or a superseded patch; they are not counted as passes.

Two additional cold `app-server` resumes exercised the locally patched, version-matched backend through `initialize`, `thread/resume` and `thread/turns/list`: a preserved task binding survived a different global default, and a subsequent explicit binding change in the shadow database survived another cold resume. Neither call supplied a model/provider override. These checks sent no generation request and left the original task history unchanged. The backend appended two settings events only to the shadow history; the original 43-record prefix was preserved.

This supplemental evidence applies to the maintainer's patched backend, not to the official-backend combination distributed here. It does not turn the public `codex-history-compat` integration into a supported combination, or establish daily-user `live_validated` status. Private fixtures and raw logs are excluded.

## v0.2.0 result

`v0.2.1` changes distribution, installer, and documentation only. The launcher artifact hashes and two-run runtime evidence below remain the retained version-bound acceptance record for 26.915.3509.0.

| Item | Result |
|---|---|
| Release target | Windows x64, Codex desktop `26.915.3509.0` |
| Official `app.asar` identity | `8227f6234cf2cc418ec8bbdeedec03f8d777f85520929ff2d9d38e774f681dfd` |
| Official `codex.exe` identity | `ff9bc3ddc08fa52b43ea170be5f628ffad1c1d9c80c5770b8e2a2f817a9ee3c9` |
| Generated `app.asar` identity | `17f443796846f12ec46f505a80a5f7cc3644d56420733e6f35f9f4ddfe7f636f` |
| Package and source gates | Passed |
| Actual bundled JavaScript contracts | Passed |
| Isolated renderer run 1 | Passed; 60 seconds observed; fresh renderer proof; packaged official backend matched by path and file identity; main and backend exited normally |
| Isolated renderer run 2 | Passed; 60 seconds observed; fresh renderer proof; packaged official backend matched by path and file identity; main and backend exited normally |
| Official bundled backend combination | Passed |
| `codex-history-compat` backend combination | Skipped and unsupported in v0.2.x |
| Real task content or credentials used | No |
| Force termination used | No |

### Verified behavior

- Priority recency ordering for ordinary and pinned items, including live refresh.
- Loading spinner, planned yellow, pinned red, and unread blue; planned yellow wins when an item is also pinned.
- A real pending-request object is required for the planned state; a display scalar alone is rejected.
- Remote project names are visible in the relevant pickers while route identity remains unchanged.
- The package contracts for preserving valid per-task model and reasoning settings passed.
- Each run produced a fresh renderer attestation tied to `2.6.10-8227f6234cf2` and closed through the application-owned quit action.

## Retained v0.1.0 result

| Item | Result |
|---|---|
| Release target | Windows x64, Codex desktop `26.908.9136.0` |
| Official `app.asar` identity | `7a46bd6fe162050afbac27d7d5271d19524e887fa0cdd06c0f2d3fa9b606a31d` |
| Generated `app.asar` identity | `304ada38ece9df561a7da99fe81f484b0da08baef127db8cc85705e62a2a2ce1` |
| Two isolated renderer runs | Passed; 60 seconds observed each; fresh renderer proof; normal exit |
| Official bundled backend combination | Passed |

## Scope

The isolated runs used synthetic data and did not copy authentication. The test route mounted the real task renderer long enough to produce the artifact-bound proof; an unauthenticated session may subsequently return to the sign-in screen. This establishes isolated renderer qualification, not validation of a user's daily environment or external services.

Earlier diagnostic attempts exposed shell-folder and normal-exit handling defects. Those attempts were retained locally as failure evidence, and the defects were fixed before the two reported runs. No failed attempt is counted as a pass.
