---
name: moewah-blog-helper
description: |
  Astro 博客文章发布工作流。处理 Markdown 文章完成：
  (1) AI 分析内容并自动分类
  (2) 生成 SEO 优化的 Frontmatter
  (3) 标点符号规范化检查（可选，交互确认）
  (4) 提取图片到统一目录 images/{年份}/{月份}/
  (5) 转换图片引用为相对路径
  (6) 删除正文 H1 标题
  (7) 重命名文件为 {年月}-{slug}.md 格式

  触发词：
  - 单篇：处理这篇博客文章、准备发布这篇博客文章、发布博客文章、整理博客、生成 frontmatter、博客文章分类、图片整理
  - 批量：处理这些博客文章、批量发布博客文章、处理草稿箱目录、发布草稿箱里的博客文章
  - 目录：处理 {目录名} 目录的博客文章、发布 {目录名} 里的博客文章、整理 {目录名} 下的博客
---

# Moewah Blog Helper

## 变量定义

```
SKILL_DIR = 当前 Skill 所在目录
```

Agent 在执行时自动识别 Skill 目录位置，无需用户配置。

## Agent 权限需求

| 工具 | 用途 | 调用场景 |
|------|------|----------|
| Bash | 执行 Python 脚本 | `scan`、`read`、`write`、`archive` 命令 |
| Read | 读取参考文件 | `categories.md`、`punctuation-rules.md`、`frontmatter-handling.md` |

## 交互环节

| 环节 | 触发时机 | 工具 | 问题 | 选项 |
|------|----------|------|------|------|
| 标点检查 | 步骤 3，分析完 frontmatter 后 | AskUserQuestion | 是否需要检查并修正文章中的标点符号？ | 1. 检查并修正（推荐）<br>2. 跳过 |

## 自动执行环节（无需交互）

| 步骤 | 操作 | 说明 |
|------|------|------|
| 1 | 扫描/读取文章 | 扫描目录或读取指定文章 |
| 2 | 分析分类、生成 Frontmatter | Agent 自动判断 |
| 4 | 写入文章 | 处理图片、删除 H1、重命名文件 |
| 5 | 归档原文件 | 移动到 processed 目录 |

## 环境配置

```bash
export ASTRO_BLOG_DIR="$HOME/WEB/BLOG/src/content/posts/OB-NOTES"  # 文章分类目录
export ASTRO_DRAFT_DIR="$HOME/WEB/BLOG/drafts"                      # 待处理目录
```

## 工作流程

```
用户提供文章路径
       │
       ▼
┌──────────────────┐
│ 1. 读取文章      │  → python publish.py read {path}
└──────────────────┘
       │
       ▼
┌──────────────────┐
│ 2. 分析并生成    │  → Agent 分析内容
│    - 确定分类    │  → Agent 决定分类
│    - 生成 FM     │  → Agent 生成 Frontmatter
└──────────────────┘
       │
       ▼
┌──────────────────┐
│ 3. 标点规范检查  │  → 询问用户是否需要标点检查
│    （可选环节）  │  → 确认后自动修正并更新正文
└──────────────────┘
       │
       ▼
┌──────────────────┐
│ 4. 写入文章      │  → python publish.py write {path} --category {cat} --frontmatter "{fm}"
│    - 处理图片    │     (自动：图片提取、H1删除、文件重命名)
│    - 生成文件    │     若标点已修正，使用修正后的正文
└──────────────────┘
       │
       ▼
┌──────────────────┐
│ 5. 归档原文件    │  → python publish.py archive {path}
└──────────────────┘
```

## CLI 命令

```bash
# 扫描待处理目录
python $SKILL_DIR/scripts/publish.py scan

# 读取文章内容
python $SKILL_DIR/scripts/publish.py read {文章路径}

# 写入文章（自动处理图片、删除H1、重命名文件）
python $SKILL_DIR/scripts/publish.py write {文章路径} --category {分类} --frontmatter "{YAML内容}"

# 写入文章（使用修正后的正文）
python $SKILL_DIR/scripts/publish.py write {文章路径} --category {分类} --frontmatter "{YAML内容}" --body "{修正后的正文}"

# 归档原文件
python $SKILL_DIR/scripts/publish.py archive {文章路径}
```

## 分类规则

根据文章内容匹配 [references/categories.md](references/categories.md) 中的分类。

## 标点符号规范（可选环节）

处理包含代码块、中英文混排的技术文章时，可检查并修正标点符号。

详见 [references/punctuation-rules.md](references/punctuation-rules.md)。

**核心规则**：
- 中文叙述用全角标点，英文/数字/代码用半角
- 中英文/数字/行内代码之间加空格
- 行内代码前后加空格，标点在反引号外
- 代码块内部保持原始格式，不加中文标点

### 交互确认流程

在步骤 3，Agent **必须询问用户**是否需要进行标点检查：

```
使用 AskUserQuestion 工具询问：

标题：标点检查
问题：是否需要检查并修正文章中的标点符号？

选项：
1. 检查并修正（推荐）- 自动检查中英文混排、行内代码等标点问题
2. 跳过 - 保持原样，直接进入写入步骤
```

### 处理方式

| 用户选择 | 操作 |
|----------|------|
| 检查并修正 | Agent 按 punctuation-rules.md 规则修正正文，在写入时使用修正后的内容 |
| 跳过 | 直接使用原始正文写入 |

### 标点检查范围

当用户选择"检查并修正"时，Agent 自动处理：

1. **中英文混排空格**：中文与英文/数字/行内代码之间加空格
2. **行内代码格式**：`code` 前后加空格，标点放在反引号外
3. **全角/半角标点**：中文叙述用全角，代码上下文用半角
4. **括号引号**：中文叙述中用全角括号和引号
5. **列表标点统一**：完整句子加句号，短语不加

## 已有 Frontmatter 处理

文章可能已有 frontmatter（如从 Obsidian 导出），处理规则详见 [references/frontmatter-handling.md](references/frontmatter-handling.md)。

**核心规则**：
- 保留：`slug`、`published`（若存在）
- 更新：`updated` 改为当前日期
- 重生成：`title`、`description`、`category`、`tags`、`image`

## Frontmatter 模板

```yaml
title: "爆款标题，30字内，无 Emoji"
description: "80-100字描述，包含核心关键词"
category: 分类名
tags:
  - 第一层：赛道/行业
  - 第二层：方法论/深度
  - 第三层：核心术语
slug: "english-url-slug"
image: "api"
published: YYYY-MM-DD
updated: YYYY-MM-DD
```

### 字段说明

| 字段 | 规则 |
|------|------|
| title | 30字内，无 Emoji，吸引点击 |
| description | 80-100字，包含核心关键词 |
| tags | 三层标签法（见下表） |
| slug | 英文小写+连字符，14单词内，如 `docker-deploy-beginner-guide` |
| image | 固定值 `"api"`，启用 CuteLeaf/Firefly 主题随机封面 API |
| published | 发布时间（文章创建时间），格式 YYYY-MM-DD，后续不变 |
| updated | 更新时间，格式 YYYY-MM-DD，每次更新内容都改为当前日期 |

### tags 三层标签法

| 层级 | 定义 | 示例 |
|------|------|------|
| 第一层 | 赛道/行业 | 自媒体运营、AI工具、Web开发 |
| 第二层 | 方法论/深度 | 实战复盘、避坑指南、底层逻辑 |
| 第三层 | 核心术语 | SEO优化、Docker部署、Prompt工程 |

## 目录处理

| 场景 | 目录来源 | 操作 |
|------|----------|------|
| 草稿箱目录 | 环境变量 `ASTRO_DRAFT_DIR` | 使用 `scan` 命令扫描，结果排除 `processed/` 目录 |
| 自定义目录 | 用户自然语言指定（如"处理 ~/Desktop/articles 目录"） | 直接读取该目录下的 `.md` 文件 |

### 草稿箱目录流程

```bash
# 1. 扫描待处理文章
python $SKILL_DIR/scripts/publish.py scan

# 2. 批量处理（标点检查需确认，其他自动完成）
```

### 自定义目录流程

1. 列出目录中的 `.md` 文件：`ls {用户指定目录}`
2. 批量处理：read → 分析 → write → archive（无需逐篇确认）

## 批量处理说明

批量处理时，**标点检查需要单独确认**，其他步骤无需逐篇确认：

1. 读取所有文章
2. 分析并生成 frontmatter
3. **询问用户是否需要标点检查**（所有文章统一处理）
4. 逐篇写入并归档
5. 完成后汇报结果

### 标点检查批量选项

```
使用 AskUserQuestion 工具询问：

标题：标点检查
问题：是否检查并修正所有文章的标点符号？

选项：
1. 全部检查并修正 - 对所有文章进行标点规范化
2. 全部跳过 - 所有文章保持原样
```

## 归档规则

| 场景 | 归档操作 |
|------|----------|
| 草稿箱目录 | 归档到 `$ASTRO_DRAFT_DIR/processed/` |
| 博客目录 | **不归档**（直接覆盖更新） |
| 其他目录 | 归档到 `$ASTRO_DRAFT_DIR/processed/` |
| write 失败 | **不执行 archive**，向用户报错并停止流程 |

**归档作用**：
- 将原文件移动到草稿箱的 `processed/` 目录，避免重复处理
- 保留原始文件作为备份

## 错误处理

| 错误场景 | 处理方式 |
|----------|----------|
| 环境变量未设置 | 提示用户设置 `ASTRO_BLOG_DIR` 或 `ASTRO_DRAFT_DIR` |
| 文件不存在 | 报错并跳过该文件 |
| write 失败 | 报错、不归档、停止当前流程 |
| 图片不存在 | 警告但继续处理（图片引用保留原样） |

## 图片处理

脚本自动检测是否需要处理图片：

| 场景 | 图片处理 |
|------|----------|
| 无 frontmatter | 处理图片引用（提取、转换路径） |
| 有 frontmatter | **自动跳过**（通常只给文章文件，不含图片） |

支持格式：
- Markdown: `![](path)`
- Obsidian: `![[image.png]]`

输出统一转换为：`![](../images/{年份}/{月份}/{文件名})`

## 文件命名

文件名格式：`{年月}-{slug}.md`

| 场景 | 年月来源 |
|------|----------|
| 有 published | 使用 published 的年月 |
| 无 published | 使用当前日期的年月 |

示例：`2026-03-docker-deploy-beginner-guide.md`