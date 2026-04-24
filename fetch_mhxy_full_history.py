#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
梦幻西游全面历史数据采集器

采集官方论坛各类更新数据：
1. 门派调整
2. 资料片
3. 系统调整
4. 玩法更新
5. 赛事相关
"""

import re
import json
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import urllib.request
import hashlib

BASE_URL = "https://xyq.163.com"


class MHXYFullScraper:
    """梦幻西游全量数据采集器"""

    def __init__(self):
        self.cache = {}
        self.scraper_name = "MHXYFullScraper"

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
            'type': self._classify(html),
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

    def _classify(self, html: str) -> str:
        if '门派调整' in html:
            return '门派调整'
        elif '资料片' in html and ('重磅' in html or '来袭' in html or '上线' in html):
            return '资料片'
        elif '系统调整' in html or '玩法调整' in html:
            return '系统调整'
        elif '维护公告' in html:
            return '维护公告'
        elif '赛事' in html or '武神坛' in html or '比武' in html:
            return '赛事'
        elif '召唤兽' in html and ('技能' in html or '调整' in html):
            return '召唤兽调整'
        elif '召唤兽' in html:
            return '召唤兽'
        elif '法宝' in html or '灵宝' in html:
            return '法宝灵宝'
        elif '经脉' in html or '奇经八脉' in html:
            return '经脉调整'
        else:
            return '其他'

    def _extract_text(self, html: str) -> str:
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        text = text.replace('&nbsp;', ' ').replace('&amp;', '&')
        text = re.sub(r'<[^>]+>', '\n', text)
        text = re.sub(r'\n+', '\n', text)
        return text.strip()[:10000]


def main():
    print("=" * 60)
    print("梦幻西游全量历史数据采集")
    print("=" * 60)

    scraper = MHXYFullScraper()

    # 重要URL列表（手动整理，确保能找到）
    important_urls = [
        # 资料片类
        ("2016点石成金", "资料片", "https://xyq.163.com/m/introduce/20231107/23210_644261.html"),
        ("2017聚圣三界", "资料片", "https://xyq.163.com/m/news/20231218/4905_666865.html"),
        ("2021绮梦长安", "资料片", "https://xyq.163.com/news/20210914/4905_971919.html"),
        ("2022弈决风云", "资料片", "https://xyq.163.com/org_bg/20220719/15743_1031617.html"),
        ("2022撼海狂龙", "资料片", "https://xyq.163.com/org_bg/20221220/15743_1058400.html"),
        ("2023暑期九黎城", "资料片", "https://xyq.163.com/2023/sqzlp/"),
        ("2024寒假", "资料片", "https://xyq.163.com/2024/hjzlp/"),
        ("2024千变万化", "资料片", "https://xyq.163.com/wh/20241223/4907_1201705.html"),

        # 系统调整类
        ("2024系统玩法调整", "系统调整", "https://xyq.163.com/news/20240520/4999_1156134.html"),
        ("2024天命副本", "系统调整", "https://xyq.163.com/wh/20241129/4907_1196906.html"),

        # 召唤兽类
        ("2023召唤兽赐福", "召唤兽", "https://xyq.163.com/news/20231218/4905_666865.html"),
        ("2024超级技能", "召唤兽", "https://xyq.163.com/2024/hjzlp/"),
    ]

    all_data = {
        "source": "梦幻西游官方论坛",
        "generated_at": datetime.now().isoformat(),
        "updates": []
    }

    # 统计
    type_count = {}

    for name, category, url in important_urls:
        print(f"\n获取: {name}")
        result = scraper.parse_page(url)
        if result:
            result['category'] = category
            result['name'] = name
            print(f"  标题: {result.get('title', '')[:50]}")
            print(f"  日期: {result.get('date', '')}")
            print(f"  类型: {result.get('type', '')}")
            all_data["updates"].append(result)
            type_count[category] = type_count.get(category, 0) + 1
        else:
            print(f"  获取失败!")
        time.sleep(0.5)

    # 保存
    output_file = Path(__file__).parent / "docs" / "mhxy_full_history.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print(f"\n" + "=" * 60)
    print(f"采集完成!")
    print(f"总计: {len(all_data['updates'])} 条")
    print(f"各类统计:")
    for t, c in type_count.items():
        print(f"  {t}: {c} 条")
    print(f"保存到: {output_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()
