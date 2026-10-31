# 跨框架移植说明（Claude Code / Codex / 其他 Agent 框架）

gzh-article-generator 的 SKILL.md 用的是标准「Agent Skills」格式（YAML frontmatter 只要求 `name` + `description`），Claude Code 原生支持，Codex 等也兼容。移植时只需处理 Hermes 专属依赖。

## 可移植部分（核心价值，100% 通用）

以下全在 SKILL.md 主文档里，无框架依赖，直接复用：

- 十大元素框架（情感：亲情/爱情/友情；情绪：愤怒/怀旧/愧疚/暖心/孤独；地域细节；群体代入感）
- 5 段式文章结构（人物背景 → 事件还原 → 争议焦点 → 深层追问 → 收尾表态）
- 六大维度审核清单（标题公式/开头公式/正文结构/金句密度/…）
- 选题筛选标准、A/B/C/D 分类、情绪映射表、禁止清单

## Hermes 专属部分（需按目标框架适配）

| 内容 | 位置 | 适配方式 |
|------|------|---------|
| `metadata.hermes` frontmatter | SKILL.md 头部 | 其他框架会忽略，无害，可留可删 |
| 数据目录路径 | scripts/hot_topics.py | 已支持 `WEIBO_HOT_DATA_DIR` 环境变量（默认 `~/.weibo_hot`），设变量即可，无需改代码 |
| `~/.hermes/scripts/` + cron 调度 | references/cron-deployment.md | 目标框架用各自的定时机制重配 |

## 安装到 Claude Code

```bash
mkdir -p ~/.claude/skills/gzh-article-generator
cp -r <本skill目录>/* ~/.claude/skills/gzh-article-generator/
```

Claude Code 自动发现 `~/.claude/skills/<name>/SKILL.md`。

## 安装到 Codex

```bash
mkdir -p ~/.codex/skills/gzh-article-generator
cp -r <本skill目录>/* ~/.codex/skills/gzh-article-generator/
```

## 结论

写作方法论这套是 skill 的核心价值，跨框架零成本移植；自动抓热搜 + 定时推送这条数据管道是 Hermes 专属的，目标框架需重配调度。
