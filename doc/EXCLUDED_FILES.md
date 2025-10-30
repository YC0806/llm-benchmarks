# 排除的文件说明

## benchmark_serving_structured_output.py

### 状态
❌ 此文件未移除 vLLM 依赖

### 原因
此文件专门用于测试 vLLM 的结构化输出功能，依赖于：
- `vllm.transformers_utils.tokenizer`
- `vllm.utils.FlexibleArgumentParser`
- `vllm.v1.structured_output.backend_xgrammar`

这些是 vLLM 特有的功能，无法在纯远程 API 模式下使用。

### 影响
- 该文件在远程 API 测试场景中不可用
- 不影响其他核心测试功能
- 如果需要结构化输出测试，需要：
  1. 安装 vLLM
  2. 使用 vLLM 本地部署
  3. 使用原始的 `benchmark_serving_structured_output.py`

### 替代方案
对于远程 API 的结构化输出测试，建议：
1. 使用 `benchmark_serving.py` 配合 OpenAI 的 JSON mode
2. 在请求中通过 `extra_body` 参数传递结构化要求
3. 后处理验证输出格式

### 示例（OpenAI JSON mode）
```bash
# 注意：这需要服务器支持 JSON mode
python benchmark_serving.py \
    --backend openai-chat \
    --model gpt-4 \
    --base-url https://api.openai.com \
    --dataset-name custom \
    --dataset-path prompts.jsonl
```

在 prompt 中指定 JSON 格式：
```jsonl
{"prompt": "Return the answer as JSON: {\"answer\": \"...\"}"}
```

## 建议
如果你的测试场景**不需要**结构化输出测试：
- ✅ 可以安全地忽略此文件
- ✅ 所有其他功能都已完全兼容远程 API 模式

如果你**确实需要**结构化输出测试：
- ⚠️ 需要保留 vLLM 环境
- ⚠️ 或者使用支持结构化输出的远程 API（如 OpenAI 的 JSON mode）
