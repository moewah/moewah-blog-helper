# Moewah Blog Helper

Astro 博客文章发布 Agent Skill，一个自用的面向 [Astro Firefly](https://github.com/CuteLeaf/Firefly) 博客文章助手，配合 Claude Code 等 AI Agent 使用，聚焦 Frontmatter SEO生成、文章分类整理、标点符号规范，实现博客文章智能预处理。

## 功能

- **智能分类**：AI 分析内容自动匹配分类
- **SEO Frontmatter**：生成优化后的标题、描述、标签
- **图片处理**：提取图片到统一目录，转换引用路径
- **标点规范**：自动修正中英文混排版式
- **批量处理**：支持目录级批量操作

## 环境要求

- Python 3.8+
- Claude Code 或其他支持 Skill 的 AI Agent

## 安装

```bash
git clone https://github.com/moewah/moewah-blog-helper.git ~/.claude/skills/moewah-blog-helper
```

## 配置

```bash
export ASTRO_BLOG_DIR="$HOME/path/to/blog/src/content/posts"  # 博客文章目录
export ASTRO_DRAFT_DIR="$HOME/path/to/drafts"                 # 草稿箱目录
```

## 使用

在 Claude Code 中：

```
处理这篇博客文章 /path/to/article.md
批量发布草稿箱里的博客文章
处理 ~/Desktop/articles 目录的博客文章
```

## 目录结构

```
moewah-blog-helper/
├── SKILL.md              # Agent 指令
├── scripts/
│   └── publish.py        # 核心脚本
└── references/
    ├── categories.md     # 分类规则
    ├── punctuation-rules.md   # 标点规范
    └── frontmatter-handling.md # Frontmatter 处理规则
```

## 文件命名

输出格式：`{年月}-{slug}.md`

示例：`2026-03-docker-deploy-guide.md`

## License

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)