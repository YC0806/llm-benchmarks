# vLLM 依赖移除说明

## 概述

本项目已成功移除 vLLM 相关依赖，现在可以完全独立运行，专注于通过 URL 访问远程大模型 API 进行基准测试。

## 修改的文件

### 1. `benchmark_serving.py`
**修改内容：**
- 移除了 `from vllm.transformers_utils.tokenizer import get_tokenizer`
- 移除了 `from vllm.utils import FlexibleArgumentParser`
- 移除了 `from vllm.benchmarks.serve import get_request`
- 直接使用 `argparse.ArgumentParser` 替代 `FlexibleArgumentParser`
- 从 `backend_request_func` 导入 `get_tokenizer`
- 添加了 `get_request()` 函数的本地实现，支持：
  - 固定请求速率（Poisson 过程）
  - 可调节的突发性（burstiness）
  - 线性和指数请求速率递增策略

### 2. `benchmark_dataset.py`
**修改内容：**
- 移除了所有 vLLM 相关导入：
  - `vllm.lora.request.LoRARequest`
  - `vllm.lora.utils.get_adapter_absolute_path`
  - `vllm.multimodal.MultiModalDataDict`
  - `vllm.multimodal.image.convert_image_mode`
  - `vllm.transformers_utils.tokenizer.{AnyTokenizer, get_lora_tokenizer}`
- 添加了替代实现：
  - `LoRARequest` 类（占位符，远程 API 模式不使用）
  - `convert_image_mode()` 函数（使用 PIL 的标准 API）
  - `get_lora_tokenizer()` 函数（返回 None）
  - `get_adapter_absolute_path()` 函数（返回原路径）
  - 类型别名：`MultiModalDataDict` 和 `AnyTokenizer`

### 3. `backend_request_func.py`
**修改内容：**
- 简化了 `get_model()` 函数，移除了 ModelScope 集成
- 移除了 `vllm.model_executor.model_loader.weight_utils.get_lock`
- 修改了 `get_tokenizer()` 函数，不再支持 Mistral tokenizer 模式
  - 如果用户尝试使用 `tokenizer_mode="mistral"`，会抛出清晰的错误提示

### 4. `benchmark_serving_structured_output.py`
**状态：** 未修改
- 此文件依赖 vLLM 的结构化输出功能（`vllm.v1.structured_output`）
- 不适用于远程 API 测试场景
- 建议在纯远程 API 测试时不使用此脚本

## 功能影响

### ✅ 保留的功能
1. **所有远程 API 后端支持**：
   - OpenAI (Completions 和 Chat Completions)
   - OpenAI Audio (语音识别)
   - vLLM Server (通过 OpenAI 兼容 API)
   - TGI (Text Generation Inference)
   - TensorRT-LLM
   - LMDeploy
   - ScaleLLM
   - SGLang
   - llama.cpp
   - DeepSpeed-MII

2. **所有数据集支持**：
   - ShareGPT
   - Random (合成数据)
   - Sonnet
   - BurstGPT
   - Custom (自定义 JSONL)
   - HuggingFace 数据集（VisionArena、InstructCoder、MTBench 等）

3. **完整的基准测试功能**：
   - TTFT (Time to First Token)
   - TPOT (Time per Output Token)
   - ITL (Inter-token Latency)
   - E2EL (End-to-end Latency)
   - 吞吐量和goodput 指标
   - 多客户端并发测试
   - 多轮对话测试

4. **请求速率控制**：
   - 固定请求速率
   - Poisson 过程
   - Gamma 分布（可调节突发性）
   - 线性/指数请求速率递增

### ❌ 不再支持的功能
1. **本地模型部署**：无法直接使用 vLLM 启动本地模型服务
2. **LoRA 适配器**：本地 LoRA 适配器不再支持（远程 API 可能自行支持）
3. **Mistral Tokenizer 模式**：必须使用 `auto` 或 `slow` tokenizer 模式
4. **ModelScope 集成**：不再支持从 ModelScope 自动下载模型
5. **结构化输出测试**：`benchmark_serving_structured_output.py` 不可用

## 使用示例

### 基础测试
```bash
python benchmark_serving.py \
    --backend openai-chat \
    --model gpt-4 \
    --base-url https://api.openai.com \
    --dataset-name sharegpt \
    --dataset-path ./sharegpt.json \
    --num-prompts 100 \
    --request-rate 10
```

### 多轮对话测试
```bash
python multi_turn/benchmark_serving_multi_turn.py \
    -i ./conversations.json \
    -m gpt-4 \
    -u https://api.openai.com \
    -p 4 \
    --request-rate 5
```

### vLLM 服务器兼容模式
```bash
# 服务器端（如果你有 vLLM 环境）
vllm serve meta-llama/Llama-2-7b-hf --port 8000

# 客户端（使用本项目测试）
python benchmark_serving.py \
    --backend vllm \
    --model meta-llama/Llama-2-7b-hf \
    --base-url http://localhost:8000 \
    --dataset-name random \
    --num-prompts 200
```

## 依赖要求

### 核心依赖（必需）
```
numpy>=1.24
pandas>=2.0.0
aiohttp>=3.10
transformers>=4.46
tqdm
```

### 可选依赖
```
# 用于多轮测试的 Excel 导出（不安装会自动降级到 CSV）
# xlsxwriter>=3.2.1

# 用于多模态数据集（图像）
# Pillow
# datasets

# 用于音频数据集
# soundfile
# librosa
```

**注意**：所有可选依赖都已注释，按需安装即可。

## 验证安装

运行以下命令验证安装：
```bash
python3 -c "
from backend_request_func import get_tokenizer
from benchmark_dataset import ShareGPTDataset, RandomDataset
import benchmark_serving
print('✓ All modules imported successfully!')
"
```

## 迁移指南

### 从 vLLM 集成版本迁移
如果你之前使用了带 vLLM 依赖的版本：

1. **Tokenizer 模式**：
   ```bash
   # 旧版本
   --tokenizer-mode mistral  # 不再支持

   # 新版本
   --tokenizer-mode auto     # 使用这个
   ```

2. **LoRA 适配器**：
   ```bash
   # 旧版本
   --lora-modules adapter1 adapter2  # 本地 LoRA

   # 新版本
   # 远程 API 不支持，需要在服务器端配置
   ```

3. **模型路径**：
   ```bash
   # 旧版本（本地）
   --model /path/to/local/model

   # 新版本（远程）
   --model model-name-on-remote-server
   ```

## 故障排除

### 问题：`No module named 'vllm'`
**解决方案**：这是正常的，项目已不再需要 vLLM。

### 问题：Mistral tokenizer 错误
**解决方案**：使用 `--tokenizer-mode auto` 或 `--tokenizer-mode slow`

### 问题：找不到模型文件
**解决方案**：确保 `--model` 参数指向远程 API 服务器上存在的模型名称，不是本地路径。

## 性能考虑

移除 vLLM 依赖后：
- ✅ 启动更快（无需加载大型依赖）
- ✅ 内存占用更低
- ✅ 安装更简单
- ⚠️ 某些 vLLM 特定优化不可用（但不影响远程 API 测试）

## 下一步优化建议

1. **进一步减少依赖**：
   - 将多模态依赖（Pillow、soundfile、librosa）改为可选
   - 考虑用更轻量的库替代 pandas（如 polars）

2. **添加功能**：
   - 支持更多远程 API 后端
   - 添加自定义认证机制
   - 支持 API 密钥轮转

3. **改进文档**：
   - 为每个后端提供详细示例
   - 添加常见问题解答

## 贡献

如果你发现任何问题或有改进建议，欢迎提交 Issue 或 Pull Request。

---

**最后更新**: 2025-10-28
**版本**: 2.0 (vLLM-free)
