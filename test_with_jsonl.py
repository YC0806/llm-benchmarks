#!/usr/bin/env python3
"""
使用 online_query_etl_100.jsonl 测试大模型 API 的便捷脚本

用法:
    python test_with_jsonl.py --help
    python test_with_jsonl.py --model gpt-4 --num-prompts 10
"""

import argparse
import json
import os
import subprocess
import sys


def count_jsonl_lines(file_path):
    """统计 JSONL 文件的行数"""
    with open(file_path, 'r') as f:
        return sum(1 for _ in f)


def validate_jsonl(file_path, num_lines=3):
    """验证 JSONL 文件格式"""
    try:
        with open(file_path, 'r') as f:
            for i, line in enumerate(f):
                if i >= num_lines:
                    break
                json.loads(line)
        return True
    except json.JSONDecodeError as e:
        print(f"❌ JSONL 格式错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="使用 online_query_etl_100.jsonl 测试大模型 API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基础测试（10条数据）
  python test_with_jsonl.py --model gpt-4

  # 测试50条，请求速率5 RPS
  python test_with_jsonl.py --model gpt-4 --num-prompts 50 --request-rate 5

  # 使用完整 API URL（自动解析 base-url 和 endpoint）
  python test_with_jsonl.py \\
      --model deepseek-chat \\
      --api-url https://api.deepseek.com/v1/chat/completions \\
      --num-prompts 20

  # 使用基础 URL（使用默认 endpoint）
  python test_with_jsonl.py \\
      --model Qwen/Qwen2.5-7B-Instruct \\
      --api-url http://localhost:8000 \\
      --backend vllm \\
      --num-prompts 20

  # 保存结果并指定输出目录
  python test_with_jsonl.py \\
      --model gpt-4 \\
      --num-prompts 100 \\
      --save-result \\
      --result-dir ./my_results

支持的后端类型:
  - openai-chat: OpenAI Chat Completions API
  - openai: OpenAI Completions API
  - vllm: vLLM OpenAI 兼容服务器
  - tgi: HuggingFace TGI
  - lmdeploy: LMDeploy
  - sglang: SGLang
  - tensorrt-llm: TensorRT-LLM
        """
    )

    # 必需参数
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4",
        help="模型名称 (默认: gpt-4)"
    )

    # API 配置
    parser.add_argument(
        "--api-url",
        type=str,
        default="https://api.openai.com",
        help="API URL (可以是基础 URL 或完整 URL，默认: https://api.openai.com)"
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default=None,
        help="[已弃用] 使用 --api-url 代替"
    )
    parser.add_argument(
        "--backend",
        type=str,
        default="openai-chat",
        choices=["openai-chat", "openai", "vllm", "tgi", "lmdeploy",
                 "sglang", "tensorrt-llm", "llama.cpp", "deepspeed-mii"],
        help="后端类型 (默认: openai-chat)"
    )

    # 数据集配置
    parser.add_argument(
        "--dataset-path",
        type=str,
        default="online_query_etl_100.jsonl",
        help="JSONL 数据文件路径 (默认: online_query_etl_100.jsonl)"
    )
    parser.add_argument(
        "--num-prompts",
        type=int,
        default=10,
        help="测试的对话数量 (默认: 10)"
    )

    # 性能参数
    parser.add_argument(
        "--request-rate",
        type=float,
        default=1.0,
        help="请求速率 (RPS, 默认: 1.0)"
    )
    parser.add_argument(
        "--max-concurrency",
        type=int,
        default=None,
        help="最大并发请求数"
    )

    # 输出配置
    parser.add_argument(
        "--save-result",
        action="store_true",
        help="保存测试结果到文件"
    )
    parser.add_argument(
        "--result-dir",
        type=str,
        default="./results",
        help="结果保存目录 (默认: ./results)"
    )
    parser.add_argument(
        "--result-filename",
        type=str,
        default=None,
        help="结果文件名（可选）"
    )

    # 其他选项
    parser.add_argument(
        "--disable-tqdm",
        action="store_true",
        help="禁用进度条"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="详细输出"
    )

    args = parser.parse_args()

    # 处理 base-url 的向后兼容
    if args.base_url:
        print("⚠️  警告: --base-url 已弃用，请使用 --api-url")
        args.api_url = args.base_url

    # 检查数据文件
    if not os.path.exists(args.dataset_path):
        print(f"❌ 错误: 找不到数据文件 '{args.dataset_path}'")
        sys.exit(1)

    print("=" * 50)
    print("  LLM API 测试")
    print("=" * 50)
    print()

    # 验证 JSONL 格式
    print("📝 验证数据文件格式...")
    if not validate_jsonl(args.dataset_path):
        sys.exit(1)

    # 统计文件信息
    total_lines = count_jsonl_lines(args.dataset_path)
    print(f"✓ 数据文件格式正确")
    print()

    # 显示配置
    print("📊 测试配置:")
    print(f"  数据文件: {args.dataset_path}")
    print(f"  总对话数: {total_lines}")
    print(f"  测试数量: {args.num_prompts}")
    print(f"  模型: {args.model}")
    print(f"  API地址: {args.api_url}")
    print(f"  后端类型: {args.backend}")
    print(f"  请求速率: {args.request_rate} RPS")
    if args.max_concurrency:
        print(f"  最大并发: {args.max_concurrency}")
    if args.save_result:
        print(f"  结果保存: {args.result_dir}")
    print()

    # 检查数量
    if args.num_prompts > total_lines:
        print(f"⚠️  警告: 请求数量({args.num_prompts})超过文件行数({total_lines})")
        args.num_prompts = total_lines
        print(f"  已调整为: {args.num_prompts}")
        print()

    # 检查 API Key（如果是 OpenAI）
    if "openai" in args.backend and not os.getenv("OPENAI_API_KEY"):
        print("⚠️  警告: OPENAI_API_KEY 环境变量未设置")
        print("请先设置: export OPENAI_API_KEY='your-api-key'")
        print()
        response = input("是否继续? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)
        print()

    # 解析 API URL 为 base-url 和 endpoint
    # 支持输入完整 URL (如 https://api.openai.com/v1/chat/completions)
    # 或基础 URL (如 https://api.openai.com)
    from urllib.parse import urlparse

    parsed_url = urlparse(args.api_url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    endpoint = parsed_url.path if parsed_url.path else None

    # 如果用户提供了完整的 endpoint 路径，使用它
    # 否则让 benchmark_serving.py 使用默认 endpoint

    # 构建命令
    cmd = [
        "python", "benchmark_serving.py",
        "--backend", args.backend,
        "--model", args.model,
        "--base-url", base_url,
        "--dataset-name", "custom",
        "--dataset-path", args.dataset_path,
        "--num-prompts", str(args.num_prompts),
        "--request-rate", str(args.request_rate),
    ]

    # 如果提供了非默认的 endpoint，添加它
    if endpoint and endpoint not in ['', '/']:
        cmd.extend(["--endpoint", endpoint])

    if args.max_concurrency:
        cmd.extend(["--max-concurrency", str(args.max_concurrency)])

    if args.save_result:
        cmd.append("--save-result")
        cmd.extend(["--result-dir", args.result_dir])
        if args.result_filename:
            cmd.extend(["--result-filename", args.result_filename])

    if args.disable_tqdm:
        cmd.append("--disable-tqdm")

    print("=" * 50)
    print("  🚀 开始测试...")
    print("=" * 50)
    print()

    if args.verbose:
        print("执行命令:")
        print(" ".join(cmd))
        print()

    # 执行测试
    try:
        result = subprocess.run(cmd, check=True)
        print()
        print("=" * 50)
        print("  ✅ 测试完成！")
        print("=" * 50)

        if args.save_result:
            print()
            print(f"📁 结果已保存到 {args.result_dir}/ 目录")
            print()
            print("查看结果:")
            print(f"  ls -lt {args.result_dir}/*.json | head -1")

    except subprocess.CalledProcessError as e:
        print()
        print("=" * 50)
        print("  ❌ 测试失败")
        print("=" * 50)
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        print()
        print()
        print("⚠️  测试被用户中断")
        sys.exit(130)


if __name__ == "__main__":
    main()
