# Agent Skills

可跨框架复用的 Agent Skills 集合。

## 技能列表

| Skill | 说明 |
|-------|------|
| [gzh-article-generator](gzh-article-generator/) | 公众号内容工作台 — 文章生成 / 文章审核 / 每日选题推荐，共用一套「十大元素」框架 |

## 安装方式

### Hermes Agent

```bash
hermes skills install q8b39q6y-star/skills/gzh-article-generator
```

或直接 clone：

```bash
git clone https://github.com/q8b39q6y-star/skills.git
cp -r skills/gzh-article-generator ~/.hermes/skills/productivity/
```

### Claude Code

```bash
mkdir -p ~/.claude/skills
cp -r skills/gzh-article-generator ~/.claude/skills/
```

Claude Code 会自动发现 `~/.claude/skills/<name>/SKILL.md`。

### Codex

```bash
mkdir -p ~/.codex/skills
cp -r skills/gzh-article-generator ~/.codex/skills/
```

## 兼容性

所有 skill 使用标准 Agent Skills 格式（YAML frontmatter：`name` + `description`），Claude Code 原生支持，Codex / Hermes / OpenCode 等兼容。

各框架的定时任务配置方式不同，详见 `gzh-article-generator/references/portability.md`。
