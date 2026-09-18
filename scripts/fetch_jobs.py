# -*- coding: utf-8 -*-
"""招聘信息检索：长沙/娄底，大专及以上"""
import os
import re
import datetime
import requests
from bs4 import BeautifulSoup

CITIES = ["长沙", "娄底"]
EDUCATION = "大专"

# 黑中介特征关键词（严格过滤）
BLACKLIST_KEYWORDS = [
    "刷单", "打字员", "手工活", "网络兼职", "游戏代练",
    "在家工作", "日结", "无需经验不限学历", "代理加盟",
    "微商", "淘宝刷单", "兼职打字"
]

# 可信招聘网站域名（大幅扩充）
TRUSTED_DOMAINS = [
    "zhaopin.com", "51job.com", "liepin.com", "lagou.com",
    "boss.com", "kanzhun.com", "jobui.com", "ganji.com",
    "58.com", "jobs.cn", "zhaopin.cn", "hrsalon.cn",
    "hunanedu.cn", "hunanrc.com", "csrc.gov", "loudi.gov",
    "changsha.gov", "job.com", "recruit.com", "talent.com",
    "zpwanted.com", "liepin.com", "zhipin.com", "kanzhun.com",
    "lagou.com", "51job.com", "zhaopin.com", "ganji.com",
    "dajie.com", "jobui.com", "kuaidi100.com", "58.com"
]

def search_jobs(city, education):
    """通过多个渠道搜索招聘信息"""
    jobs = []
    
    # 渠道1: 百度搜索
    query = f"{city} {education} 招聘 2026"
    url = f"https://www.baidu.com/s?wd={query}&rn=20"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        for item in soup.select('.result'):
            title_tag = item.select_one('h3 a')
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            link = title_tag.get('href', '')
            
            # 检查是否包含招聘相关
            if not any(kw in title for kw in ['招聘', '职位', '岗位', '人才', '求职']):
                continue
            
            # 检查黑名单
            if any(kw in title for kw in BLACKLIST_KEYWORDS):
                continue
            
            # 提取域名
            domain = ''
            try:
                if 'http' in link:
                    domain = link.split('/')[2]
            except:
                pass
            
            jobs.append({
                "title": title,
                "url": link,
                "city": city,
                "source": domain or "百度"
            })
    except Exception as e:
        print(f"[warn] 百度搜索 {city} 失败: {e}")
    
    # 渠道2: 直接访问主流招聘网站搜索页
    try:
        # Boss直聘搜索
        boss_url = f"https://www.zhipin.com/web/geek/job?query={city}+{education}&city=101250100"
        resp = requests.get(boss_url, headers=headers, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            for item in soup.select('.job-card-wrapper')[:10]:
                title_tag = item.select_one('.job-name')
                if title_tag:
                    title = title_tag.get_text(strip=True)
                    link_tag = item.select_one('a')
                    link = link_tag.get('href', '') if link_tag else ''
                    if link and not link.startswith('http'):
                        link = 'https://www.zhipin.com' + link
                    jobs.append({
                        "title": f"[Boss直聘] {title}",
                        "url": link,
                        "city": city,
                        "source": "zhipin.com"
                    })
    except Exception as e:
        print(f"[warn] Boss直聘搜索失败: {e}")
    
    return jobs

def deduplicate(jobs):
    seen = set()
    unique = []
    for job in jobs:
        key = job['title'][:20]  # 用前20字符去重
        if key not in seen:
            seen.add(key)
            unique.append(job)
    return unique

def format_jobs(jobs):
    if not jobs:
        return "今日暂无符合条件的招聘信息，建议明天再试或调整搜索条件。"
    
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
    
    lines.append("💡 提示：点击链接查看详情，注意甄别信息真伪")
    return "\n".join(lines)

def main():
    print("[1/3] 检索招聘信息...")
    all_jobs = []
    for city in CITIES:
        print(f"  检索 {city}...")
        jobs = search_jobs(city, EDUCATION)
        print(f"    找到 {len(jobs)} 条")
        all_jobs.extend(jobs)
    
    print(f"[2/3] 去重处理...")
    unique = deduplicate(all_jobs)
    print(f"  去重后: {len(unique)} 条")
    
    print(f"[3/3] 格式化输出...")
    content = format_jobs(unique)
    
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs")
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "jobs.txt"), "w", encoding="utf-8") as f:
        f.write(content)
    print("done")

if __name__ == "__main__":
    main()
