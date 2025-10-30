#!/usr/bin/env python3
"""
测试数据集加载功能（无需 API key）
"""

from benchmark_dataset import CustomDataset
from backend_request_func import estimate_token_count

def test_custom_dataset():
    print("=" * 70)
    print("测试 CustomDataset 加载和采样")
    print("=" * 70)

    # Load dataset
    dataset = CustomDataset(dataset_path='online_query_etl_100.jsonl')
    print(f"✓ 成功加载数据集: {len(dataset.data)} 条对话")

    # Sample requests
    num_samples = 5
    samples = dataset.sample(num_requests=num_samples, output_len=256)
    print(f"✓ 成功采样: {len(samples)} 条请求\n")

    # Analyze samples
    for i, sample in enumerate(samples, 1):
        print(f"样本 {i}:")
        print(f"  类型: {type(sample.prompt)}")

        if isinstance(sample.prompt, list):
            # Messages format
            print(f"  消息数: {len(sample.prompt)} 条")
            print(f"  对话类型: 多轮对话" if len(sample.prompt) > 2 else "  对话类型: 单轮对话")

            # Show first and last message
            if len(sample.prompt) > 0:
                first_msg = sample.prompt[0]
                print(f"  首条消息: [{first_msg['role']}] {first_msg['content'][:80]}...")

            if len(sample.prompt) > 1:
                last_msg = sample.prompt[-1]
                print(f"  末条消息: [{last_msg['role']}] {last_msg['content'][:80]}...")
        else:
            # String format
            print(f"  提示词: {str(sample.prompt)[:100]}...")

        print(f"  估算 token 数: {sample.prompt_len}")
        print(f"  期望输出长度: {sample.expected_output_len}")
        print()

    # Statistics
    total_tokens = sum(s.prompt_len for s in samples)
    avg_tokens = total_tokens / len(samples)

    print("=" * 70)
    print("统计信息:")
    print(f"  总 token 数: {total_tokens}")
    print(f"  平均 token 数: {avg_tokens:.1f}")
    print(f"  最小 token 数: {min(s.prompt_len for s in samples)}")
    print(f"  最大 token 数: {max(s.prompt_len for s in samples)}")
    print("=" * 70)

    print("\n✅ 所有测试通过！数据集加载和采样功能正常工作。")
    print("✅ 可以使用以下命令进行实际 API 测试：")
    print("   export OPENAI_API_KEY='your-key'")
    print("   python test_with_jsonl.py --model gpt-4 --num-prompts 5")

if __name__ == "__main__":
    test_custom_dataset()
