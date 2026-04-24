"""
生成 report_data.json，包含多游戏类型的报告数据

支持：
- mhxy: 梦幻西游Like（8条设计原则 + 27条检查清单）
- pokemon: 宝可梦Like（10条设计原则 + 47条检查清单）

Usage:
    python scripts/generate_multi_game_report_data.py
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from report_generator_config import (
    MHXY_PRINCIPLES,
    MHXY_CHECKLISTS,
    GAME_TYPE_METADATA,
    get_report_data_for_game,
)


def load_pokemon_data_from_git():
    """从 git 获取宝可梦数据"""
    project_root = Path(__file__).parent.parent
    
    try:
        result = subprocess.run(
            ['git', '-C', str(project_root), 'show', 'HEAD:docs/report_data.json'],
            capture_output=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"Git 命令失败: {result.stderr.decode('utf-8', errors='replace')}")
            return None, None, None, None
        
        content = result.stdout.decode('utf-8')
        data = json.loads(content)
        
        return (
            data.get("principles", []),
            data.get("checklist", []),
            data.get("meta", {}),
            data.get("timelines", {})
        )
    except Exception as e:
        print(f"加载宝可梦数据失败: {e}")
        return None, None, None, None


def main():
    output_path = Path(__file__).parent.parent / "docs" / "report_data.json"
    
    # 从 git 加载宝可梦数据
    print("正在从 git 加载宝可梦数据...")
    pokemon_principles, pokemon_checklist, pokemon_meta, timelines = load_pokemon_data_from_git()
    
    if pokemon_principles is None:
        print("错误: 无法从 git 加载数据")
        return
    
    print(f"原始数据: principles={len(pokemon_principles)}, checklist={len(pokemon_checklist)}")
    
    # 生成两种游戏类型的报告数据
    print("正在生成梦幻西游Like数据...")
    mhxy_report = get_report_data_for_game("mhxy")
    
    print("正在生成宝可梦Like数据...")
    pokemon_report = get_report_data_for_game(
        "pokemon", 
        pokemon_principles_data=pokemon_principles,
        pokemon_checklist_data=pokemon_checklist,
        pokemon_meta=pokemon_meta
    )
    
    # 计算检查清单条目总数
    mhxy_checklist_count = sum(len(cat["items"]) for cat in MHXY_CHECKLISTS)
    pokemon_checklist_count = sum(len(cat.get("items", [])) for cat in pokemon_checklist)
    
    # 构建完整的 report_data.json
    report_data = {
        "meta": {
            "title": "综合研究报告：游戏设计演进",
            "subtitle": "Game Design Evolution Research",
            "version": "4.0-multi",
            "generated_at": datetime.now().isoformat(),
            "description": "多游戏类型设计演进研究",
            "game_types": {
                "mhxy": {
                    "name": "梦幻西游Like",
                    "description": "回合制MMO（门派技能+召唤兽+阵法克制）",
                    "principles_count": len(MHXY_PRINCIPLES),
                    "checklist_count": mhxy_checklist_count,
                },
                "pokemon": {
                    "name": "宝可梦Like", 
                    "description": "宝可梦系列多人对战设计经验",
                    "principles_count": len(pokemon_principles),
                    "checklist_count": pokemon_checklist_count,
                }
            }
        },
        "mhxy": {
            "meta": mhxy_report["meta"],
            "principles": mhxy_report["principles"],
            "checklist": mhxy_report["checklist"],
            "scenarios": mhxy_report["scenarios"],
            "generation_metadata": mhxy_report["generation_metadata"],
        },
        "pokemon": {
            "meta": pokemon_report["meta"],
            "principles": pokemon_report["principles"],
            "checklist": pokemon_report["checklist"],
            "scenarios": pokemon_report["scenarios"],
        },
        # 保留原有的时间轴数据
        "timelines": timelines,
        # 保留顶层 principles 和 checklist（向后兼容）
        "principles": pokemon_principles,
        "checklist": pokemon_checklist,
    }
    
    # 写入文件
    print(f"正在写入 {output_path}...")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    
    # 打印统计信息
    print(f"\n报告数据生成完成!")
    print(f"输出路径: {output_path}")
    print(f"\n梦幻西游Like游戏:")
    print(f"  - 设计原则: {len(report_data['mhxy']['principles'])} 条")
    print(f"  - 检查清单: {mhxy_checklist_count} 条")
    print(f"  - 场景维度: {len(report_data['mhxy']['scenarios'])} 个")
    print(f"\n宝可梦Like游戏:")
    print(f"  - 设计原则: {len(report_data['pokemon']['principles'])} 条")
    print(f"  - 检查清单: {pokemon_checklist_count} 条")
    print(f"  - 场景维度: {len(report_data['pokemon']['scenarios'])} 个")
    # timelines.pokemon 是列表类型
    pokemon_timeline = timelines.get('pokemon', [])
    print(f"  - 时间轴条目: pokemon={len(pokemon_timeline) if isinstance(pokemon_timeline, list) else 'N/A'} 条")


if __name__ == "__main__":
    main()
