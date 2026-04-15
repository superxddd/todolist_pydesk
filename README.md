# AI Todo Manager

一个基于 Tkinter 的 Windows 桌面待办应用，提供本地任务管理、今日视图、AI 任务拆解与优先级建议，并包含可直接上传 GitHub 的工程化配置与 CI/CD。

## 功能

- 本地单机 Todo 管理：新建、编辑、删除、完成、筛选、搜索
- 今日视图：展示今日到期、逾期、已完成任务
- AI 建议：通过 OpenAI 兼容接口生成子任务和优先级建议
- 系统托盘：常驻托盘、快速显示主窗口、退出应用
- JSON 数据存储：任务和设置分别存储，便于备份和迁移

## 项目结构

```text
src/ai_todo/
  app/        应用入口、版本、配置、启动流程
  core/       任务模型、筛选、调度、AI 建议合并
  services/   AI 客户端、日志、托盘、通知、备份
  storage/    JSON 仓储、设置、路径、示例数据
  ui/         Tkinter 主窗口、面板、对话框
tests/        单元测试与轻量集成测试
.github/      GitHub Actions 工作流
```

## 本地开发

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .[dev]
pytest
python -m ai_todo
```

## 配置 AI

在应用设置中填写：

- `Base URL`
- `Model`
- `API Key`

应用使用 OpenAI 兼容的 `/chat/completions` 接口，不限制具体服务商。

也可以通过本地环境变量覆盖配置，避免把密钥写进仓库或截图里：

```powershell
$env:AI_TODO_BASE_URL="https://api.deepseek.com/v1"
$env:AI_TODO_MODEL="deepseek-chat"
$env:AI_TODO_API_KEY="your-api-key"
py -m ai_todo
```

## 发布

- CI：`push` / `pull_request` 运行 Ruff 和 Pytest
- Release：打 tag 或手动触发时，GitHub Actions 构建 Windows 可执行文件并上传到 Release

## 安全提示

API Key 当前以本地明文形式保存在用户设置文件中。首版没有做系统级密钥保管，请不要在共享电脑上保存生产密钥。
