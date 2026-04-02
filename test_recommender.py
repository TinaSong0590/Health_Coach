#!/usr/bin/env python3
"""
Health Coach 补充剂推荐引擎 一键测试脚本
"""

import sys
sys.path.insert(0, "/home/knan/health_coach")

from tools.supplement_recommender import recommend_supplements_basic

if __name__ == "__main__":
    print("=== Health Coach 推荐引擎测试 ===\n")
    
    stages = ["general", "preconception", "fat_loss", "jetlag_travel"]
    
    for stage in stages:
        print(f"\n{'='*60}")
        print(f"测试阶段: {stage}")
        print(f"{'='*60}")
        result = recommend_supplements_basic(stage)
        print("-" * 40)
