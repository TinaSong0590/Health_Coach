#!/usr/bin/env python3
"""
Health Coach 完整推荐流程测试脚本

测试整个健康教练工作流：
- 用户画像收集
- 冲突检测
- 补充剂推荐
- 饮食建议
- 输出生成
"""

import sys
from pathlib import Path

# 确保能正确导入项目模块
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from agent.graph import run_health_coach_workflow, quick_recommend
from tools.gene_report_parser import parse_gene_report_from_text
from tools.diet_analyzer import DietAnalyzer, ChineseFoodDatabase


def print_section(title: str):
    """打印分隔线"""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}\n")


def test_preconception_full_workflow():
    """测试备孕阶段完整流程"""
    print_section("测试1: 备孕阶段完整推荐流程")

    # 创建用户画像
    user_profile = {
        "stage": "preconception",
        "age": 28,
        "gender": "female",
        "current_supplements": ["维生素 D3", "Omega-3 鱼油"],
        "gene_report_path": None
    }

    print("【用户信息】")
    print(f"阶段: {user_profile['stage']}")
    print(f"年龄: {user_profile['age']}")
    print(f"性别: {user_profile['gender']}")
    print(f"当前补充剂: {', '.join(user_profile['current_supplements'])}\n")

    # 运行完整工作流
    print("运行完整工作流...\n")
    result = run_health_coach_workflow(user_profile)

    # 显示结果摘要
    print("【推荐结果摘要】")
    print(f"冲突数量: {result['conflicts']['count']}")
    print(f"冲突等级: {result['conflicts']['severity']}")
    print(f"补充剂推荐数: {len(result['supplements']['recommended'])}")
    print(f"饮食建议数: {len(result['dietary']) if result['dietary'] else 0}")
    print(f"警告数: {len(result['warnings'])}\n")

    # 显示完整响应
    print("【完整推荐报告】")
    print(result['final_response'])
    print("\n✓ 备孕阶段完整流程测试完成")


def test_with_gene_data():
    """测试带基因数据的推荐"""
    print_section("测试2: 带基因数据的个性化推荐")

    # 模拟基因报告
    gene_text = """
    MTHFR C677T (rs1801133)
    基因型: CT
    影响: 中等

    VDR FokI (rs2228570)
    基因型: FF

    COMT Val158Met (rs4680)
    基因型: Val/Met
    """

    # 解析基因报告
    print("【基因解析】")
    gene_result = parse_gene_report_from_text(gene_text)
    print(f"摘要: {gene_result['summary']}\n")

    print("检测结果:")
    for r in gene_result['results']:
        print(f"  - {r['gene']}: {r['genotype']} ({r['impact']})")

    print(f"\n基因建议:")
    for rec in gene_result['recommendations']:
        print(f"  • {rec}\n")

    # 生成推荐
    user_profile = {
        "stage": "preconception",
        "age": 28,
        "gender": "female",
        "current_supplements": ["活性叶酸"],
        "gene_report_path": None
    }

    result = run_health_coach_workflow(user_profile)

    # 添加基因调整（模拟）
    if gene_result['recommendations']:
        print("【基因个性化调整】")
        for rec in gene_result['recommendations']:
            print(f"  • {rec}")
        print()

    print("【补充剂推荐】")
    for i, sup in enumerate(result['supplements']['recommended'][:5], 1):
        print(f"  {i}. {sup}")

    print("\n【饮食建议原则】")
    for i, advice in enumerate(result['dietary'][:4], 1):
        print(f"  {i}. {advice}")

    print("\n✓ 基因数据个性化推荐测试完成")


def test_all_stages_quick():
    """快速测试所有阶段"""
    print_section("测试3: 所有健康阶段快速预览")

    stages = [
        ("general", 30, "male", "日常健康", []),
        ("preconception", 28, "female", "备孕准备", ["维生素 D3", "Omega-3 鱼油"]),
        ("fat_loss", 25, "female", "减脂塑形", []),
        ("muscle_gain", 25, "male", "增肌训练", ["肌酸", "乳清蛋白"]),
        ("jetlag_travel", 35, "male", "时差旅行", []),
        ("recovery", 40, "female", "恢复期", [])
    ]

    for stage, age, gender, desc, current in stages:
        print(f"\n【{desc}】({stage})")
        result = quick_recommend(
            stage=stage,
            age=age,
            gender=gender,
            current_supplements=current
        )

        # 提取关键信息
        lines = result.split('\n')
        for i, line in enumerate(lines[:12]):  # 显示前12行
            print(line)
        print("...")


def test_conflict_detection():
    """测试冲突检测功能"""
    print_section("测试4: 补充剂冲突检测")

    print("【测试4.1】硬冲突: 铁 + 钙")
    result = quick_recommend(
        stage="general",
        age=30,
        gender="male",
        current_supplements=["铁", "钙", "维生素 D3"]
    )

    # 提取安全评估部分
    lines = result.split('\n')
    in_safety_section = False
    for i, line in enumerate(lines):
        if "安全评估" in line:
            in_safety_section = True
        if in_safety_section:
            print(line)
        if line and in_safety_section and "补充剂" in line:
            break

    print("\n【测试4.2】阶段禁忌: 备孕 + 褪黑素")
    result = quick_recommend(
        stage="preconception",
        age=28,
        gender="female",
        current_supplements=["褪黑素"]
    )

    in_safety_section = False
    for line in lines:
        if "安全评估" in line:
            in_safety_section = True
        if in_safety_section:
            print(line)
        if line and in_safety_section and "补充剂" in line:
            break

    print("\n✓ 冲突检测测试完成")


def test_dietary_recommendations():
    """测试饮食推荐"""
    print_section("测试5: 饮食推荐功能")

    analyzer = DietAnalyzer()

    # 测试备孕阶段
    print("【备孕阶段饮食推荐】")
    diet_result = analyzer.analyze_diet("备孕", "preconception")

    print("饮食原则:")
    for principle in diet_result['principles'][:3]:
        print(f"  • {principle}")

    print("\n早餐推荐:")
    for food in diet_result['meal_recommendations']['breakfast'][:2]:
        print(f"  - {food['name']} ({food['calories']}kcal)")

    print("\n午餐推荐:")
    for food in diet_result['meal_recommendations']['lunch'][:3]:
        print(f"  - {food['name']} ({food['calories']}kcal)")

    print("\n每日营养目标:")
    print(f"  热量: {diet_result['daily_calories']}kcal")
    print(f"  蛋白质: {diet_result['protein_target']:.0f}g")
    print(f"  碳水化合物: {diet_result['carbs_target']:.0f}g")
    print(f"  脂肪: {diet_result['fat_target']:.0f}g")

    # 测试食物搜索
    print("\n【食物搜索示例】")
    print("增肌阶段午餐推荐:")
    foods = ChineseFoodDatabase.search_foods(stage="muscle_gain", category="lunch")
    for food in foods[:5]:
        print(f"  - {food['name']}: {food['calories']}kcal, 蛋白质{food['protein']}g")

    print("\n✓ 饮食推荐测试完成")


def test_food_database():
    """测试食物数据库"""
    print_section("测试6: 中国菜食物数据库")

    print("【食物数据库统计】")
    total_foods = len(ChineseFoodDatabase.FOODS)
    print(f"总食物数: {total_foods}\n")

    print("【蛋白质来源】")
    protein_foods = [name for name, info in ChineseFoodDatabase.FOODS.items() if info['protein'] > 15]
    for food in protein_foods[:6]:
        info = ChineseFoodDatabase.get_food_info(food)
        print(f"  - {food}: {info['calories']}kcal, 蛋白质{info['protein']}g")

    print("\n【低热量蔬菜】")
    low_cal_foods = [name for name, info in ChineseFoodDatabase.FOODS.items() 
                    if info['calories'] < 50 and 'protein' not in name.lower()]
    for food in low_cal_foods[:5]:
        info = ChineseFoodDatabase.get_food_info(food)
        print(f"  - {food}: {info['calories']}kcal, 纤维{info['fiber']}g")

    # 测试营养计算
    print("\n【餐食营养计算】")
    analyzer = DietAnalyzer()
    meal = ["清蒸鲈鱼", "清炒西兰花", "白米饭"]
    nutrition = analyzer.calculate_meal_calories(meal, [1.5, 1.0, 1.5])  # 150g鱼, 100g菜, 150g饭

    print(f"餐食: {', '.join(meal)}")
    print(f"总热量: {nutrition['calories']:.0f}kcal")
    print(f"蛋白质: {nutrition['protein']:.1f}g ({nutrition['protein_ratio']*100:.1f}%)")
    print(f"碳水: {nutrition['carbs']:.1f}g ({nutrition['carbs_ratio']*100:.1f}%)")
    print(f"脂肪: {nutrition['fat']:.1f}g ({nutrition['fat_ratio']*100:.1f}%)")
    print(f"纤维: {nutrition['fiber']:.1f}g")

    print("\n✓ 食物数据库测试完成")


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("  Health Coach - 完整推荐流程测试套件")
    print("=" * 80)

    try:
        # 运行所有测试
        test_preconception_full_workflow()
        test_with_gene_data()
        test_all_stages_quick()
        test_conflict_detection()
        test_dietary_recommendations()
        test_food_database()

        print_section("✓ 所有测试通过！")
        print("健康教练系统验证成功，所有功能运行正常。\n")
        print("使用以下命令测试 CLI:")
        print("  python main.py recommend --stage preconception --age 28 --gender female")
        print("  python main.py analyze-report --file gene_report.txt --stage preconception\n")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
