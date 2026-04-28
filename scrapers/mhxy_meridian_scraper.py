"""
梦幻西游经脉/奇经八脉调整专项采集器

数据来源：https://xyq.163.com/{year}/mptz/
目标：采集经脉系统的历史调整原始内容，填补 mhxy_history.py 中
     MHXY_CLASS_ADJUSTMENTS 只有摘要、缺少原始文本的缺口。

输出文件：docs/mhxy_meridian_history.json
"""

import re
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


BASE_URL = "https://xyq.163.com"

# 经脉相关关键词
MERIDIAN_KEYWORDS = [
    "经脉", "奇经八脉", "乾元丹", "乾元", "镶嵌", "镶嵌位",
    "星辉石", "星辉", "经脉点", "经脉路线", "经脉技能",
    "飞升", "渡劫", "师门技能", "飞升技能", "130技能",
]


def _extract_text(html: str) -> str:
    """从 HTML 中提取纯文本"""
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
    text = text.replace('&nbsp;', ' ').replace('&amp;', '&')
    text = text.replace('&lt;', '<').replace('&gt;', '>')
    text = text.replace('&#39;', "'").replace('&quot;', '"')
    text = re.sub(r'<[^>]+>', '\n', text)
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r' +\n', '\n', text)
    return text.strip()


class MHXYMeridianScraper:
    """经脉/奇经八脉调整数据采集器"""

    def __init__(self):
        self.cache: Dict[str, str] = {}

    def fetch_url(self, url: str) -> Optional[str]:
        """带缓存的 URL 获取，重试 2 次"""
        cache_key = hash(url)
        if cache_key in self.cache:
            return self.cache[cache_key]

        for attempt in range(3):
            try:
                req = Request(
                    url,
                    headers={
                        'User-Agent': (
                            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                            'AppleWebKit/537.36 (KHTML, like Gecko) '
                            'Chrome/120.0.0.0 Safari/537.36'
                        ),
                        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                    }
                )
                with urlopen(req, timeout=20) as resp:
                    content = resp.read()
                    encoding = resp.headers.get_content_charset() or 'utf-8'
                    try:
                        decoded = content.decode(encoding)
                    except Exception:
                        decoded = content.decode('gbk', errors='replace')
                    self.cache[cache_key] = decoded
                    return decoded
            except (URLError, HTTPError) as e:
                if attempt < 2:
                    time.sleep(2 ** attempt)
                    continue
                print(f"  获取失败 {url}: {e}")
                return None
        return None

    def _is_meridian_page(self, text: str) -> bool:
        """判断页面内容是否与经脉相关"""
        for kw in MERIDIAN_KEYWORDS:
            if kw in text:
                return True
        return False

    def _extract_links(self, html: str) -> List[Dict[str, str]]:
        """从 HTML 中提取站内链接"""
        links = []
        for m in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>([^<]+)</a>', html):
            href = m.group(1)
            title = m.group(2).strip()
            if '/update/' in href or '/wh/' in href or '/news/' in href:
                full_url = href if href.startswith('http') else BASE_URL + href
                links.append({'url': full_url, 'title': title})
        return links

    def _extract_date(self, html: str, fallback_url: str = "") -> str:
        """从页面或 URL 中提取日期"""
        m = re.search(r'(\d{4})[年-](\d{1,2})[月-](\d{1,2})', html)
        if m:
            return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
        m = re.search(r'/(\d{4})(\d{2})(\d{2})/', fallback_url)
        if m:
            return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
        return ""

    def _extract_title(self, html: str) -> str:
        """从页面提取标题"""
        m = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
        if not m:
            m = re.search(r'<title>([^<]+)</title>', html)
        if m:
            return m.group(1).strip()
        return ""

    def parse_patch_page(self, url: str) -> Optional[Dict[str, Any]]:
        """解析门派调整/维护公告详情页，返回经脉相关内容"""
        html = self.fetch_url(url)
        if not html:
            return None

        text = _extract_text(html)
        if not self._is_meridian_page(text):
            return None

        result = {
            'url': url,
            'title': self._extract_title(html),
            'date': self._extract_date(html, url),
            'content': text[:8000],
            'update_type': '经脉调整',
            'keywords': [kw for kw in MERIDIAN_KEYWORDS if kw in text],
        }

        return result

    def _scrape_index_page(self, year: int) -> List[Dict[str, str]]:
        """抓取某年的门派调整汇总索引页，返回所有链接"""
        urls = []
        for url_pattern in [
            f"https://xyq.163.com/{year}/mptz/",
            f"https://xyq.163.com/{year}/mptz/index.html",
        ]:
            html = self.fetch_url(url_pattern)
            if html and '门派' in html:
                for link in self._extract_links(html):
                    urls.append(link)
                break
        return urls

    def _scrape_update_list(self, year: int, month: int) -> List[Dict[str, str]]:
        """抓取某年某月的更新列表页"""
        month_str = f"{month:02d}"
        urls = []
        for page in range(1, 5):
            list_url = f"https://xyq.163.com/update/{year}/{month_str}/index_{page}.html"
            html = self.fetch_url(list_url)
            if not html or '没有' in html or '不存在' in html:
                break
            for link in self._extract_links(html):
                urls.append(link)
            time.sleep(0.3)
        return urls

    def scrape_year(self, year: int) -> List[Dict[str, Any]]:
        """采集指定年份的经脉调整数据"""
        results: List[Dict[str, Any]] = []
        seen: set = set()

        print(f"\n  抓取 {year} 年索引页...")
        index_links = self._scrape_index_page(year)
        print(f"  索引页找到 {len(index_links)} 个链接")

        for link in index_links:
            url = link['url']
            if url in seen:
                continue
            seen.add(url)
            print(f"  -> {link['title'][:30]}")
            item = self.parse_patch_page(url)
            if item:
                results.append(item)
            time.sleep(0.5)

        current_month = datetime.now().month if year == datetime.now().year else 12
        for month in range(1, current_month + 1):
            print(f"\n  抓取 {year}-{month:02d} 月更新列表...")
            list_links = self._scrape_update_list(year, month)
            print(f"  列表找到 {len(list_links)} 个链接")
            for link in list_links:
                url = link['url']
                if url in seen:
                    continue
                seen.add(url)
                print(f"  -> {link['title'][:30]}")
                item = self.parse_patch_page(url)
                if item:
                    results.append(item)
                time.sleep(0.5)

        return results

    def scrape_range(self, start_year: int = 2007, end_year: int = None) -> List[Dict[str, Any]]:
        """
        采集指定年份范围的经脉调整数据。

        2007 年是经脉系统上线年份，2009 年开始经脉调整成为常规更新内容。
        """
        if end_year is None:
            end_year = datetime.now().year

        all_results: List[Dict[str, Any]] = []
        for year in range(start_year, end_year + 1):
            if year == 2026 and datetime.now().month < 4:
                pass
            elif year > datetime.now().year:
                continue

            print(f"\n{'=' * 50}")
            print(f"采集 {year} 年经脉调整数据")
            print(f"{'=' * 50}")
            results = self.scrape_year(year)
            all_results.extend(results)
            print(f"  本年有效经脉记录: {len(results)} 条")

        return all_results


def main():
    """主函数：采集经脉调整数据并保存"""
    import urllib.request

    scraper = MHXYMeridianScraper()

    print("=" * 60)
    print("梦幻西游经脉/奇经八脉调整数据采集")
    print("=" * 60)

    # 采集 2009-当前年份的经脉调整数据
    results = scraper.scrape_range(start_year=2009)

    output: Dict[str, Any] = {
        "source": "梦幻西游官方论坛",
        "fetched_at": datetime.now().isoformat(),
        "total": len(results),
        "meridians": results,
    }

    output_file = Path(__file__).parent.parent / "docs" / "mhxy_meridian_history.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n采集完成，共 {len(results)} 条经脉相关记录")
    print(f"保存到: {output_file}")


if __name__ == "__main__":
    main()
