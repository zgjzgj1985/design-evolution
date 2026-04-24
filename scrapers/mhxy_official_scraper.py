"""
梦幻西游官方论坛门派调整数据采集器

数据来源：https://xyq.163.com/update/
支持获取历史门派调整数据，包括：
- 门派技能调整
- 门派经脉调整
- 召唤兽调整
- 法宝/灵宝调整
"""

import re
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import urllib.request
import urllib.parse
import hashlib

# 官方论坛URL模板
BASE_URL = "https://xyq.163.com"
UPDATE_LIST_URL = "https://so.xyq.163.com/search?qs=%E9%97%A8%E6%B4%BE%E8%B0%83%E6%95%B4"

# 已知的门派调整汇总页
SUMMARY_PAGES = {
    "2024": "https://xyq.163.com/mptz/index.html",
    "2023": "https://xyq.163.com/2023/mptz/index.html",
    "2022": "https://xyq.163.com/2022/mptz/index.html",
    "2021": "https://xyq.163.com/2021/mptz/index.html",
}


class MHXYOfficialScraper:
    """梦幻西游官方论坛数据采集器"""
    
    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path(__file__).parent.parent / "data" / "mhxy"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache = {}  # 简单缓存
        
    def fetch_url(self, url: str, encoding: str = 'utf-8') -> Optional[str]:
        """获取URL内容"""
        # 检查缓存
        cache_key = hashlib.md5(url.encode()).hexdigest()
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        try:
            req = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                }
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                content = response.read()
                # 检测编码
                if response.headers.get_content_charset():
                    encoding = response.headers.get_content_charset()
                try:
                    decoded = content.decode(encoding)
                except:
                    decoded = content.decode('gbk', errors='replace')
                
                self.cache[cache_key] = decoded
                return decoded
        except Exception as e:
            print(f"获取失败 {url}: {e}")
            return None
    
    def parse_patch_detail_page_from_url(self, url: str) -> Optional[Dict[str, Any]]:
        """从URL解析门派调整详情"""
        html = self.fetch_url(url)
        if not html:
            return None
        
        result = {
            'url': url,
            'title': '',
            'date': '',
            'sections': [],
            'content': ''
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
        
        # 清理HTML获取纯文本
        text = self._extract_text(html)
        result['content'] = text
        
        # 提取门派名称
        mhxy_sects = [
            '大唐官府', '大唐', '化生寺', '化生', '女儿村', '女儿', '方寸山', '方寸',
            '神木林', '神木', '天机城', '天宫', '普陀山', '普陀', '龙宫', '五庄观',
            '五庄', '凌波城', '凌波', '花果山', '花果', '狮驼岭', '狮驼', '魔王寨',
            '魔王', '阴曹地府', '地府', '盘丝洞', '盘丝', '无底洞', '无底', '女魃墓',
            '女魃', '东海渊', '东海', '九黎城', '九黎', '弥勒山', '弥勒'
        ]
        
        found_sects = set()
        for sect in mhxy_sects:
            if sect in text:
                found_sects.add(sect)
        
        result['sections'] = list(found_sects)
        
        return result
    
    def _extract_text(self, html: str) -> str:
        """从HTML中提取纯文本"""
        # 移除script和style
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        
        # 处理常见的HTML实体
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&#39;', "'")
        text = text.replace('&quot;', '"')
        
        # 移除所有HTML标签
        text = re.sub(r'<[^>]+>', '\n', text)
        
        # 清理多余空白
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r' +\n', '\n', text)
        text = text.strip()
        
        return text
    
    def get_patch_urls_by_year(self, year: int) -> List[str]:
        """获取指定年份的门派调整URL列表"""
        # 网易论坛使用不同的URL结构
        # 需要通过搜索或直接访问更新列表页
        
        # 常见门派调整页面的URL模式
        urls = []
        
        # 按月份遍历
        for month in range(1, 13):
            if year == 2026 and month > 4:
                break
            if year == datetime.now().year and month > datetime.now().month:
                break
                
            month_str = f"{month:02d}"
            
            # 尝试直接访问更新列表
            # 格式: https://xyq.163.com/update/YYYY/MM/
            test_url = f"https://xyq.163.com/update/{year}/{month_str}/"
            
            html = self.fetch_url(test_url)
            if html and '门派' in html:
                # 提取相关URL
                pattern = rf'href="(/update/{year}/{month_str}/\d+_\d+\.html)"'
                matches = re.findall(pattern, html)
                for url in matches:
                    if '门派' in self.fetch_url(BASE_URL + url, 'utf-8') or '技能' in self.fetch_url(BASE_URL + url, 'utf-8') or '经脉' in self.fetch_url(BASE_URL + url, 'utf-8') or '调整' in self.fetch_url(BASE_URL + url, 'utf-8'):
                        urls.append(BASE_URL + url)
                    time.sleep(0.5)
        
        return list(set(urls))
    
    def scrape_all_history(self, start_year: int = 2009, end_year: int = None) -> List[Dict[str, Any]]:
        """抓取所有历史数据"""
        if end_year is None:
            end_year = datetime.now().year
        
        all_patches = []
        
        print(f"开始抓取 {start_year}-{end_year} 年的门派调整数据...")
        
        for year in range(start_year, end_year + 1):
            print(f"\n正在抓取 {year} 年数据...")
            
            # 通过搜索引擎获取该年的门派调整链接
            search_url = f"https://so.xyq.163.com/search?qs={urllib.parse.quote('门派调整')}&year={year}"
            html = self.fetch_url(search_url)
            
            if html:
                patches = self.parse_patch_list_page(html)
                for patch in patches:
                    # 过滤年份
                    if patch['date'].startswith(str(year)):
                        print(f"  发现: {patch['title']} ({patch['date']})")
                        all_patches.append(patch)
                        
                        # 获取详情
                        time.sleep(0.5)
            
            time.sleep(1)
        
        return all_patches
    
    def scrape_official_updates(self) -> Dict[str, Any]:
        """抓取官方更新页面"""
        # 门派调整汇总页
        summary_pages = [
            ("2024", "https://xyq.163.com/mptz/index.html"),
            ("2025", "https://xyq.163.com/2025/mptz/index.html"),
            ("2026", "https://xyq.163.com/2026/mptz/index.html"),
        ]
        
        results = {}
        for year, url in summary_pages:
            print(f"\n正在抓取 {year}年门派调整汇总...")
            html = self.fetch_url(url)
            if html:
                results[year] = {
                    'url': url,
                    'content': html,
                    'links': self._extract_links(html)
                }
                print(f"  获取成功，找到 {len(results[year]['links'])} 个链接")
            time.sleep(1)
        
        return results
    
    def _extract_links(self, html: str) -> List[Dict[str, str]]:
        """从HTML中提取链接"""
        links = []
        pattern = r'<a[^>]+href="([^"]+)"[^>]*>([^<]+)</a>'
        matches = re.findall(pattern, html)
        
        for url, title in matches:
            if '/update/' in url or '/hot/' in url or '/org_bg/' in url:
                links.append({
                    'url': url if url.startswith('http') else BASE_URL + url,
                    'title': title.strip()
                })
        
        return links


def main():
    """主函数"""
    scraper = MHXYOfficialScraper()
    
    print("=" * 50)
    print("梦幻西游官方论坛门派调整数据采集器")
    print("=" * 50)
    
    # 测试获取单个页面
    test_url = "https://xyq.163.com/update/2009/1/6/5092_196271.html"
    print(f"\n测试获取: {test_url}")
    
    html = scraper.fetch_url(test_url)
    if html:
        result = scraper.parse_patch_detail_page(html, test_url)
        print(f"解析成功!")
        print(f"  包含门派: {result['sections']}")
        print(f"  内容预览: {result['raw_content'][:200]}...")
    
    # 抓取官方汇总页
    print("\n\n抓取官方门派调整汇总页...")
    results = scraper.scrape_official_updates()
    
    # 保存结果
    output_file = Path(__file__).parent.parent / "docs" / "mhxy_official_updates.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n数据已保存到: {output_file}")


if __name__ == "__main__":
    main()
