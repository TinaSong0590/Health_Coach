"""
基因报告解析工具

支持解析 PDF 基因报告，提取关键 SNP 变异信息。
兼容常见的基因检测报告格式。
"""

import re
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
from enum import Enum


class SNPVariant(str, Enum):
    """常见 SNP 变异"""
    MTHFR_C677T = "MTHFR C677T (rs1801133)"
    MTHFR_A1298C = "MTHFR A1298C (rs1801131)"
    VDR_FokI = "VDR FokI (rs2228570)"
    VDR_TaqI = "VDR TaqI (rs731236)"
    FADS1_rs174546 = "FADS1 rs174546"
    FADS2_rs174537 = "FADS2 rs174537"
    HFE_C282Y = "HFE C282Y (rs1800562)"
    HFE_H63D = "HFE H63D (rs1799945)"
    COMT_Val158Met = "COMT Val158Met (rs4680)"
    BDNF_Val66Met = "BDNF Val66Met (rs6265)"
    IL6_rs1800795 = "IL-6 rs1800795"
    FTO_rs9939609 = "FTO rs9939609"
    APOE_E4 = "APOE ε4 (rs429358/rs7412)"


class GenotypeResult:
    """基因型结果"""
    def __init__(self, gene: str, variant: str, genotype: str, impact: str = "unknown"):
        self.gene = gene
        self.variant = variant
        self.genotype = genotype
        self.impact = impact  # high, moderate, low, unknown

    def to_dict(self) -> Dict:
        return {
            "gene": self.gene,
            "variant": self.variant,
            "genotype": self.genotype,
            "impact": self.impact
        }

    def __repr__(self):
        return f"{self.gene} {self.variant}: {self.genotype} ({self.impact})"


class GeneReportParser:
    """基因报告解析器"""

    # 常见 SNP 模式匹配规则
    SNP_PATTERNS = {
        "MTHFR": [
            r"MTHFR\s*C677T\s*\(rs1801133\)",
            r"MTHFR.*?C677T",
            r"rs1801133",
        ],
        "VDR": [
            r"VDR\s*FokI\s*\(rs2228570\)",
            r"VDR.*?FokI",
            r"rs2228570",
            r"VDR\s*TaqI\s*\(rs731236\)",
            r"VDR.*?TaqI",
            r"rs731236",
        ],
        "FADS1": [
            r"FADS1.*?rs174546",
            r"rs174546",
        ],
        "FADS2": [
            r"FADS2.*?rs174537",
            r"rs174537",
        ],
        "HFE": [
            r"HFE\s*C282Y\s*\(rs1800562\)",
            r"HFE.*?C282Y",
            r"rs1800562",
            r"HFE\s*H63D\s*\(rs1799945\)",
            r"HFE.*?H63D",
            r"rs1799945",
        ],
        "COMT": [
            r"COMT\s*Val158Met\s*\(rs4680\)",
            r"COMT.*?Val158Met",
            r"rs4680",
        ],
        "BDNF": [
            r"BDNF\s*Val66Met\s*\(rs6265\)",
            r"BDNF.*?Val66Met",
            r"rs6265",
        ],
        "IL6": [
            r"IL-?6.*?rs1800795",
            r"rs1800795",
        ],
        "FTO": [
            r"FTO.*?rs9939609",
            r"rs9939609",
        ],
        "APOE": [
            r"APOE.*?ε4",
            r"APOE.*?rs429358",
            r"APOE.*?rs7412",
        ],
    }

    # 基因型影响评估
    GENOTYPE_IMPACTS = {
        "MTHFR": {
            "CC": "low",
            "CT": "moderate",
            "TT": "high",
        },
        "VDR": {
            "FF": "low",
            "Ff": "moderate",
            "ff": "high",
            "TT": "low",
            "Tt": "moderate",
            "tt": "high",
        },
        "HFE": {
            "CC": "low",
            "CY": "moderate",
            "YY": "high",
        },
        "COMT": {
            "Val/Val": "low",
            "Val/Met": "moderate",
            "Met/Met": "high",
        },
    }

    def __init__(self):
        """初始化解析器"""
        self.results: List[GenotypeResult] = []
        self.raw_text: str = ""

    def parse_from_text(self, text: str) -> Dict[str, Any]:
        """
        从文本内容解析基因报告

        参数:
            text: 基因报告文本内容

        返回:
            解析结果字典
        """
        self.raw_text = text
        self.results = []

        # 提取各个 SNP 信息
        for gene, patterns in self.SNP_PATTERNS.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    genotype = self._extract_genotype_near_match(text, match)
                    if genotype:
                        impact = self._assess_impact(gene, genotype)
                        result = GenotypeResult(
                            gene=gene,
                            variant=match.group(),
                            genotype=genotype,
                            impact=impact
                        )
                        self.results.append(result)

        # 去重
        unique_results = {}
        for r in self.results:
            key = f"{r.gene}_{r.variant}"
            if key not in unique_results:
                unique_results[key] = r

        return {
            "total_snps_found": len(unique_results),
            "results": [r.to_dict() for r in unique_results.values()],
            "summary": self._generate_summary(unique_results.values()),
            "recommendations": self._generate_recommendations(unique_results.values())
        }

    def parse_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        从文件解析基因报告

        参数:
            file_path: 基因报告文件路径（支持 .txt 和部分 PDF）

        返回:
            解析结果字典
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        # 根据文件类型处理
        if path.suffix.lower() == ".pdf":
            return self._parse_pdf(file_path)
        elif path.suffix.lower() == ".txt":
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return self.parse_from_text(f.read())
        elif path.suffix.lower() == ".json":
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 假设 JSON 格式包含原始文本或结构化数据
                if "raw_text" in data:
                    return self.parse_from_text(data["raw_text"])
                else:
                    return self._parse_structured_json(data)
        else:
            raise ValueError(f"不支持的文件格式: {path.suffix}")

    def _parse_pdf(self, file_path: str) -> Dict[str, Any]:
        """
        解析 PDF 文件

        注意: 需要安装 PyPDF2 或 pdfplumber
        """
        try:
            import PyPDF2
            text = ""
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return self.parse_from_text(text)
        except ImportError:
            try:
                import pdfplumber
                text = ""
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        text += page.extract_text() + "\n"
                return self.parse_from_text(text)
            except ImportError:
                raise ImportError(
                    "PDF 解析需要 PyPDF2 或 pdfplumber 库。"
                    "请安装: pip install PyPDF2 或 pip install pdfplumber"
                )

    def _parse_structured_json(self, data: Dict) -> Dict[str, Any]:
        """解析结构化 JSON 格式"""
        # 这里假设 JSON 包含基因型字段
        results = []
        for item in data.get("genotypes", []):
            gene = item.get("gene")
            variant = item.get("variant", "")
            genotype = item.get("genotype")
            if gene and genotype:
                impact = self._assess_impact(gene, genotype)
                results.append({
                    "gene": gene,
                    "variant": variant,
                    "genotype": genotype,
                    "impact": impact
                })

        return {
            "total_snps_found": len(results),
            "results": results,
            "summary": "从结构化数据提取",
            "recommendations": self._generate_recommendations(
                [GenotypeResult(**r) for r in results]
            )
        }

    def _extract_genotype_near_match(self, text: str, match: re.Match) -> Optional[str]:
        """
        在匹配位置附近提取基因型

        基因型通常是两个字母的组合，如: CC, CT, TT, Val/Val, Met/Met
        """
        start_pos = max(0, match.start() - 50)
        end_pos = min(len(text), match.end() + 100)
        context = text[start_pos:end_pos]

        # 常见基因型模式
        genotype_patterns = [
            r"\b([ACGT]{2})\b",  # DNA: CC, CT, TT
            r"\b(Val|Met|Phe|Trp|Leu)/([Val|Met|Phe|Trp|Leu])\b",  # 氨基酸
            r"\b([A-Z][a-z]{2})/([A-Z][a-z]{2})\b",  # Val/Val
            r"基因型[:\s]*([A-Za-z/\-]+)",
            r"Genotype[:\s]*([A-Za-z/\-]+)",
        ]

        for pattern in genotype_patterns:
            matches = re.findall(pattern, context)
            if matches:
                if isinstance(matches[0], tuple):
                    return "/".join(matches[0])
                return str(matches[0])

        return None

    def _assess_impact(self, gene: str, genotype: str) -> str:
        """评估基因型影响"""
        # 规范化基因型格式
        norm_genotype = genotype.replace("/", "").replace("-", "")

        # 清理常见表示
        if "ValVal" in genotype or "Val/Val" in genotype:
            norm_genotype = "Val/Val"
        elif "ValMet" in genotype or "Val/Met" in genotype:
            norm_genotype = "Val/Met"
        elif "MetMet" in genotype or "Met/Met" in genotype:
            norm_genotype = "Met/Met"

        return self.GENOTYPE_IMPACTS.get(gene, {}).get(norm_genotype, "unknown")

    def _generate_summary(self, results: List[GenotypeResult]) -> str:
        """生成解析摘要"""
        high_impact = [r for r in results if r.impact == "high"]
        moderate_impact = [r for r in results if r.impact == "moderate"]

        summary = f"检测到 {len(results)} 个 SNP 位点"
        if high_impact:
            genes = ", ".join(set(r.gene for r in high_impact))
            summary += f"，其中 {len(high_impact)} 个高影响基因: {genes}"
        if moderate_impact:
            summary += f"，{len(moderate_impact)} 个中等影响"

        return summary

    def _generate_recommendations(self, results: List[GenotypeResult]) -> List[str]:
        """基于基因型生成营养补充建议"""
        recommendations = []

        gene_actions = {
            "MTHFR": "推荐使用活性叶酸（L-5-MTHF）而非普通叶酸",
            "VDR": "可能需要更高剂量的维生素D3（3000-5000 IU）",
            "FADS1": "建议直接补充 EPA+DHA 而非依赖体内转化",
            "FADS2": "建议直接补充 EPA+DHA 而非依赖体内转化",
            "HFE": "避免补充铁剂，定期监测铁蛋白水平",
            "COMT": "压力敏感型，建议增加压力管理和镁摄入",
            "BDNF": "关注 Omega-3 和认知支持营养素",
            "IL6": "炎症倾向，增加抗炎营养素（Omega-3、姜黄素）",
            "FTO": "食欲控制相关，关注饱腹感和代谢优化",
        }

        for result in results:
            if result.impact in ["high", "moderate"]:
                action = gene_actions.get(result.gene)
                if action:
                    recommendations.append(f"{result.gene}: {action}")

        return recommendations


# 便捷函数
def parse_gene_report(file_path: str) -> Dict[str, Any]:
    """
    快速解析基因报告

    参数:
        file_path: 基因报告文件路径

    返回:
        解析结果字典
    """
    parser = GeneReportParser()
    return parser.parse_from_file(file_path)


def parse_gene_report_from_text(text: str) -> Dict[str, Any]:
    """
    从文本快速解析基因报告

    参数:
        text: 基因报告文本内容

    返回:
        解析结果字典
    """
    parser = GeneReportParser()
    return parser.parse_from_text(text)


if __name__ == "__main__":
    # 测试示例
    test_text = """
    MTHFR C677T (rs1801133)
    基因型: CT
    影响: 中等

    VDR FokI (rs2228570)
    基因型: FF

    COMT Val158Met (rs4680)
    基因型: Val/Met
    """

    print("=== 基因报告解析测试 ===\n")
    result = parse_gene_report_from_text(test_text)

    print(f"摘要: {result['summary']}")
    print(f"\n检测结果:")
    for r in result['results']:
        print(f"  {r['gene']} {r['variant']}: {r['genotype']} ({r['impact']})")

    print(f"\n建议:")
    for rec in result['recommendations']:
        print(f"  - {rec}")
