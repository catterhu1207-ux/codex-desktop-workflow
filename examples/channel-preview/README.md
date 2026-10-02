# Channel preview and Responses diagnostics

This optional example checks a Codex channel before any configuration change. It reads `config.toml`, the selected model catalog, and the local thread index. It does not switch providers, change task bindings, or start Codex. The desktop workflow installer does not install it automatically.

From the repository root on Windows, run:

```powershell
py -3 examples/channel-preview/preview.py --target mimo
py -3 examples/channel-preview/diagnostics.py --target mimo
```

The preview lists changed top-level settings and estimates how many unarchived local tasks belong to another provider. It excludes archived and external tasks. The actual migration set can change before the next safe start; this example does not perform that migration.

The diagnostics command performs local checks by default. Add `--online` to send three minimal Responses requests: text, a function call, and an image where the model catalog advertises image input. These requests may consume your provider allowance. They contain only synthetic test content. A model-list endpoint alone is not considered a compatibility test. Keys are read from Windows user environment variables, never printed or stored in the example's files.

`profiles.json` is a sample configuration. Check each provider endpoint and model against its current official documentation before using an online probe. MiniMax, DeepSeek, GLM, and MiMo use distinct environment-variable names. Kimi in this sample is routed through an external local proxy; without a direct credential variable the online probe reports unavailable.

The current public desktop release does not qualify cross-provider continuation with this example. Use the repository's [compatibility matrix](../../COMPATIBILITY.md) for supported desktop behavior.

[中文说明](README.zh-CN.md)
