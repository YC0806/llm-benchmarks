# LLM Benchmarks - Remote API Testing

基于 vLLM 基准测试工具改造的轻量级远程 API 测试框架，无需安装 vLLM。

## 🎯 特性

- ✅ **零 vLLM 依赖**：专注于远程 API 测试，不需要本地模型部署
- ✅ **多后端支持**：OpenAI、vLLM Server、TGI、TensorRT-LLM 等
- ✅ **丰富的数据集**：ShareGPT、Random、HuggingFace 等
- ✅ **全面的指标**：TTFT、TPOT、ITL、E2EL、吞吐量等
- ✅ **并发测试**：支持多客户端并发、多轮对话测试
- ✅ **灵活的请求速率控制**：固定速率、Poisson 过程、线性/指数递增

## 📦 安装

### 最小化安装（仅 4 个依赖）⭐
```bash
pip install numpy pandas aiohttp tqdm
```
> 注意：Token 统计将使用 API 响应数据或字符估算（误差约 ±10-20%）

### 推荐安装（包含精确 token 计数）
```bash
pip install numpy pandas aiohttp tqdm transformers
```

### 可选依赖

**Excel 导出**（多轮测试）：
```bash
pip install xlsxwriter
```
> 注意：如果不安装 xlsxwriter，使用 `--excel-output` 时会自动降级到 CSV 导出

**图像模型测试**：
```bash
pip install Pillow datasets
```

**音频模型测试**：
```bash
pip install soundfile librosa
```

## 🚀 快速开始

### 1. 测试 OpenAI API
```bash
export OPENAI_API_KEY="your-api-key"

python benchmark_serving.py \
    --backend openai-chat \
    --model gpt-4 \
    --base-url https://api.openai.com \
    --dataset-name random \
    --num-prompts 10 \
    --request-rate 1
```

### 2. 测试 vLLM 服务器
```bash
# 假设你的 vLLM 服务器运行在 http://localhost:8000
python benchmark_serving.py \
    --backend vllm \
    --model meta-llama/Llama-2-7b-hf \
    --base-url http://localhost:8000 \
    --dataset-name sharegpt \
    --dataset-path ./data/sharegpt.json \
    --num-prompts 100 \
    --request-rate 10
```

### 3. 使用自定义数据集
创建 `custom_prompts.jsonl`：
```jsonl
{"prompt": "What is the capital of France?"}
{"prompt": "Explain quantum computing in simple terms."}
{"prompt": "Write a haiku about coding."}
```

运行测试：
```bash
python benchmark_serving.py \
    --backend openai-chat \
    --model gpt-4 \
    --base-url https://api.openai.com \
    --dataset-name custom \
    --dataset-path ./custom_prompts.jsonl \
    --num-prompts 3
```

### 4. 多轮对话测试
```bash
python multi_turn/benchmark_serving_multi_turn.py \
    -i ./data/conversations.json \
    -m gpt-4 \
    -u https://api.openai.com \
    -p 4 \
    --request-rate 2 \
    --excel-output
```

## 📊 支持的后端

| 后端 | 参数值 | 说明 |
|------|--------|------|
| OpenAI Completions | `openai` | OpenAI 标准完成 API |
| OpenAI Chat | `openai-chat` | OpenAI 聊天完成 API |
| OpenAI Audio | `openai-audio` | OpenAI 语音识别 API |
| vLLM Server | `vllm` | vLLM OpenAI 兼容服务器 |
| TGI | `tgi` | HuggingFace Text Generation Inference |
| TensorRT-LLM | `tensorrt-llm` | NVIDIA TensorRT-LLM |
| LMDeploy | `lmdeploy` | LMDeploy 服务器 |
| SGLang | `sglang` | SGLang 服务器 |
| llama.cpp | `llama.cpp` | llama.cpp 服务器 |
| DeepSpeed-MII | `deepspeed-mii` | DeepSpeed MII 服务器 |
| ScaleLLM | `scalellm` | ScaleLLM 服务器 |

## 📁 数据集类型

| 数据集 | 参数值 | 说明 |
|--------|--------|------|
| Random | `random` | 随机生成的合成数据 |
| ShareGPT | `sharegpt` | ShareGPT 对话数据 |
| Sonnet | `sonnet` | 诗歌文本数据 |
| BurstGPT | `burstgpt` | 突发请求模式数据 |
| Custom | `custom` | 自定义 JSONL 格式 |
| HuggingFace | `hf` | HuggingFace 数据集 |

## 📈 基准测试指标

- **TTFT** (Time to First Token): 首个 token 生成时间
- **TPOT** (Time per Output Token): 每个输出 token 平均时间
- **ITL** (Inter-token Latency): token 间延迟
- **E2EL** (End-to-end Latency): 端到端延迟
- **Throughput**: 吞吐量（tokens/s 或 requests/s）
- **Goodput**: 满足 SLO 的请求吞吐量

## 🔧 常用参数

### 基础参数
```bash
--backend <backend>           # 后端类型
--model <model_name>          # 模型名称
--base-url <url>              # API 基础 URL
--dataset-name <name>         # 数据集类型
--dataset-path <path>         # 数据集路径（如需要）
```

### 性能控制
```bash
--num-prompts <n>             # 请求数量
--request-rate <rate>         # 请求速率（RPS），inf 表示无限制
--max-concurrency <n>         # 最大并发请求数
--burstiness <factor>         # 突发因子（1.0 = Poisson）
```

### 请求速率递增
```bash
--ramp-up-strategy <strategy> # linear 或 exponential
--ramp-up-start-rps <n>       # 起始 RPS
--ramp-up-end-rps <n>         # 结束 RPS
```

### 输出控制
```bash
--save-result                 # 保存结果到 JSON
--result-dir <dir>            # 结果保存目录
--result-filename <name>      # 结果文件名
--disable-tqdm                # 禁用进度条
```

### Tokenizer 配置
```bash
--tokenizer <path>            # Tokenizer 路径（可选）
--tokenizer-mode <mode>       # auto（默认）或 slow
--trust-remote-code           # 信任远程代码（Tokenizer）
```

## 💡 高级用法

### 1. 性能压测（最大吞吐量）
```bash
python benchmark_serving.py \
    --backend vllm \
    --model meta-llama/Llama-2-7b-hf \
    --base-url http://localhost:8000 \
    --dataset-name random \
    --num-prompts 1000 \
    --request-rate inf \
    --max-concurrency 100
```

### 2. 稳定性测试（固定速率）
```bash
python benchmark_serving.py \
    --backend openai-chat \
    --model gpt-4 \
    --base-url https://api.openai.com \
    --dataset-name sharegpt \
    --dataset-path ./data/sharegpt.json \
    --num-prompts 500 \
    --request-rate 10 \
    --burstiness 1.0
```

### 3. 渐进式压测（流量递增）
```bash
python benchmark_serving.py \
    --backend vllm \
    --model meta-llama/Llama-2-7b-hf \
    --base-url http://localhost:8000 \
    --dataset-name random \
    --num-prompts 1000 \
    --ramp-up-strategy linear \
    --ramp-up-start-rps 1 \
    --ramp-up-end-rps 50
```

### 4. Goodput 测试（SLO 约束）
```bash
python benchmark_serving.py \
    --backend vllm \
    --model meta-llama/Llama-2-7b-hf \
    --base-url http://localhost:8000 \
    --dataset-name sharegpt \
    --dataset-path ./data/sharegpt.json \
    --num-prompts 200 \
    --request-rate 10 \
    --goodput ttft:200 tpot:50 e2el:5000
```

### 5. 多客户端并发测试
```bash
python multi_turn/benchmark_serving_multi_turn.py \
    -i ./data/conversations.json \
    -m gpt-4 \
    -u https://api.openai.com \
    -p 10 \
    -k 50 \
    --request-rate 5 \
    --max-num-requests 1000
```

## 📝 数据集格式

### ShareGPT 格式
```json
[
  {
    "conversations": [
      {"role": "user", "value": "Hello!"},
      {"role": "assistant", "value": "Hi! How can I help?"}
    ]
  }
]
```

### Custom 格式（JSONL）
```jsonl
{"prompt": "Question 1"}
{"prompt": "Question 2"}
{"prompt": "Question 3"}
```

## 🐛 故障排除

### 问题：找不到 vLLM 模块
这是正常的！本项目已移除 vLLM 依赖，不需要安装 vLLM。

### 问题：Mistral tokenizer 错误
**解决方案**：使用 `--tokenizer-mode auto`（默认）或 `--tokenizer-mode slow`

### 问题：连接超时
**解决方案**：
1. 检查 `--base-url` 是否正确
2. 确保 API 服务器正在运行
3. 检查防火墙设置

### 问题：Token 计数不准确
**解决方案**：使用 `--tokenizer` 参数指定与服务器相同的 tokenizer

## 🔄 从 vLLM 版本迁移

详见 [VLLM_DEPENDENCY_REMOVAL.md](VLLM_DEPENDENCY_REMOVAL.md)

主要变化：
- ✅ 不再需要安装 vLLM
- ✅ 所有远程 API 功能保留
- ❌ 不支持本地模型部署
- ❌ 不支持 Mistral tokenizer 模式
- ❌ 不支持本地 LoRA 适配器

## 📚 参考资料

- [原始 README（vLLM 版本）](README_original.md)
- [vLLM 项目](https://github.com/vllm-project/vllm)
- [OpenAI API 文档](https://platform.openai.com/docs/api-reference)
- [HuggingFace Transformers](https://huggingface.co/docs/transformers)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

Apache-2.0 License

---

**项目状态**: 活跃开发中
**最后更新**: 2025-10-28
**版本**: 2.0 (vLLM-free)
