# Health Coach v2.0

一个基于 LLM 驱动的智能健康教练系统，支持多阶段个性化补充剂和饮食推荐，内置智能冲突检测机制和基因个性化分析。

## ✨ v2.0 新特性

- 🤖 **LLM 驱动**: 接入 OpenAI GPT 模型，提供更智能的个性化建议
- 🎨 **Web 前端**: 基于 Streamlit 的交互式界面
- 🧬 **基因分析**: 支持解析基因报告并提供个性化调整
- 📊 **健康数据**: 集成 Apple Health 数据分析
- 🏥 **体检报告**: 支持上传体检报告作为参考
- 🏙️ **城市化**: 基于城市提供本地化饮食建议
- 🔐 **安全存储**: 使用环境变量管理 API 密钥

## 特性

- **多阶段支持**: 普通期、备孕/孕期、减脂期、增肌期、倒时差/旅行、恢复期
- **智能冲突检测**: 自动检测补充剂、饮食、基因报告间的潜在冲突
- **基因个性化**: 解析基因报告，提供基于基因型的个性化建议
- **饮食分析**: 内置中国菜营养数据库，提供阶段化饮食建议
- **LangGraph 工作流**: 状态机驱动的完整推荐流程
- **LLM 增强**: AI 驱动的自然语言生成，提供更人性化的建议
- **Web 界面**: Streamlit 交互式前端，支持文件上传和实时结果展示
- **模块化设计**: 清晰的代码结构，便于维护和扩展

## 核心功能

### 1. 阶段选择系统

| 阶段 | 代码标识 | 适用人群 | 推荐重点 |
|------|----------|----------|----------|
| 普通期 | `general` | 日常健康维护 | 基础营养素、抗氧化剂 |
| 备孕/孕期 | `preconception` | 计划怀孕、孕期女性 | 叶酸、DHA、铁剂 |
| 减脂期 | `fat_loss` | 减重人群 | 蛋白质、左旋肉碱、代谢支持 |
| 增肌期 | `muscle_gain` | 健身人群 | 肌酸、乳清蛋白、恢复支持 |
| 倒时差/旅行 | `jetlag_travel` | 频繁出差/旅行者 | 褪黑素、B族维生素 |
| 恢复期 | `recovery` | 疾病/术后恢复人群 | 维生素C、锌、益生菌 |

### 2. 冲突检测机制

系统采用三级评估体系：

- 🟢 **安全**: 无冲突，可直接使用
- 🟡 **优化**: 建议调整剂量或服用时间
- 🔴 **警告**: 存在严重冲突，需专业评估

检测范围包括：
- 补充剂间相互作用（如铁+钙、铁+锌）
- 阶段禁忌（如备孕禁用褪黑素）
- 基因变异对代谢的影响（如MTHFR基因与叶酸代谢）

### 3. 基因报告解析

支持的基因位点：
- **MTHFR** (C677T, A1298C): 叶酸代谢
- **VDR** (FokI, TaqI): 维生素D代谢
- **FADS1/FADS2**: Omega-3转化
- **HFE** (C282Y, H63D): 铁代谢
- **COMT** (Val158Met): 压力代谢
- **BDNF** (Val66Met): 认知功能
- **IL-6**: 炎症倾向
- **FTO**: 体重调节

支持格式：PDF、TXT、JSON

### 4. 饮食分析

内置中国菜营养数据库（20+种常见食物）：
- 蛋白质来源：清蒸鲈鱼、白切鸡、红烧牛肉等
- 蔬菜类：清炒西兰花、凉拌菠菜、蒜蓉空心菜等
- 主食类：白米饭、杂粮饭、小米粥等
- 汤类：紫菜蛋花汤、冬瓜排骨汤等

根据阶段提供：
- 饮食原则
- 餐食推荐（早餐/午餐/晚餐）
- 每日营养目标（热量、蛋白质、碳水、脂肪）

## 安装

### 环境要求

- Python 3.8+
- pip 或 pipenv

### 安装步骤

```bash
# 1. 克隆或下载项目
cd health_coach

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt
```

### 配置环境变量

1. 复制 `.env` 文件（如果不存在）:
```bash
cp .env.example .env  # 如果有示例文件
```

2. 编辑 `.env` 文件，设置你的 API Key:
```env
OPENAI_API_KEY=your_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

⚠️ **重要**: `.env` 文件已添加到 `.gitignore`，请勿提交到版本控制系统！

可选依赖（PDF解析）：
```bash
pip install PyPDF2
# 或
pip install pdfplumber
```

## 使用方法

### Web 界面（推荐）

启动 Streamlit 前端：

```bash
# 使用一键启动脚本
bash run_frontend.sh

# 或直接运行
streamlit run frontend.py
```

前端功能包括：
- 📝 用户信息输入（姓名、年龄、性别、城市）
- 🎯 健康阶段选择
- 🏥 伤病位置选择
- 📊 身体数据输入（体重、体脂、腰围历史）
- 💊 当前补充剂列表
- 🧬 基因报告上传（PDF/TXT）
- 📱 Apple Health 数据上传（JSON/CSV）
- 🩺 体检报告上传（PDF）
- 🍎 食物热量估算（文字描述）
- 📋 完整健康报告生成和导出

### CLI 模式

#### 显示欢迎信息
```bash
python main.py hello
```

#### 查看所有阶段
```bash
python main.py stages
```

#### 创建用户档案
```bash
python main.py profile --name "张三" --stage preconception
```

#### 获取完整推荐方案
```bash
# 基础推荐（补充剂 + 饮食）
python main.py recommend --stage preconception --age 28 --gender female

# 带当前补充剂的推荐
python main.py recommend --stage preconception --age 28 --gender female --current "维生素 D3" --current "Omega-3 鱼油"

# 带基因报告的推荐
python main.py recommend --stage preconception --age 28 --gender female --gene gene_report.txt
```

#### 解析基因报告
```bash
# 基础解析
python main.py analyze-report --file gene_report.txt

# 解析并生成推荐
python main.py analyze-report --file gene_report.txt --stage preconception --age 28 --gender female
```

### 测试套件

运行完整测试：
```bash
# LLM 集成测试
python test_llm_integration.py

# 基础推荐测试
python test_recommender.py

# 完整工作流测试
python test_workflow.py

# 全功能测试（包含饮食分析）
python test_full_recommend.py
```

### 代码集成

```python
from agent.graph import quick_recommend, run_health_coach_workflow
from tools.conflict_checker import check_supplement_conflicts
from tools.gene_report_parser import parse_gene_report
from tools.diet_analyzer import analyze_diet, DietAnalyzer
from agent.llm_integration import get_llm, is_llm_available

# 检查 LLM 是否可用
if is_llm_available():
    print("✅ LLM 已启用，将使用 AI 驱动的推荐")
else:
    print("⚠️  LLM 不可用，使用规则引擎")

# 快速推荐
result = quick_recommend(
    stage="preconception",
    age=28,
    gender="female",
    current_supplements=["维生素 D3", "Omega-3 鱼油"]
)
print(result)

# 完整工作流
user_profile = {
    "stage": "preconception",
    "age": 28,
    "gender": "female",
    "city": "西安",
    "current_supplements": ["维生素 D3"],
    "gene_report_path": "gene_report.txt",
    "injury_areas": ["膝盖"],
    "lifestyle": {
        "exercise_level": 3,
        "sleep_hours": 7,
        "stress_level": "中",
        "diet_type": "均衡"
    }
}
result = run_health_coach_workflow(user_profile)
print(result['final_response'])

# 冲突检测
severity, conflicts, suggestions = check_supplement_conflicts(
    ["铁", "钙"],
    "preconception"
)

# 饮食分析
advice = analyze_diet("日常", "preconception")
for s in advice[:5]:
    print(s)

# 直接使用 LLM（如果可用）
llm = get_llm()
if llm and llm.is_available():
    import asyncio
    recommendation = asyncio.run(llm.generate_supplement_recommendations(
        stage="preconception",
        age=28,
        gender="female",
        current_supplements=["维生素D3"]
    ))
    print(recommendation)
```

## 项目结构

```
health_coach/
├── README.md                    # 项目文档
├── requirements.txt             # Python 依赖
├── .env                        # 环境变量（包含API密钥）
├── .gitignore                  # Git 忽略文件
├── skill.json                  # OpenClaw Skill 配置
├── main.py                     # CLI 入口
├── frontend.py                 # Streamlit Web 前端
├── run_frontend.sh             # 前端启动脚本
│
├── schemas/                    # 数据模型定义
│   ├── __init__.py
│   └── user_profile.py        # 用户画像模型
│
├── tools/                     # MCP 工具实现
│   ├── __init__.py
│   ├── conflict_checker.py           # 冲突检测引擎
│   ├── supplement_recommender.py     # 补充剂推荐引擎
│   ├── gene_report_parser.py         # 基因报告解析器
│   └── diet_analyzer.py             # 饮食分析模块
│
├── data/                      # 静态数据
│   ├── __init__.py
│   ├── supplements.json               # 20种补充剂数据库
│   └── interactions.json             # 冲突规则库
│
├── prompts/                   # 提示词模板
│   ├── __init__.py
│   └── system_prompt.py             # 系统提示词
│
├── agent/                     # Agent 逻辑
│   ├── __init__.py
│   ├── graph.py                      # LangGraph 工作流
│   └── llm_integration.py            # LLM 集成模块
│
└── tests/                    # 测试脚本
    ├── test_recommender.py           # 基础推荐测试
    ├── test_workflow.py              # 工作流测试
    ├── test_full_recommend.py       # 完整功能测试
    └── test_llm_integration.py     # LLM 集成测试
```

## 已完成功能

- [x] 第一批：基础文件结构
  - [x] `main.py` CLI 入口
  - [x] `skill.json` 配置文件
  - [x] `requirements.txt` 依赖管理
  - [x] `README.md` 文档

- [x] 第二批：核心功能模块
  - [x] `schemas/user_profile.py` 用户画像模型（Pydantic v2）
  - [x] `data/supplements.json` 20种补充剂数据库
  - [x] `data/interactions.json` 冲突规则库
  - [x] `tools/conflict_checker.py` 冲突检测引擎
  - [x] `tools/supplement_recommender.py` 补充剂推荐引擎

- [x] 第三批：LangGraph 工作流和基因解析
  - [x] `agent/graph.py` 状态机工作流
  - [x] `prompts/system_prompt.py` 系统提示词
  - [x] `tools/gene_report_parser.py` 基因报告解析器
  - [x] 更新 `main.py` 新增 `gene-report` 和 `full_recommend` 命令

- [x] 第四批：饮食分析和完整集成
  - [x] `tools/diet_analyzer.py` 饮食分析模块
  - [x] 内置20+种中国菜营养数据
  - [x] 更新 `agent/graph.py` 集成饮食分析
  - [x] 新增 `run_health_coach_workflow()` 公共接口
  - [x] 更新 `main.py` 新增 `recommend` 和 `analyze-report` 命令
  - [x] `test_full_recommend.py` 完整功能测试脚本
  - [x] 更新 `README.md` 文档

- [x] v2.0：LLM 集成和 Web 前端
  - [x] `.env` 环境变量配置文件
  - [x] `.gitignore` Git 忽略文件
  - [x] `agent/llm_integration.py` LLM 集成模块
  - [x] 更新 `agent/graph.py` 集成 LLM 调用
  - [x] 更新 `prompts/system_prompt.py` 增强系统提示词
  - [x] `frontend.py` Streamlit Web 前端（1175行）
  - [x] `run_frontend.sh` 一键启动脚本
  - [x] `test_llm_integration.py` LLM 集成测试脚本
  - [x] 更新 `requirements.txt` 添加 langchain-openai 和 pandas
  - [x] 更新 `README.md` v2.0 文档

## 开发计划

### v2.1 计划功能
- [ ] 图像识别：食物图像识别和热量估算
- [ ] 基因数据库扩展：更多SNP位点
- [ ] 饮食数据库扩展：更多中国菜和国际化食物
- [ ] 历史记录：保存用户推荐历史
- [ ] 数据导出：PDF/Excel 格式报告导出
- [ ] 用户账户系统：保存个人资料和历史记录

### 长期规划
- [ ] AI 对话集成：基于 GPT 的自然语言交互（已完成基础）
- [ ] 个性化学习：根据用户反馈优化推荐
- [ ] 健康数据集成：接入智能手表等健康数据
- [ ] 专业知识库：整合更多医学研究文献
- [ ] 移动端 APP：iOS 和 Android 原生应用
- [ ] 社交功能：分享健康方案和经验

## 技术栈

- **Python**: 3.8+
- **Pydantic**: v2 数据验证
- **LangGraph**: 状态机工作流（可选）
- **Typer**: CLI 框架
- **Rich**: 终端美化输出
- **PyPDF2/pdfplumber**: PDF 解析（可选）

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
