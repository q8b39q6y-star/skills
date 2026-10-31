# gzh-article-generator

公众号内容工作台 — 文章生成、文章审核、每日选题推荐；同一套十大元素框架贯穿。

## 三个模块

| 模块 | 功能 |
|------|------|
| **模块 1** 文章生成 | 十大元素框架 + 5 段式结构，产出完整推文 |
| **模块 2** 文章审核 | 六大维度逐项打分 → 修改建议 |
| **模块 3** 每日选题推荐 | 基于微博热搜生成 10 条爆款选题 |

## 快速开始

```bash
# 手动抓取微博热搜
python3 scripts/hot_topics.py

# 输出 JSON（不写盘）
python3 scripts/hot_topics.py --json

# 自定义条数
python3 scripts/hot_topics.py --limit 15
```

数据默认写到 `~/.weibo_hot/`，可用 `WEIBO_HOT_DATA_DIR` 环境变量覆盖。

## 依赖

- Python 3.9+
- **无第三方依赖** — 脚本只用标准库 `urllib`，无需 pip install

## 数据源状态

| 平台 | 状态 | 说明 |
|------|------|------|
| 微博热搜 ✅ | `https://weibo.com/ajax/side/hotSearch` | 无需认证，JSON 直取 |
| 百度热搜 ❌ | JS 渲染 | 需 headless browser |
| 知乎热榜 ❌ | 需登录 | 返回 403 |

## 参考文档

- `references/portability.md` — 跨框架移植说明（Claude Code / Codex / 其他）+ 安装命令
- `references/cron-deployment.md` — Hermes Cron 部署实录（含交付目标陷阱）

## 框架专属提醒

`references/cron-deployment.md` 讲的是 **Hermes** 的 cron 命令。其他框架（Claude Code / Codex 等）没有 `hermes cron`，需要用各自的定时机制重配调度。

写作方法论部分（十大元素、5 段式、六大维度审核）跨框架零成本移植。
