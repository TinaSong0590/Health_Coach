#!/usr/bin/env python3
"""
Health Coach - 前端界面
基于 Streamlit 的交互式健康方案生成工具
"""

import streamlit as st
import sys
import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

# 确保能正确导入项目模块
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from agent.graph import run_health_coach_workflow
from tools.gene_report_parser import parse_gene_report_from_text
from tools.diet_analyzer import DietAnalyzer


# ============================================
# 页面配置
# ============================================
st.set_page_config(
    page_title="基因健康教练",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# 自定义CSS样式
# ============================================
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1e3a5f;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.3rem;
        color: #2c5282;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #ebf8ff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #4299e1;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #f0fff4;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #48bb78;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fffaf0;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ed8936;
        margin: 1rem 0;
    }
    .danger-box {
        background-color: #fff5f5;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #f56565;
        margin: 1rem 0;
    }
    .supplement-card {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    .meal-card {
        background-color: #fafafa;
        padding: 0.8rem;
        border-radius: 0.5rem;
        border: 1px solid #e2e8f0;
        margin: 0.3rem 0;
    }
    .upload-section {
        background-color: #f7fafc;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 2px dashed #cbd5e0;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


# ============================================
# 辅助函数
# ============================================
def format_severity(severity):
    """格式化严重程度显示"""
    if "安全" in severity:
        return "🟢 " + severity
    elif "优化" in severity:
        return "🟡 " + severity
    elif "冲突" in severity:
        return "🔴 " + severity
    return severity


def get_stage_description(stage):
    """获取阶段描述"""
    descriptions = {
        "general": "日常健康维护",
        "preconception": "备孕准备期",
        "fat_loss": "减脂塑形",
        "muscle_gain": "增肌训练",
        "jetlag_travel": "时差旅行",
        "recovery": "恢复期"
    }
    return descriptions.get(stage, stage)


def parse_gene_file(uploaded_file):
    """解析上传的基因文件"""
    try:
        if uploaded_file.name.endswith('.pdf'):
            # PDF文件需要额外库，暂时返回提示
            return None, "PDF文件已上传，将在报告中分析"
        else:
            # 读取文本内容
            text = uploaded_file.read().decode('utf-8')
            result = parse_gene_report_from_text(text)
            return result, None
    except Exception as e:
        return None, f"文件解析错误: {str(e)}"


def parse_apple_health(uploaded_file):
    """解析Apple Health数据"""
    try:
        if uploaded_file.name.endswith('.json'):
            data = json.load(uploaded_file)
            return data, None
        elif uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
            return df.to_dict('records'), None
        else:
            return None, "不支持的文件格式，请上传JSON或CSV文件"
    except Exception as e:
        return None, f"文件解析错误: {str(e)}"


# ============================================
# 初始化Session State
# ============================================
if 'body_metrics' not in st.session_state:
    st.session_state.body_metrics = None
if 'apple_health_data' not in st.session_state:
    st.session_state.apple_health_data = None
if 'medical_report_uploaded' not in st.session_state:
    st.session_state.medical_report_uploaded = False


# ============================================
# 侧边栏 - 用户输入表单
# ============================================
with st.sidebar:
    st.markdown("## 👤 基本信息")

    # 基本信息
    name = st.text_input("姓名", placeholder="请输入您的姓名")
    age = st.number_input("年龄", min_value=1, max_value=100, value=30)
    gender = st.selectbox("性别", ["女", "男"])
    city = st.selectbox("生活城市", ["西安", "北京", "上海", "广州", "深圳", "成都", "杭州", "南京"], index=0)

    st.markdown("---")
    st.markdown("## 🎯 健康阶段")

    # 阶段选择
    stage = st.selectbox(
        "当前阶段",
        options=["general", "preconception", "fat_loss", "muscle_gain", "jetlag_travel", "recovery"],
        format_func=lambda x: f"{x} - {get_stage_description(x)}",
        index=0
    )

    st.markdown("---")
    st.markdown("## 🏥 伤病不适位置")

    # 伤病不适
    injury_areas = st.multiselect(
        "选择不适位置（可多选）",
        options=["无", "膝盖", "腰椎", "颈椎", "肩膀", "手腕", "脚踝", "肘部", "背部", "髋部", "其他"],
        default=["无"]
    )

    if "其他" in injury_areas:
        other_injury = st.text_input("请描述其他不适部位")
    else:
        other_injury = ""

    st.markdown("---")
    st.markdown("## 📊 身体数据（当前）")

    # 身体数据输入 - 改为当前值
    col1, col2, col3 = st.columns(3)
    with col1:
        weight_kg = st.number_input("体重 (kg)", min_value=20.0, max_value=200.0, value=70.0, step=0.1)
    with col2:
        body_fat_pct = st.number_input("体脂率 (%)", min_value=3.0, max_value=50.0, value=22.0, step=0.1)
    with col3:
        waist_cm = st.number_input("腰围 (cm)", min_value=40.0, max_value=150.0, value=75.0, step=0.1)

    st.markdown("---")
    st.markdown("## 💊 当前补充剂")

    # 当前补充剂
    available_supplements = [
        "维生素D3", "Omega-3鱼油", "镁", "锌", "维生素B复合",
        "活性叶酸", "铁剂", "辅酶Q10", "肌酸", "乳清蛋白粉",
        "褪黑素", "益生菌", "姜黄素", "红景天", "电解质混合",
        "维生素C", "维生素E", "左旋肉碱"
    ]

    current_supplements = st.multiselect(
        "正在使用的补充剂",
        options=available_supplements,
        default=[]
    )

    # 自定义补充剂输入
    custom_supplement = st.text_input("或输入其他补充剂（用逗号分隔）", placeholder="例如: 螺旋藻, 酵母粉")

    st.markdown("---")
    st.markdown("## 🧬 基因报告")

    # 基因文件上传（支持PDF和TXT）
    uploaded_file = st.file_uploader(
        "📄 上传基因报告（支持PDF、TXT格式）",
        type=['pdf', 'txt'],
        help="上传包含基因型信息的PDF或文本文件"
    )

    # 或手动输入基因信息
    with st.expander("或手动输入基因型信息"):
        manual_genes = st.text_area(
            "输入基因型（每行一个，格式：基因名:基因型）",
            placeholder="例如：\nMTHFR:CT\nVDR:TT\nACTN3:RR",
            height=150
        )

    st.markdown("---")
    st.markdown("## 📱 Apple Health 数据")

    # Apple Health 数据上传
    apple_health_file = st.file_uploader(
        "📱 上传 Apple Health 数据（支持CSV、JSON）",
        type=['csv', 'json'],
        help="上传 Apple Health 导出的健康数据文件"
    )

    st.markdown("---")
    st.markdown("## 🏃 生活方式")

    # 生活方式信息
    diet_type = st.selectbox(
        "饮食类型",
        options=["均衡", "高蛋白", "低碳", "低脂", "素食", "生酮"],
        index=0
    )

    activity_level = st.selectbox(
        "运动水平",
        options=["久坐", "轻度活动", "中度活动", "高度活动", "高强度训练"],
        index=2
    )


# ============================================
# 主界面
# ============================================
st.markdown('<h1 class="main-header">🧬 基因健康教练</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center;color:#666;">基于基因数据、Apple Health 和个人信息的个性化健康建议</p>', unsafe_allow_html=True)

st.markdown("---")

# 生成按钮
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    generate_btn = st.button("🚀 生成个性化健康方案", type="primary", use_container_width=True)

if generate_btn:
    # 构建用户画像
    user_profile = {
        "name": name,
        "age": age,
        "gender": gender,
        "stage": stage,
        "city": city,
        "injury_areas": injury_areas if "无" not in injury_areas else [],
        "weight_kg": weight_kg,
        "body_fat_pct": body_fat_pct,
        "waist_cm": waist_cm,
        "current_supplements": current_supplements,
        "lifestyle": {
            "diet_type": diet_type,
            "activity_level": activity_level
        }
    }

    # 处理补充剂自定义输入
    if custom_supplement:
        custom_list = [s.strip() for s in custom_supplement.split(',') if s.strip()]
        user_profile["current_supplements"].extend(custom_list)

    # 处理基因文件上传
    gene_data = None
    if uploaded_file:
        with st.spinner("正在解析基因报告..."):
            gene_data, error = parse_gene_file(uploaded_file)
            if error:
                st.warning(f"基因报告解析: {error}")
            elif gene_data:
                user_profile["gene_data"] = gene_data
                st.success(f"✅ 成功解析基因报告，检测到 {gene_data.get('total_snps_found', 0)} 个 SNP 位点")

    # 处理手动输入的基因信息
    if not gene_data and manual_genes:
        try:
            lines = [line.strip() for line in manual_genes.split('\n') if line.strip() and ':' in line]
            gene_results = []
            for line in lines:
                gene, genotype = line.split(':', 1)
                gene_results.append({
                    "gene": gene.strip(),
                    "genotype": genotype.strip(),
                    "impact": "未知"
                })
            if gene_results:
                user_profile["gene_data"] = {
                    "total_snps_found": len(gene_results),
                    "results": gene_results,
                    "recommendations": []
                }
                st.success(f"✅ 成功解析手动输入的 {len(gene_results)} 个基因位点")
        except Exception as e:
            st.error(f"解析手动基因信息失败: {e}")

    # 处理 Apple Health 数据
    apple_health_data = None
    if apple_health_file:
        with st.spinner("正在解析 Apple Health 数据..."):
            apple_health_data, error = parse_apple_health(apple_health_file)
            if error:
                st.warning(f"Apple Health 数据解析: {error}")
            elif apple_health_data:
                user_profile["apple_health_data"] = apple_health_data
                st.success(f"✅ 成功解析 Apple Health 数据")

    # 显示处理进度
    with st.spinner("正在生成个性化健康方案..."):
        try:
            # 运行健康教练工作流
            result = run_health_coach_workflow(user_profile)

            # 显示结果
            st.markdown("---")
            st.markdown('<h2 class="sub-header">📋 您的个性化健康方案</h2>', unsafe_allow_html=True)

            # 显示 LLM 生成的完整报告
            if result.get("final_response"):
                st.markdown(result["final_response"])

            # 显示补充剂推荐（如果有单独的数据）
            if result.get("supplements"):
                st.markdown("---")
                st.markdown("### 💊 补充剂推荐详情")

                supplements = result["supplements"]
                if supplements.get("recommended"):
                    st.success(f"推荐补充剂 ({len(supplements['recommended'])} 种):")
                    for sup in supplements["recommended"]:
                        st.markdown(f"- {sup}")

                if supplements.get("avoid"):
                    st.warning("避免使用:")
                    for sup in supplements["avoid"]:
                        st.markdown(f"- {sup}")

            # 显示冲突检测结果
            if result.get("conflicts"):
                st.markdown("---")
                st.markdown("### 🔍 安全评估")

                conflicts = result["conflicts"]
                severity = conflicts.get("severity", "未知")
                severity_formatted = format_severity(severity)
                st.markdown(f"**冲突等级**: {severity_formatted}")

                if conflicts.get("conflicts"):
                    for conflict in conflicts["conflicts"]:
                        if conflict.get("severity") == "critical":
                            st.error(f"⚠️ {conflict.get('reason', '未知冲突')}")
                        elif conflict.get("severity") == "warning":
                            st.warning(f"⚠️ {conflict.get('reason', '未知冲突')}")
                else:
                    st.success("✅ 未检测到补充剂冲突")

            # 显示基因数据摘要
            if result.get("gene_data") and result["gene_data"].get("results"):
                st.markdown("---")
                st.markdown("### 🧬 基因检测结果")

                gene_results = result["gene_data"]["results"][:10]
                for gene in gene_results:
                    impact_color = "🔴" if gene.get("impact") == "high" else ("🟡" if gene.get("impact") == "moderate" else "🟢")
                    st.markdown(f"{impact_color} **{gene['gene']}**: {gene['genotype']} ({gene.get('impact', '未知')})")

        except Exception as e:
            st.error(f"生成健康方案失败: {e}")
            import traceback
            st.error(traceback.format_exc())


# ============================================
# 底部信息
# ============================================
st.markdown("---")
st.markdown('<p style="text-align:center;color:#999;font-size:0.9rem;">'
            '💡 提示：本建议仅供参考，不能替代专业医疗建议。如有健康问题，请咨询专业医生。'
            '</p>', unsafe_allow_html=True)
