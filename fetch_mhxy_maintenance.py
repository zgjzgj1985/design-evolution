#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
梦幻西游定期维护公告采集器

采集官方论坛的定期维护公告，提取系统和玩法调整内容
"""

import re
import json
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import urllib.request
import hashlib


class MHXYMaintenanceScraper:
    """维护公告采集器"""

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

    def parse_maintenance_page(self, url: str) -> Optional[Dict]:
        """解析维护公告页面"""
        html = self.fetch_url(url)
        if not html:
            return None

        result = {
            'url': url,
            'title': '',
            'date': '',
            'content': '',
            'adjustments': []
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

        # 提取正文内容
        result['content'] = self._extract_text(html)

        # 提取调整相关内容
        result['adjustments'] = self._extract_adjustments(html)

        return result

    def _extract_text(self, html: str) -> str:
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        text = text.replace('&nbsp;', ' ').replace('&amp;', '&')
        text = re.sub(r'<[^>]+>', '\n', text)
        text = re.sub(r'\n+', '\n', text)
        return text.strip()[:15000]

    def _extract_adjustments(self, html: str) -> List[str]:
        """提取系统调整、召唤兽调整等内容"""
        adjustments = []

        # 定义关键词
        keywords = [
            '召唤兽调整', '召唤兽技能', '召唤兽特性', '内丹调整', '宝宝调整',
            '系统调整', '玩法调整', '副本调整', '装备调整', '灵饰调整',
            '法宝调整', '灵宝调整', '经脉调整', '锦衣调整', '祥瑞调整',
            '剧情调整', '任务调整', '活动调整', ' PK调整', '战斗调整',
        ]

        # 提取相关内容段落
        lines = html.split('\n')
        for i, line in enumerate(lines):
            for kw in keywords:
                if kw in line:
                    # 获取上下文
                    context = ' '.join(lines[max(0, i-2):min(len(lines), i+5)])
                    if len(context) > 20:
                        adjustments.append(context.strip())
                    break

        return adjustments[:20]  # 限制数量


def main():
    print("=" * 70)
    print("梦幻西游定期维护公告采集")
    print("=" * 70)

    scraper = MHXYMaintenanceScraper()

    # 重要维护公告URL列表
    maintenance_urls = [
        # 2023年
        ("2023年6月", "https://xyq.163.com/wh/20230626/4907_1095030.html"),
        ("2023年7月", "https://xyq.163.com/wh/20230717/4907_1099023.html"),
        ("2023年12月", "https://xyq.163.com/wh/20231225/4907_1128031.html"),

        # 2022年
        ("2022年4月门派调整", "https://xyq.163.com/news/20220426/4905_1014565.html"),
        ("2022年10月门派", "http://xyq.163.com/20221012/4999_1046571.html"),

        # 2024年
        ("2024年4月门派调整", "https://xyq.163.com/news/20240422/4999_1150946.html"),
        ("2024年10月门派", "https://xyq.163.com/news/20241017/4999_1187508.html"),

        # 2025年
        ("2025年4月门派", "https://xyq.163.com/wh/20250418/4907_1228406.html"),

        # 召唤兽相关
        ("2024超级技能", "https://xyq.163.com/news/20240520/4999_1156134.html"),
        ("2023召唤兽赐福", "https://xyq.163.com/news/20231218/4905_666865.html"),
        ("2022召唤兽", "https://xyq.163.com/org_bg/20221220/15743_1058400.html"),
        ("2020灵宝", "https://xyq.163.com/org_bg/20200728/15743_895016.html"),
        ("2019灵宝系统", "https://xyq.163.com/20191016/4999_841018.html"),
        ("2018召唤兽", "https://xyq.163.com/20181029/4999_782197.html"),
        ("2017神器谱", "https://xyq.163.com/2017/sq/"),
        ("2014召唤兽进阶", "https://xyq.163.com/m/introduce/20231107/23210_647092.html"),
    ]

    all_data = {
        "source": "梦幻西游官方论坛维护公告",
        "generated_at": datetime.now().isoformat(),
        "maintenance": []
    }

    success = 0
    for name, url in maintenance_urls:
        print(f"\n获取: {name}")
        result = scraper.parse_maintenance_page(url)
        if result and (result.get('content') or result.get('adjustments')):
            print(f"  标题: {result.get('title', '')[:50]}")
            print(f"  日期: {result.get('date', '')}")
            print(f"  内容长度: {len(result.get('content', ''))} 字符")
            print(f"  调整条目: {len(result.get('adjustments', []))} 条")
            all_data["maintenance"].append(result)
            success += 1
        else:
            print(f"  获取失败或无内容!")
        time.sleep(0.5)

    # 保存
    output_file = Path(__file__).parent / "docs" / "mhxy_maintenance.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print(f"\n" + "=" * 70)
    print(f"采集完成! 成功: {success} 条")
    print(f"保存到: {output_file}")
    print("=" * 70)


if __name__ == "__main__":
    main()
