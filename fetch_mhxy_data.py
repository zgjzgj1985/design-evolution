"""
梦幻西游Like游戏数据采集脚本

数据来源优先级：
1. 内置数据（scrapers/mhxy_data.py）- 主要来源
2. 网络抓取（预留扩展接口）

运行方式：
    python fetch_mhxy_data.py              # 采集所有支持的游戏
    python fetch_mhxy_data.py --game 梦幻西游  # 只采集指定游戏
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# 导入内置数据模块
from scrapers.mhxy_data import MHXYDataProvider


# 预留：网络数据源（后续扩展）
# MHXY_OFFICIAL_NEWS_URL = "https://xyq.163.com/news/"
# MHXY_NGA_URL = "https://nga.178.com/thread.php?fid=-7&bbsid=..."
# YEZIZHU_URL = "https://www.yezizhu.com/"


def export_game_data(game: str, output_dir: str = "data") -> Dict:
    """
    导出指定游戏的数据到本地JSON文件
    """
    print(f"正在导出 {game} 数据...")

    patches = MHXYDataProvider.get_all_patches(game)
    metadata = MHXYDataProvider.get_generation_metadata(game)

    output_data = {
        "game": game,
        "fetched_at": datetime.now().isoformat(),
        "total_patches": len(patches),
        "generations": metadata,
        "patches": patches,
    }

    # 确定输出目录
    game_key = game.lower()
    output_dir_path = Path(output_dir) / game_key
    output_dir_path.mkdir(parents=True, exist_ok=True)

    output_file = output_dir_path / "patches.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"  -> {len(patches)} 条更新日志已保存到 {output_file}")

    return {
        "game": game,
        "total_patches": len(patches),
        "output_file": str(output_file),
    }


def export_all_games(output_dir: str = "data") -> List[Dict]:
    """
    导出所有支持游戏的数据
    """
    results = []
    supported_games = MHXYDataProvider.get_supported_games()

    print(f"开始导出 {len(supported_games)} 个游戏的数据...\n")

    for game in supported_games:
        try:
            result = export_game_data(game, output_dir)
            results.append(result)
        except Exception as e:
            print(f"  -> 导出 {game} 失败: {e}")
            results.append({
                "game": game,
                "status": "failed",
                "error": str(e),
            })

    return results


def generate_timeline_data(game: str = "梦幻西游", output_dir: str = "docs") -> str:
    """
    生成时间轴数据结构，用于前端展示
    """
    patches = MHXYDataProvider.get_all_patches(game)

    # 按时期分组
    timeline_by_period = {}
    for patch in patches:
        period = patch.get("period", "未知时期")
        if period not in timeline_by_period:
            timeline_by_period[period] = []
        timeline_by_period[period].append({
            "id": patch.get("title", ""),
            "title": patch.get("title", ""),
            "date": patch.get("date", ""),
            "description": patch.get("content", "")[:200],
            "categories": patch.get("categories", []),
            "pvp_impact": patch.get("pvp_impact", "无"),
            "pve_impact": patch.get("pve_impact", "无"),
        })

    timeline_data = {
        "game": game,
        "generated_at": datetime.now().isoformat(),
        "periods": [
            {
                "period": period,
                "events": events,
            }
            for period, events in timeline_by_period.items()
        ],
    }

    output_file = Path(output_dir) / "timeline_data.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(timeline_data, f, ensure_ascii=False, indent=2)

    print(f"时间轴数据已保存到 {output_file}")
    return str(output_file)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="梦幻西游Like游戏数据采集")
    parser.add_argument(
        "--game",
        type=str,
        default=None,
        help="指定游戏名称（默认：导出所有支持的游戏）"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data",
        help="输出目录（默认：data）"
    )
    parser.add_argument(
        "--timeline",
        action="store_true",
        help="同时生成时间轴数据结构"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("梦幻西游Like游戏数据采集工具")
    print("=" * 60)
    print()

    if args.game:
        # 导出指定游戏
        results = [export_game_data(args.game, args.output_dir)]
    else:
        # 导出所有游戏
        results = export_all_games(args.output_dir)

    # 生成时间轴数据
    if args.timeline:
        generate_timeline_data(output_dir=args.output_dir.replace("data", "docs") if args.output_dir == "data" else args.output_dir)

    # 汇总报告
    print()
    print("=" * 60)
    print("导出汇总")
    print("=" * 60)

    total_patches = 0
    for result in results:
        if "total_patches" in result:
            print(f"  {result['game']}: {result['total_patches']} 条")
            total_patches += result["total_patches"]
        elif "status" in result and result["status"] == "failed":
            print(f"  {result['game']}: 导出失败 - {result.get('error', '未知错误')}")

    print(f"\n总计: {total_patches} 条更新日志")
    print()
    print("数据来源: scrapers/mhxy_data.py（内置历史数据）")
    print("说明: 梦幻西游作为国产游戏，数据主要来自社区整理和官方公告。")
    print()


if __name__ == "__main__":
    main()
