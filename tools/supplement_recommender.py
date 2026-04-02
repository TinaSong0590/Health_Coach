#!/usr/bin/env python3
"""
补充剂推荐引擎 - 最终版（彻底解决 green_tea_extract 错误）
"""

import sys
from pathlib import Path
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.conflict_checker import check_supplement_conflicts

def recommend_supplements_basic(stage: str = "general", age: int = 30, gender: str = "female", **kwargs) -> Dict[str, Any]:
    """使用数据库中真实存在的名称"""
    print(f"  → 生成 {stage} 阶段补充剂推荐 (年龄:{age}, 性别:{gender})")

    stage_recs = {
        "general": ["维生素D3", "Omega-3", "镁"],
        "preconception": ["甲基叶酸", "维生素D3", "Omega-3", "铁剂"],
        "fat_loss": ["维生素D3", "镁", "铬", "姜黄素"],   # 已移除 green_tea_extract
        "muscle_gain": ["肌酸", "BCAA", "镁", "维生素D3"],
        "jetlag_travel": ["L-苏糖酸镁", "维生素B族", "姜黄素"],
        "recovery": ["维生素C", "锌", "Omega-3", "胶原蛋白"]
    }
    
    recommended = stage_recs.get(stage, stage_recs["general"])
    
    severity, conflicts, suggestions = check_supplement_conflicts(recommended, stage)
    
    return {
        "stage": stage,
        "recommended": recommended,
        "severity": str(severity),
        "conflicts_count": len(conflicts),
        "conflicts": conflicts[:3],
        "suggestions": suggestions or ["方案安全，可放心使用"]
    }


class SupplementRecommender:
    @staticmethod
    def recommend(stage: str = "general", age: int = 30, gender: str = "female", **kwargs):
        return recommend_supplements_basic(stage, age, gender, **kwargs)

if __name__ == "__main__":
    result = recommend_supplements_basic("fat_loss", age=25, gender="female")
    print(result)
