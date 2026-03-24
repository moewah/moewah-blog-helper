# 置顶管理

## 置顶机制

| 操作 | Frontmatter 变更 |
|------|------------------|
| 置顶文章 | 添加 `pinned: true`（在 `updated` 字段下方） |
| 取消置顶 | 移除 `pinned` 字段（推荐）或设为 `pinned: false` |

## CLI 命令

```bash
# 列出所有置顶文章
python $SKILL_DIR/scripts/publish.py list-pinned

# 搜索文章（匹配 title 或 slug）
python $SKILL_DIR/scripts/publish.py search "关键词"

# 设置置顶状态
python $SKILL_DIR/scripts/publish.py set-pinned {文章路径} --status true
python $SKILL_DIR/scripts/publish.py set-pinned {文章路径} --status false
```

## 工作流程

### 场景一：管理已置顶文章

```
用户请求查看/管理置顶文章
       │
       ▼
┌──────────────────┐
│ 1. 列出置顶文章  │  → python publish.py list-pinned
└──────────────────┘
       │
       ▼
┌──────────────────┐
│ 2. 用户决策      │  → AskUserQuestion 让用户选择操作
│    - 取消置顶    │
│    - 保持不变    │
└──────────────────┘
       │
       ▼
┌──────────────────┐
│ 3. 执行操作      │  → python publish.py set-pinned {path} --status false
└──────────────────┘
```

### 场景二：置顶特定文章

```
用户提供关键词（title 或 slug）
       │
       ▼
┌──────────────────┐
│ 1. 搜索文章      │  → python publish.py search "关键词"
└──────────────────┘
       │
       ▼
┌──────────────────┐
│ 2. 用户决策      │  → AskUserQuestion 让用户选择目标文章
│    - 选择文章    │
│    - 置顶/取消   │
└──────────────────┘
       │
       ▼
┌──────────────────┐
│ 3. 执行操作      │  → python publish.py set-pinned {path} --status true/false
└──────────────────┘
```

## 交互示例

### 列出置顶文章后

使用 AskUserQuestion 提供操作选项：

```
标题：置顶管理
问题：请选择要执行的操作

选项：
1. 取消置顶 [文章A]
2. 取消置顶 [文章B]
3. 全部取消置顶
4. 保持不变
```

### 搜索文章后

使用 AskUserQuestion 让用户选择目标文章：

```
标题：选择文章
问题：请选择要置顶/取消置顶的文章

选项：
1. 📌 文章标题A（已置顶）
2. 文章标题B
3. 文章标题C
```

选择后再询问置顶或取消。

## 输出格式

### list-pinned 输出

```
📌 找到 2 篇置顶文章:
  1. Docker 部署入门指南
     slug: docker-deploy-beginner-guide
     path: /path/to/article.md
  2. SEO 优化实战
     slug: seo-optimization-guide
     path: /path/to/article.md
```

### search 输出

```
🔍 找到 3 篇匹配文章:
  1. 📌 Docker 部署入门指南
     slug: docker-deploy-beginner-guide
     path: /path/to/article.md
  2. Docker Compose 进阶用法
     slug: docker-compose-advanced
     path: /path/to/article.md
```

📌 标记表示该文章已置顶。

## 触发词

- 查看置顶文章、列出置顶、置顶文章列表
- 搜索文章、找文章
- 置顶这篇文章、取消置顶、pin 管理