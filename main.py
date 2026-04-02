#!/usr/bin/env python3
"""
Health Coach - CLI 入口
支持多阶段健康建议、补充剂推荐、冲突检测和每周健康周报
"""

import json
import asyncio
from pathlib import Path
from typing import Optional, List

import typer
from rich.console import Console
from rich.table import Table
from rich.markdown import Markdown

app = typer.Typer(help="Health Coach - 个性化健康建议系统")
console = Console()

# 阶段标签映射
STAGE_LABELS = {
    "general": "普通期",
    "preconception": "备孕/孕期",
    "fat_loss": "减脂期",
    "muscle_gain": "增肌期",
    "jetlag_travel": "倒时差/旅行",
    "recovery": "恢复期"
}


def load_skill_config() -> dict:
    """加载 skill.json 配置"""
    config_path = Path(__file__).parent / "skill.json"
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_stage(stage: str) -> bool:
    """验证阶段参数是否有效"""
    return stage in STAGE_LABELS


@app.command()
def hello():
    """显示欢迎信息和能力列表"""
    config = load_skill_config()

    console.print(f"\n[bold cyan]🏥 {config['name']} v{config['version']}[/bold cyan]\n")
    console.print(f"{config['description']}\n")
    console.print(f"作者: {config['author']}\n")

    # 显示 capabilities 表格
    table = Table(title="支持的功能 (Capabilities)")
    table.add_column("功能名称", style="cyan")
    table.add_column("描述", style="green")

    for cap in config.get("capabilities", []):
        table.add_row(cap["name"], cap["description"])

    console.print(table)
    console.print("\n使用 [bold]python main.py --help[/bold] 查看所有命令\n")


@app.command()
def profile(
    name: str = typer.Option(..., "--name", "-n", help="用户姓名"),
    stage: str = typer.Option(..., "--stage", "-s", help="当前阶段")
):
    """创建或查看用户档案"""
    if not validate_stage(stage):
        console.print(f"[red]错误: 无效的阶段 '{stage}'[/red]")
        console.print(f"\n有效阶段: {', '.join(STAGE_LABELS.keys())}")
        raise typer.Exit(1)

    console.print(f"\n[bold green]✓ 用户档案创建成功[/bold green]\n")
    console.print(f"[cyan]姓名:[/cyan] {name}")
    console.print(f"[cyan]阶段:[/cyan] {STAGE_LABELS[stage]} ({stage})")
    console.print("\n使用 [bold]python main.py recommend --stage {stage}[/bold] 获取推荐方案\n")


@app.command()
def stages():
    """列出所有支持的健康阶段"""
    config = load_skill_config()

    table = Table(title="支持的健康阶段")
    table.add_column("代码标识", style="cyan")
    table.add_column("名称", style="green")
    table.add_column("描述", style="yellow")

    for stage in config.get("stages", []):
        table.add_row(stage["id"], stage["name"], stage["description"])

    console.print(table)
    console.print("\n使用 [bold]python main.py profile --name <姓名> --stage <阶段>[/bold] 创建档案\n")


@app.command()
def recommend(
    stage: str = typer.Option(..., "--stage", "-s", help="目标阶段"),
    age: int = typer.Option(30, "--age", "-a", help="年龄"),
    gender: str = typer.Option("male", "--gender", "-g", help="性别"),
    current: Optional[List[str]] = typer.Option(None, "--current", "-c", help="当前补充剂"),
    gene_report: Optional[str] = typer.Option(None, "--gene", help="基因报告路径")
):
    """生成完整推荐方案（补充剂 + 饮食 + 注意事项）"""
    if not validate_stage(stage):
        console.print(f"[red]错误: 无效的阶段 '{stage}'[/red]")
        console.print(f"\n有效阶段: {', '.join(STAGE_LABELS.keys())}")
        raise typer.Exit(1)

    from agent.graph import run_health_coach_workflow
    from tools.diet_analyzer import analyze_diet

    console.print(f"\n[bold cyan]🏥 健康推荐报告[/bold cyan]\n")
    console.print(f"[cyan]阶段:[/cyan] {STAGE_LABELS[stage]} ({stage})")
    console.print(f"[cyan]年龄:[/cyan] {age}")
    console.print(f"[cyan]性别:[/cyan] {gender}")
    if gene_report:
        console.print(f"[cyan]基因报告:[/cyan] {gene_report}")
    console.print()

    try:
        # 构建用户画像
        user_profile = {
            "stage": stage,
            "age": age,
            "gender": gender,
            "current_supplements": current or [],
            "gene_report_path": gene_report
        }

        # 生成完整推荐
        result = run_health_coach_workflow(user_profile)

        # 以 Markdown 格式显示结果
        if result.get("final_response"):
            md = Markdown(result["final_response"])
            console.print(md)

        console.print()

    except Exception as e:
        console.print(f"[red]生成推荐失败: {e}[/red]")
        import traceback
        traceback.print_exc()
        raise typer.Exit(1)


@app.command()
def analyze_report(
    file_path: str = typer.Option(..., "--file", "-f", help="基因报告文件路径（支持 .txt, .pdf, .json）"),
    stage: str = typer.Option("general", "--stage", "-s", help="健康阶段"),
    age: int = typer.Option(30, "--age", "-a", help="年龄"),
    gender: str = typer.Option("male", "--gender", "-g", help="性别")
):
    """解析基因报告并生成个性化方案"""
    path = Path(file_path)
    if not path.exists():
        console.print(f"[red]错误: 文件不存在: {file_path}[/red]")
        raise typer.Exit(1)

    if not validate_stage(stage):
        console.print(f"[red]错误: 无效的阶段 '{stage}'[/red]")
        console.print(f"\n有效阶段: {', '.join(STAGE_LABELS.keys())}")
        raise typer.Exit(1)

    from tools.gene_report_parser import parse_gene_report
    from agent.graph import run_health_coach_workflow

    console.print(f"\n[bold cyan]🧬 基因报告分析与推荐[/bold cyan]\n")
    console.print(f"[cyan]文件:[/cyan] {file_path}")
    console.print(f"[cyan]阶段:[/cyan] {STAGE_LABELS[stage]}")
    console.print()

    try:
        # 解析基因报告
        gene_result = parse_gene_report(file_path)

        console.print(f"[bold green]解析摘要:[/bold green]")
        console.print(f"  {gene_result['summary']}\n")

        if gene_result["results"]:
            console.print(f"[bold yellow]检测结果:[/bold yellow]")
            for r in gene_result["results"]:
                impact_color = "red" if r["impact"] == "high" else ("yellow" if r["impact"] == "moderate" else "green")
                console.print(f"  [bold]{r['gene']}[/bold]: {r['genotype']} ([{impact_color}]{r['impact']}[/{impact_color}])")

        if gene_result["recommendations"]:
            console.print(f"\n[bold cyan]基于基因的建议:[/bold cyan]")
            for rec in gene_result["recommendations"]:
                console.print(f"  • {rec}")

        # 生成完整推荐
        console.print(f"\n[bold cyan]📋 个性化推荐方案[/bold cyan]\n")
        user_profile = {
            "stage": stage,
            "age": age,
            "gender": gender,
            "current_supplements": [],
            "gene_report_path": file_path
        }
        result = run_health_coach_workflow(user_profile)

        if result.get("final_response"):
            md = Markdown(result["final_response"])
            console.print(md)

    except Exception as e:
        console.print(f"[red]解析失败: {e}[/red]")
        import traceback
        traceback.print_exc()
        raise typer.Exit(1)


@app.command()
def weekly_report(
    name: str = typer.Option(..., "--name", "-n", help="用户姓名"),
    stage: str = typer.Option(..., "--stage", "-s", help="健康阶段"),
    data_file: Optional[str] = typer.Option(None, "--data", "-d", help="本周数据文件路径（JSON格式，可选）")
):
    """生成每周健康周报（总结本周数据 + 建议）"""
    if not validate_stage(stage):
        console.print(f"[red]错误: 无效的阶段 '{stage}'[/red]")
        console.print(f"\n有效阶段: {', '.join(STAGE_LABELS.keys())}")
        raise typer.Exit(1)

    from agent.llm_integration import get_llm, is_llm_available

    console.print(f"\n[bold cyan]📊 每周健康周报[/bold cyan]\n")
    console.print(f"[cyan]姓名:[/cyan] {name}")
    console.print(f"[cyan]阶段:[/cyan] {STAGE_LABELS[stage]} ({stage})")
    console.print()

    # 检查 LLM 可用性
    if not is_llm_available():
        console.print("[red]错误: LLM 不可用，无法生成周报。请检查 API Key 配置。[/red]")
        raise typer.Exit(1)

    # 加载本周数据
    weekly_data = None
    if data_file:
        data_path = Path(data_file)
        if data_path.exists():
            try:
                with open(data_path, 'r', encoding='utf-8') as f:
                    weekly_data = json.load(f)
                console.print(f"[cyan]本周数据:[/cyan] 已加载 {data_file}")
            except Exception as e:
                console.print(f"[yellow]警告: 无法加载数据文件: {e}[/yellow]")
        else:
            console.print(f"[yellow]警告: 数据文件不存在: {data_file}[/yellow]")

    try:
        llm = get_llm()
        report = asyncio.run(llm.generate_weekly_report(name, stage, weekly_data))

        # 以 Markdown 格式显示周报
        md = Markdown(report)
        console.print(md)

        console.print()

    except Exception as e:
        console.print(f"[red]生成周报失败: {e}[/red]")
        import traceback
        traceback.print_exc()
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
