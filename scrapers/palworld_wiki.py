"""
Palworld Wiki 爬虫 — 从 paldb.cc/version 补全早期版本数据

用于填补 Steam News API 未覆盖的早期版本（v0.1.x - v0.4.x），
数据来源为 paldb.cc Wiki 页面的版本历史整理。

使用方式:
    python scrapers/palworld_wiki.py          # 抓取并输出 JSON
    python scrapers/palworld_wiki.py --merge  # 直接合并到 data/palworld/patches.json
"""

import argparse
import json
import re
import hashlib
from datetime import datetime
from pathlib import Path
import requests
from bs4 import BeautifulSoup


PALDB_URL = "https://paldb.cc/version"
TIMEOUT = 30


def extract_version_number(title_text: str) -> str | None:
    """从标题文本中提取版本号字符串。"""
    for pattern, group_idx in [
        (r"^#?\s*Version\s+v?(\d+\.\d+(?:\.\d+)?[a-zA-Z]?)", 1),
        (r"^#?\s*v?(\d+\.\d+(?:\.\d+)?[a-zA-Z]?)\s*[:\s]", 1),
        (r"^#?\s*Patch\s+Note[sd]?\s+v?(\d+\.\d+(?:\.\d+)?[a-zA-Z]?)", 1),
        (r"^#?\s*Crossplay\s+Update[,\s]+v?(\d+\.\d+(?:\.\d+)?[a-zA-Z]?)", 1),
    ]:
        m = re.match(pattern, title_text.strip(), re.IGNORECASE)
        if m:
            return f"v{m.group(group_idx)}"
    # Fallback: try to find any version-like number
    m = re.search(r"v?(\d+\.\d+(?:\.\d+)?[a-zA-Z]?)", title_text, re.IGNORECASE)
    if m:
        v = m.group(1)
        if not v.startswith("v"):
            return f"v{v}"
        return v
    return None


def parse_date(text: str) -> str | None:
    """从文本中提取日期，返回 YYYY/MM/DD 格式。"""
    m = re.search(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})", text)
    if m:
        return f"{m.group(1)}/{m.group(2).zfill(2)}/{m.group(3).zfill(2)}"
    return None


def clean_list_items(ul) -> list[str]:
    """从 <ul> 中提取所有 <li> 的文本。"""
    lines = []
    for li in ul.find_all("li", recursive=False):
        text = li.get_text(strip=True)
        if text:
            lines.append(f"- {text}")
    # 如果没有直接子 <li>，尝试所有后代
    if not lines:
        for li in ul.find_all("li"):
            text = li.get_text(strip=True)
            if text:
                lines.append(f"- {text}")
    return lines


def parse_palworld_wiki(html: str) -> list[dict]:
    """解析 paldb.cc/version 页面，返回版本列表（按时间倒序）。"""
    soup = BeautifulSoup(html, "html.parser")
    all_patches = []

    # 所有版本标题都在 h1 中
    h1_tags = soup.find_all("h1")

    # 特殊版本的日期查表（当 HTML 中没有日期段落时使用）
    KNOWN_DATES = {
        "v0.4.12": "2025/01/13",  # No date paragraph in HTML; Steam API: 2025-01-13
        "v0.3.10": "2024/10/31",  # No date paragraph in HTML; inferred
        "v0.6.8":  "2024/08/31",  # No date paragraph in HTML; inferred from sequence
        "v0.6.4":  "2025/07/30",  # No date paragraph in HTML; Steam API: 2025-07-30
    }

    for idx, tag in enumerate(h1_tags):
        raw_title = tag.get_text(strip=True)
        ver = extract_version_number(raw_title)
        if not ver:
            continue

        version_title = ver
        date_str = None
        content_lines = []

        # 遍历该 h1 之后的所有兄弟元素，直到遇到下一个 h1
        next_tag = tag.find_next_sibling()
        while next_tag:
            # 遇到下一个 h1 → 停止
            if next_tag.name == "h1":
                break

            if next_tag.name == "p":
                text = next_tag.get_text(strip=True)
                if not date_str:
                    d = parse_date(text)
                    if d:
                        date_str = d
                        next_tag = next_tag.find_next_sibling()
                        continue

            if next_tag.name == "ul":
                content_lines.extend(clean_list_items(next_tag))

            next_tag = next_tag.find_next_sibling()

        # 日期默认值：先尝试查表，再从 HTML 中解析
        if not date_str:
            date_str = KNOWN_DATES.get(ver)
        if not date_str:
            date_str = "2000/01/01"

        # 解析 timestamp
        try:
            dt = datetime.strptime(date_str, "%Y/%m/%d")
        except ValueError:
            dt = datetime(2000, 1, 1)
        ts = int(dt.timestamp())

        all_patches.append({
            "gid": hashlib.md5(version_title.encode()).hexdigest()[:16],
            "title": version_title,
            "url": PALDB_URL,
            "date": dt.strftime("%Y-%m-%d"),
            "timestamp": ts,
            "author": "pocketpair_dev",
            "feed_label": "Community Announcements",
            "content": "\n".join(content_lines),
            "source": "wiki_compilation",
        })

    return all_patches


def fetch_wiki_patches() -> list[dict]:
    """从 paldb.cc 获取完整版本历史。"""
    headers = {"User-Agent": "Mozilla/5.0 (compatible; research-bot/1.0)"}
    resp = requests.get(PALDB_URL, headers=headers, timeout=TIMEOUT)
    resp.raise_for_status()
    return parse_palworld_wiki(resp.text)


def filter_early_versions(patches: list[dict]) -> list[dict]:
    """只保留 Steam API 未覆盖的早期版本。

    Steam News API 覆盖从 v0.4.13 (2025-01-15) 开始，
    因此以 2025-01-16 作为分界线，捕获 v0.4.12 及更早的所有版本。
    """
    cutoff = "2025-01-16"
    return [p for p in patches if p["date"] < cutoff]


def merge_into_existing(new_patches: list[dict], existing_path: Path) -> int:
    """将新版本合并到 patches.json，返回新增条目数。"""
    with open(existing_path, "r", encoding="utf-8") as f:
        existing = json.load(f)

    existing_titles = {p["title"] for p in existing["patches"]}
    existing_dates = {p["date"] for p in existing["patches"]}

    added = 0
    for patch in new_patches:
        if patch["title"] not in existing_titles and patch["date"] not in existing_dates:
            existing["patches"].append(patch)
            added += 1

    # 按 timestamp 倒序排列
    existing["patches"].sort(key=lambda x: x["timestamp"], reverse=True)
    existing["fetched_at"] = datetime.now().isoformat()

    with open(existing_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

    return added


def main():
    parser = argparse.ArgumentParser(description="Palworld Wiki 爬虫 — 补全早期版本数据")
    parser.add_argument("--merge", action="store_true", help="直接合并到 patches.json")
    args = parser.parse_args()

    print(f"正在抓取 {PALDB_URL} ...")
    all_patches = fetch_wiki_patches()
    print(f"共解析 {len(all_patches)} 条版本记录")

    early = filter_early_versions(all_patches)
    print(f"其中早期版本（v0.1 - v0.4.x，共 {len(early)} 条）不在 Steam API 数据中")

    if args.merge:
        data_path = Path(__file__).parent.parent / "data" / "palworld" / "patches.json"
        added = merge_into_existing(early, data_path)
        print(f"已合并 {added} 条新版本到 {data_path}")
    else:
        output_path = Path(__file__).parent.parent / "data" / "palworld" / "patches_early.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({"patches": early}, f, ensure_ascii=False, indent=2)
        print(f"已保存到 {output_path}")
        print("\n前 3 条示例:")
        for p in early[:3]:
            print(f"  {p['title']} ({p['date']}): {p['content'][:100]}...")


if __name__ == "__main__":
    main()
