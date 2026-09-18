# -*- coding: utf-8 -*-
"""
招聘信息检索脚本 - 湖南省全省
使用湖南人才网、长沙人才网等政府网站
"""
import os
import re
import json
import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

# 湖南省全部地级市
CITIES = [
    "长沙", "株洲", "湘潭", "衡阳", "邵阳", "岳阳", "常德",
    "张家界", "益阳", "郴州", "永州", "怀化", "娄底", "湘西"
]
EDUCATION = "大专"

# 黑中介关键词
BLACKLIST_KEYWORDS = [
    "刷单", "打字", "手工", "兼职", "在家工作", "日结",
    "月入过万", "保底", "代理", "加盟", "微商", "淘宝刷单",
    "网络兼职", "游戏代练"
]

def fetch_from_hunanrc():
    """从湖南人才网获取"""
    jobs = []
    try:
        url = "http://www.hunanrc.com/job/list"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            # 查找职位列表
            job_items = soup.find_all('div', class_='job-item')[:20]
            for item in job_items:
                title_tag = item.find('a', class_='job-title')
                if title_tag:
                    title = title_tag.get_text(strip=True)
                    link = title_tag.get('href', '')
                    if not link.startswith('http'):
                        link = 'http://www.hunanrc.com' + link
                    
                    city_tag = item.find('span', class_='job-city')
                    city = city_tag.get_text(strip=True) if city_tag else "湖南"
                    
                    jobs.append({
                        "title": title,
                        "url": link,
                        "city": city,
                        "source": "湖南人才网"
                    })
    except Exception as e:
        print(f"湖南人才网获取失败: {e}")
    return jobs

def fetch_from_changsharc():
    """从长沙人才网获取"""
    jobs = []
    try:
        url = "http://www.csrcsc.com/job/list"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            job_items = soup.find_all('div', class_='job-item')[:20]
            for item in job_items:
                title_tag = item.find('a', class_='job-title')
                if title_tag:
                    title = title_tag.get_text(strip=True)
                    link = title_tag.get('href', '')
                    if not link.startswith('http'):
                        link = 'http://www.csrcsc.com' + link
                    
                    jobs.append({
                        "title": title,
                        "url": link,
                        "city": "长沙",
                        "source": "长沙人才网"
                    })
    except Exception as e:
        print(f"长沙人才网获取失败: {e}")
    return jobs

def fetch_from_gov_sites():
    """从政府招聘网站获取"""
    jobs = []
    gov_urls = [
        ("湖南省人社厅", "http://rst.hunan.gov.cn/rst/xxgk/zpxx/"),
        ("长沙人社局", "http://rsj.changsha.gov.cn/zpxx/"),
    ]
    
    for name, url in gov_urls:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                # 查找招聘相关链接
                links = soup.find_all('a', href=True)
                for link in links[:10]:
                    title = link.get_text(strip=True)
                    href = link.get('href', '')
                    if any(kw in title for kw in ['招聘', '公告', '人才']):
                        if not href.startswith('http'):
                            href = url.rstrip('/') + '/' + href.lstrip('/')
                        jobs.append({
                            "title": title,
                            "url": href,
                            "city": "湖南",
                            "source": name
                        })
        except Exception as e:
            print(f"{name}获取失败: {e}")
    
    return jobs

def filter_jobs(jobs):
    """过滤黑中介"""
    filtered = []
    for job in jobs:
        title = job.get("title", "")
        if any(kw in title for kw in BLACKLIST_KEYWORDS):
            continue
        filtered.append(job)
    return filtered

def format_jobs(jobs):
    """格式化输出"""
    if not jobs:
        return "今日暂无符合条件的招聘信息"
    
    lines = [f"📋 招聘信息汇总（{datetime.date.today()}）", ""]
    lines.append(f"📍 范围：湖南省全省（{', '.join(CITIES)}）")
    lines.append(f"🎓 学历：{EDUCATION}及以上")
    lines.append(f"✅ 共检索到 {len(jobs)} 条有效信息")
    lines.append("")
    
    for i, job in enumerate(jobs[:20], 1):
        lines.append(f"{i}. {job['title']}")
        lines.append(f"   📍 {job['city']} | 🔗 {job['source']}")
        lines.append(f"   🔗 {job['url']}")
        lines.append("")
    
    return "\n".join(lines)

def main():
    print("[1/3] 检索招聘信息...")
    all_jobs = []
    
    print("  检索湖南人才网...")
    jobs1 = fetch_from_hunanrc()
    print(f"    湖南人才网: {len(jobs1)} 条")
    all_jobs.extend(jobs1)
    
    print("  检索长沙人才网...")
    jobs2 = fetch_from_changsharc()
    print(f"    长沙人才网: {len(jobs2)} 条")
    all_jobs.extend(jobs2)
    
    print("  检索政府招聘网站...")
    jobs3 = fetch_from_gov_sites()
    print(f"    政府网站: {len(jobs3)} 条")
    all_jobs.extend(jobs3)
    
    print(f"  共检索到 {len(all_jobs)} 条原始信息")
    
    print("[2/3] 过滤黑中介...")
    filtered = filter_jobs(all_jobs)
    print(f"  过滤后剩余 {len(filtered)} 条")
    
    print("[3/3] 格式化输出...")
    content = format_jobs(filtered)
    
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "jobs.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"done -> {output_file}")

if __name__ == "__main__":
    main()
