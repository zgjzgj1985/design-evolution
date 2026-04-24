#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
梦幻西游召唤兽和系统调整专项采集器
"""

import re
import json
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import urllib.request
import hashlib


class MHXYSummonScraper:
    """召唤兽和系统调整采集器"""

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
            'update_type': '其他'
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

        # 判断更新类型
        title_content = result['title'] + result['content']
        if '召唤兽' in title_content and ('技能' in title_content or '特性' in title_content or '内丹' in title_content):
            result['update_type'] = '召唤兽调整'
        elif '召唤兽' in title_content:
            result['update_type'] = '召唤兽'
        elif '系统' in title_content or '玩法' in title_content:
            result['update_type'] = '系统调整'
        elif '锦衣' in title_content or '祥瑞' in title_content:
            result['update_type'] = '外观系统'
        elif '法宝' in title_content or '灵宝' in title_content:
            result['update_type'] = '法宝灵宝'
        elif '副本' in title_content or '活动' in title_content:
            result['update_type'] = '玩法调整'
        elif '装备' in title_content or '灵饰' in title_content:
            result['update_type'] = '装备调整'

        return result

    def _extract_text(self, html: str) -> str:
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        text = text.replace('&nbsp;', ' ').replace('&amp;', '&')
        text = re.sub(r'<[^>]+>', '\n', text)
        text = re.sub(r'\n+', '\n', text)
        return text.strip()[:15000]


def main():
    print("=" * 70)
    print("梦幻西游召唤兽和系统调整专项采集")
    print("=" * 70)

    scraper = MHXYSummonScraper()

    # 召唤兽和系统调整URL列表
    urls = [
        # 召唤兽特性
        ("召唤兽特性", "https://xyq.163.com/news/glz/sjxt/20200708/33424_891540.html"),
        ("召唤兽进阶", "https://xyq.163.com/news/glz/sjxt/20200708/33424_891445.html"),
        ("召唤兽进阶与特性", "https://xyq.163.com/m/introduce/20250605/5018_580451.html"),

        # 灵宝系统
        ("2019灵宝系统", "https://xyq.163.com/20191016/4999_841018.html"),
        ("2020灵宝升级", "https://xyq.163.com/org_bg/20200728/15743_895016.html"),

        # 召唤兽相关调整
        ("2018召唤兽调整", "https://xyq.163.com/20181029/4999_782197.html"),
        ("2017召唤兽", "https://xyq.163.com/20171023/4999_718949.html"),
        ("2014召唤兽进阶", "https://xyq.163.com/m/introduce/20231107/23210_647092.html"),

        # 神器和灵宝
        ("2017神器谱", "https://xyq.163.com/2017/sq/"),
        ("2017神器", "https://xyq.163.com/2017/sqp/"),

        # 系统调整
        ("2016系统", "https://xyq.163.com/2016/09/26/4999_644417.html"),
        ("2015系统", "https://xyq.163.com/2015/10/16/4999_574504.html"),

        # 2024-2026
        ("2024超级技能", "https://xyq.163.com/news/20240520/4999_1156134.html"),
        ("2024生肖神兽", "https://xyq.163.com/wh/20260110/4907_1281205.html"),
        ("2026灵猴降世", "https://xyq.163.com/wh/20260123/4907_1283382.html"),
    ]

    all_data = {
        "source": "梦幻西游官方论坛",
        "generated_at": datetime.now().isoformat(),
        "items": []
    }

    type_count = {}
    success = 0

    for name, url in urls:
        print(f"\n获取: {name}")
        result = scraper.parse_page(url)
        if result and result.get('content'):
            print(f"  标题: {result.get('title', '')[:50]}")
            print(f"  日期: {result.get('date', '')}")
            print(f"  类型: {result.get('update_type', '')}")
            print(f"  内容长度: {len(result.get('content', ''))} 字符")
            all_data["items"].append(result)
            t = result.get('update_type', '其他')
            type_count[t] = type_count.get(t, 0) + 1
            success += 1
        else:
            print(f"  获取失败!")
        time.sleep(0.5)

    # 保存
    output_file = Path(__file__).parent / "docs" / "mhxy_summon_system.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print(f"\n" + "=" * 70)
    print(f"采集完成! 成功: {success} 条")
    print("各类型统计:")
    for t, c in sorted(type_count.items(), key=lambda x: -x[1]):
        print(f"  {t}: {c}条")
    print(f"保存到: {output_file}")
    print("=" * 70)


if __name__ == "__main__":
    main()
