#!/usr/bin/env python3
"""
检查和分析 JSONL 文件的工具

用法:
    python inspect_jsonl.py online_query_etl_100.jsonl
"""

import argparse
import json
import sys
from collections import Counter


def analyze_jsonl(file_path, show_samples=True, num_samples=3):
    """分析 JSONL 文件"""

    print("=" * 60)
    print(f"  分析文件: {file_path}")
    print("=" * 60)
    print()

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return False

    # 基本信息
    print("📊 基本信息:")
    print(f"  总对话数: {len(lines)}")
    print()

    # 统计信息
    turns_distribution = Counter()
    total_user_messages = 0
    total_assistant_messages = 0
    user_content_lengths = []
    assistant_content_lengths = []

    valid_count = 0
    invalid_lines = []

    for i, line in enumerate(lines, 1):
        try:
            messages = json.loads(line.strip())

            if not isinstance(messages, list):
                invalid_lines.append((i, "不是列表格式"))
                continue

            # 统计轮数
            turns = len(messages)
            turns_distribution[turns] += 1

            # 统计消息
            for msg in messages:
                if not isinstance(msg, dict):
                    continue

                role = msg.get('role', '')
                content = msg.get('content', '')

                if role == 'user':
                    total_user_messages += 1
                    user_content_lengths.append(len(content))
                elif role == 'assistant':
                    total_assistant_messages += 1
                    assistant_content_lengths.append(len(content))

            valid_count += 1

        except json.JSONDecodeError as e:
            invalid_lines.append((i, f"JSON 解析错误: {e}"))
        except Exception as e:
            invalid_lines.append((i, f"未知错误: {e}"))

    # 显示统计
    print("✅ 有效性:")
    print(f"  有效对话: {valid_count}")
    if invalid_lines:
        print(f"  ⚠️  无效行数: {len(invalid_lines)}")
        print()
        print("  无效行详情:")
        for line_num, error in invalid_lines[:5]:
            print(f"    行 {line_num}: {error}")
        if len(invalid_lines) > 5:
            print(f"    ... 还有 {len(invalid_lines) - 5} 个错误")
    print()

    print("💬 消息统计:")
    print(f"  用户消息数: {total_user_messages}")
    print(f"  助手消息数: {total_assistant_messages}")
    print(f"  总消息数: {total_user_messages + total_assistant_messages}")
    print()

    print("🔢 对话轮数分布:")
    for turns in sorted(turns_distribution.keys()):
        count = turns_distribution[turns]
        percentage = (count / len(lines)) * 100
        bar = "█" * int(percentage / 2)
        print(f"  {turns:2d} 轮: {count:3d} 条 ({percentage:5.1f}%) {bar}")
    print()

    # 内容长度统计
    if user_content_lengths:
        print("📏 用户消息长度统计 (字符数):")
        print(f"  平均: {sum(user_content_lengths) / len(user_content_lengths):.1f}")
        print(f"  最小: {min(user_content_lengths)}")
        print(f"  最大: {max(user_content_lengths)}")
        print()

    if assistant_content_lengths:
        print("📏 助手消息长度统计 (字符数):")
        print(f"  平均: {sum(assistant_content_lengths) / len(assistant_content_lengths):.1f}")
        print(f"  最小: {min(assistant_content_lengths)}")
        print(f"  最大: {max(assistant_content_lengths)}")
        print()

    # 显示示例
    if show_samples and valid_count > 0:
        print("=" * 60)
        print(f"  示例对话 (前 {num_samples} 条)")
        print("=" * 60)

        sample_count = 0
        for i, line in enumerate(lines, 1):
            if sample_count >= num_samples:
                break

            try:
                messages = json.loads(line.strip())
                if not isinstance(messages, list):
                    continue

                print()
                print(f"📝 对话 #{i} ({len(messages)} 轮):")
                print("-" * 60)

                for j, msg in enumerate(messages[:4], 1):  # 只显示前4条消息
                    role = msg.get('role', '未知')
                    content = msg.get('content', '')

                    # 截断过长的内容
                    if len(content) > 100:
                        content = content[:100] + "..."

                    role_emoji = "👤" if role == "user" else "🤖"
                    print(f"{role_emoji} {role}:")
                    print(f"   {content}")
                    print()

                if len(messages) > 4:
                    print(f"   ... 还有 {len(messages) - 4} 条消息")

                sample_count += 1

            except Exception:
                continue

    print("=" * 60)
    return valid_count > 0


def main():
    parser = argparse.ArgumentParser(
        description="检查和分析 JSONL 文件",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "file",
        type=str,
        help="JSONL 文件路径"
    )
    parser.add_argument(
        "--no-samples",
        action="store_true",
        help="不显示示例对话"
    )
    parser.add_argument(
        "--num-samples",
        type=int,
        default=3,
        help="显示的示例数量 (默认: 3)"
    )

    args = parser.parse_args()

    success = analyze_jsonl(
        args.file,
        show_samples=not args.no_samples,
        num_samples=args.num_samples
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
