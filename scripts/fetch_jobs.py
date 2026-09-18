# -*- coding: utf-8 -*-
"""招聘信息检索：长沙/娄底，大专及以上"""
import os
import re
import datetime
from duckduckgo_search import DDGS

CITIES = ["长沙", "娄底"]
EDUCATION = "大专"
MIN_SALARY = 3000
MAX_SALARY = 50000

BLACKLIST_KEYWORDS = [
    "急聘", "大量招聘", "不限学历", "无需经验", "日结", "兼职",
    "在家工作", "月入过万", "保底", "提成", "代理", "加盟",
    "刷单", "打字", "手工", "网络兼职", "游戏代练"
]

TRUSTED_DOMAINS = [
    "zhaopin.com", "51job.com", "liepin.com", "lagou.com",
    "boss.com", "kanzhun.com", "jobui.com", "ganji.com"
]

def search_jobs(city, education):
    query = f"{city} 招聘 {education}及以上 2026"
    jobs = []
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=20))
            for r in results:
                url = r.get('href', '')
                title = r.get('title', '')
                if not any(domain in url for domain in TRUSTED_DOMAINS):
                    continue
                if any(kw in title for kw in BLACKLIST_KEYWORDS):
                    continue
                jobs.append({"title": title, "url": url, "city": city, "source": url.split('/')[2]})
    except Exception as e:
        print(f"[warn] 搜索 {city} 失败: {e}")
    return jobs

def format_jobs(jobs):
    if not jobs:
        return "今日暂无符合条件的招聘信息"
    lines = [f"📋 招聘信息汇总（{datetime.date.today()}）", "", f"📍 城市：{', '.join(CITIES)}", f"🎓 学历：{EDUCATION}及以上", f"✅ 共检索到 {len(jobs)} 条有效信息", ""]
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
        all_jobs.extend(search_jobs(city, EDUCATION))
    
    print(f"[2/3] 去重处理...")
    seen = set()
    unique = []
    for job in all_jobs:
        key = (job['title'], job['city'])
        if key not in seen:
            seen.add(key)
            unique.append(job)
    
    print(f"[3/3] 格式化输出...")
    content = format_jobs(unique)
    
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs")
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "jobs.txt"), "w", encoding="utf-8") as f:
        f.write(content)
    print("done")

if __name__ == "__main__":
    main()
