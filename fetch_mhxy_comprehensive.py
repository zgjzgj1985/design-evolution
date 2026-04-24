#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
梦幻西游全面数据采集器

采集官方论坛各类更新数据：
1. 门派调整
2. 资料片
3. 系统调整
4. 玩法更新
"""

import re
import json
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import urllib.request
import hashlib

# 官方论坛URL
BASE_URL = "https://xyq.163.com"


class MHXYComprehensiveScraper:
    """梦幻西游综合数据采集器"""

    def __init__(self):
        self.cache = {}

    def fetch_url(self, url: str) -> Optional[str]:
        """获取URL内容"""
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
        except Exception as e:
            print(f"  获取失败: {e}")
            return None

    def parse_announcement(self, url: str) -> Optional[Dict[str, Any]]:
        """解析维护公告页面"""
        html = self.fetch_url(url)
        if not html:
            return None

        result = {
            'url': url,
            'title': '',
            'date': '',
            'content': '',
            'type': self._classify_content(html),
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

        return result

    def _classify_content(self, html: str) -> str:
        """根据内容分类"""
        title_content = html[:2000].lower()

        if '门派调整' in html:
            return '门派调整'
        elif '资料片' in html or '重磅来袭' in html:
            return '资料片'
        elif '系统调整' in html or '玩法调整' in html:
            return '系统调整'
        elif '召唤兽' in html and ('技能' in html or '调整' in html):
            return '召唤兽调整'
        elif '维护公告' in html:
            return '维护公告'
        elif '赛事' in html or '比武' in html:
            return '赛事'
        else:
            return '其他'

    def _extract_text(self, html: str) -> str:
        """从HTML中提取纯文本"""
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        text = text.replace('&nbsp;', ' ').replace('&amp;', '&')
        text = re.sub(r'<[^>]+>', '\n', text)
        text = re.sub(r'\n+', '\n', text)
        return text.strip()[:8000]  # 限制长度


def main():
    """主函数"""
    print("=" * 60)
    print("梦幻西游综合数据采集器")
    print("=" * 60)

    scraper = MHXYComprehensiveScraper()

    # 各类重要URL（按类型分类）
    important_urls = {
        # 资料片
        "资料片": [
            ("2024寒假", "https://xyq.163.com/2024/hjzlp/"),
            ("2024千变万化", "https://xyq.163.com/wh/20241223/4907_1201705.html"),
            ("2024寒假内容", "https://xyq.163.com/news/20240520/4999_1156134.html"),
        ],
        # 系统调整
        "系统调整": [
            ("2024锁系统", "https://xyq.163.com/news/20240520/4999_1156134.html"),
            ("2023天命副本", "https://xyq.163.com/wh/20241129/4907_1196906.html"),
        ],
        # 赛事
        "赛事": [
            ("武神坛", "https://xyq.163.com/news/20241017/4999_1187508.html"),
        ],
    }

    all_data = {
        "source": "梦幻西游官方论坛",
        "generated_at": datetime.now().isoformat(),
        "announcements": []
    }

    for category, urls in important_urls.items():
        print(f"\n{'='*40}")
        print(f"采集 {category} 数据...")
        print(f"{'='*40}")

        for name, url in urls:
            print(f"\n正在获取: {name}")
            print(f"  URL: {url}")

            result = scraper.parse_announcement(url)
            if result:
                print(f"  标题: {result.get('title', 'N/A')[:50]}")
                print(f"  日期: {result.get('date', 'N/A')}")
                print(f"  类型: {result.get('type', 'N/A')}")
                print(f"  内容长度: {len(result.get('content', ''))} 字符")
                all_data["announcements"].append(result)
            else:
                print(f"  获取失败!")

            time.sleep(1)

    # 保存结果
    output_file = Path(__file__).parent / "docs" / "mhxy_comprehensive_updates.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print(f"\n数据已保存到: {output_file}")
    print(f"\n总计采集: {len(all_data['announcements'])} 条公告")


if __name__ == "__main__":
    main()
