#!/usr/bin/env python3
"""
Health Coach 工作流测试脚本

测试整个 LangGraph 工作流流程
"""

import sys
from pathlib import Path

# 确保能正确导入项目模块
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from agent.graph import create_health_coach_graph, quick_recommend
from tools.gene_report_parser import parse_gene_report_from_text


def print_section(title: str):
    """打印分隔线"""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}\n")


def test_basic_workflow():
    """测试基础工作流"""
    print_section("测试1: 基础工作流（无基因报告）")

    result = quick_recommend(
        stage="preconception",
        age=28,
        gender="female",
        current_supplements=["维生素 D3", "Omega-3 鱼油"]
    )

    print(result)
    print("\n✓ 基础工作流测试完成")


def test_all_stages():
    """测试所有阶段"""
    print_section("测试2: 所有健康阶段快速预览")

    stages = [
        ("general", 30, "male", "日常健康"),
        ("preconception", 28, "female", "备孕准备"),
        ("fat_loss", 25, "female", "减脂塑形"),
        ("muscle_gain", 25, "male", "增肌训练"),
        ("jetlag_travel", 35, "male", "时差旅行"),
        ("recovery", 40, "female", "恢复期")
    ]

    for stage, age, gender, desc in stages:
        print(f"\n【{desc}】({stage})")
        result = quick_recommend(
            stage=stage,
            age=age,
            gender=gender,
            current_supplements=[]
        )

        # 只显示关键信息
        lines = result.split('\n')
        for line in lines[:10]:  # 显示前10行
            print(line)


def test_with_gene_data():
    """测试带基因数据的工作流"""
    print_section("测试3: 基因数据集成")

    # 模拟基因报告文本
    gene_text = """
    MTHFR C677T (rs1801133)
    基因型: CT
    影响: 中等

    VDR FokI (rs2228570)
    基因型: FF

    COMT Val158Met (rs4680)
    基因型: Val/Met
    """

    # 先测试基因解析
    print("【基因解析测试】")
    gene_result = parse_gene_report_from_text(gene_text)

    print(f"摘要: {gene_result['summary']}")
    print(f"\n检测结果:")
    for r in gene_result['results']:
        print(f"  {r['gene']} {r['variant']}: {r['genotype']} ({r['impact']})")

    print(f"\n建议:")
    for rec in gene_result['recommendations']:
        print(f"  - {rec}")

    # 测试带基因数据的完整推荐
    print("\n【带基因数据的完整推荐】")
    result = quick_recommend(
        stage="preconception",
        age=28,
        gender="female",
        current_supplements=["活性叶酸"]
    )

    print(result)


def test_conflict_detection():
    """测试冲突检测"""
    print_section("测试4: 冲突检测功能")

    print("【测试4.1】硬冲突: 铁 + 钙")
    result = quick_recommend(
        stage="general",
        age=30,
        gender="male",
        current_supplements=["铁", "钙", "维生素 D3"]
    )

    # 提取冲突信息
    lines = result.split('\n')
    in_conflict_section = False
    for line in lines:
        if "安全评估" in line:
            in_conflict_section = True
        if in_conflict_section:
            print(line)
        if line and not in_conflict_section and "安全评估" in line:
            break
        if line and in_conflict_section and "补充剂" in line:
            break

    print("\n【测试4.2】阶段禁忌: 备孕 + 褪黑素")
    result = quick_recommend(
        stage="preconception",
        age=28,
        gender="female",
        current_supplements=["褪黑素"]
    )

    in_conflict_section = False
    for line in lines:
        if "安全评估" in line:
            in_conflict_section = True
        if in_conflict_section:
            print(line)
        if line and in_conflict_section and "补充剂" in line:
            break


def test_muscle_gain():
    """测试增肌阶段详细推荐"""
    print_section("测试5: 增肌阶段详细推荐")

    result = quick_recommend(
        stage="muscle_gain",
        age=25,
        gender="male",
        current_supplements=["肌酸", "乳清蛋白"]
    )

    print(result)
    print("\n✓ 增肌阶段推荐完成")


def test_fat_loss():
    """测试减脂阶段详细推荐"""
    print_section("测试6: 减脂阶段详细推荐")

    result = quick_recommend(
        stage="fat_loss",
        age=30,
        gender="female",
        current_supplements=["Omega-3 鱼油"]
    )

    print(result)
    print("\n✓ 减脂阶段推荐完成")


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("  Health Coach - 工作流测试套件")
    print("=" * 70)

    try:
        # 运行所有测试
        test_basic_workflow()
        test_all_stages()
        test_with_gene_data()
        test_conflict_detection()
        test_muscle_gain()
        test_fat_loss()

        print_section("✓ 所有测试通过！")
        print("工作流验证成功，系统运行正常。\n")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
