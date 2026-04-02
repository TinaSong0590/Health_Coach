"""
LLM 集成模块 - 为健康教练提供大模型能力
"""

import os
from typing import Dict, Any, List, Optional
from pathlib import Path

# 尝试导入 LangChain 组件
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.runnables import RunnablePassthrough
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("警告: LangChain 未安装，LLM 功能将不可用")

# 尝试加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class HealthCoachLLM:
    """健康教练 LLM 集成"""

    def __init__(self, model_name: Optional[str] = None, api_key: Optional[str] = None, use_qwen: bool = True):
        """
        初始化 LLM

        参数:
            model_name: 模型名称（默认从环境变量读取）
            api_key: API Key（默认从环境变量读取）
            use_qwen: 是否使用通义千问（默认True）
        """
        if not LANGCHAIN_AVAILABLE:
            self.llm = None
            self.available = False
            return

        # 优先使用通义千问配置，回退到 OpenAI 配置
        if use_qwen:
            self.api_key = api_key or os.getenv("QWEN_API_KEY") or os.getenv("OPENAI_API_KEY")
            self.base_url = os.getenv("QWEN_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
            self.model_name = model_name or os.getenv("QWEN_MODEL", "qwen-max-latest")
            self.llm_provider = "Qwen"
        else:
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
            self.base_url = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
            self.model_name = model_name or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            self.llm_provider = "OpenAI"

        if not self.api_key:
            print(f"警告: 未找到 API Key 环境变量 ({self.llm_provider})")
            self.llm = None
            self.available = False
        else:
            try:
                self.llm = ChatOpenAI(
                    model=self.model_name,
                    api_key=self.api_key,
                    base_url=self.base_url,
                    temperature=0.7,
                )
                self.available = True
                print(f"✅ {self.llm_provider} LLM 初始化成功: {self.model_name}")
            except Exception as e:
                print(f"❌ {self.llm_provider} LLM 初始化失败: {e}")
                self.llm = None
                self.available = False

    def is_available(self) -> bool:
        """检查 LLM 是否可用"""
        return self.available

    async def generate_comprehensive_analysis(self, user_profile: Dict[str, Any]) -> str:
        """
        生成综合健康分析报告（包含补充剂、饮食、冲突检测等）

        参数:
            user_profile: 用户画像字典，包含:
                - stage: 健康阶段
                - age: 年龄
                - gender: 性别
                - name: 姓名（可选）
                - city: 城市
                - current_supplements: 当前补充剂列表
                - gene_data: 基因数据
                - injury_areas: 伤病位置列表
                - weight_kg: 当前体重(kg)
                - body_fat_pct: 当前体脂率(%)
                - waist_cm: 当前腰围(cm)
                - apple_health_data: Apple Health 数据（可选）
                - lifestyle: 生活方式信息（可选）

        返回:
            完整的健康分析报告
        """
        if not self.available:
            return "LLM 不可用，使用规则引擎生成推荐"

        # 提取用户信息
        stage = user_profile.get("stage", "general")
        age = user_profile.get("age", 30)
        gender = user_profile.get("gender", "男")
        name = user_profile.get("name", "")
        city = user_profile.get("city", "未知")
        current_supplements = user_profile.get("current_supplements", [])
        injury_areas = user_profile.get("injury_areas", [])
        weight_kg = user_profile.get("weight_kg")
        body_fat_pct = user_profile.get("body_fat_pct")
        waist_cm = user_profile.get("waist_cm")
        gene_data = user_profile.get("gene_data")
        apple_health_data = user_profile.get("apple_health_data")
        lifestyle = user_profile.get("lifestyle", {})

        # 构建基因信息文本
        gene_info = "未提供基因报告"
        if gene_data and gene_data.get("results"):
            gene_results = gene_data["results"]
            gene_info = "\n".join([f"- {r['gene']}: {r['genotype']} ({r.get('impact', '未知')})" for r in gene_results[:8]])

        # 构建伤病信息
        injury_info = "无不适" if not injury_areas or "无" in injury_areas else ", ".join(injury_areas)

        # 构建身体数据信息
        body_data_parts = []
        if weight_kg:
            body_data_parts.append(f"体重: {weight_kg} kg")
        if body_fat_pct:
            body_data_parts.append(f"体脂率: {body_fat_pct}%")
        if waist_cm:
            body_data_parts.append(f"腰围: {waist_cm} cm")
        body_info = "未提供" if not body_data_parts else "\n".join([f"- {item}" for item in body_data_parts])

        # 构建 Apple Health 数据摘要
        apple_health_info = "未提供"
        if apple_health_data:
            if isinstance(apple_health_data, list) and len(apple_health_data) > 0:
                apple_health_info = f"已提供 {len(apple_health_data)} 条健康数据记录"
            elif isinstance(apple_health_data, dict):
                apple_health_info = "已提供健康数据"

        # 构建生活方式信息
        lifestyle_info = "未提供"
        if lifestyle:
            parts = []
            if lifestyle.get("diet_type"):
                parts.append(f"饮食类型: {lifestyle['diet_type']}")
            if lifestyle.get("activity_level"):
                parts.append(f"运动水平: {lifestyle['activity_level']}")
            lifestyle_info = "\n".join([f"- {p}" for p in parts]) if parts else "未提供"

        # 构建补充剂列表
        supplements_list = ", ".join(current_supplements) if current_supplements else "无"

        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一位专业的健康教练和营养师，擅长基于科学证据提供个性化健康建议。

请根据用户信息生成一份全面、专业的健康分析报告，必须包含以下部分：

1. **整体个性化建议** - 一段综合性的健康建议，整合所有信息
2. **安全评估与冲突检测** - 必须明确输出：
   - 如果当前补充剂之间无冲突：输出"当前服用补剂没有冲突"
   - 如果存在冲突：输出"存在以下冲突：[具体冲突描述] 建议：[具体建议]"
3. **补充剂推荐** - 3-5种推荐补充剂，包含理由、剂量、服用时间
4. **饮食建议** - 每日营养目标、饮食原则、三餐推荐
5. **生活方式建议** - 运动、睡眠、压力管理
6. **品牌推荐** - 3个知名老牌保健品品牌（如 NOW Foods、Jarrow Formulas、Nordic Naturals、Solgar、Thorne Research）

安全第一：任何冲突或风险都要明确指出！确保建议符合科学证据，实用且易于执行。"""),
            ("user", """请为以下用户生成全面的健康分析报告：

---
基本信息
---
- 姓名: {name}
- 阶段: {stage}
- 年龄: {age}岁
- 性别: {gender}
- 城市: {city}

---
身体数据（当前）
---
{body_info}

---
伤病信息
---
- 不适部位: {injury_info}

---
当前补充剂
---
- 正在服用: {supplements_list}

---
基因信息
---
{gene_info}

---
Apple Health 数据
---
{apple_health_info}

---
生活方式
---
{lifestyle_info}

请生成一份专业、全面的健康分析报告，重点突出整体个性化建议和冲突检测结果。""")
        ])

        chain = prompt | self.llm | StrOutputParser()

        try:
            result = await chain.ainvoke({
                "name": name,
                "stage": stage,
                "age": age,
                "gender": gender,
                "city": city,
                "body_info": body_info,
                "injury_info": injury_info,
                "supplements_list": supplements_list,
                "gene_info": gene_info,
                "apple_health_info": apple_health_info,
                "lifestyle_info": lifestyle_info
            })
            return result
        except Exception as e:
            print(f"LLM 生成综合分析失败: {e}")
            return f"LLM 调用失败，错误: {str(e)}"

    async def generate_weekly_report(self, name: str, stage: str, weekly_data: Optional[Dict] = None) -> str:
        """
        生成每周健康周报

        参数:
            name: 用户姓名
            stage: 健康阶段
            weekly_data: 本周数据（可选）

        返回:
            周报文本
        """
        if not self.available:
            return "LLM 不可用，无法生成周报"

        # 构建本周数据摘要
        data_summary = "未提供本周数据"
        if weekly_data:
            parts = []
            for key, value in weekly_data.items():
                parts.append(f"- {key}: {value}")
            data_summary = "\n".join(parts) if parts else "未提供本周数据"

        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一位专业的健康教练，擅长生成简洁、实用的每周健康周报。

请为用户生成本周健康周报，包括：
1. 本周数据总结（简洁明了）
2. 周末目标设定（3个具体、可执行的目标）
3. 下周行动计划（营养、运动、睡眠、补水）

格式：简洁、鼓励性、可执行。"""),
            ("user", """请为以下用户生成本周健康周报：

---
用户信息
---
- 姓名: {name}
- 健康阶段: {stage}

---
本周数据
---
{data_summary}

请生成一份鼓励性的周报，帮助用户下周做得更好。""")
        ])

        chain = prompt | self.llm | StrOutputParser()

        try:
            result = await chain.ainvoke({
                "name": name,
                "stage": stage,
                "data_summary": data_summary
            })
            return result
        except Exception as e:
            print(f"LLM 生成周报失败: {e}")
            return f"LLM 调用失败，错误: {str(e)}"


# 全局实例
_llm_instance = None


def get_llm() -> Optional[HealthCoachLLM]:
    """获取 LLM 实例（单例模式）"""
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = HealthCoachLLM()
    return _llm_instance


def is_llm_available() -> bool:
    """检查 LLM 是否可用"""
    llm = get_llm()
    return llm is not None and llm.is_available()
