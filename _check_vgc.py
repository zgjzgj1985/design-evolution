"""检查 VGC 历史数据文件"""
import sys
import json
from pathlib import Path

sys.path.insert(0, "d:/设计演化档案")

# 检查文件
vgc_file = Path("d:/设计演化档案/data/pokemon/vgc_history.json")
print(f"文件存在: {vgc_file.exists()}")

if vgc_file.exists():
    with open(vgc_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"赛季数量: {data.get('total_seasons')}")
    print(f"采集时间: {data.get('fetched_at')}")
    print()

    # 检查 Gen 4 对应的赛季
    gen4_seasons = [s for s in data.get("seasons", []) if s.get("generation") == 4]
    print(f"Gen 4 赛季: {len(gen4_seasons)}")
    for s in gen4_seasons:
        print(f"  - {s.get('version')} {s.get('game')}")

    # 测试懒加载
    print("\n测试懒加载:")
    from scrapers.pokemon_wiki import _load_vgc_history
    vgc_data = _load_vgc_history()
    print(f"加载的赛季数: {len(vgc_data)}")
