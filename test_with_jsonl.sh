#!/bin/bash

# 使用 online_query_etl_100.jsonl 测试大模型 API
# 使用方法：./test_with_jsonl.sh

set -e

echo "=========================================="
echo "  LLM API 测试脚本"
echo "  数据集: online_query_etl_100.jsonl"
echo "=========================================="
echo ""

# 配置参数
JSONL_FILE="online_query_etl_100.jsonl"
MODEL="gpt-4"  # 修改为你的模型名称
BASE_URL="https://api.openai.com"  # 修改为你的 API 地址
BACKEND="openai-chat"  # 使用 openai-chat 后端

# 检查文件是否存在
if [ ! -f "$JSONL_FILE" ]; then
    echo "❌ 错误: 找不到文件 $JSONL_FILE"
    exit 1
fi

# 检查环境变量
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  警告: OPENAI_API_KEY 环境变量未设置"
    echo "请设置 API Key:"
    echo "  export OPENAI_API_KEY='your-api-key'"
    echo ""
    read -p "是否继续？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "📊 测试配置:"
echo "  数据文件: $JSONL_FILE"
echo "  模型: $MODEL"
echo "  API 地址: $BASE_URL"
echo "  后端类型: $BACKEND"
echo ""

# 统计文件信息
TOTAL_LINES=$(wc -l < "$JSONL_FILE")
echo "  总对话数: $TOTAL_LINES"
echo ""

# 询问测试参数
read -p "请输入要测试的对话数量 [1-$TOTAL_LINES, 默认 10]: " NUM_PROMPTS
NUM_PROMPTS=${NUM_PROMPTS:-10}

read -p "请输入请求速率 (RPS, 默认 1): " REQUEST_RATE
REQUEST_RATE=${REQUEST_RATE:-1}

read -p "是否保存结果？(y/n, 默认 y): " SAVE_RESULT
SAVE_RESULT=${SAVE_RESULT:-y}

echo ""
echo "=========================================="
echo "  开始测试..."
echo "=========================================="
echo ""

# 构建命令
CMD="python benchmark_serving.py \
    --backend $BACKEND \
    --model $MODEL \
    --base-url $BASE_URL \
    --dataset-name custom \
    --dataset-path $JSONL_FILE \
    --num-prompts $NUM_PROMPTS \
    --request-rate $REQUEST_RATE"

# 添加可选参数
if [[ $SAVE_RESULT =~ ^[Yy]$ ]]; then
    CMD="$CMD --save-result --result-dir ./results"
fi

# 执行测试
echo "🚀 执行命令:"
echo "$CMD"
echo ""

eval $CMD

echo ""
echo "=========================================="
echo "  ✅ 测试完成！"
echo "=========================================="

if [[ $SAVE_RESULT =~ ^[Yy]$ ]]; then
    echo ""
    echo "📁 结果已保存到 ./results/ 目录"
    echo ""
    echo "查看最新结果:"
    echo "  ls -lt ./results/*.json | head -1"
fi
