# 开发与高级用法

[返回安装首页](../README.zh-CN.md)

## 可选兼容后端

默认安装使用官方后端。需要历史请求兼容功能时，从发行页下载 `install.ps1` 后运行：

```powershell
.\install.ps1 -BackendMode compat
```

源码构建需要 Python 3.11 以上、Git、Rust 1.95.0、x64 MSVC 和 Windows SDK，请在 x64 开发者环境中运行。已有匹配构建可通过 `-BackendManifest` 指定；`-DryRun` 可查看模式选择和前置条件。具体受支持配置见 [codex-history-compat](https://github.com/catterhu1207-ux/codex-history-compat)。

以下目录命令以受支持的 `26.924.2738.0` 为示例，使用时对应你实际取得的受支持来源。

## 手动安装与开发

需要：

- Python 3.11+
- Git
- 你自己取得的受支持官方 Codex 应用目录

下面假设官方包根目录为：

```text
C:\official\OpenAI.Codex_26.924.2738.0_x64__2p2nqsd0c76g0
```

安装：

```powershell
git clone https://github.com/catterhu1207-ux/codex-desktop-workflow.git
cd codex-desktop-workflow
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
```

### 1. 检查官方包是否为支持版本

```powershell
.\.venv\Scripts\codex-desktop-workflow.exe inspect `
  --source C:\official\OpenAI.Codex_26.924.2738.0_x64__2p2nqsd0c76g0
```

### 2. 生成独立修改版

目标目录必须不存在：

```powershell
.\.venv\Scripts\codex-desktop-workflow.exe build `
  --source C:\official\OpenAI.Codex_26.924.2738.0_x64__2p2nqsd0c76g0 `
  --target C:\codex-workflow\app
```

### 3. 验证真实组件和启动结果

```powershell
.\.venv\Scripts\codex-desktop-workflow.exe verify `
  --source C:\official\OpenAI.Codex_26.924.2738.0_x64__2p2nqsd0c76g0 `
  --portable C:\codex-workflow\app `
  --runs-root C:\codex-workflow\verification
```

`verify` 按对应版本要求两次或三次启动，每次分别出现公共工件自身的 `codex.exe` 后端、真实 renderer 证明和正常退出。任意一次超时、后台残留或证明不匹配都会失败。它不会强行终止用户进程。保留的 `26.908.9136.0` profile 在提供对应官方包时使用相同命令。

隔离验收不复制认证。工具会在未登录的独立环境中短暂挂载真实任务界面以生成与本次产物绑定的 renderer 证明，随后界面可能回到登录页。

各版本的脱敏结果见 [验收记录](../ACCEPTANCE.md)(ACCEPTANCE.md)。

## 导入自己的任务副本

隔离验收使用全新数据。

如果需要在修改版中继续自己的任务，请先完全退出所有 Codex / ChatGPT 桌面进程和后端，再显式创建独立数据副本：

```powershell
.\.venv\Scripts\codex-desktop-workflow.exe import-data `
  --source C:\Users\you\.codex `
  --target C:\codex-workflow\data

.\.venv\Scripts\codex-desktop-workflow.exe launch `
  --portable C:\codex-workflow\app `
  --data C:\codex-workflow\data `
  --runs-root C:\codex-workflow\daily-runs
```

导入使用 SQLite 一致性备份并复制任务记录目录。

它**不会复制**：

- `auth.json`
- `config.toml`
- 插件
- 技能
- 认证信息

首次启动后请在独立环境重新登录或配置服务。官方数据与修改版数据之后各自保存，不自动同步或合并。

`launch` 会输出运行目录。用同一个目录查看状态或正常关闭：

```powershell
codex-desktop-workflow status --run C:\codex-workflow\daily-runs\run-<id>
codex-desktop-workflow stop --run C:\codex-workflow\daily-runs\run-<id>
```

`stop` 通过本地调试端口调用该版本应用自身的退出动作，并再次核对主进程与已登记后端。身份不符或超时会报告阻塞，不会强制结束进程。

## 安全边界

- 所有构建都写入不存在的新目录，拒绝源目标嵌套和重复补丁。
- 未知版本、摘要不符、补丁匹配不唯一、功能契约失败或运行证明缺失都会停止。
- 生成报告会记录你选择的位置；分享前请自行检查。
- 报告不记录任务正文、凭据或令牌。
- 项目不提供、不下载、不重新分发官方 Codex 二进制。
- 本项目是非官方实验性社区工具，不代表 OpenAI，也不替代官方更新和支持。

