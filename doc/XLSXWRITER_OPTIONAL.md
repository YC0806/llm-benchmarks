# xlsxwriter 依赖优化说明

## 📋 概述

xlsxwriter 已从必需依赖改为可选依赖。如果未安装，多轮测试的 `--excel-output` 选项会自动降级到 CSV 导出。

## ✅ 完成的修改

### 1. 代码修改
**文件**: [multi_turn/benchmark_serving_multi_turn.py](multi_turn/benchmark_serving_multi_turn.py:1156-1241)

**修改内容**:
- 添加了 xlsxwriter 的导入检测
- 如果 xlsxwriter 未安装，自动使用 CSV 导出作为后备方案
- 提供清晰的错误提示和安装指引

**后备逻辑**:
```python
if excel_output:
    try:
        import xlsxwriter
        # 使用 Excel 导出
    except ImportError:
        # 自动降级到 CSV 导出
        logger.info("Falling back to CSV export...")
```

### 2. CSV 导出格式
当使用 CSV 后备方案时，会生成多个文件：

| 文件名 | 内容 |
|--------|------|
| `*_params.csv` | 测试参数 |
| `*_gen_params.csv` | 对话生成参数（如适用） |
| `*_stats_0_params.csv` | 统计参数（warmup 0%） |
| `*_stats_0.csv` | 统计数据（warmup 0%） |
| `*_raw_data.csv` | 原始测试数据 |

**优点**:
- ✅ 无需额外依赖
- ✅ 易于用其他工具打开（Excel、Google Sheets 等）
- ✅ 文本格式，便于版本控制
- ✅ 可以用 Python 脚本轻松处理

### 3. Requirements 更新

**主 requirements.txt**:
```
# REQUIRED DEPENDENCIES
numpy>=1.24
pandas>=2.0.0
aiohttp>=3.10
transformers>=4.46
tqdm>=4.66

# OPTIONAL DEPENDENCIES (已注释)
# xlsxwriter>=3.2.1  # Excel export
```

**multi_turn/requirements.txt**:
```
# Required
numpy>=1.24
pandas>=2.0.0
aiohttp>=3.10
transformers>=4.46
tqdm>=4.66

# Optional: Excel export (CSV works without this)
# xlsxwriter>=3.2.1
```

## 🚀 使用方式

### 不安装 xlsxwriter（推荐）
```bash
# 安装核心依赖
pip install numpy pandas aiohttp transformers tqdm

# 运行多轮测试，自动使用 CSV 导出
python multi_turn/benchmark_serving_multi_turn.py \
    -i ./conversations.json \
    -m gpt-4 \
    -u https://api.openai.com \
    -p 4 \
    --excel-output

# 输出: statistics_4_clients__DD-MM-YYYY_HH-MM-SS_*.csv
```

### 安装 xlsxwriter（可选）
如果你更喜欢 Excel 格式：
```bash
pip install xlsxwriter

# 运行多轮测试，使用 Excel 导出
python multi_turn/benchmark_serving_multi_turn.py \
    -i ./conversations.json \
    -m gpt-4 \
    -u https://api.openai.com \
    -p 4 \
    --excel-output

# 输出: statistics_4_clients__DD-MM-YYYY_HH-MM-SS.xlsx
```

## 📊 导出格式对比

| 特性 | Excel (.xlsx) | CSV |
|------|---------------|-----|
| **依赖** | 需要 xlsxwriter | 无需额外依赖 |
| **文件数** | 单个文件 | 多个文件 |
| **多工作表** | ✅ 支持 | ❌ 每个 CSV 一个数据集 |
| **格式化** | ✅ 可以格式化 | ❌ 纯文本 |
| **文件大小** | 较小（压缩） | 较大（文本） |
| **通用性** | ✅ Excel 专有 | ✅ 所有工具支持 |
| **版本控制** | ❌ 二进制格式 | ✅ 文本格式 |
| **自动化处理** | 可以 | ✅ 更容易 |

## 💡 最佳实践

### 使用 CSV（推荐场景）
- ✅ CI/CD 自动化测试
- ✅ 需要版本控制测试结果
- ✅ 使用脚本处理数据
- ✅ 减少依赖安装

### 使用 Excel（推荐场景）
- ✅ 手动分析数据
- ✅ 需要复杂的格式化
- ✅ 分享给非技术人员
- ✅ 单文件更方便

## 🔧 处理 CSV 文件

### 合并 CSV 文件（Python）
```python
import pandas as pd
import glob

# 读取所有统计文件
csv_files = glob.glob('statistics_*_stats_*.csv')
dfs = []
for file in csv_files:
    df = pd.read_csv(file)
    dfs.append(df)

# 合并
combined = pd.concat(dfs, ignore_index=True)
combined.to_csv('combined_stats.csv', index=False)
```

### 转换 CSV 到 Excel（Python）
```python
import pandas as pd
import glob

# 如果后来安装了 xlsxwriter，可以转换
csv_files = glob.glob('statistics_*_*.csv')

with pd.ExcelWriter('converted.xlsx', engine='xlsxwriter') as writer:
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        sheet_name = csv_file.replace('.csv', '').split('_')[-1]
        df.to_excel(writer, sheet_name=sheet_name, index=False)
```

## 🐛 故障排除

### 问题：想要 Excel 但没有安装 xlsxwriter
**输出**:
```
[ERROR] Excel export requires xlsxwriter. Install it with: pip install xlsxwriter
[INFO] Falling back to CSV export instead...
[SUCCESS] Client metrics exported to CSV files: statistics_*_*.csv
```

**解决方案**:
```bash
pip install xlsxwriter
```

### 问题：CSV 文件太多
**解决方案**:
使用上面的 Python 脚本合并或转换为单个文件。

## 📈 性能影响

| 操作 | Excel | CSV |
|------|-------|-----|
| **写入速度** | 慢（需要压缩） | 快（直接写入） |
| **内存占用** | 较高 | 较低 |
| **依赖大小** | ~1 MB | 0 |

## 🎯 总结

- ✅ **xlsxwriter 现在是可选的**
- ✅ **CSV 自动后备，无需手动配置**
- ✅ **核心依赖减少到 5 个包**
- ✅ **两种格式各有优势，按需选择**

---

**建议**: 对于大多数自动化测试场景，使用 CSV 后备即可。只在需要手动分析时安装 xlsxwriter。
