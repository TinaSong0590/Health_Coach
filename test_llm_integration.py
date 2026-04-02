#!/usr/bin/env python3
"""
测试 LLM 集成 - 通义千问版本
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from agent.llm_integration import HealthCoachLLM


def test_qwen_llm_connection():
    """测试通义千问 LLM 连接"""
    print("=" * 60)
    print("测试通义千问 LLM 集成")
    print("=" * 60)

    # 初始化通义千问 LLM
    llm = HealthCoachLLM(use_qwen=True)

    # 检查 LLM 是否可用
    if not llm.is_available():
        print("❌ 通义千问 LLM 不可用，请检查:")
        print("  1. 是否已安装 langchain-openai")
        print("  2. 是否已设置 QWEN_API_KEY 环境变量")
        print("  3. .env 文件是否存在且配置正确")
        print("  4. 网络连接是否正常")
        return False

    print("✅ 通义千问 LLM 可用")
    print(f"📦 模型: {llm.model_name}")
    print(f"🔗 API Base: {llm.base_url}")

    # 测试简单调用
    print("\n测试简单调用...")
    try:
        import asyncio
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser

        prompt = ChatPromptTemplate.from_template("你好，请用一句话介绍你自己。")
        chain = prompt | llm.llm | StrOutputParser()
        result = asyncio.run(chain.ainvoke({}))

        print(f"✅ LLM 响应: {result}")
    except Exception as e:
        print(f"❌ LLM 调用失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 测试补充剂推荐
    print("\n测试补充剂推荐生成...")
    try:
        result = asyncio.run(llm.generate_supplement_recommendations(
            stage="肌少症前期",
            age=65,
            gender="男",
            current_supplements=["钙片", "维生素D3"],
            gene_data={
                "results": [
                    {"gene": "VDR", "genotype": "TT", "impact": "高风险"}
                ]
            }
        ))
        print(f"✅ 补充剂推荐生成成功（前200字符）:")
        print(result[:200] + "...")
    except Exception as e:
        print(f"❌ 补充剂推荐生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 测试饮食建议
    print("\n测试饮食建议生成...")
    try:
        result = asyncio.run(llm.generate_dietary_advice(
            stage="肌少症前期",
            age=65,
            gender="男",
            city="北京",
            diet_type="高蛋白"
        ))
        print(f"✅ 饮食建议生成成功（前200字符）:")
        print(result[:200] + "...")
    except Exception as e:
        print(f"❌ 饮食建议生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "=" * 60)
    print("✅ 通义千问 LLM 所有测试通过！")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_qwen_llm_connection()
    sys.exit(0 if success else 1)
