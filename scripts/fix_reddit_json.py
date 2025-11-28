#!/usr/bin/env python3
"""修复Reddit JSON文件中的格式问题"""

import json
import re
from pathlib import Path

def fix_json_content(content: str) -> str:
    """修复JSON内容中的常见问题"""
    # 移除可能的BOM
    if content.startswith('\ufeff'):
        content = content[1:]

    # 统一换行符
    content = content.replace('\r\n', '\n').replace('\r', '\n')

    # 修复未转义的控制字符
    # 在JSON字符串中，这些字符需要转义
    def escape_control_chars(match):
        s = match.group(0)
        # 保留已转义的字符
        result = []
        i = 0
        while i < len(s):
            if s[i] == '\\' and i + 1 < len(s):
                # 已转义的字符，保留
                result.append(s[i:i+2])
                i += 2
            elif s[i] == '\n':
                result.append('\\n')
                i += 1
            elif s[i] == '\r':
                result.append('\\r')
                i += 1
            elif s[i] == '\t':
                result.append('\\t')
                i += 1
            elif ord(s[i]) < 32:
                # 其他控制字符
                result.append(f'\\u{ord(s[i]):04x}')
                i += 1
            else:
                result.append(s[i])
                i += 1
        return ''.join(result)

    # 查找所有字符串值并修复
    # 匹配 "..." 形式的字符串
    fixed_content = []
    in_string = False
    escape_next = False
    string_start = 0

    i = 0
    while i < len(content):
        char = content[i]

        if escape_next:
            escape_next = False
            i += 1
            continue

        if char == '\\' and in_string:
            escape_next = True
            i += 1
            continue

        if char == '"' and not escape_next:
            if in_string:
                # 字符串结束
                in_string = False
            else:
                # 字符串开始
                in_string = True

        i += 1

    return content


def load_and_fix_reddit_json(file_path: Path) -> dict | None:
    """加载并修复Reddit JSON文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 尝试直接解析
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # 修复常见问题
        content = fix_json_content(content)

        # 再次尝试解析
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            # 找到错误位置附近的内容
            pos = e.pos
            context_start = max(0, pos - 100)
            context_end = min(len(content), pos + 100)
            error_context = content[context_start:context_end]

            print(f"  错误位置附近: ...{error_context}...")

            # 尝试手动修复常见问题
            # 有时候是引号内的换行符没有正确转义
            lines = content.split('\n')
            fixed_lines = []
            for line in lines:
                # 检查是否有未闭合的字符串
                fixed_lines.append(line)

            return None

    except Exception as e:
        print(f"  读取文件失败: {e}")
        return None


def extract_posts_manually(file_path: Path) -> dict | None:
    """手动提取帖子数据"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 尝试使用正则表达式提取关键字段
        post = {}

        # 提取标题
        title_match = re.search(r'"title":\s*"([^"]*(?:\\"[^"]*)*)"', content)
        if title_match:
            post['title'] = title_match.group(1).replace('\\"', '"')

        # 提取内容
        content_match = re.search(r'"content":\s*"([^"]*(?:\\"[^"]*)*)"', content)
        if content_match:
            post['content'] = content_match.group(1).replace('\\"', '"')

        # 提取作者
        author_match = re.search(r'"author":\s*"([^"]*)"', content)
        if author_match:
            post['author'] = author_match.group(1)

        # 提取URL
        url_match = re.search(r'"url":\s*"([^"]*)"', content)
        if url_match:
            post['url'] = url_match.group(1)

        # 提取subreddit
        sub_match = re.search(r'"subreddit":\s*"([^"]*)"', content)
        if sub_match:
            post['subreddit'] = sub_match.group(1)

        # 提取创建时间
        created_match = re.search(r'"created_at":\s*"([^"]*)"', content)
        if created_match:
            post['created_at'] = created_match.group(1)

        # 提取评论数
        count_match = re.search(r'"comment_count":\s*(\d+)', content)
        if count_match:
            post['comment_count'] = int(count_match.group(1))

        # 提取评论 - 这个比较复杂
        comments = []
        comment_pattern = re.compile(
            r'\{\s*"author":\s*"([^"]*)"[^}]*"content":\s*"([^"]*(?:\\"[^"]*)*)"[^}]*"upvotes":\s*(\d+)',
            re.DOTALL
        )

        for match in comment_pattern.finditer(content):
            comments.append({
                'author': match.group(1),
                'content': match.group(2).replace('\\"', '"'),
                'upvotes': int(match.group(3)),
                'created_at': ''
            })

        if comments:
            post['comments'] = comments

        post['platform'] = 'reddit'

        if post.get('title'):
            return post
        return None

    except Exception as e:
        print(f"  手动提取失败: {e}")
        return None


def main():
    raw_dir = Path("data/raw")

    print("=" * 60)
    print("修复Reddit JSON文件")
    print("=" * 60)

    fixed_posts = []

    for i in range(1, 11):
        file_path = raw_dir / f"reddit_post_{i}.json"
        if not file_path.exists():
            continue

        print(f"\n处理 {file_path.name}...")

        # 首先尝试正常加载
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"  ✓ 正常加载成功")
            fixed_posts.append(data)
            continue
        except json.JSONDecodeError as e:
            print(f"  JSON错误: {e}")

        # 尝试手动提取
        data = extract_posts_manually(file_path)
        if data:
            print(f"  ✓ 手动提取成功: {data.get('title', '')[:50]}...")
            print(f"    评论数: {len(data.get('comments', []))}")
            fixed_posts.append(data)
        else:
            print(f"  ✗ 无法修复")

    # 保存修复后的数据
    if fixed_posts:
        output_path = raw_dir / "reddit_posts_fixed.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(fixed_posts, f, ensure_ascii=False, indent=2)
        print(f"\n✓ 保存修复后的数据到: {output_path}")
        print(f"  成功修复: {len(fixed_posts)} 个帖子")


if __name__ == "__main__":
    main()
