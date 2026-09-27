# Real interface illustrations

The images preserve screenshots from the real Desktop 26.924.2738.0 renderer. Captions and legends are placed outside the screenshots. The tasks, responses, timestamps and plan requests are fictional fixtures; no account credentials or paid service are used.

## Time inputs

| Task title in both languages | Chinese meaning | Start | Latest update |
|---|---|---|---|
| Edit docs | 编辑文档 | 09:10 | 10:05 |
| Update API | 更新 API | 09:50 | 09:55 |
| Fix tests | 修复测试 | 10:00 | 10:01 |

The update-time control uses these update timestamps as its synthetic recency input in the unmodified official Recents view. The modified Priority example uses the start timestamps as recency input. They demonstrate the two ordering rules using the same three unpinned tasks; they do not describe every official view's default sorting. The native task titles remain English in both UI languages.

The pinned example is separate. Fix tests and Update API are pinned through the native buttons. Their pin group is separate from Edit docs. A real completed plan event creates a pending implementation request through the renderer's normal producer. Its yellow indicator persists after reading and pinning. A new start moves Edit docs first and an active-status event shows its native spinner. A subsequent ordinary completion clears the pending plan indicator.

## Reproduce

1. Build the official-backend workflow copy with the public CLI and your own supported official source. Keep an unmodified official control copy. Use fresh, independent test homes and browser profiles; retain the daily instance separately.
2. Create only the three fixture tasks above in the isolated data home. Use the `fixture` model provider with a loopback-only endpoint and authentication disabled. Each native session metadata record must include its ID, session ID, timestamp, originator, workspace, source, provider and CLI version. Set the table's synthetic start/update timestamps from the table above. Native `thread/list` with `useStateDbOnly: true` supplies the input JSON. Confirm native `thread/read` succeeds before capturing.
3. Select English or 简体中文 with the actual Settings language picker. Complete onboarding in the isolated profile using synthetic input. Set `ISOLATED_DEBUG_PORT` to that instance's loopback debugging port and `CAPTURE_ASAR_PATH` to its actual `resources/app.asar`. The capture tool hash-gates the supported unmodified or patched ASAR. Node 22+ is required.
4. Run `node capture_real_ui.cjs thread-list.json raw updated en` for the control, or `node capture_real_ui.cjs thread-list.json raw start en states` for the workflow. Repeat with `zh` in a fresh renderer. The default clip captures the sidebar at the acceptance viewport; `CAPTURE_CLIP` can supply another reviewed CDP clip.
5. The tool dispatches ordinary thread, turn, item and status notifications into the production host-message route. Its fixture clock is restored after each event. It never replaces DOM rows or paints status dots. Use the native quit action and verify the owned processes exit.
6. Review every raw PNG for title order, native state, crop and privacy. Run `python generate_demo_assets.py` with Pillow installed. Preserve `raw/` and its checksums; inspect every GIF frame after composition. The animation is one sidebar wide for mobile readability.

The tracked social preview is referenced by Pages metadata. GitHub's repository-level custom social card is a separate setting.

Captured application UI belongs to its respective rights holders. Original capture and composition tooling and captions use the repository's MIT license.
