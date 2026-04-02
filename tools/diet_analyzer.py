"""
饮食分析模块

支持根据健康阶段分析饮食需求，提供个性化建议
包含常见中国菜的热量和营养成分数据
"""

from typing import List, Dict, Optional
from enum import Enum


class MealCategory(str, Enum):
    """餐食类别"""
    BREAKFAST = "早餐"
    LUNCH = "午餐"
    DINNER = "晚餐"
    SNACK = "加餐"


class ChineseFoodDatabase:
    """中国菜食物数据库"""

    # 常见中国菜营养数据（每100g）
    FOODS = {
        # 蛋白质来源
        "清蒸鲈鱼": {
            "calories": 115,
            "protein": 20,
            "fat": 3,
            "carbs": 0,
            "fiber": 0,
            "categories": ["lunch", "dinner"],
            "good_for": ["muscle_gain", "preconception", "recovery"]
        },
        "红烧牛肉": {
            "calories": 280,
            "protein": 22,
            "fat": 18,
            "carbs": 6,
            "fiber": 0,
            "categories": ["lunch", "dinner"],
            "good_for": ["muscle_gain"]
        },
        "白切鸡": {
            "calories": 170,
            "protein": 25,
            "fat": 7,
            "carbs": 0,
            "fiber": 0,
            "categories": ["lunch", "dinner"],
            "good_for": ["muscle_gain", "recovery"]
        },
        "清炒虾仁": {
            "calories": 130,
            "protein": 24,
            "fat": 2,
            "carbs": 2,
            "fiber": 0,
            "categories": ["lunch", "dinner"],
            "good_for": ["fat_loss", "recovery"]
        },
        
        # 蔬菜类
        "清炒西兰花": {
            "calories": 35,
            "protein": 3,
            "fat": 0.5,
            "carbs": 7,
            "fiber": 2.6,
            "categories": ["lunch", "dinner"],
            "good_for": ["general", "fat_loss", "preconception"]
        },
        "凉拌菠菜": {
            "calories": 23,
            "protein": 3,
            "fat": 0.4,
            "carbs": 4,
            "fiber": 2.2,
            "categories": ["lunch", "dinner"],
            "good_for": ["general", "fat_loss", "preconception"]
        },
        "清炒芦笋": {
            "calories": 20,
            "protein": 2,
            "fat": 0.1,
            "carbs": 4,
            "fiber": 2,
            "categories": ["lunch", "dinner"],
            "good_for": ["general", "fat_loss", "preconception"]
        },
        "蒜蓉空心菜": {
            "calories": 28,
            "protein": 2,
            "fat": 0.3,
            "carbs": 5,
            "fiber": 2.5,
            "categories": ["lunch", "dinner"],
            "good_for": ["general", "fat_loss"]
        },
        
        # 主食类
        "白米饭": {
            "calories": 130,
            "protein": 2.7,
            "fat": 0.3,
            "carbs": 28,
            "fiber": 0.4,
            "categories": ["lunch", "dinner"],
            "good_for": ["general", "muscle_gain", "recovery"]
        },
        "杂粮饭": {
            "calories": 125,
            "protein": 3.5,
            "fat": 0.5,
            "carbs": 26,
            "fiber": 3,
            "categories": ["lunch", "dinner"],
            "good_for": ["general", "fat_loss", "preconception"]
        },
        "小米粥": {
            "calories": 46,
            "protein": 1.2,
            "fat": 0.7,
            "carbs": 9,
            "fiber": 0.8,
            "categories": ["breakfast"],
            "good_for": ["general", "recovery", "jetlag_travel"]
        },
        
        # 汤类
        "紫菜蛋花汤": {
            "calories": 50,
            "protein": 4,
            "fat": 2,
            "carbs": 3,
            "fiber": 0.5,
            "categories": ["lunch", "dinner"],
            "good_for": ["general", "recovery", "jetlag_travel"]
        },
        "冬瓜排骨汤": {
            "calories": 80,
            "protein": 8,
            "fat": 5,
            "carbs": 3,
            "fiber": 0.5,
            "categories": ["lunch", "dinner"],
            "good_for": ["general", "recovery"]
        },
        
        # 减脂友好
        "水煮鸡胸肉": {
            "calories": 165,
            "protein": 31,
            "fat": 3.6,
            "carbs": 0,
            "fiber": 0,
            "categories": ["lunch", "dinner"],
            "good_for": ["fat_loss", "muscle_gain"]
        },
        "清蒸鳕鱼": {
            "calories": 82,
            "protein": 18,
            "fat": 0.7,
            "carbs": 0,
            "fiber": 0,
            "categories": ["lunch", "dinner"],
            "good_for": ["fat_loss", "preconception"]
        },
        
        # 早餐
        "豆浆": {
            "calories": 31,
            "protein": 3,
            "fat": 1.6,
            "carbs": 1.5,
            "fiber": 0,
            "categories": ["breakfast"],
            "good_for": ["general", "preconception", "recovery"]
        },
        "煮鸡蛋": {
            "calories": 143,
            "protein": 12.6,
            "fat": 9.5,
            "carbs": 0.7,
            "fiber": 0,
            "categories": ["breakfast", "snack"],
            "good_for": ["general", "muscle_gain", "preconception"]
        },
        "全麦面包": {
            "calories": 250,
            "protein": 13,
            "fat": 3.2,
            "carbs": 41,
            "fiber": 6,
            "categories": ["breakfast"],
            "good_for": ["general", "muscle_gain", "recovery"]
        },
    }

    @classmethod
    def get_food_info(cls, food_name: str) -> Optional[Dict]:
        """获取食物营养信息"""
        return cls.FOODS.get(food_name)

    @classmethod
    def search_foods(
        cls,
        stage: Optional[str] = None,
        category: Optional[str] = None,
        max_calories: Optional[int] = None
    ) -> List[Dict]:
        """搜索食物"""
        results = []
        
        for name, info in cls.FOODS.items():
            # 阶段筛选
            if stage and stage not in info.get("good_for", []):
                continue
            
            # 类别筛选
            if category and category not in info.get("categories", []):
                continue
            
            # 热量筛选
            if max_calories and info["calories"] > max_calories:
                continue
            
            results.append({
                "name": name,
                **info
            })
        
        return results


class DietAnalyzer:
    """饮食分析器"""

    # 各阶段营养目标
    STAGE_TARGETS = {
        "general": {
            "protein_ratio": 0.2,
            "carbs_ratio": 0.5,
            "fat_ratio": 0.3,
            "daily_calories": 2000
        },
        "preconception": {
            "protein_ratio": 0.2,
            "carbs_ratio": 0.5,
            "fat_ratio": 0.3,
            "daily_calories": 2200
        },
        "fat_loss": {
            "protein_ratio": 0.35,
            "carbs_ratio": 0.35,
            "fat_ratio": 0.3,
            "daily_calories": 1600
        },
        "muscle_gain": {
            "protein_ratio": 0.3,
            "carbs_ratio": 0.5,
            "fat_ratio": 0.2,
            "daily_calories": 2800
        },
        "jetlag_travel": {
            "protein_ratio": 0.2,
            "carbs_ratio": 0.55,
            "fat_ratio": 0.25,
            "daily_calories": 2000
        },
        "recovery": {
            "protein_ratio": 0.25,
            "carbs_ratio": 0.45,
            "fat_ratio": 0.3,
            "daily_calories": 2200
        },
    }

    # 各阶段饮食原则
    STAGE_PRINCIPLES = {
        "general": [
            "保持食物多样性，每天摄入至少5种不同颜色的蔬菜",
            "优质蛋白质每餐必备（鱼、禽、蛋、豆类）",
            "控制精制糖和加工食品的摄入",
            "保证充足饮水（每日1.5-2L）"
        ],
        "preconception": [
            "增加富含叶酸的食物：深绿色蔬菜、豆类、坚果",
            "确保铁摄入：红肉、菠菜、红枣",
            "摄入足够的Omega-3：深海鱼类、亚麻籽",
            "避免生食和含酒精的食品",
            "补充碘：海带、紫菜、碘盐"
        ],
        "fat_loss": [
            "控制总热量，制造合理的热量缺口（约500kcal/天）",
            "高蛋白饮食维持饱腹感和肌肉量",
            "选择低GI碳水化合物：糙米、燕麦、红薯",
            "健康脂肪来源：牛油果、橄榄油、坚果",
            "避免高热量酱料和油炸食品"
        ],
        "muscle_gain": [
            "蛋白质摄入：每公斤体重1.6-2.2g",
            "训练后30分钟内补充蛋白质和碳水",
            "保证足够总热量支持肌肉合成",
            "优质碳水：米饭、红薯、香蕉",
            "健康脂肪：坚果、橄榄油、牛油果"
        ],
        "jetlag_travel": [
            "旅行前后保持规律的饮食时间",
            "避免过量的咖啡因和酒精",
            "补充水分，预防脱水",
            "选择易消化的食物",
            "时差调整前3天逐步调整饮食时间"
        ],
        "recovery": [
            "增加抗氧化食物：浆果、深色蔬菜",
            "确保足量蛋白质支持组织修复",
            "补充维生素C和锌支持免疫功能",
            "保持充足水分促进代谢",
            "避免过量糖分和油炸食品"
        ]
    }

    def __init__(self):
        """初始化饮食分析器"""
        self.food_db = ChineseFoodDatabase()

    def analyze_diet(self, description: str, stage: str = "general") -> Dict:
        """
        分析饮食描述
        
        参数:
            description: 饮食描述（如"日常"、"减脂"）
            stage: 健康阶段
            
        返回:
            分析结果字典
        """
        # 获取阶段目标
        targets = self.STAGE_TARGETS.get(stage, self.STAGE_TARGETS["general"])
        principles = self.STAGE_PRINCIPLES.get(stage, [])
        
        # 推荐食物
        recommended_foods = self.food_db.search_foods(stage=stage)
        
        # 按类别分组
        breakfast_foods = [f for f in recommended_foods if "breakfast" in f["categories"]]
        lunch_foods = [f for f in recommended_foods if "lunch" in f["categories"]]
        dinner_foods = [f for f in recommended_foods if "dinner" in f["categories"]]
        
        return {
            "stage": stage,
            "targets": targets,
            "principles": principles,
            "meal_recommendations": {
                "breakfast": breakfast_foods[:3],
                "lunch": lunch_foods[:5],
                "dinner": dinner_foods[:5]
            },
            "daily_calories": targets["daily_calories"],
            "protein_target": targets["daily_calories"] * targets["protein_ratio"] / 4,
            "carbs_target": targets["daily_calories"] * targets["carbs_ratio"] / 4,
            "fat_target": targets["daily_calories"] * targets["fat_ratio"] / 9
        }

    def get_food_suggestions(
        self,
        stage: str,
        meal: str = "lunch",
        count: int = 3
    ) -> List[str]:
        """
        获取餐食推荐
        
        参数:
            stage: 健康阶段
            meal: 餐食类别（breakfast, lunch, dinner）
            count: 推荐数量
            
        返回:
            推荐食物名称列表
        """
        foods = self.food_db.search_foods(stage=stage, category=meal)
        return [f["name"] for f in foods[:count]]

    def calculate_meal_calories(self, foods: List[str], portions: List[float] = None) -> Dict:
        """
        计算餐食热量和营养素
        
        参数:
            foods: 食物名称列表
            portions: 份数列表（默认每份100g）
            
        返回:
            营养信息字典
        """
        if portions is None:
            portions = [1.0] * len(foods)
        
        total_calories = 0
        total_protein = 0
        total_fat = 0
        total_carbs = 0
        total_fiber = 0
        
        for food_name, portion in zip(foods, portions):
            info = self.food_db.get_food_info(food_name)
            if info:
                factor = portion
                total_calories += info["calories"] * factor
                total_protein += info["protein"] * factor
                total_fat += info["fat"] * factor
                total_carbs += info["carbs"] * factor
                total_fiber += info["fiber"] * factor
        
        return {
            "calories": total_calories,
            "protein": total_protein,
            "fat": total_fat,
            "carbs": total_carbs,
            "fiber": total_fiber,
            "protein_ratio": total_protein * 4 / total_calories if total_calories > 0 else 0,
            "carbs_ratio": total_carbs * 4 / total_calories if total_calories > 0 else 0,
            "fat_ratio": total_fat * 9 / total_calories if total_calories > 0 else 0
        }


# 便捷函数
def analyze_diet(description: str, stage: str = "general") -> List[str]:
    """
    快速分析饮食
    
    参数:
        description: 饮食描述
        stage: 健康阶段
        
    返回:
        饮食建议列表
    """
    analyzer = DietAnalyzer()
    result = analyzer.analyze_diet(description, stage)
    
    suggestions = []
    
    # 添加阶段原则
    suggestions.append(f"【{stage.upper()}阶段饮食原则】")
    for principle in result["principles"]:
        suggestions.append(f"• {principle}")
    
    suggestions.append("")
    suggestions.append("【推荐餐食】")
    
    # 早餐推荐
    if result["meal_recommendations"]["breakfast"]:
        suggestions.append("早餐推荐:")
        for food in result["meal_recommendations"]["breakfast"][:2]:
            suggestions.append(f"  - {food['name']} ({food['calories']}kcal)")
    
    # 午餐推荐
    if result["meal_recommendations"]["lunch"]:
        suggestions.append("\n午餐推荐:")
        for food in result["meal_recommendations"]["lunch"][:3]:
            suggestions.append(f"  - {food['name']} ({food['calories']}kcal)")
    
    # 晚餐推荐
    if result["meal_recommendations"]["dinner"]:
        suggestions.append("\n晚餐推荐:")
        for food in result["meal_recommendations"]["dinner"][:3]:
            suggestions.append(f"  - {food['name']} ({food['calories']}kcal)")
    
    suggestions.append("")
    suggestions.append(f"【营养目标】")
    suggestions.append(f"每日热量: {result['daily_calories']}kcal")
    suggestions.append(f"蛋白质: {result['protein_target']:.0f}g")
    suggestions.append(f"碳水化合物: {result['carbs_target']:.0f}g")
    suggestions.append(f"脂肪: {result['fat_target']:.0f}g")
    
    return suggestions


if __name__ == "__main__":
    # 测试示例
    print("=== 饮食分析模块测试 ===\n")
    
    print("【测试1】备孕阶段饮食分析")
    suggestions = analyze_diet("备孕", "preconception")
    for s in suggestions[:10]:
        print(s)
    
    print("\n" + "=" * 60 + "\n")
    
    print("【测试2】减脂阶段饮食分析")
    suggestions = analyze_diet("减脂", "fat_loss")
    for s in suggestions[:10]:
        print(s)
    
    print("\n" + "=" * 60 + "\n")
    
    print("【测试3】增肌阶段餐食推荐")
    analyzer = DietAnalyzer()
    lunch_foods = analyzer.get_food_suggestions("muscle_gain", "lunch", 5)
    print(f"增肌阶段午餐推荐:")
    for food in lunch_foods:
        info = ChineseFoodDatabase.get_food_info(food)
        print(f"  - {food}: {info['calories']}kcal, 蛋白质{info['protein']}g")
