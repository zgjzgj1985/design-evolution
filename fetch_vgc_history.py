"""采集 VGC 历史数据 - 从 Serebii.net 采集历代 VGC 规则和赛季数据"""
import sys
import json
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from scrapers.bulbapedia import SerebiiScraper


def collect_all_vgc_data():
    """采集 2009-2021 所有 VGC 赛季数据"""
    scraper = SerebiiScraper()

    all_seasons = []

    # VGC 从 2009 年首届世锦赛开始
    for year in range(2009, 2022):
        print(f"正在采集 {year} 年 VGC 数据...", flush=True)

        season = scraper.get_vgc_season_rules(year)

        if season.get("rule_set") or season.get("banned_pokemon"):
            # 构建易读的内容摘要
            content_parts = []

            # 添加规则
            rules = season.get("rule_set", {})
            if rules.get("Battle Type"):
                content_parts.append(f"对战类型: {rules['Battle Type']}")
            if rules.get("Pokédex Restriction"):
                content_parts.append(f"图鉴限制: {rules['Pokédex Restriction']}图鉴")

            # 添加禁用宝可梦
            banned = season.get("banned_pokemon", [])
            if banned:
                banned_str = "、".join(banned[:10])
                if len(banned) > 10:
                    banned_str += f"等{len(banned)}只"
                content_parts.append(f"禁用宝可梦: {banned_str}")

            # 添加特殊条款
            clauses = season.get("special_clauses", [])
            if clauses:
                content_parts.append(f"特殊条款: {'、'.join(clauses[:5])}")

            # 添加世界冠军
            if season.get("champion"):
                content_parts.append(f"世界冠军: {season['champion']}")

            season_data = {
                "version": str(year),
                "date": f"{year}-01-01",
                "game": season.get("game", ""),
                "source_url": season.get("url", ""),
                "generation": season.get("generation", 0),
                "official_notes": f"VGC {year} Series - {season.get('game', '')}",
                "changes": [
                    {
                        "category": "PvP",
                        "content": f"{year}年VGC赛季规则：" + " | ".join(content_parts),
                        "intent": f"记录第{season.get('generation', 0)}世代VGC赛季规则变更，包括图鉴限制、禁用列表和特殊条款",
                        "detail": f"规则详情: {json.dumps(season.get('rule_set', {}), ensure_ascii=False)}\n"
                                 f"禁用宝可梦: {', '.join(season.get('banned_pokemon', []))}\n"
                                 f"特殊条款: {', '.join(season.get('special_clauses', []))}\n"
                                 f"世界冠军: {season.get('champion', 'N/A')}",
                    }
                ],
            }

            all_seasons.append(season_data)
            print(f"  -> 成功采集 {year} 年数据 (Gen {season.get('generation', 0)})")
        else:
            print(f"  -> {year} 年无数据")

        # 礼貌延迟，避免请求过快
        time.sleep(0.5)

    return all_seasons


def main():
    print("=" * 60)
    print("VGC 历史数据采集工具")
    print("=" * 60)

    seasons = collect_all_vgc_data()

    print()
    print(f"共采集 {len(seasons)} 个赛季数据")

    # 保存到 data/pokemon/vgc_history.json
    output_dir = Path(__file__).parent / "data" / "pokemon"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "vgc_history.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "description": "VGC (Video Game Championships) 历史规则数据",
            "source": "Serebii.net",
            "fetched_at": datetime.now().isoformat(),
            "total_seasons": len(seasons),
            "seasons": seasons,
        }, f, ensure_ascii=False, indent=2)

    print(f"数据已保存到: {output_file}")

    # 打印摘要
    print()
    print("各赛季数据摘要:")
    print("-" * 60)
    for s in seasons:
        gen = s.get("generation", 0)
        game = s.get("game", "")
        banned = len(s.get("changes", [{}])[0].get("detail", "").split("禁用宝可梦: "))
        print(f"  {s['version']} | Gen {gen} | {game}")


if __name__ == "__main__":
    main()
