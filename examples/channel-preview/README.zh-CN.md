# 渠道预览与 Responses 接入诊断

这个可选示例用于在修改 Codex 配置前查看目标渠道。它只读取 `config.toml`、模型目录和本地任务索引，不切换渠道、不修改任务绑定，也不启动应用。桌面工作流安装程序不会自动安装此示例。

在仓库根目录运行：

```powershell
py -3 examples/channel-preview/preview.py --target mimo
py -3 examples/channel-preview/diagnostics.py --target mimo
```

预览会列出将改变的顶层设置，并估计当前有多少未归档本地任务属于其他渠道；归档任务及外部任务不计入。实际续接范围以日后安全启动时的核验为准，此示例不会执行迁移。

诊断默认只做本地检查。加上 `--online` 才会发送最小的 Responses 文本、工具调用和适用图片请求，可能消耗服务商额度。测试内容均为合成数据；能列出模型不等于协议兼容。密钥从 Windows 用户环境变量读取，不会显示或写入示例文件。

`profiles.json` 是渠道配置示例。联网检查前请按服务商最新官方文档核对接口与模型。此示例中的 Kimi 通过独立本地代理路由；未配置直接凭据变量时，联网检查会显示不可用。

当前公开桌面版本尚未凭此示例取得跨渠道旧任务续接的支持资格。已验证能力以仓库的[兼容矩阵](../../COMPATIBILITY.md)为准。

[English](README.md)
