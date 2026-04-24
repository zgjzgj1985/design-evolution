"""
梦幻西游Like游戏网页数据爬虫

数据来源：
1. NGA论坛 - 梦幻西游版块有完整的更新公告历史
2. 叶子猪 - 游戏攻略和数据网站
3. 官方公告 - 官方更新页面

使用方法：
    python -m scrapers.mhxy_scraper
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path


# ============================================================
# 配置
# ============================================================

# 请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

# 请求间隔（秒）
REQUEST_DELAY = 1.0

# NGA 梦幻西游版块
NGA_MHXY_BOARD_URL = "https://nga.178.com/thread.php?fid=-7&lite=js"

# 叶子猪梦幻西游公告
YEZIZHU_URL = "https://www.yezizhu.com/news/"


# ============================================================
# 网页爬虫基类
# ============================================================

class BaseScraper:
    """网页爬虫基类"""

    def __init__(self, delay: float = REQUEST_DELAY):
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def _get(self, url: str, retries: int = 3) -> Optional[str]:
        """带重试的GET请求"""
        for i in range(retries):
            try:
                time.sleep(self.delay)
                resp = self.session.get(url, timeout=30)
                resp.raise_for_status()
                resp.encoding = resp.apparent_encoding or 'utf-8'
                return resp.text
            except Exception as e:
                print(f"请求失败 ({i+1}/{retries}): {url} - {e}")
                time.sleep(self.delay * 2)
        return None

    def _parse_date(self, date_str: str) -> str:
        """解析日期字符串"""
        # 常见格式：2024-01-15、2024年1月15日、1月15日等
        patterns = [
            (r'(\d{4})年(\d{1,2})月(\d{1,2})日', '%Y年%m月%d日'),
            (r'(\d{4})-(\d{1,2})-(\d{1,2})', '%Y-%m-%d'),
            (r'(\d{1,2})月(\d{1,2})日', None),  # 需要补充年份
        ]

        for pattern, fmt in patterns:
            match = re.search(pattern, date_str)
            if match:
                if fmt:
                    try:
                        return datetime.strptime(date_str[:10], '%Y-%m-%d').strftime('%Y-%m-%d')
                    except:
                        pass
                else:
                    # 处理只有月日的情况，假设是今年
                    month, day = match.groups()
                    return f"{datetime.now().year}-{int(month):02d}-{int(day):02d}"

        return datetime.now().strftime('%Y-%m-%d')


# ============================================================
# NGA 爬虫
# ============================================================

class NGAMHXYScraper(BaseScraper):
    """NGA梦幻西游版块爬虫"""

    def __init__(self, delay: float = REQUEST_DELAY):
        super().__init__(delay)
        self.base_url = "https://nga.178.com/thread.php"

    def get_thread_list(self, page: int = 1, page_size: int = 40) -> List[Dict]:
        """获取帖子列表"""
        params = {
            "fid": "-7",  # 梦幻西游版块
            "page": page,
            "order_by": "postdate",
            "ascdesc": "desc",
        }

        url = f"{self.base_url}?fid=-7&page={page}"
        html = self._get(url)

        if not html:
            return []

        soup = BeautifulSoup(html, "lxml")
        threads = []

        # NGA帖子列表解析
        # 注意：NGA使用JavaScript渲染，直接解析HTML可能不完整
        # 这里提供一个基础解析，实际使用时可能需要API或其他方式

        # 查找帖子条目
        for item in soup.select(".topic-item, .row, tr[class*='topic']"):
            try:
                title_elem = item.select_one("a[class*='subject'], .subject a, td.subject a")
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)
                href = title_elem.get("href", "")

                # 提取tid
                tid_match = re.search(r'tid=(\d+)', href)
                if not tid_match:
                    continue
                tid = tid_match.group(1)

                # 提取日期
                date_elem = item.select_one(".postdate, .date, td:last-child")
                date_str = date_elem.get_text(strip=True) if date_elem else ""
                date = self._parse_date(date_str)

                threads.append({
                    "tid": tid,
                    "title": title,
                    "url": f"https://nga.178.com/read.php?tid={tid}",
                    "date": date,
                })
            except Exception as e:
                continue

        return threads

    def get_thread_content(self, tid: str) -> Optional[Dict]:
        """获取帖子内容"""
        url = f"https://nga.178.com/read.php?tid={tid}"
        html = self._get(url)

        if not html:
            return None

        soup = BeautifulSoup(html, "lxml")

        # 提取标题
        title_elem = soup.select_one("h1.topic-title, .topic-title, h1")
        title = title_elem.get_text(strip=True) if title_elem else ""

        # 提取正文
        content_elem = soup.select_one(".postcontent, .post-content, .content")
        content = content_elem.get_text(strip=True, separator="\n") if content_elem else ""

        # 提取楼层
        posts = []
        for floor in soup.select(".post-item, .post"):
            try:
                floor_num = floor.select_one(".floor-num, .louzhu")
                floor_text = floor_num.get_text(strip=True) if floor_num else "1"

                floor_content = floor.select_one(".postcontent, .post-content")
                floor_text = floor_content.get_text(strip=True, separator="\n") if floor_content else ""

                posts.append({
                    "floor": floor_text,
                    "content": floor_text,
                })
            except:
                continue

        return {
            "tid": tid,
            "title": title,
            "content": content,
            "posts": posts,
            "url": url,
        }


# ============================================================
# 叶子猪爬虫
# ============================================================

class YezizhuScraper(BaseScraper):
    """叶子猪梦幻西游爬虫"""

    def __init__(self, delay: float = REQUEST_DELAY):
        super().__init__(delay)
        self.base_url = "https://www.yezizhu.com"

    def get_news_list(self, page: int = 1) -> List[Dict]:
        """获取新闻列表"""
        url = f"{self.base_url}/news/list-{page}.html"
        html = self._get(url)

        if not html:
            return []

        soup = BeautifulSoup(html, "lxml")
        news_list = []

        for item in soup.select(".news-list li, .article-list li, .list-item"):
            try:
                title_elem = item.select_one("a")
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)
                href = title_elem.get("href", "")

                # 补充完整URL
                if href and not href.startswith("http"):
                    href = self.base_url + href

                # 提取日期
                date_elem = item.select_one(".date, .time, span")
                date_str = date_elem.get_text(strip=True) if date_elem else ""
                date = self._parse_date(date_str)

                news_list.append({
                    "title": title,
                    "url": href,
                    "date": date,
                })
            except Exception as e:
                continue

        return news_list

    def get_article_content(self, url: str) -> Optional[str]:
        """获取文章内容"""
        html = self._get(url)

        if not html:
            return None

        soup = BeautifulSoup(html, "lxml")

        # 提取正文
        content_elem = soup.select_one(".article-content, .content, .post-content")
        content = content_elem.get_text(strip=True, separator="\n") if content_elem else ""

        return content


# ============================================================
# 梦幻西游官方公告爬虫
# ============================================================

class MHXYOfficialScraper(BaseScraper):
    """梦幻西游官方公告爬虫"""

    def __init__(self, delay: float = REQUEST_DELAY):
        super().__init__(delay)
        # 梦幻西游没有公开的API，这里使用游戏干线等第三方数据源

    def get_update_announcements(self, year: int = None) -> List[Dict]:
        """获取更新公告"""
        # 尝试从游戏干线获取
        url = "https://xyq.163.com/news/"

        html = self._get(url)
        if not html:
            return []

        soup = BeautifulSoup(html, "lxml")
        announcements = []

        for item in soup.select(".news-list li, .update-list li"):
            try:
                title_elem = item.select_one("a")
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)
                href = title_elem.get("href", "")

                # 过滤更新公告
                if not any(kw in title for kw in ["更新", "维护", "公告", "调整", "技能", "门派"]):
                    continue

                date_elem = item.select_one(".date, .time")
                date_str = date_elem.get_text(strip=True) if date_elem else ""
                date = self._parse_date(date_str)

                announcements.append({
                    "title": title,
                    "url": href,
                    "date": date,
                    "type": "official",
                })
            except:
                continue

        return announcements


# ============================================================
# 工具函数
# ============================================================

def scrape_mhxy_updates(max_pages: int = 10) -> List[Dict]:
    """
    抓取梦幻西游更新公告

    从多个来源抓取数据
    """
    all_updates = []

    # 1. 叶子猪新闻
    print("正在从叶子猪抓取数据...")
    scraper = YezizhuScraper()
    for page in range(1, min(max_pages + 1, 20)):
        news_list = scraper.get_news_list(page)
        if not news_list:
            break
        all_updates.extend(news_list)
        print(f"  第{page}页：获取 {len(news_list)} 条")

    # 2. NGA帖子
    print("正在从NGA抓取数据...")
    nga_scraper = NGAMHXYScraper()
    for page in range(1, min(max_pages + 1, 10)):
        threads = nga_scraper.get_thread_list(page)
        if not threads:
            break
        all_updates.extend(threads)
        print(f"  第{page}页：获取 {len(threads)} 条")

    # 3. 去重
    seen_urls = set()
    unique_updates = []
    for update in all_updates:
        url = update.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_updates.append(update)

    # 4. 按日期排序
    unique_updates.sort(key=lambda x: x.get("date", ""), reverse=True)

    print(f"\n共获取 {len(unique_updates)} 条更新公告")

    return unique_updates


def save_updates_to_json(updates: List[Dict], output_file: str = "data/mhxy/updates_raw.json"):
    """保存抓取的更新到JSON文件"""
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    data = {
        "source": "web_scraping",
        "fetched_at": datetime.now().isoformat(),
        "total": len(updates),
        "updates": updates,
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"已保存到 {output_file}")
    return output_file


# ============================================================
# 主函数
# ============================================================

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="梦幻西游数据爬虫")
    parser.add_argument("--pages", type=int, default=5, help="抓取页数")
    parser.add_argument("--output", type=str, default="data/mhxy/updates_raw.json", help="输出文件")

    args = parser.parse_args()

    print("=" * 60)
    print("梦幻西游Like游戏数据爬虫")
    print("=" * 60)
    print()

    # 抓取数据
    updates = scrape_mhxy_updates(max_pages=args.pages)

    if updates:
        # 保存数据
        save_updates_to_json(updates, args.output)
        print(f"\n抓取完成！共获取 {len(updates)} 条更新公告")
    else:
        print("\n未能获取数据，请检查网络连接或数据源")


if __name__ == "__main__":
    main()
