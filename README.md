# Agent Skills

可跨框架复用的 Agent Skills 集合。

## 技能列表

| Skill | 说明 |
|-------|------|
| [gzh-article-generator](gzh-article-generator/) | 公众号内容工作台 — 文章生成 / 文章审核 / 每日选题推荐，共用一套「十大元素」框架 |

## 一键安装

### Claude Code

```bash
git clone https://github.com/q8b39q6y-star/skills.git ~/skills \
  && mkdir -p ~/.claude/skills \
  && cp -r ~/skills/gzh-article-generator ~/.claude/skills/
```

装完重启 Claude Code 即可用，在对话里说「用 gzh-article-generator 帮我写一篇公众号」触发。

### Codex

```bash
git clone https://github.com/q8b39q6y-star/skills.git ~/skills \
  && mkdir -p ~/.codex/skills \
  && cp -r ~/skills/gzh-article-generator ~/.codex/skills/
```

### Hermes Agent

```bash
hermes skills install q8b39q6y-star/skills/gzh-article-generator
```

装完重启 gateway（`hermes gateway restart`）。

### 其他兼容 Agent Skills 格式的框架

把 `gzh-article-generator/` 整个目录放进该框架的 skills 目录即可。

## 依赖

**无第三方依赖。** 抓取脚本 `scripts/hot_topics.py` 只用 Python 标准库（urllib），无需 pip install。

需要 Python 3.9+。

## 使用

```bash
# 抓取微博热搜
python3 gzh-article-generator/scripts/hot_topics.py

# 只看输出，不写盘
python3 gzh-article-generator/scripts/hot_topics.py --json

# 自定义条数 / 输出目录
python3 gzh-article-generator/scripts/hot_topics.py --limit 15 --out /tmp/hot
```

数据写入 `<out>/YYYY-MM-DD.json` 和 `<out>/latest.json`（默认 `~/.weibo_hot/`）。

## 定时任务

各框架的调度机制不同：

- **Hermes**：见 `gzh-article-generator/references/cron-deployment.md`（含 `--deliver` 交付目标陷阱）
- **Claude Code / Codex / 其他**：用框架自身的定时机制调用 `scripts/hot_topics.py`，把 stdout 喂给 agent 即可

跨框架移植细节见 `gzh-article-generator/references/portability.md`。

## 兼容性

所有 skill 使用标准 Agent Skills 格式（YAML frontmatter：`name` + `description`），Claude Code 原生支持，Codex / Hermes / OpenCode 等兼容。

## License

MIT
