from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Literal
from enum import Enum
from datetime import date


class Stage(str, Enum):
    """健康阶段枚举"""
    GENERAL = "general"
    PRECONCEPTION = "preconception"
    FAT_LOSS = "fat_loss"
    MUSCLE_GAIN = "muscle_gain"
    JETLAG_TRAVEL = "jetlag_travel"
    RECOVERY = "recovery"


class Gender(str, Enum):
    """性别枚举"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class Lifestyle(BaseModel):
    """生活习惯模型"""
    sleep_hours: float = Field(..., ge=0, le=24, description="每日睡眠时长（小时）")
    exercise_frequency: str = Field(..., description="运动频率（如：每周3次）")
    stress_level: int = Field(..., ge=1, le=10, description="压力水平（1-10）")
    diet_type: str = Field(..., description="饮食类型（如：均衡饮食、素食、生酮等）")
    water_intake_ml: Optional[int] = Field(None, ge=0, description="每日饮水量（毫升）")
    smoking: bool = Field(default=False, description="是否吸烟")
    alcohol: bool = Field(default=False, description="是否饮酒")


class CurrentSupplement(BaseModel):
    """当前补充剂记录"""
    name: str = Field(..., description="补充剂名称")
    dosage: str = Field(..., description="剂量")
    frequency: str = Field(..., description="服用频率")
    start_date: Optional[date] = Field(None, description="开始服用日期")


class GeneticReport(BaseModel):
    """基因报告信息"""
    file_path: Optional[str] = Field(None, description="基因报告文件路径")
    provider: Optional[str] = Field(None, description="检测服务商")
    report_date: Optional[date] = Field(None, description="报告日期")
    key_variants: Optional[List[str]] = Field(None, description="关键基因变异列表")


class UserProfile(BaseModel):
    """用户画像模型"""
    
    # 基本信息
    name: str = Field(..., min_length=1, description="用户姓名")
    age: int = Field(..., ge=0, le=120, description="年龄")
    gender: Gender = Field(..., description="性别")
    
    # 健康目标与阶段
    primary_goal: str = Field(..., description="主要健康目标")
    stage: Stage = Field(..., description="当前健康阶段")
    secondary_goals: Optional[List[str]] = Field(None, description="次要目标列表")
    
    # 基因报告
    genetic_report: Optional[GeneticReport] = Field(None, description="基因报告信息")
    
    # 生活习惯
    lifestyle: Lifestyle = Field(..., description="生活习惯")
    
    # 当前补充剂
    current_supplements: Optional[List[CurrentSupplement]] = Field(
        default_factory=list,
        description="当前正在服用的补充剂列表"
    )
    
    # 其他信息
    allergies: Optional[List[str]] = Field(None, description="过敏信息")
    medical_conditions: Optional[List[str]] = Field(None, description="医疗状况")
    medications: Optional[List[str]] = Field(None, description="正在服用的处方药")
    notes: Optional[str] = Field(None, description="额外备注")
    
    @field_validator('stage')
    @classmethod
    def validate_stage(cls, v):
        """验证阶段字段的合法性"""
        if v not in Stage:
            raise ValueError(f"无效的阶段: {v}. 必须是以下之一: {[s.value for s in Stage]}")
        return v
    
    @field_validator('age')
    @classmethod
    def validate_age_for_stage(cls, v, info):
        """根据阶段验证年龄的合理性"""
        if info and 'stage' in info.data:
            stage = info.data['stage']
            if stage == Stage.PRECONCEPTION and v < 18:
                raise ValueError("备孕阶段要求年龄至少18岁")
        return v
    
    def get_supplement_names(self) -> List[str]:
        """获取当前补充剂名称列表"""
        return [s.name for s in (self.current_supplements or [])]
    
    def is_stage_sensitive(self) -> bool:
        """检查当前阶段是否敏感（需要特别注意补充剂）"""
        sensitive_stages = [Stage.PRECONCEPTION, Stage.PREGNANCY, Stage.RECOVERY]
        return self.stage in sensitive_stages


# 预留：未来扩展的 Pregnant 阶段（从 PRECONCEPTION 演变）
class UserProfileWithPregnancy(UserProfile):
    """扩展的用户画像（包含怀孕相关字段）"""
    is_pregnant: Optional[bool] = Field(None, description="是否怀孕")
    pregnancy_week: Optional[int] = Field(None, ge=0, le=42, description="孕周")
    is_breastfeeding: Optional[bool] = Field(None, description="是否哺乳")
