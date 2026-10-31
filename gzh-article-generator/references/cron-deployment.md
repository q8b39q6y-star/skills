# Hermes Cron 部署实录（gzh 选题推荐任务）

本文档记录 gzh 选题推荐任务的完整部署过程，包含踩过的坑。
当前生效：本 skill 已被合并到 `productivity/gzh-article-generator`（公众号内容工作台），脚本现位于 `productivity/gzh-article-generator/scripts/hot_topics.py`。

---

## 部署架构

```
cron scheduler (gateway 进程内)
  │
  ├── 7:00  ──┐
  ├── 11:00 ──┤  每天三次触发
  └── 18:00 ──┘
       │
       ▼
  ~/.hermes/scripts/hot_topics.py    ← --script（数据采集）
       │
       ▼  stdout 注入 agent prompt
  Agent + gzh-daily-topics skill     ← --skill（选题生成）
       │
       ▼
  Telegram 推送                       ← --deliver telegram
```

## 创建命令

```bash
# 1. 把脚本放到 cron 可访问的路径
cp ~/.hermes/skills/productivity/gzh-article-generator/scripts/hot_topics.py \
   ~/.hermes/scripts/hot_topics.py

# 2. 创建 cron job（不带中文提示词——见下方陷阱）
#    注意：--skill 用当前生效的 umbrella skill 名（gzh-article-generator），
#    旧的 gzh-daily-topics 已被合并、引用会静默失效（见陷阱 8）
hermes cron create '0 7,11,18 * * *' \
  --name 'gzh-daily-topics' \
  --script 'hot_topics.py' \
  --skill 'gzh-article-generator' \
  --deliver 'telegram'

# 3. 用 edit 补上中文提示词（create 不接受中文 positiona...）
hermes cron edit <job_id> --prompt '基于微博热搜数据使用gzh-daily-topics技能生成10个爆款选题'
```

## 陷阱

### 陷阱 1：`--deliver local` 不推送

`--deliver local` 只把输出写入 cron 自身的 session DB（`~/.hermes/state.db`），**不会**弹到用户面前。用户收不到任何通知。

正确做法：`--deliver telegram`（或 discord / slack 等已配置的网关平台）。

### 陷阱 2：`hermes cron create ... 中文` 解析失败

`hermes cron create` 的第二个位置参数是 `prompt`，但包含中文时会被 argparse 误解析为顶层 `hermes` 的参数，报 `unrecognized arguments`。

绕过方法：
- 创建时不带 prompt
- 然后用 `hermes cron edit <id> --prompt '中文...'` 补上

### 陷阱 3：`--script` 必须在 `~/.hermes/scripts/` 下

cron 的 `--script` 参数只接受相对路径（相对于 `~/.hermes/scripts/`），不接受绝对路径。

### 陷阱 4：多 Telegram bot 不支持

Hermes 目前只支持一个 Telegram 平台实例。如果需要不同 bot 推送不同内容，唯一的绕行方案是 `--no-agent` 模式 + 脚本直接调用 Telegram Bot API。

### 陷阱 5：gateway 必须运行中

cron 调度器运行在 gateway 进程内。如果 gateway 没启动，cron 不会触发。

```bash
hermes cron status   # 确认 "✓ Gateway is running"
```

### 陷阱 6：`hermes cron edit` 没有 `--model` / `--provider` 参数

`hermes cron edit --help` 只暴露 schedule/prompt/name/deliver/skill/script/workdir，**没有 model/provider 开关**——尽管 `~/.hermes/cron/jobs.json` 的 schema 里 `model`/`provider` 字段是存在的。

要按 job 级别覆盖模型，只能直接改 jobs.json：

```python
# 停 -> 改 -> 启，避免 scheduler 并发写回覆盖
import json, os
path = os.path.expanduser('~/.hermes/cron/jobs.json')
data = json.load(open(path))
for j in data['jobs']:
    if j['id'] == '<job_id>':
        j['model'] = 'deepseek-v4-pro'   # 覆盖默认模型
        j['provider'] = 'deepseek'
json.dump(data, open(path, 'w'), ensure_ascii=False, indent=2)
```

改完 `hermes cron resume <id>` + `hermes cron run <id>` 手动验证。job 的 `model`/`provider` 为 `null` 时走 config 默认模型。

### 陷阱 7：cron 报 `credit insufficient balance` —— 先定位是哪个 provider 欠费

错误 `{'code': 'insufficient_user_quota', 'message': 'credit insufficient balance: balance=... required=...'}` 是 **MiniMax** 的报错格式（不是 DeepSeek）。cron 用默认模型时，欠费的是 `config.yaml` 里 `model.default` + `model.provider` 指向的那个 provider，不是当前会话正在跑的模型。

定位三步：
1. `hermes config` 看 `Model: {'default': ..., 'provider': ...}`
2. `cat ~/.hermes/cron/jobs.json` 看 job 的 `model`/`provider` 是否为 null（null=走默认）
3. 对号入座：谁欠费，就切走（改 jobs.json 或 config 默认值）或充值

### 陷阱 8：skill 被合并/重命名后，cron 引用会静默失效

cron job 按名字引用 skill。若该 skill 被合并进 umbrella（例如 `gzh-daily-topics` → `gzh-article-generator`），cron 运行时会提示 `Skill(s) not found and skipped: <旧名>`，agent 会自行降级处理，但每次都带警告且可能偏离预期。

修复：`hermes cron edit <job_id> --skill '<新skill名>'`。创建新 job 时也要用当前生效的 skill 名。

## 验证流程

```bash
# 1. 确认 gateway 在跑
hermes cron status

# 2. 手动触发一次
hermes cron run <job_id>

# 3. 等 ~30 秒（scheduler tick 间隔），确认数据已刷新
ls -lt ~/.hermes/data/weibo_hot/

# 4. 查看 cron 产出（如果有问题）
hermes sessions list | head -5  # 找 cron_ 前缀的 session
```

## 维护命令

```bash
hermes cron list              # 查看所有 job
hermes cron status            # 调度器状态
hermes cron pause <id>        # 暂停
hermes cron resume <id>       # 恢复
hermes cron remove <id>       # 删除
hermes cron edit <id>         # 修改配置
```
