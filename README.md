# codex-desktop-workflow

**这是可以直接用于 Codex 桌面端魔改的本地生成工具。** 你提供自己已经取得的、受支持的官方 Codex 应用目录，它会在新目录中生成独立魔改版，核验真实界面代码，并用两次隔离启动确认产物能够运行和正常退出。

[English README](README.en.md)

## 我为什么做这个？

我同时处理很多 Codex 任务时，官方 Priority 无法准确表达我下一步应该看什么。刚开始处理的任务、停在待实施计划上的任务、我主动置顶的任务和普通未读消息，对人的注意力并不是一回事。远程项目显示内部 ID，以及全局默认模型覆盖任务原有设置，也会破坏并行工作时的上下文。

我因此修改了桌面端的工作流，并把每次官方更新后的重新适配做成可核验流程。这个仓库是实际入口：它读取用户自己的官方安装包，在本地生成魔改副本。它不提供或下载官方二进制。

## 生成后会得到什么？

| 实际问题 | 魔改行为 |
|---|---|
| Priority 顺序无法反映当前工作 | 按任务或进程实际开始时间排序，初次加载和实时更新使用同一规则。 |
| 提示点无法表达下一步动作 | 待实施计划为黄色，置顶关注为红色，普通未读为蓝色；计划与置顶同时存在时黄色优先，加载继续转圈。 |
| 远程项目显示内部 ID | 侧栏、搜索、Work 选择器、提示和辅助功能文本显示可识别名称，同时保留原路由身份。 |
| 全局默认模型改变并行任务的上下文 | 已有任务保留有效的模型和推理设置，全局默认只用于新任务。 |

## 首发支持范围

- Windows x64。
- Codex 桌面版 `26.908.9136.0`。
- 官方 `app.asar` SHA-256 必须为 `7a46bd6fe162050afbac27d7d5271d19524e887fa0cdd06c0f2d3fa9b606a31d`。
- 默认保留官方包内的 `codex.exe`。

工具同时核对版本、完整 ASAR、后端和四个关键入口。版本号相同但文件不匹配也会拒绝。完整矩阵见 [COMPATIBILITY.md](COMPATIBILITY.md)。

第三方 Responses 兼容服务的后端修复在 [codex-history-compat](https://github.com/catterhu1207-ux/codex-history-compat) 中公开，但尚未作为本版本桌面组合完成独立验收，因此 `v0.1.0` 不把它标为可用组合。

## 最短使用路径

需要 Python 3.10+、Git，以及用户自己取得的官方应用目录。下面假设官方包根目录为 `C:\official\OpenAI.Codex_26.908.9136.0_x64__2p2nqsd0c76g0`。

```powershell
git clone https://github.com/catterhu1207-ux/codex-desktop-workflow.git
cd codex-desktop-workflow
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .

# 1. 核对版本和所有固定摘要。
.\.venv\Scripts\codex-desktop-workflow.exe inspect `
  --source C:\official\OpenAI.Codex_26.908.9136.0_x64__2p2nqsd0c76g0

# 2. 从干净官方目录生成一个全新副本；目标目录必须不存在。
.\.venv\Scripts\codex-desktop-workflow.exe build `
  --source C:\official\OpenAI.Codex_26.908.9136.0_x64__2p2nqsd0c76g0 `
  --target C:\codex-workflow\app

# 3. 运行真实组件检查和两次隔离启动，每次观察至少 60 秒。
.\.venv\Scripts\codex-desktop-workflow.exe verify `
  --source C:\official\OpenAI.Codex_26.908.9136.0_x64__2p2nqsd0c76g0 `
  --portable C:\codex-workflow\app `
  --runs-root C:\codex-workflow\verification
```

`verify` 要求两次启动分别出现匹配的 `codex.exe` 后端、真实 renderer 证明和正常退出。任意一次超时、后台残留或证明不匹配都会失败。它不会强行终止用户进程。

隔离验收不复制认证。工具会在未登录的独立环境中短暂挂载真实任务界面以生成与本次产物绑定的 renderer 证明，随后界面可能回到登录页。公开的两轮脱敏结果见 [ACCEPTANCE.md](ACCEPTANCE.md)。

## 导入自己的任务副本

隔离验收使用全新数据。需要在魔改版中继续自己的任务时，先完全退出所有 Codex/ChatGPT 桌面进程和后端，再显式创建独立副本：

```powershell
.\.venv\Scripts\codex-desktop-workflow.exe import-data `
  --source C:\Users\you\.codex `
  --target C:\codex-workflow\data

.\.venv\Scripts\codex-desktop-workflow.exe launch `
  --portable C:\codex-workflow\app `
  --data C:\codex-workflow\data `
  --runs-root C:\codex-workflow\daily-runs
```

导入使用 SQLite 一致性备份并复制任务记录目录。它不复制 `auth.json`、`config.toml`、插件、技能或认证信息；首次启动后请在独立环境重新登录或配置服务。官方数据与魔改数据之后各自保存，不自动同步或合并。

`launch` 输出运行目录。用同一个目录查看状态或正常关闭：

```powershell
codex-desktop-workflow status --run C:\codex-workflow\daily-runs\run-<id>
codex-desktop-workflow stop --run C:\codex-workflow\daily-runs\run-<id>
```

`stop` 通过本地调试端口调用该版本应用自身的退出动作，并再次核对主进程与已登记后端。身份不符或超时会报告阻塞，不会强制结束进程。

## 安全边界

- 所有构建都写入不存在的新目录，拒绝源目标嵌套和重复补丁。
- 未知版本、摘要不符、补丁匹配不唯一、功能契约失败或运行证明缺失都会停止。
- 生成报告包含用户选择的本地路径；分享前请检查。报告不记录任务正文、凭据或令牌。
- 本项目是非官方实验性社区工具，不代表 OpenAI，也不替代官方更新和支持。

通用来源暂存与进程管理固定使用 [electron-update-safety v0.1.3](https://github.com/catterhu1207-ux/electron-update-safety/releases/tag/v0.1.3)，证据阶段来自 [desktop-adaptation-lab v0.1.0](https://github.com/catterhu1207-ux/desktop-adaptation-lab/releases/tag/v0.1.0)。
