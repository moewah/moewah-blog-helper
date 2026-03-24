# 已有 Frontmatter 处理规则

## 字段保留策略

| 字段 | 处理方式 |
|------|----------|
| slug | **保留原值**（避免 URL 变化影响 SEO） |
| published | **保留原值**（发布时间不变） |
| updated | **更新为当前日期** |
| 其他字段 | 重新生成（title、description、category、tags、image） |

## 处理流程

```
读取文章
    │
    ▼
检测现有 frontmatter
    │
    ├─ 无 frontmatter → 完整生成（含图片处理）
    │
    └─ 有 frontmatter → 提取 slug、published（若存在）
                        │
                        ▼
                      重新生成其他字段
                        │
                        ▼
                      合并：保留字段 + 新生成字段
                        │
                        ▼
                      格式化为标准格式
```

## 标准格式

```yaml
title: "标题"
description: "描述"
category: 分类名
tags:
  - 标签1
  - 标签2
  - 标签3
slug: "url-slug"
image: "api"
published: YYYY-MM-DD
updated: YYYY-MM-DD
```

## 图片处理策略

| 场景 | 处理方式 |
|------|----------|
| 无 frontmatter | 处理图片引用（提取、转换路径） |
| 有 frontmatter | **跳过图片处理**（通常只给文章文件，不含图片） |

符合以下格式的图片引用也跳过处理：
```
![](../images/{年份}/{月份}/{文件名})
```

## H1 标题处理

无论是否已有 frontmatter，都执行 H1 删除：
- 正文开头的 `# 标题` 删除
- 原因：title 已在 frontmatter 中定义，避免重复

## 文件名处理

| 场景 | 文件名格式 |
|------|------------|
| 有 published | `{年月}-{slug}.md`（使用 published 的年月） |
| 无 published | `{年月}-{slug}.md`（使用当前日期的年月） |

示例：
- published: 2025-12-15, slug: docker-guide → `2025-12-docker-guide.md`
- 无 published, 当前日期 2026-03-24, slug: docker-guide → `2026-03-docker-guide.md`