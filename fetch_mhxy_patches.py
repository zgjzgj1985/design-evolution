#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
梦幻西游门派调整数据采集主脚本

从官方论坛抓取多年门派调整数据并保存到本地文件
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime

# 配置UTF-8输出
sys.stdout.reconfigure(encoding='utf-8')

from scrapers.mhxy_official_scraper import MHXYOfficialScraper, SUMMARY_PAGES


def main():
    """主函数"""
    print("=" * 60)
    print("梦幻西游门派调整数据采集器")
    print("=" * 60)
    
    scraper = MHXYOfficialScraper()
    
    # 已知的门派调整链接（按年份分类）
    # 格式: /news/YYYYMMDD/4999_XXXXX.html (官方新闻页)
    known_patches = {
        # 2026年
        "2026": [
            "https://xyq.163.com/org_bg/20260416/15743_1296385.html",  # 4月门派调整
        ],
        # 2025年
        "2025": [
            "https://xyq.163.com/wh/20250418/4907_1228406.html",  # 4月门派调整维护公告
            "https://xyq.163.com/m/news/20251017/4905_1265214.html",  # 10月门派调整
        ],
        # 2024年
        "2024": [
            "https://xyq.163.com/news/20241017/4999_1187508.html",  # 10月门派调整
            "https://xyq.163.com/news/20240422/4999_1150946.html",  # 4月门派调整
        ],
        # 2023年
        "2023": [
            "https://xyq.163.com/news/20231008/4999_1113474.html",  # 10月门派调整
            "http://xyq.163.com/20230402/4999_1081163.html",        # 4月门派调整
        ],
        # 2022年
        "2022": [
            "http://xyq.163.com/20221012/4999_1046571.html",        # 10月门派调整
            "https://xyq.163.com/news/20220426/4905_1014565.html",  # 4月门派调整
        ],
        # 2021年
        "2021": [
            "https://xyq.163.com/20211015/4999_979359.html",  # 10月门派调整
            "http://xyq.163.com/20210409/4999_941345.html",   # 4月门派调整
        ],
        # 2020年
        "2020": [
            "http://xyq.163.com/20200331/4999_872401.html",  # 4月门派调整
            "https://xyq.163.com/20201013/4999_909520.html",  # 10月门派调整
        ],
        # 2019年
        "2019": [
            "http://xyq.163.com/20191016/4999_841018.html",  # 10月门派调整
            "http://xyq.163.com/20190418/4999_809426.html",  # 4月门派调整
        ],
        # 2018年
        "2018": [
            "https://xyq.163.com/20180409/4999_748562.html",  # 4月门派调整
            "http://xyq.163.com/20181029/4999_782197.html",   # 10月门派调整
        ],
        # 2017年
        "2017": [
            "https://xyq.163.com/20171023/4999_718949.html",  # 10月门派调整
            "http://xyq.163.com/20170420/4999_684548.html",   # 4月门派调整
        ],
        # 2016年
        "2016": [
            "http://xyq.163.com/2016/09/26/4999_644417.html",  # 9月门派调整
            "https://xyq.163.com/2016/04/20/4999_620000.html",  # 4月门派调整
        ],
        # 早期
        "2015": [
            "https://xyq.163.com/2015/10/16/4999_574504.html",  # 10月奇经八脉调整
        ],
        "2014": [
            "https://xyq.163.com/2014/5/16/4999_439289.html",  # 5月门派技能调整
        ],
        "2013": [
            "http://xyq.163.com/2013/10/21/4999_399541.html",  # 10月门派调整
        ],
        "2009": [
            "https://xyq.163.com/update/2009/1/6/5092_196271.html",   # 2009年1月
        ],
    }
    
    all_data = {
        "source": "梦幻西游官方论坛",
        "generated_at": datetime.now().isoformat(),
        "patches": []
    }
    
    # 抓取每个年份的数据
    for year, urls in sorted(known_patches.items()):
        print(f"\n{'='*40}")
        print(f"抓取 {year} 年数据...")
        print(f"{'='*40}")
        
        year_data = {
            "year": year,
            "patches": []
        }
        
        for url in urls:
            print(f"\n正在获取: {url}")
            
            result = scraper.parse_patch_detail_page_from_url(url)
            if result:
                print(f"  标题: {result.get('title', 'N/A')}")
                print(f"  日期: {result.get('date', 'N/A')}")
                print(f"  涉及门派: {', '.join(result.get('sections', [])[:5])}...")
                
                year_data["patches"].append(result)
                all_data["patches"].append(result)
            else:
                print(f"  获取失败!")
            
            time.sleep(1)  # 避免请求过快
        
        # 保存年份数据
        year_file = Path(__file__).parent / "data" / "mhxy" / f"patches_{year}.json"
        year_file.parent.mkdir(parents=True, exist_ok=True)
        with open(year_file, 'w', encoding='utf-8') as f:
            json.dump(year_data, f, ensure_ascii=False, indent=2)
        print(f"\n{year}年数据已保存到: {year_file}")
    
    # 保存全部数据
    all_file = Path(__file__).parent / "docs" / "mhxy_patches_history.json"
    all_file.parent.mkdir(parents=True, exist_ok=True)
    with open(all_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"\n全部数据已保存到: {all_file}")
    
    # 统计
    print(f"\n{'='*60}")
    print("采集完成!")
    print(f"总采集: {len(all_data['patches'])} 条门派调整")
    years = {}
    for p in all_data['patches']:
        year = p.get('date', '')[:4] if p.get('date') else 'unknown'
        years[year] = years.get(year, 0) + 1
    print("各年份统计:")
    for y, c in sorted(years.items()):
        print(f"  {y}: {c} 条")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
