# 使用 online_query_etl_100.jsonl 测试大模型 API

## 📋 数据集信息

**文件**: `online_query_etl_100.jsonl`
- **格式**: JSONL (JSON Lines)
- **对话数**: 100 条
- **内容**: 中文对话，涵盖计算机知识问答等多轮对话

### 数据格式
每行是一个 JSON 数组，包含多轮对话：
```json
[
  {"role": "user", "content": "第二代计算机采用什么作为逻辑元件"},
  {"role": "assistant", "content": "第二代计算机采用的逻辑元件是**晶体管**..."}
]
```

---

## 🚀 快速开始

### 方法 1: 使用 Python 脚本（推荐）

#### 基础测试（10条数据）
```bash
python test_with_jsonl.py --model gpt-4
```

#### 查看所有选项
```bash
python test_with_jsonl.py --help
```

#### 完整示例
```bash
# 测试 50 条数据，请求速率 5 RPS，保存结果
python test_with_jsonl.py \
    --model gpt-4 \
    --num-prompts 50 \
    --request-rate 5 \
    --save-result
```

### 方法 2: 使用 Shell 脚本
```bash
./test_with_jsonl.sh
```
脚本会交互式地询问你测试参数。

### 方法 3: 直接使用 benchmark_serving.py
```bash
python benchmark_serving.py \
    --backend openai-chat \
    --model gpt-4 \
    --base-url https://api.openai.com \
    --dataset-name custom \
    --dataset-path online_query_etl_100.jsonl \
    --num-prompts 10 \
    --request-rate 1
```

---

## 🔧 配置选项

### 必需参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--model` | 模型名称 | `gpt-4`, `gpt-3.5-turbo` |

### API 配置

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--base-url` | API 基础 URL | `https://api.openai.com` |
| `--backend` | 后端类型 | `openai-chat` |

**支持的后端类型**:
- `openai-chat`: OpenAI Chat Completions API
- `openai`: OpenAI Completions API
- `vllm`: vLLM OpenAI 兼容服务器
- `tgi`: HuggingFace TGI
- `lmdeploy`: LMDeploy
- `sglang`: SGLang
- `tensorrt-llm`: TensorRT-LLM

### 测试参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--num-prompts` | 测试的对话数量 | 10 |
| `--request-rate` | 请求速率 (RPS) | 1.0 |
| `--max-concurrency` | 最大并发数 | 无限制 |

### 输出选项

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--save-result` | 保存测试结果 | 不保存 |
| `--result-dir` | 结果保存目录 | `./results` |
| `--disable-tqdm` | 禁用进度条 | 显示进度条 |

---

## 💡 使用示例

### 示例 1: 测试 OpenAI API
```bash
# 设置 API Key
export OPENAI_API_KEY="sk-..."

# 运行测试
python test_with_jsonl.py \
    --model gpt-4 \
    --num-prompts 20 \
    --request-rate 2 \
    --save-result
```

### 示例 2: 测试本地 vLLM 服务器
```bash
# 假设 vLLM 服务器运行在 http://localhost:8000
python test_with_jsonl.py \
    --model Qwen/Qwen2.5-7B-Instruct \
    --base-url http://localhost:8000 \
    --backend vllm \
    --num-prompts 100 \
    --request-rate 10
```

### 示例 3: 性能压测（最大吞吐量）
```bash
python test_with_jsonl.py \
    --model gpt-4 \
    --num-prompts 100 \
    --request-rate inf \
    --max-concurrency 50 \
    --save-result
```

### 示例 4: 稳定性测试（固定速率）
```bash
python test_with_jsonl.py \
    --model gpt-4 \
    --num-prompts 100 \
    --request-rate 5 \
    --save-result \
    --result-dir ./stability_test
```

### 示例 5: 测试自定义 API
```bash
python test_with_jsonl.py \
    --model your-model-name \
    --base-url https://your-api.com \
    --backend openai-chat \
    --num-prompts 30 \
    --request-rate 3
```

---

## 📊 结果解读

测试完成后会显示以下指标：

### 核心指标

| 指标 | 说明 | 单位 |
|------|------|------|
| **TTFT** | Time to First Token (首 token 时间) | 毫秒 |
| **TPOT** | Time per Output Token (每 token 时间) | 毫秒 |
| **ITL** | Inter-token Latency (token 间延迟) | 毫秒 |
| **E2EL** | End-to-end Latency (端到端延迟) | 毫秒 |
| **Throughput** | 吞吐量 | tokens/s 或 requests/s |

### 示例输出
```
Successful requests:                     100
Benchmark duration (s):                  50.23
Total input tokens:                      15230
Total generated tokens:                  45680
Request throughput (req/s):              1.99
Input token throughput (tok/s):          303.15
Output token throughput (tok/s):         909.45
---------------Time to First Token----------------
Mean TTFT (ms):                          234.56
Median TTFT (ms):                        198.23
P99 TTFT (ms):                           567.89
```

---

## 🔍 常见问题

### 问题 1: API Key 未设置
```
⚠️  警告: OPENAI_API_KEY 环境变量未设置
```

**解决方案**:
```bash
export OPENAI_API_KEY="your-api-key"
```

### 问题 2: 找不到数据文件
```
❌ 错误: 找不到数据文件 'online_query_etl_100.jsonl'
```

**解决方案**:
```bash
# 确保文件在当前目录
ls online_query_etl_100.jsonl

# 或指定完整路径
python test_with_jsonl.py \
    --dataset-path /path/to/online_query_etl_100.jsonl
```

### 问题 3: 连接超时
```
ConnectionError: Connection timeout
```

**解决方案**:
1. 检查 API 地址是否正确
2. 检查网络连接
3. 降低请求速率: `--request-rate 0.5`

### 问题 4: 速率限制
```
Rate limit exceeded
```

**解决方案**:
```bash
# 降低请求速率
python test_with_jsonl.py \
    --model gpt-4 \
    --request-rate 0.5  # 每秒 0.5 个请求
```

---

## 📈 高级用法

### 1. 自定义数据子集
测试前 20 条对话：
```bash
head -20 online_query_etl_100.jsonl > test_subset.jsonl

python test_with_jsonl.py \
    --dataset-path test_subset.jsonl \
    --num-prompts 20
```

### 2. 批量测试不同配置
```bash
#!/bin/bash
# 测试不同的请求速率
for rate in 1 5 10 20; do
    echo "Testing with rate: $rate RPS"
    python test_with_jsonl.py \
        --model gpt-4 \
        --num-prompts 50 \
        --request-rate $rate \
        --save-result \
        --result-dir "./results/rate_${rate}" \
        --disable-tqdm
done
```

### 3. 对比多个模型
```bash
#!/bin/bash
# 对比不同模型的性能
for model in "gpt-3.5-turbo" "gpt-4" "gpt-4-turbo"; do
    echo "Testing model: $model"
    python test_with_jsonl.py \
        --model $model \
        --num-prompts 20 \
        --save-result \
        --result-dir "./results/${model}"
done
```

### 4. 查看数据统计
```bash
# 统计对话轮数分布
python3 << 'EOF'
import json

turns_dist = {}
with open('online_query_etl_100.jsonl', 'r') as f:
    for line in f:
        messages = json.loads(line)
        turns = len(messages)
        turns_dist[turns] = turns_dist.get(turns, 0) + 1

print("对话轮数分布:")
for turns in sorted(turns_dist.keys()):
    print(f"  {turns} 轮: {turns_dist[turns]} 条对话")
EOF
```

---

## 🎯 最佳实践

### 1. 开发测试
```bash
# 快速测试（少量数据）
python test_with_jsonl.py \
    --model gpt-4 \
    --num-prompts 5 \
    --request-rate 1
```

### 2. 功能验证
```bash
# 中等规模测试
python test_with_jsonl.py \
    --model gpt-4 \
    --num-prompts 30 \
    --request-rate 2 \
    --save-result
```

### 3. 性能基准测试
```bash
# 完整测试，所有数据
python test_with_jsonl.py \
    --model gpt-4 \
    --num-prompts 100 \
    --request-rate 5 \
    --save-result \
    --result-dir ./benchmark_results
```

### 4. 压力测试
```bash
# 最大吞吐量测试
python test_with_jsonl.py \
    --model gpt-4 \
    --num-prompts 100 \
    --request-rate inf \
    --max-concurrency 100 \
    --save-result
```

---

## 📁 结果文件

如果使用 `--save-result`，会生成 JSON 格式的结果文件：

```json
{
  "duration": 50.23,
  "completed": 100,
  "total_input": 15230,
  "total_output": 45680,
  "request_throughput": 1.99,
  "input_throughput": 303.15,
  "output_throughput": 909.45,
  "mean_ttft_ms": 234.56,
  "median_ttft_ms": 198.23,
  "p99_ttft_ms": 567.89,
  ...
}
```

查看结果：
```bash
# 查看最新结果
cat results/*.json | jq .

# 提取关键指标
cat results/*.json | jq '{
  throughput: .request_throughput,
  ttft_ms: .mean_ttft_ms,
  tpot_ms: .mean_tpot_ms
}'
```

---

## 🤝 获取帮助

如有问题，请参考：
- [README.md](README.md) - 完整使用指南
- [VLLM_DEPENDENCY_REMOVAL.md](VLLM_DEPENDENCY_REMOVAL.md) - 依赖说明
- 运行 `python test_with_jsonl.py --help` 查看所有选项

---

**祝测试顺利！** 🎉
