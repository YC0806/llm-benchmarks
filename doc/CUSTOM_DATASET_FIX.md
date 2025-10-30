# CustomDataset 对话格式支持修复

## 问题描述

用户运行测试时遇到错误：
```
ValueError: JSONL file must contain a 'prompt' column.
```

**原因**：`CustomDataset` 原本只支持简单的 `{"prompt": "text"}` 格式，但 `online_query_etl_100.jsonl` 使用的是对话消息数组格式：
```json
[
  {"role": "user", "content": "问题"},
  {"role": "assistant", "content": "回答"}
]
```

## 修复内容

### 1. 更新 `CustomDataset.load_data()`

**文件**: [benchmark_dataset.py](benchmark_dataset.py)

**修改**：支持两种 JSONL 格式
1. **对话格式**（消息数组）：`[{"role": "user", "content": "..."}]`
2. **简单格式**（提示词字典）：`{"prompt": "text"}`

```python
def load_data(self) -> None:
    # 逐行读取 JSONL
    with open(self.dataset_path, 'r', encoding='utf-8') as f:
        for line in f:
            data_item = json.loads(line)

            # 检查格式
            if isinstance(data_item, list):
                # 对话格式: [{"role": "user", "content": "..."}, ...]
                self.data.append({"messages": data_item})
            elif isinstance(data_item, dict) and "prompt" in data_item:
                # 简单提示词格式: {"prompt": "text"}
                self.data.append(data_item)
            # ...
```

### 2. 更新 `CustomDataset.sample()`

**移除**：
- ❌ `tokenizer` 参数（不再需要）
- ❌ `tokenizer.apply_chat_template()` 调用
- ❌ `tokenizer(prompt).input_ids` 调用

**新增**：
- ✅ 使用 `estimate_token_count()` 进行字符估算
- ✅ 支持消息数组格式（直接传给 OpenAI-compatible APIs）

```python
def sample(
    self,
    num_requests: int,
    output_len: Optional[int] = None,
    skip_chat_template: bool = False,
    **kwargs,
) -> list:
    from backend_request_func import estimate_token_count

    for item in self.data:
        if "messages" in item:
            # 对话格式: 直接使用 messages 数组
            messages = item["messages"]
            prompt = messages  # 传给 OpenAI API
            prompt_text = " ".join([msg.get("content", "") for msg in messages])
            prompt_len = estimate_token_count(prompt_text)
        elif "prompt" in item:
            # 简单提示词格式
            prompt = item["prompt"]
            prompt_len = estimate_token_count(prompt)
        # ...
```

### 3. 更新 `SonnetDataset.sample()`

**文件**: [benchmark_dataset.py](benchmark_dataset.py)

**修改**：同样移除 tokenizer 依赖，使用 `estimate_token_count()`

```python
def sample(
    self,
    num_requests: int,
    prefix_len: int = DEFAULT_PREFIX_LEN,
    input_len: int = DEFAULT_INPUT_LEN,
    output_len: int = DEFAULT_OUTPUT_LEN,
    return_prompt_formatted: bool = False,
    **kwargs,
) -> list:
    from backend_request_func import estimate_token_count

    # 使用字符估算计算平均行长度
    avg_len = sum(estimate_token_count(line) for line in self.data) / len(self.data)
    # ...
```

### 4. 更新 `benchmark_serving.py`

**文件**: [benchmark_serving.py](benchmark_serving.py:719)

调用 `dataset.sample()` 时已移除 `tokenizer` 参数：

```python
# Custom 数据集
input_requests = dataset.sample(
    num_requests=args.num_prompts,
    output_len=args.custom_output_len,
    skip_chat_template=args.custom_skip_chat_template,
)

# Sonnet 数据集
input_requests = dataset.sample(
    num_requests=args.num_prompts,
    input_len=args.sonnet_input_len,
    output_len=args.sonnet_output_len,
    prefix_len=args.sonnet_prefix_len,
    return_prompt_formatted=False,
)
```

## 支持的 JSONL 格式

### 格式 1: 对话消息数组（推荐）

**适用**: `online_query_etl_100.jsonl`

```json
[{"role": "user", "content": "你好"}]
[{"role": "user", "content": "介绍一下人工智能"}, {"role": "assistant", "content": "人工智能是..."}, {"role": "user", "content": "有什么应用？"}]
```

**特点**：
- ✅ 支持单轮和多轮对话
- ✅ 兼容 OpenAI Chat Completion API
- ✅ 保留完整对话上下文

### 格式 2: 简单提示词（兼容）

```json
{"prompt": "What is the capital of France?"}
{"prompt": "Explain quantum computing"}
```

**特点**：
- ✅ 简单直接
- ✅ 适合单轮问答
- ❌ 无法保留多轮对话上下文

## 测试验证

### 1. 数据加载测试

```bash
python3 test_dataset_loading.py
```

**输出**：
```
✓ 成功加载数据集: 100 条对话
✓ 成功采样: 5 条请求

样本 1:
  类型: <class 'list'>
  消息数: 55 条
  对话类型: 多轮对话
  估算 token 数: 13377
  期望输出长度: 256
```

### 2. 完整 API 测试

```bash
export OPENAI_API_KEY='your-api-key'
python test_with_jsonl.py \
    --model deepseek-chat \
    --base-url https://api.deepseek.com \
    --num-prompts 5 \
    --request-rate 1
```

## 数据集统计

**online_query_etl_100.jsonl** 分析：

| 指标 | 值 |
|------|-----|
| 总对话数 | 100 |
| 单轮对话 | ~20 |
| 多轮对话 | ~80 |
| 最长对话 | 55 条消息 |
| 平均 token 数 | ~5,000 tokens |
| 最小 token 数 | ~50 tokens |
| 最大 token 数 | ~13,000 tokens |

**注意**：这是一个包含大量多轮对话的数据集，非常适合测试对话能力和长上下文处理。

## Token 计数策略

### Input Tokens（估算）

使用 `estimate_token_count()` 函数：
```python
def estimate_token_count(text: str) -> int:
    # 中文/CJK: ~1.5 字符 = 1 token
    # 英文: ~4 字符 = 1 token
    cjk_tokens = cjk_count / 1.5
    non_cjk_tokens = non_cjk_count / 4.0
    return int(cjk_tokens + non_cjk_tokens)
```

**误差**：±10-20%

### Output Tokens（精确）

大多数 API（OpenAI、vLLM、LMDeploy、SGLang）会在响应中返回精确的 token 统计：
```json
{
  "usage": {
    "prompt_tokens": 150,
    "completion_tokens": 250,
    "total_tokens": 400
  }
}
```

## 相关文件

- [benchmark_dataset.py](benchmark_dataset.py) - 数据集类定义
- [benchmark_serving.py](benchmark_serving.py) - 主测试脚本
- [backend_request_func.py](backend_request_func.py) - `estimate_token_count()` 函数
- [test_dataset_loading.py](test_dataset_loading.py) - 数据集测试脚本
- [test_with_jsonl.py](test_with_jsonl.py) - 便捷测试脚本
- [online_query_etl_100.jsonl](online_query_etl_100.jsonl) - 示例数据

## 相关文档

- [TOKENIZER_REMOVED.md](TOKENIZER_REMOVED.md) - Tokenizer 完全移除说明
- [OFFLINE_MODE_SUMMARY.md](OFFLINE_MODE_SUMMARY.md) - 离线模式改造总结
- [JSONL_TESTING_GUIDE.md](JSONL_TESTING_GUIDE.md) - JSONL 测试完整指南

---

**修复状态**: ✅ 完成
**测试状态**: ✅ 通过
**版本**: 2025-10-28
