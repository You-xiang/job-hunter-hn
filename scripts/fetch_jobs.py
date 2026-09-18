# -*- coding: utf-8 -*-
"""
招聘信息检索脚本 - 长沙/娄底
使用多个招聘网站 API 和网页抓取
"""
import os
import re
import json
import datetime
import requests
from bs4 import BeautifulSoup

# 配置
CITIES = ["长沙", "娄底"]
EDUCATION = "大专"
MIN_SALARY = 3000
MAX_SALARY = 50000

# 黑中介关键词
BLACKLIST_KEYWORDS = [
    "刷单", "打字", "手工", "兼职", "在家工作", "日结",
    "月入过万", "保底", "代理", "加盟", "微商"
]

# 可信招聘网站
TRUSTED_SITES = [
    "zhipin.com", "zhaopin.com", "51job.com", "liepin.com",
    "lagou.com", "kanzhun.com", "jobui.com", "ganji.com", "58.com"
]

def fetch_from_zhipin(city):
    """从 Boss 直聘获取"""
    jobs = []
    try:
        url = f"https://www.zhipin.com/web/geek/job?query=&city=101250100"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            # 简单解析（实际可能需要更复杂的处理）
            soup = BeautifulSoup(resp.text, 'html.parser')
            job_cards = soup.find_all('div', class_='job-card-wrapper')[:10]
            for card in job_cards:
                title_elem = card.find('span', class_='job-name')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    link = f"https://www.zhipin.com{card.find('a')['href']}"
                    jobs.append({
                        "title": title,
                        "url": link,
                        "city": city,
                        "source": "Boss直聘"
                    })
    except Exception as e:
        print(f"Boss直聘获取失败: {e}")
    return jobs

def fetch_from_zhaopin(city):
    """从智联招聘获取"""
    jobs = []
    try:
        url = f"https://sou.zhaopin.com/?jl=681&kw=&p=1"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            job_items = soup.find_all('div', class_='joblist-box__item')[:10]
            for item in job_items:
                title_elem = item.find('p', class_='iteminfo__line1__jobname')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    link_elem = item.find('a')
                    link = link_elem['href'] if link_elem else ""
                    jobs.append({
                        "title": title,
                        "url": link,
                        "city": city,
                        "source": "智联招聘"
                    })
    except Exception as e:
        print(f"智联招聘获取失败: {e}")
    return jobs

def filter_jobs(jobs):
    """过滤黑中介"""
    filtered = []
    for job in jobs:
        title = job.get("title", "")
        # 检查黑名单
        if any(kw in title for kw in BLACKLIST_KEYWORDS):
            continue
        filtered.append(job)
    return filtered

def format_jobs(jobs):
    """格式化输出"""
    if not jobs:
        return "今日暂无符合条件的招聘信息"
    
    lines = [f"📋 招聘信息汇总（{datetime.date.today()}）", ""]
    lines.append(f"📍 城市：{', '.join(CITIES)}")
    lines.append(f"🎓 学历：{EDUCATION}及以上")
    lines.append(f"✅ 共检索到 {len(jobs)} 条有效信息")
    lines.append("")
    
    for i, job in enumerate(jobs[:15], 1):
        lines.append(f"{i}. {job['title']}")
        lines.append(f"   📍 {job['city']} | 🔗 {job['source']}")
        lines.append(f"   🔗 {job['url']}")
        lines.append("")
    
    return "\n".join(lines)

def main():
    print("[1/3] 检索招聘信息...")
    all_jobs = []
    
    for city in CITIES:
        print(f"  检索 {city}...")
        # 从多个网站获取
        jobs1 = fetch_from_zhipin(city)
        jobs2 = fetch_from_zhaopin(city)
        all_jobs.extend(jobs1)
        all_jobs.extend(jobs2)
    
    print(f"  共检索到 {len(all_jobs)} 条原始信息")
    
    print("[2/3] 过滤黑中介...")
    filtered = filter_jobs(all_jobs)
    print(f"  过滤后剩余 {len(filtered)} 条")
    
    print("[3/3] 格式化输出...")
    content = format_jobs(filtered)
    
    # 保存到文件
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "jobs.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"done -> {output_file}")

if __name__ == "__main__":
    main()
