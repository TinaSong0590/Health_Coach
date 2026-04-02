"""
Health Coach Agent - 基于 LangGraph 的健康教练工作流

实现一个状态机，逐步处理用户健康数据：
1. 用户画像收集
2. 基因报告解析
3. 冲突检测
4. 综合分析（LLM）
5. 输出生成
"""

import sys
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional, TypedDict
from enum import Enum

# 确保能正确导入项目模块
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from langgraph.graph import StateGraph, END
    from langchain_core.messages import BaseMessage
except ImportError:
    # 如果 LangGraph 未安装，提供简化实现
    StateGraph = None
    BaseMessage = dict

from schemas.user_profile import UserProfile, Stage
from tools.conflict_checker import ConflictChecker, ConflictSeverity
from tools.supplement_recommender import SupplementRecommender
from tools.gene_report_parser import GeneReportParser, parse_gene_report
from tools.diet_analyzer import DietAnalyzer, analyze_diet
from prompts.system_prompt import SYSTEM_PROMPT, get_stage_prompt, get_gene_adjustment_prompt
from agent.llm_integration import get_llm, is_llm_available


class HealthCoachState(TypedDict):
    """健康教练工作流状态"""
    # 输入
    user_input: str
    stage: Optional[str]
    age: Optional[int]
    gender: Optional[str]
    gene_report_path: Optional[str]
    current_supplements: Optional[List[str]]

    # 中间结果
    user_profile: Optional[Dict]
    gene_data: Optional[Dict]
    conflict_results: Optional[Dict]
    supplement_recommendations: Optional[Dict]
    dietary_recommendations: Optional[List[str]]
    dietary_analysis: Optional[Dict]

    # 输出
    final_response: Optional[str]
    suggestions: List[str]
    warnings: List[str]

    # 元数据
    current_step: str
    completed_steps: List[str]


class WorkflowStep(str, Enum):
    """工作流步骤"""
    INITIAL = "initial"
    PROFILE_COLLECTION = "profile_collection"
    GENE_PARSING = "gene_parsing"
    CONFLICT_CHECKING = "conflict_checking"
    COMPREHENSIVE_ANALYSIS = "comprehensive_analysis"
    RESPONSE_GENERATION = "response_generation"
    COMPLETE = "complete"


class HealthCoachGraph:
    """健康教练工作流图"""

    def __init__(self):
        """初始化工作流"""
        self.conflict_checker = ConflictChecker()
        self.supplement_recommender = SupplementRecommender()
        self.gene_parser = GeneReportParser()
        self.diet_analyzer = DietAnalyzer()
        self.llm = get_llm()

        # 检查 LLM 可用性
        if is_llm_available():
            print("✅ LLM 已启用，将使用 AI 驱动的综合分析")
        else:
            print("⚠️  LLM 不可用，使用规则引擎生成推荐")

        # 构建状态机
        self.graph = self._build_graph()

    def _build_graph(self):
        """构建 LangGraph 状态机"""
        if StateGraph is None:
            # 简化版本：不使用 LangGraph
            return None

        graph = StateGraph(HealthCoachState)

        # 添加节点
        graph.add_node("initial", self._initial_step)
        graph.add_node("profile_collection", self._collect_profile)
        graph.add_node("gene_parsing", self._parse_gene_report)
        graph.add_node("conflict_checking", self._check_conflicts)
        graph.add_node("comprehensive_analysis", self._comprehensive_analysis)
        graph.add_node("response_generation", self._generate_response)

        # 设置入口
        graph.set_entry_point("initial")

        # 添加边（转换规则）
        graph.add_edge("initial", "profile_collection")
        graph.add_conditional_edges(
            "profile_collection",
            self._should_parse_gene,
            {
                "yes": "gene_parsing",
                "no": "conflict_checking"
            }
        )
        graph.add_edge("gene_parsing", "conflict_checking")
        graph.add_edge("conflict_checking", "comprehensive_analysis")
        graph.add_edge("comprehensive_analysis", "response_generation")
        graph.add_edge("response_generation", END)

        return graph.compile()

    # ========== 节点函数 ==========

    def _initial_step(self, state: HealthCoachState) -> HealthCoachState:
        """初始步骤：解析用户输入"""
        print(f"[初始] 处理用户输入: {state['user_input'][:50]}...")

        state["current_step"] = WorkflowStep.INITIAL.value
        state["completed_steps"] = []

        return state

    def _collect_profile(self, state: HealthCoachState) -> HealthCoachState:
        """收集用户画像"""
        print(f"[画像] 收集用户画像...")

        # 从状态或用户输入中提取信息
        stage = state.get("stage", "general")
        age = state.get("age", 30)
        gender = state.get("gender", "male")

        # 验证阶段
        valid_stages = [s.value for s in Stage]
        if stage not in valid_stages:
            stage = "general"

        profile = {
            "stage": stage,
            "age": age,
            "gender": gender,
            "current_supplements": state.get("current_supplements", []),
        }

        state["user_profile"] = profile
        state["current_step"] = WorkflowStep.PROFILE_COLLECTION.value
        state["completed_steps"].append(WorkflowStep.PROFILE_COLLECTION.value)

        return state

    def _parse_gene_report(self, state: HealthCoachState) -> HealthCoachState:
        """解析基因报告"""
        print(f"[基因] 解析基因报告...")

        gene_path = state.get("gene_report_path")
        gene_data = None

        if gene_path and Path(gene_path).exists():
            try:
                gene_data = parse_gene_report(gene_path)
                print(f"  - 检测到 {gene_data['total_snps_found']} 个 SNP 位点")
            except Exception as e:
                print(f"  - 解析失败: {e}")
                gene_data = {"error": str(e)}
        else:
            print(f"  - 未提供基因报告，使用默认假设")
            gene_data = {"total_snps_found": 0, "results": [], "recommendations": []}

        state["gene_data"] = gene_data
        state["current_step"] = WorkflowStep.GENE_PARSING.value
        state["completed_steps"].append(WorkflowStep.GENE_PARSING.value)

        return state

    def _check_conflicts(self, state: HealthCoachState) -> HealthCoachState:
        """检查补充剂冲突"""
        print(f"[冲突] 检测补充剂冲突...")

        current_sups = state["user_profile"].get("current_supplements", [])
        stage = state["user_profile"]["stage"]

        severity, conflicts, suggestions = self.conflict_checker.check_supplement_conflicts(
            current_sups, stage
        )

        conflict_results = {
            "severity": severity.value,
            "conflicts": conflicts,
            "suggestions": suggestions,
            "count": len(conflicts)
        }

        state["conflict_results"] = conflict_results
        state["warnings"] = [c["reason"] for c in conflicts if c.get("severity") == "critical"]
        state["current_step"] = WorkflowStep.CONFLICT_CHECKING.value
        state["completed_steps"].append(WorkflowStep.CONFLICT_CHECKING.value)

        return state

    def _comprehensive_analysis(self, state: HealthCoachState) -> HealthCoachState:
        """综合分析：调用 LLM 生成完整的健康分析"""
        print(f"[综合] 生成综合健康分析...")

        # 构建完整的用户画像用于 LLM 分析
        comprehensive_profile = {
            "stage": state["user_profile"]["stage"],
            "age": state["user_profile"]["age"],
            "gender": state["user_profile"]["gender"],
            "current_supplements": state["user_profile"].get("current_supplements", []),
            "gene_data": state["gene_data"],
            "injury_areas": state["user_profile"].get("injury_areas", []),
            "weight_kg": state["user_profile"].get("weight_kg"),
            "body_fat_pct": state["user_profile"].get("body_fat_pct"),
            "waist_cm": state["user_profile"].get("waist_cm"),
            "city": state["user_profile"].get("city", "未知"),
            "name": state["user_profile"].get("name", ""),
            "apple_health_data": state["user_profile"].get("apple_health_data"),
            "lifestyle": state["user_profile"].get("lifestyle", {})
        }

        # 尝试使用 LLM 生成综合分析
        if is_llm_available():
            try:
                llm_analysis = asyncio.run(self.llm.generate_comprehensive_analysis(comprehensive_profile))
                print(f"  → LLM 生成的综合分析已应用")

                # 使用 LLM 分析结果作为最终响应
                state["final_response"] = llm_analysis

                # 仍然保留规则引擎的结果作为补充信息
                from tools.supplement_recommender import recommend_supplements_basic
                rule_based = recommend_supplements_basic(
                    stage=state["user_profile"]["stage"],
                    age=state["user_profile"]["age"],
                    gender=state["user_profile"]["gender"],
                    current_supplements=comprehensive_profile["current_supplements"]
                )
                state["supplement_recommendations"] = rule_based
                state["conflict_results"] = state["conflict_results"]
            except Exception as e:
                print(f"  → LLM 生成失败: {e}")
                state["final_response"] = None
        else:
            # LLM 不可用，在响应生成阶段使用规则引擎
            state["final_response"] = None

        state["current_step"] = WorkflowStep.COMPREHENSIVE_ANALYSIS.value
        state["completed_steps"].append(WorkflowStep.COMPREHENSIVE_ANALYSIS.value)

        return state

    def _generate_response(self, state: HealthCoachState) -> HealthCoachState:
        """生成最终响应"""
        print(f"[响应] 生成最终响应...")

        # 如果 LLM 已生成综合分析，直接使用
        if state.get("final_response"):
            print(f"  → 使用 LLM 生成的综合分析")
        else:
            # 使用规则引擎生成响应
            state["final_response"] = self._generate_rule_based_response(state)

        state["current_step"] = WorkflowStep.RESPONSE_GENERATION.value
        state["completed_steps"].append(WorkflowStep.RESPONSE_GENERATION.value)

        return state

    def _generate_rule_based_response(self, state: HealthCoachState) -> str:
        """基于规则生成响应（备选方案）"""
        response_parts = []

        # 开场
        stage = state["user_profile"]["stage"]
        response_parts.append(f"# 健康建议报告\n")
        response_parts.append(f"**当前阶段**: {stage}\n")

        # 冲突检测结果
        if state["conflict_results"]:
            severity = state["conflict_results"]["severity"]
            response_parts.append(f"## 🔍 安全评估\n")
            response_parts.append(f"**冲突等级**: {severity}\n")

            if state["warnings"]:
                response_parts.append(f"**重要警告**:\n")
                for w in state["warnings"]:
                    response_parts.append(f"- ⚠️ {w}\n")

        # 补充剂推荐
        if state["supplement_recommendations"]:
            response_parts.append(f"\n## 💊 补充剂推荐\n")
            sups = state["supplement_recommendations"]["recommended"]
            response_parts.append(f"**推荐补充剂** ({len(sups)}):\n")
            for i, sup in enumerate(sups[:8], 1):
                response_parts.append(f"{i}. {sup}\n")

            if "avoid" in state["supplement_recommendations"] and state["supplement_recommendations"]["avoid"]:
                response_parts.append(f"\n**避免使用**:\n")
                for sup in state["supplement_recommendations"]["avoid"]:
                    response_parts.append(f"- {sup}\n")

        # 饮食建议
        response_parts.append(f"\n## 🥗 饮食建议\n")
        response_parts.append(f"**饮食原则**:\n")
        response_parts.append(f"- 根据您的健康阶段 {stage}，建议采用均衡饮食\n")
        response_parts.append(f"- 保证充足的蛋白质摄入\n")
        response_parts.append(f"- 多吃新鲜蔬菜和水果\n")

        # 整体个性化建议
        response_parts.append(f"\n## 📋 整体个性化建议\n")
        response_parts.append(f"基于您的健康阶段 {stage} 和个人信息，建议您:\n")
        response_parts.append(f"- 坚持规律作息，保证充足睡眠\n")
        response_parts.append(f"- 根据自身情况选择合适的运动方式\n")
        response_parts.append(f"- 定期监测身体指标，及时调整生活方式\n")

        return "".join(response_parts)

    # ========== 条件函数 ==========

    def _should_parse_gene(self, state: HealthCoachState) -> str:
        """判断是否需要解析基因报告"""
        gene_path = state.get("gene_report_path")
        return "yes" if gene_path and Path(gene_path).exists() else "no"

    # ========== 公共接口 ==========

    def run(self, initial_state: Dict[str, Any]) -> HealthCoachState:
        """运行完整工作流"""
        if self.graph is None:
            # 简化版本：逐步执行
            return self._run_simple(initial_state)

        # 使用 LangGraph 执行
        return self.graph.invoke(initial_state)

    def _run_simple(self, initial_state: Dict[str, Any]) -> HealthCoachState:
        """简化版本执行（无 LangGraph）"""
        state = HealthCoachState(**initial_state)

        # 逐步执行
        state = self._initial_step(state)
        state = self._collect_profile(state)

        if self._should_parse_gene(state) == "yes":
            state = self._parse_gene_report(state)

        state = self._check_conflicts(state)
        state = self._comprehensive_analysis(state)
        state = self._generate_response(state)

        return state


# 便捷函数
def create_health_coach_graph() -> HealthCoachGraph:
    """创建健康教练工作流实例"""
    return HealthCoachGraph()


def run_health_coach_workflow(user_profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    运行健康教练完整工作流

    参数:
        user_profile: 用户画像字典，包含所有用户信息:
            - stage: 健康阶段
            - age: 年龄
            - gender: 性别
            - current_supplements: 当前补充剂列表（可选）
            - gene_report_path: 基因报告路径（可选）
            - injury_areas: 伤病位置（可选）
            - weight_kg: 当前体重（可选）
            - body_fat_pct: 当前体脂率（可选）
            - waist_cm: 当前腰围（可选）
            - city: 城市（可选）
            - name: 姓名（可选）
            - apple_health_data: Apple Health 数据（可选）
            - lifestyle: 生活方式信息（可选）

    返回:
        包含所有推荐结果的字典:
            - final_response: 完整推荐文本
            - supplements: 补充剂推荐
            - dietary: 饮食建议
            - conflicts: 冲突检测结果
            - gene_data: 基因数据（如果有）
    """
    graph = create_health_coach_graph()

    # 构建初始状态
    initial_state = {
        "user_input": f"健康推荐 - 阶段:{user_profile.get('stage')}",
        "stage": user_profile.get("stage", "general"),
        "age": user_profile.get("age", 30),
        "gender": user_profile.get("gender", "male"),
        "gene_report_path": user_profile.get("gene_report_path"),
        "current_supplements": user_profile.get("current_supplements", []),
        "user_profile": user_profile,  # 直接使用传入的用户画像
        "gene_data": None,
        "conflict_results": None,
        "supplement_recommendations": None,
        "dietary_recommendations": None,
        "dietary_analysis": None,
        "final_response": None,
        "suggestions": [],
        "warnings": [],
        "current_step": "",
        "completed_steps": []
    }

    # 运行工作流
    result_state = graph.run(initial_state)

    # 返回结构化结果
    return {
        "final_response": result_state["final_response"],
        "supplements": result_state.get("supplement_recommendations"),
        "dietary": result_state.get("dietary_recommendations"),
        "dietary_analysis": result_state.get("dietary_analysis"),
        "conflicts": result_state.get("conflict_results"),
        "gene_data": result_state.get("gene_data"),
        "warnings": result_state.get("warnings"),
        "suggestions": result_state.get("suggestions")
    }


if __name__ == "__main__":
    # 测试示例
    print("=== 健康教练工作流测试 ===\n")

    result = run_health_coach_workflow({
        "stage": "preconception",
        "age": 28,
        "gender": "female",
        "current_supplements": ["维生素 D3", "Omega-3 鱼油"],
        "name": "Linxia",
        "city": "西安"
    })

    print(result["final_response"])
