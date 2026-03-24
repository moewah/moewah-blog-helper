#!/usr/bin/env python3
"""
Astro 博客文章发布脚本
功能：图片整理、路径转换、文件移动、Frontmatter 写入
"""

import argparse
import os
import re
import shutil
from datetime import datetime

# ==================== 配置 ====================
BLOG_DIR = os.environ.get("ASTRO_BLOG_DIR")
DRAFT_DIR = os.environ.get("ASTRO_DRAFT_DIR")

if not BLOG_DIR:
    print("❌ 请设置环境变量 ASTRO_BLOG_DIR")
    print("   export ASTRO_BLOG_DIR='$HOME/WEB/BLOG/src/content/posts/OB-NOTES'")
    exit(1)

if not DRAFT_DIR:
    print("❌ 请设置环境变量 ASTRO_DRAFT_DIR")
    print("   export ASTRO_DRAFT_DIR='$HOME/WEB/BLOG/drafts'")
    exit(1)
# 统一图片目录（相对于 BLOG_DIR）
IMAGES_BASE_DIR = "images"
# 已处理文件归档目录
PROCESSED_DIR = "processed"


# ==================== Frontmatter 解析 ====================

def parse_frontmatter_field(frontmatter: str, field: str) -> str:
    """从 frontmatter 中提取指定字段的值"""
    # 匹配 field: value 或 field: "value" 格式
    pattern = rf'^{field}:\s*["\']?([^"\':\n]+(?:\s*[^"\':\n]+)*?)["\']?\s*$'
    match = re.search(pattern, frontmatter, re.MULTILINE)
    if match:
        return match.group(1).strip().strip('"\'')
    return ""


# ==================== H1 标题处理 ====================

def remove_h1_title(content: str) -> str:
    """删除正文开头的 H1 标题（frontmatter 已定义 title）"""
    # 匹配 # 标题 格式（H1）
    # 支持：# Title 或 #Title
    content = re.sub(r'^#\s+.+\n*', '', content, count=1)
    # 清除开头多余空行
    content = content.lstrip('\n')
    return content


# ==================== 图片处理 ====================

def extract_image_refs(content: str) -> list[dict]:
    """提取图片引用"""
    images = []

    # Markdown 格式 ![alt](path)
    for match in re.finditer(r'!\[([^\]]*)\]\(([^)]+)\)', content):
        images.append({
            "full": match.group(0),
            "alt": match.group(1),
            "path": match.group(2),
            "type": "markdown"
        })

    # Obsidian 格式 ![[image.png]]
    for match in re.finditer(r'!\[\[([^\]]+)\]\]', content):
        images.append({
            "full": match.group(0),
            "alt": "",
            "path": match.group(1),
            "type": "obsidian"
        })

    return images


def get_images_target_dir() -> str:
    """获取图片目标目录：OB-NOTES/images/{年份}/{月份}/"""
    now = datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m")
    return os.path.join(BLOG_DIR, IMAGES_BASE_DIR, year, month)


def get_relative_image_path() -> str:
    """获取图片相对路径：../images/{年份}/{月份}/"""
    now = datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m")
    return f"../images/{year}/{month}"


def process_images(content: str, article_dir: str) -> tuple[str, int]:
    """处理图片：复制到统一目录并更新引用"""
    images = extract_image_refs(content)
    if not images:
        return content, 0

    # 创建目标目录
    target_dir = get_images_target_dir()
    os.makedirs(target_dir, exist_ok=True)

    # 相对路径前缀
    rel_path_prefix = get_relative_image_path()

    processed = 0
    for img in images:
        src_path = img["path"]

        # 处理相对路径
        if not os.path.isabs(src_path):
            src_path = os.path.join(article_dir, src_path)

        # 跳过网络图片
        if src_path.startswith("http") or img["path"].startswith("http"):
            continue

        # 跳过已经是目标目录的图片
        if f"../images/" in img["path"] or f"./images/" in img["path"]:
            # 已经是规范路径，检查文件是否存在
            if not os.path.exists(src_path):
                print(f"  ⚠️ 图片不存在: {src_path}")
            continue

        # 检查文件是否存在
        if not os.path.exists(src_path):
            print(f"  ⚠️ 图片不存在: {src_path}")
            continue

        # 复制图片到统一目录
        img_name = os.path.basename(src_path)
        dst_path = os.path.join(target_dir, img_name)

        # 如果目标已存在同名文件，添加时间戳避免覆盖
        if os.path.exists(dst_path) and os.path.abspath(src_path) != os.path.abspath(dst_path):
            base, ext = os.path.splitext(img_name)
            timestamp = datetime.now().strftime("%H%M%S")
            img_name = f"{base}_{timestamp}{ext}"
            dst_path = os.path.join(target_dir, img_name)

        if os.path.abspath(src_path) != os.path.abspath(dst_path):
            shutil.copy2(src_path, dst_path)
            print(f"  📷 复制图片: {img_name}")

        # 更新引用为规范相对路径
        new_ref = f'![{img["alt"]}]({rel_path_prefix}/{img_name})'
        content = content.replace(img["full"], new_ref)
        processed += 1

    return content, processed


# ==================== 文件操作 ====================

def scan_drafts() -> list[str]:
    """扫描待处理目录中的 Markdown 文章"""
    articles = []
    if not os.path.exists(DRAFT_DIR):
        print(f"❌ 待处理目录不存在: {DRAFT_DIR}")
        return articles

    for item in os.listdir(DRAFT_DIR):
        # 跳过 processed 目录
        if item == PROCESSED_DIR:
            continue

        item_path = os.path.join(DRAFT_DIR, item)

        # 直接是 .md 文件
        if item.endswith(".md"):
            articles.append(item_path)

        # 是目录，查找其中的 .md 文件
        elif os.path.isdir(item_path):
            for sub_item in os.listdir(item_path):
                if sub_item.endswith(".md"):
                    articles.append(os.path.join(item_path, sub_item))

    return sorted(articles)


def get_related_images(article_path: str) -> list[str]:
    """获取文章同级的图片文件"""
    article_dir = os.path.dirname(os.path.abspath(article_path))
    images = []

    for item in os.listdir(article_dir):
        if item.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg")):
            images.append(os.path.join(article_dir, item))

    return images


def archive_article(article_path: str) -> str:
    """归档原文件和同级图片到草稿箱的 processed 目录"""
    article_path = os.path.abspath(article_path)
    article_name = os.path.basename(article_path)

    # 检查是否在博客目录中，如果是则跳过归档
    if BLOG_DIR and article_path.startswith(os.path.abspath(BLOG_DIR)):
        print(f"  ℹ️ 文章在博客目录中，跳过归档")
        return ""

    # 创建 processed 目录（统一在草稿箱下）
    processed_dir = os.path.join(DRAFT_DIR, PROCESSED_DIR)
    os.makedirs(processed_dir, exist_ok=True)

    # 移动文章
    src_article = os.path.abspath(article_path)
    dst_article = os.path.join(processed_dir, article_name)

    # 避免同名覆盖
    if os.path.exists(dst_article):
        base, ext = os.path.splitext(article_name)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        dst_article = os.path.join(processed_dir, f"{base}_{timestamp}{ext}")

    shutil.move(src_article, dst_article)
    print(f"  📦 归档文章: {article_name}")

    # 移动同级图片
    images = get_related_images(article_path)
    for img_path in images:
        img_name = os.path.basename(img_path)
        dst_img = os.path.join(processed_dir, img_name)

        # 避免同名覆盖
        if os.path.exists(dst_img):
            base, ext = os.path.splitext(img_name)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            dst_img = os.path.join(processed_dir, f"{base}_{timestamp}{ext}")

        shutil.move(img_path, dst_img)
        print(f"  📦 归档图片: {img_name}")

    return processed_dir


def read_article(article_path: str) -> tuple[str, str]:
    """读取文章，返回 (frontmatter, body)"""
    with open(article_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 提取现有 frontmatter
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if match:
        return match.group(1), content[match.end():]
    return "", content


def write_article(article_path: str, category: str, frontmatter: str, body: str, has_existing_frontmatter: bool = False) -> str:
    """写入文章到目标目录"""
    # 目标目录：{BLOG_DIR}/{分类}/
    target_dir = os.path.join(BLOG_DIR, category)
    os.makedirs(target_dir, exist_ok=True)

    # 删除正文中的 H1 标题（title 已在 frontmatter 中定义）
    body = remove_h1_title(body)

    # 处理图片（已有 frontmatter 时跳过图片处理）
    if not has_existing_frontmatter:
        article_dir = os.path.dirname(os.path.abspath(article_path))
        body, img_count = process_images(body, article_dir)
        if img_count > 0:
            print(f"  ✅ 处理 {img_count} 张图片")
    else:
        print("  ℹ️ 已有 frontmatter，跳过图片处理")

    # 组装最终内容
    final_content = f"---\n{frontmatter}\n---\n\n{body}"

    # 生成文件名：{年月}-{slug}.md
    published = parse_frontmatter_field(frontmatter, "published")
    slug = parse_frontmatter_field(frontmatter, "slug")

    if slug:
        if published:
            # 使用 published 的年月
            year_month = "-".join(published.split("-")[:2])
        else:
            # 无 published 时使用当前日期年月
            now = datetime.now()
            year_month = f"{now.strftime('%Y')}-{now.strftime('%m')}"
            print(f"  ℹ️ 无 published 字段，使用当前日期: {year_month}")
        new_filename = f"{year_month}-{slug}.md"
    else:
        # 无 slug 时使用原文件名
        new_filename = os.path.basename(article_path)
        print("  ⚠️ 未找到 slug 字段，使用原文件名")

    # 写入文件
    target_path = os.path.join(target_dir, new_filename)
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(final_content)

    print(f"  📄 文件名: {new_filename}")
    return target_path


# ==================== 置顶管理 ====================

def get_all_articles() -> list[str]:
    """获取博客目录下所有文章"""
    articles = []
    if not os.path.exists(BLOG_DIR):
        print(f"❌ 博客目录不存在: {BLOG_DIR}")
        return articles

    for root, dirs, files in os.walk(BLOG_DIR):
        # 跳过 images 目录
        if "images" in root:
            continue
        for file in files:
            if file.endswith(".md"):
                articles.append(os.path.join(root, file))

    return sorted(articles)


def get_article_info(article_path: str) -> dict:
    """获取文章关键信息：title, slug, pinned"""
    frontmatter, _ = read_article(article_path)
    title = parse_frontmatter_field(frontmatter, "title")
    slug = parse_frontmatter_field(frontmatter, "slug")

    # 检查 pinned 状态
    pinned_match = re.search(r'^pinned:\s*(true|false)', frontmatter, re.MULTILINE)
    pinned = pinned_match.group(1) == "true" if pinned_match else False

    return {
        "path": article_path,
        "title": title,
        "slug": slug,
        "pinned": pinned
    }


def list_pinned_articles() -> list[dict]:
    """列出所有置顶文章"""
    articles = get_all_articles()
    pinned_articles = []

    for article_path in articles:
        info = get_article_info(article_path)
        if info["pinned"]:
            pinned_articles.append(info)

    return pinned_articles


def search_articles(keyword: str) -> list[dict]:
    """搜索文章（匹配 title 或 slug）"""
    articles = get_all_articles()
    results = []
    keyword_lower = keyword.lower()

    for article_path in articles:
        info = get_article_info(article_path)
        # 匹配 title 或 slug
        if keyword_lower in info["title"].lower() or keyword_lower in info["slug"].lower():
            results.append(info)

    return results


def set_pinned_status(article_path: str, pinned: bool) -> bool:
    """设置文章置顶状态"""
    with open(article_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 提取 frontmatter
    match = re.match(r'^(---\s*\n)(.*?)(\n---\s*\n)', content, re.DOTALL)
    if not match:
        print(f"❌ 文章没有 frontmatter: {article_path}")
        return False

    fm_start, frontmatter, fm_end = match.groups()
    body = content[match.end():]

    # 检查是否已有 pinned 字段
    pinned_pattern = r'^pinned:\s*(true|false)\s*$'
    has_pinned = re.search(pinned_pattern, frontmatter, re.MULTILINE)

    if pinned:
        # 设置置顶
        if has_pinned:
            # 更新现有 pinned 值
            frontmatter = re.sub(pinned_pattern, "pinned: true", frontmatter, flags=re.MULTILINE)
        else:
            # 在 updated 字段后添加 pinned
            updated_pattern = r'^(updated:\s*\d{4}-\d{2}-\d{2})\s*$'
            if re.search(updated_pattern, frontmatter, re.MULTILINE):
                frontmatter = re.sub(updated_pattern, r"\1\npinned: true", frontmatter, flags=re.MULTILINE)
            else:
                # 在 frontmatter 末尾添加
                frontmatter = frontmatter.rstrip() + "\npinned: true"
    else:
        # 取消置顶
        if has_pinned:
            # 移除 pinned 行
            frontmatter = re.sub(r'^pinned:\s*(true|false)\s*\n?', '', frontmatter, flags=re.MULTILINE)
        else:
            print(f"  ℹ️ 文章未置顶，无需取消: {article_path}")
            return True

    # 写回文件
    new_content = f"{fm_start}{frontmatter.rstrip()}{fm_end}{body}"
    with open(article_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    return True


# ==================== CLI ====================

def main():
    parser = argparse.ArgumentParser(description="Astro 博客文章发布工具")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 扫描命令
    scan_parser = subparsers.add_parser("scan", help="扫描待处理目录")

    # 读取命令
    read_parser = subparsers.add_parser("read", help="读取文章内容")
    read_parser.add_argument("article", help="文章路径")

    # 写入命令
    write_parser = subparsers.add_parser("write", help="写入文章")
    write_parser.add_argument("article", help="原文章路径")
    write_parser.add_argument("--category", required=True, help="分类")
    write_parser.add_argument("--frontmatter", required=True, help="Frontmatter 内容")
    write_parser.add_argument("--body", help="正文内容（可选，用于标点修正后的正文）")

    # 归档命令
    archive_parser = subparsers.add_parser("archive", help="归档原文件")
    archive_parser.add_argument("article", help="文章路径")

    # 置顶管理命令
    list_pinned_parser = subparsers.add_parser("list-pinned", help="列出所有置顶文章")

    search_parser = subparsers.add_parser("search", help="搜索文章（匹配 title 或 slug）")
    search_parser.add_argument("keyword", help="搜索关键词")

    set_pinned_parser = subparsers.add_parser("set-pinned", help="设置文章置顶状态")
    set_pinned_parser.add_argument("article", help="文章路径")
    set_pinned_parser.add_argument("--status", type=lambda x: x.lower() == "true", required=True,
                                    help="置顶状态: true 或 false")

    args = parser.parse_args()

    if args.command == "scan":
        articles = scan_drafts()
        if not articles:
            print("📭 待处理目录为空")
            return
        print(f"📄 找到 {len(articles)} 篇文章:")
        for i, article in enumerate(articles, 1):
            print(f"  {i}. {article}")

    elif args.command == "read":
        if not os.path.exists(args.article):
            print(f"❌ 文件不存在: {args.article}")
            return
        frontmatter, body = read_article(args.article)
        print(f"FRONTMATTER_START\n{frontmatter}\nFRONTMATTER_END")
        print(f"BODY_START\n{body}\nBODY_END")

    elif args.command == "write":
        if not os.path.exists(args.article):
            print(f"❌ 文件不存在: {args.article}")
            return
        # 读取原文正文和现有 frontmatter
        existing_fm, body = read_article(args.article)
        has_existing_fm = bool(existing_fm.strip())
        # 如果传入了修正后的正文，使用修正后的版本
        if args.body:
            body = args.body
            print("  📝 使用修正后的正文")
        target = write_article(args.article, args.category, args.frontmatter, body, has_existing_fm)
        print(f"✅ 已保存: {target}")

    elif args.command == "archive":
        if not os.path.exists(args.article):
            print(f"❌ 文件不存在: {args.article}")
            return
        result = archive_article(args.article)
        if result:
            print(f"✅ 已归档到: {result}")
        # 博客目录中的文章会跳过归档，已在函数内打印提示

    elif args.command == "list-pinned":
        pinned_articles = list_pinned_articles()
        if not pinned_articles:
            print("📭 当前没有置顶文章")
            return
        print(f"📌 找到 {len(pinned_articles)} 篇置顶文章:")
        for i, article in enumerate(pinned_articles, 1):
            print(f"  {i}. {article['title']}")
            print(f"     slug: {article['slug']}")
            print(f"     path: {article['path']}")

    elif args.command == "search":
        results = search_articles(args.keyword)
        if not results:
            print(f"📭 未找到匹配 '{args.keyword}' 的文章")
            return
        print(f"🔍 找到 {len(results)} 篇匹配文章:")
        for i, article in enumerate(results, 1):
            pinned_mark = "📌 " if article["pinned"] else ""
            print(f"  {i}. {pinned_mark}{article['title']}")
            print(f"     slug: {article['slug']}")
            print(f"     path: {article['path']}")

    elif args.command == "set-pinned":
        if not os.path.exists(args.article):
            print(f"❌ 文件不存在: {args.article}")
            return
        info = get_article_info(args.article)
        success = set_pinned_status(args.article, args.status)
        if success:
            action = "置顶" if args.status else "取消置顶"
            print(f"✅ 已{action}: {info['title']}")


if __name__ == "__main__":
    main()