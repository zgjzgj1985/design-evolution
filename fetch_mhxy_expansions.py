#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
梦幻西游资料片和大型更新全面采集器

根据官方论坛和社区整理的完整资料片列表进行采集
"""

import re
import json
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import urllib.request
import hashlib


class MHXYExpansionScraper:
    """梦幻西游资料片采集器"""

    def __init__(self):
        self.cache = {}

    def fetch_url(self, url: str) -> Optional[str]:
        cache_key = hashlib.md5(url.encode()).hexdigest()
        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            req = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml',
                }
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                content = response.read()
                encoding = response.headers.get_content_charset() or 'utf-8'
                try:
                    decoded = content.decode(encoding)
                except:
                    decoded = content.decode('gbk', errors='replace')
                self.cache[cache_key] = decoded
                return decoded
        except Exception:
            return None

    def parse_page(self, url: str) -> Optional[Dict]:
        html = self.fetch_url(url)
        if not html:
            return None

        result = {
            'url': url,
            'title': '',
            'date': '',
            'content': '',
        }

        # 提取标题
        title_match = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
        if not title_match:
            title_match = re.search(r'<title>([^<]+)</title>', html)
        if title_match:
            result['title'] = title_match.group(1).strip()

        # 提取日期
        date_match = re.search(r'(\d{4})[年-](\d{1,2})[月-](\d{1,2})', html)
        if date_match:
            result['date'] = f"{date_match.group(1)}-{int(date_match.group(2)):02d}-{int(date_match.group(3)):02d}"

        # 提取正文
        result['content'] = self._extract_text(html)

        return result

    def _extract_text(self, html: str) -> str:
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        text = text.replace('&nbsp;', ' ').replace('&amp;', '&')
        text = re.sub(r'<[^>]+>', '\n', text)
        text = re.sub(r'\n+', '\n', text)
        return text.strip()[:10000]


def main():
    print("=" * 70)
    print("梦幻西游资料片和大型更新全面采集")
    print("=" * 70)

    scraper = MHXYExpansionScraper()

    # 完整资料片列表（基于官方论坛和社区整理）
    expansions = [
        # ========== 2004-2009 早期资料片 ==========
        ("2004欢乐家园", "资料片", "https://xyq.163.com/"),
        ("2004神鬼玄机", "资料片", "https://xyq.163.com/"),
        ("2005美丽人生", "资料片", "https://xyq.163.com/"),
        ("2005化境", "资料片", "https://xyq.163.com/"),
        ("2006天命之战", "资料片", "https://xyq.163.com/"),
        ("2007宝藏", "资料片", "https://xyq.163.com/"),
        ("2007法宝传奇", "资料片", "https://xyq.163.com/m/introduce/20231107/23210_644175.html"),
        ("2008坐骑天下", "资料片", "https://xyq.163.com/"),
        ("2009上古神符", "资料片", "https://xyq.163.com/"),

        # ========== 2010-2014 中期 ==========
        ("2011功成名就", "资料片", "https://xyq.163.com/update/2011/9/9/5092_248605.html"),
        ("2014腾云驾雾", "资料片", "https://xyq.163.com/update/2014/1/9/5091_417423.html"),
        ("2014异兽奇兵", "资料片", "https://xyq.163.com/m/introduce/20231107/23210_647092.html"),
        ("2015群雄涿鹿", "资料片", "https://xyq.163.com/"),
        ("2015金戈铁马", "资料片", "https://xyq.163.com/"),

        # ========== 2016-2020 近期 ==========
        ("2016点石成金", "资料片", "https://xyq.163.com/m/introduce/20231107/23210_644261.html"),
        ("2016超凡入圣", "资料片", "https://xyq.163.com/"),
        ("2017聚圣三界", "资料片", "https://xyq.163.com/m/news/20231218/4905_666865.html"),
        ("2017神器谱", "资料片", "https://xyq.163.com/2017/sq/"),
        ("2018赤水传说", "资料片", "https://xyq.163.com/2018/zlp/"),
        ("2018天机奇谈", "资料片", "https://xyq.163.com/2018/tjqt/index.html"),
        ("2018齐天大圣", "资料片", "https://xyq.163.com/2018/qtds/"),
        ("2020绘梦山河", "资料片", "https://xyq.163.com/org_bg/20200728/15743_895016.html"),

        # ========== 2021-2024 最新 ==========
        ("2021东海秘境", "资料片", "https://xyq.163.com/2021/dhmj/"),
        ("2021九头妖王", "资料片", "https://xyq.163.com/"),
        ("2021绮梦长安", "资料片", "https://xyq.163.com/news/20210914/4905_971919.html"),
        ("2022弈决风云", "资料片", "https://xyq.163.com/org_bg/20220719/15743_1031617.html"),
        ("2022撼海狂龙", "资料片", "https://xyq.163.com/org_bg/20221220/15743_1058400.html"),
        ("2023暑期九黎城", "资料片", "https://xyq.163.com/2023/sqzlp/"),
        ("2024寒假", "资料片", "https://xyq.163.com/2024/hjzlp/"),
        ("2024千变万化", "资料片", "https://xyq.163.com/wh/20241223/4907_1201705.html"),
    ]

    all_data = {
        "source": "梦幻西游官方论坛及资料片专题",
        "generated_at": datetime.now().isoformat(),
        "expansions": []
    }

    success_count = 0
    fail_count = 0

    for name, category, url in expansions:
        if url == "https://xyq.163.com/" or not url:
            print(f"\n跳过(无URL): {name}")
            continue

        print(f"\n获取: {name}")
        result = scraper.parse_page(url)
        if result and result.get('content'):
            result['category'] = category
            result['name'] = name
            print(f"  标题: {result.get('title', '')[:50]}")
            print(f"  日期: {result.get('date', '')}")
            print(f"  内容长度: {len(result.get('content', ''))} 字符")
            all_data["expansions"].append(result)
            success_count += 1
        else:
            print(f"  获取失败!")
            fail_count += 1
        time.sleep(0.5)

    # 保存
    output_file = Path(__file__).parent / "docs" / "mhxy_expansions.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print(f"\n" + "=" * 70)
    print(f"采集完成!")
    print(f"成功: {success_count} 条")
    print(f"失败: {fail_count} 条")
    print(f"保存到: {output_file}")
    print("=" * 70)


if __name__ == "__main__":
    main()
