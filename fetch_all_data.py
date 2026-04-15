"""从 Steam API 采集更新日志，保存为本地 JSON 文件（一次性采集）"""
import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup
import sys

STEAM_NEWS_API = "https://api.steampowered.com/ISteamNews/GetNewsForApp/v0002/"

GAMES = {
    "temtem": {"id": "745920", "name": "Temtem"},
    "cassette_beasts": {"id": "1322240", "name": "Cassette Beasts"},
    "palworld": {"id": "1623730", "name": "Palworld"},
}


def clean_html(html_content: str) -> str:
    soup = BeautifulSoup(html_content, "lxml")
    for tag in soup(["script", "style"]):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    return "\n".join(lines)


def fetch_game(game_key: str, info: dict) -> dict:
    url = f"{STEAM_NEWS_API}?appid={info['id']}&count=100&format=json"
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    items = data.get("appnews", {}).get("newsitems", [])

    cleaned = []
    for item in items:
        cleaned.append({
            "gid": item.get("gid"),
            "title": item.get("title"),
            "url": item.get("url"),
            "date": datetime.fromtimestamp(item.get("date", 0)).strftime("%Y-%m-%d") if item.get("date") else "",
            "timestamp": item.get("date"),
            "author": item.get("author"),
            "feed_label": item.get("feedlabel"),
            "content": clean_html(item.get("contents", "")),
        })
    return cleaned


def main():
    for game_key, info in GAMES.items():
        print(f"Fetching {info['name']}...", flush=True)
        try:
            patches = fetch_game(game_key, info)
            output = {
                "game": info["name"],
                "app_id": info["id"],
                "fetched_at": datetime.now().isoformat(),
                "total_count": len(patches),
                "patches": patches,
            }
            filepath = f"data/{game_key}/patches.json"
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
            print(f"  -> {len(patches)} 条已保存到 {filepath}", flush=True)
        except Exception as e:
            print(f"  -> {info['name']} 失败: {e}", flush=True)
            sys.exit(1)

    print("全部采集完成！", flush=True)


if __name__ == "__main__":
    main()
