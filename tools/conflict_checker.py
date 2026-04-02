import json
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from enum import Enum

# 确保能正确导入项目模块
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class ConflictSeverity(str, Enum):
    """冲突严重程度"""
    SAFE = "🟢 安全"
    OPTIMIZATION_NEEDED = "🟡 需要优化"
    CRITICAL = "🔴 严重冲突"


class ConflictChecker:
    """补充剂冲突检测引擎"""
    
    def __init__(self, data_dir: str = "data"):
        """初始化冲突检测器"""
        self.data_dir = Path(data_dir)
        self.supplements_data = self._load_supplements()
        self.interactions_data = self._load_interactions()
    
    def _load_supplements(self) -> Dict:
        """加载补充剂数据"""
        path = self.data_dir / "supplements.json"
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # 创建ID到补充剂的映射
        return {s['id']: s for s in data['supplements']}
    
    def _load_interactions(self) -> Dict:
        """加载冲突规则数据"""
        path = self.data_dir / "interactions.json"
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _normalize_supplement_name(self, name: str) -> Optional[str]:
        """标准化补充剂名称，返回对应的ID"""
        name_lower = name.lower().strip()
        
        # 直接ID匹配
        if name_lower in self.supplements_data:
            return name_lower
        
        # 名称匹配（中英文）
        for sup_id, sup_info in self.supplements_data.items():
            if (name_lower in sup_info['name'].lower() or 
                sup_info['name'].lower() in name_lower):
                return sup_id
        
        return None
    
    def check_supplement_conflicts(
        self, 
        supplements: List[str], 
        stage: str,
        check_details: bool = True
    ) -> Tuple[ConflictSeverity, List[Dict], List[str]]:
        """
        检查补充剂冲突
        
        参数:
            supplements: 补充剂名称列表
            stage: 当前健康阶段
            check_details: 是否返回详细冲突信息
            
        返回:
            Tuple[严重程度, 冲突详情列表, 优化建议列表]
        """
        normalized = []
        conflicts = []
        suggestions = []
        
        # 标准化名称
        for name in supplements:
            sup_id = self._normalize_supplement_name(name)
            if sup_id:
                normalized.append(sup_id)
            else:
                # 未知补充剂，添加警告
                conflicts.append({
                    "type": "unknown_supplement",
                    "supplement": name,
                    "severity": "warning",
                    "reason": f"未知的补充剂: {name}",
                    "recommendation": "请确认补充剂名称或咨询专业人士"
                })
        
        if not normalized:
            return ConflictSeverity.SAFE, conflicts, ["未识别任何已知补充剂"]
        
        # 1. 检查阶段禁忌
        stage_conflicts = self._check_stage_contraindications(normalized, stage)
        conflicts.extend(stage_conflicts)
        
        # 2. 检查硬冲突
        hard_conflicts = self._check_hard_conflicts(normalized)
        conflicts.extend(hard_conflicts)
        
        # 3. 检查软冲突
        soft_conflicts = self._check_soft_conflicts(normalized)
        conflicts.extend(soft_conflicts)
        
        # 4. 生成优化建议
        suggestions = self._generate_suggestions(normalized, stage, conflicts)
        
        # 5. 检查阶段推荐补充剂是否缺失
        missing = self._check_missing_required(normalized, stage)
        if missing:
            suggestions.append({
                "type": "missing_recommended",
                "supplements": missing,
                "message": f"当前阶段建议补充: {', '.join(missing)}"
            })
        
        # 6. 评估整体安全性
        severity = self._assess_overall_severity(conflicts)
        
        return severity, conflicts, suggestions
    
    def _check_stage_contraindications(
        self, 
        supplement_ids: List[str], 
        stage: str
    ) -> List[Dict]:
        """检查阶段禁忌"""
        conflicts = []
        
        for rule_section in self.interactions_data["conflict_rules"]:
            if rule_section["type"] == "stage_contraindication":
                for rule in rule_section["rules"]:
                    if rule["stage"] == stage:
                        # 检查禁用的补充剂
                        if "supplements" in rule:
                            forbidden = rule["supplements"]
                            for sup_id in supplement_ids:
                                if sup_id in forbidden:
                                    sup_name = self.supplements_data[sup_id]["name"]
                                    conflicts.append({
                                        "type": "stage_contraindication",
                                        "supplement": sup_name,
                                        "stage": stage,
                                        "severity": "critical",
                                        "reason": f"{stage}阶段不推荐使用{sup_name}",
                                        "recommendation": rule["recommendation"]
                                    })
        
        return conflicts
    
    def _check_hard_conflicts(self, supplement_ids: List[str]) -> List[Dict]:
        """检查硬冲突"""
        conflicts = []
        
        for rule_section in self.interactions_data["conflict_rules"]:
            if rule_section["type"] == "hard_conflict":
                for rule in rule_section["rules"]:
                    conflict_sups = rule["supplements"]
                    # 检查是否有冲突组合
                    matched = [s for s in conflict_sups if s in supplement_ids]
                    
                    if len(matched) >= 2:
                        sup_names = [
                            self.supplements_data[s]["name"] 
                            for s in matched
                        ]
                        conflicts.append({
                            "type": "hard_conflict",
                            "supplements": sup_names,
                            "severity": "critical",
                            "reason": rule["reason"],
                            "recommendation": rule["recommendation"]
                        })
        
        return conflicts
    
    def _check_soft_conflicts(self, supplement_ids: List[str]) -> List[Dict]:
        """检查软冲突"""
        conflicts = []
        
        for rule_section in self.interactions_data["conflict_rules"]:
            if rule_section["type"] == "soft_conflict":
                for rule in rule_section["rules"]:
                    conflict_sups = rule["supplements"]
                    matched = [s for s in conflict_sups if s in supplement_ids]
                    
                    if len(matched) >= 2:
                        sup_names = [
                            self.supplements_data[s]["name"] 
                            for s in matched
                        ]
                        conflicts.append({
                            "type": "soft_conflict",
                            "supplements": sup_names,
                            "severity": "moderate",
                            "reason": rule["reason"],
                            "recommendation": rule["recommendation"]
                        })
        
        return conflicts
    
    def _check_missing_required(
        self, 
        supplement_ids: List[str], 
        stage: str
    ) -> List[str]:
        """检查缺失的阶段推荐补充剂"""
        missing = []
        
        for rule_section in self.interactions_data["conflict_rules"]:
            if rule_section["type"] == "stage_contraindication":
                for rule in rule_section["rules"]:
                    if rule["stage"] == stage and "recommended" in rule:
                        required = rule["recommended"]
                        for sup_id in required:
                            if sup_id not in supplement_ids:
                                missing.append(self.supplements_data[sup_id]["name"])
        
        return missing
    
    def _generate_suggestions(
        self, 
        supplement_ids: List[str], 
        stage: str,
        conflicts: List[Dict]
    ) -> List[Dict]:
        """生成优化建议"""
        suggestions = []
        
        # 从冲突中提取建议
        for conflict in conflicts:
            if "recommendation" in conflict:
                suggestions.append({
                    "type": "conflict_resolution",
                    "message": conflict["recommendation"]
                })
        
        # 检查协同效应
        synergies = self._find_synergies(supplement_ids)
        for synergy in synergies:
            suggestions.append({
                "type": "synergy",
                "message": f"💡 提示: {synergy}"
            })
        
        return suggestions
    
    def _find_synergies(self, supplement_ids: List[str]) -> List[str]:
        """寻找协同效应"""
        synergies = []
        
        # D3 + K2
        if "vitamin_d3" in supplement_ids and "vitamin_k2" not in supplement_ids:
            synergies.append("维生素D3配合维生素K2使用可优化钙代谢")
        
        # 铁缺乏维生素C
        if "iron" in supplement_ids and "vitamin_c" not in supplement_ids:
            synergies.append("铁剂配合维生素C可提高吸收率")
        
        # Omega-3缺乏维生素E
        if "omega3" in supplement_ids and "vitamin_e" not in supplement_ids:
            synergies.append("Omega-3配合维生素E可减少氧化")
        
        return synergies
    
    def _assess_overall_severity(self, conflicts: List[Dict]) -> ConflictSeverity:
        """评估整体严重程度"""
        if not conflicts:
            return ConflictSeverity.SAFE
        
        # 检查是否有critical冲突
        critical_count = sum(
            1 for c in conflicts 
            if c.get("severity") == "critical"
        )
        
        if critical_count > 0:
            return ConflictSeverity.CRITICAL
        
        # 检查是否有moderate冲突
        moderate_count = sum(
            1 for c in conflicts 
            if c.get("severity") == "moderate"
        )
        
        if moderate_count > 0:
            return ConflictSeverity.OPTIMIZATION_NEEDED
        
        return ConflictSeverity.SAFE
    
    def get_supplement_info(self, supplement_name: str) -> Optional[Dict]:
        """获取补充剂详细信息"""
        sup_id = self._normalize_supplement_name(supplement_name)
        if sup_id:
            return self.supplements_data[sup_id]
        return None
    
    def get_stage_recommended(self, stage: str) -> List[str]:
        """获取特定阶段的推荐补充剂"""
        recommended = []
        
        for rule_section in self.interactions_data["conflict_rules"]:
            if rule_section["type"] == "stage_contraindication":
                for rule in rule_section["rules"]:
                    if rule["stage"] == stage and "recommended" in rule:
                        for sup_id in rule["recommended"]:
                            recommended.append(self.supplements_data[sup_id]["name"])
        
        return recommended


# 便捷函数
def check_supplement_conflicts(
    supplements: List[str], 
    stage: str
) -> Tuple[ConflictSeverity, List[Dict], List[str]]:
    """
    快速冲突检查函数
    
    参数:
        supplements: 补充剂名称列表
        stage: 当前健康阶段
        
    返回:
        Tuple[严重程度, 冲突详情列表, 建议列表]
    """
    checker = ConflictChecker()
    severity, conflicts, suggestions = checker.check_supplement_conflicts(
        supplements, stage
    )
    
    # 格式化建议列表
    formatted_suggestions = []
    for suggestion in suggestions:
        if isinstance(suggestion, dict):
            formatted_suggestions.append(suggestion["message"])
        else:
            formatted_suggestions.append(str(suggestion))
    
    return severity, conflicts, formatted_suggestions
