# -*- coding: utf-8 -*-
"""招聘信息检索：长沙/娄底，大专及以上 - 改进版"""
import os
import re
import datetime
import requests

CITIES = ["长沙", "娄底"]
EDUCATION = "大专"

# 黑中介特征关键词
BLACKLIST_KEYWORDS = [
    "刷单", "打字员", "手工活", "网络兼职", "游戏代练",
    "在家工作", "日结", "代理加盟", "微商", "淘宝刷单"
]

def search_bing(city, education):
    """使用 Bing 搜索"""
    jobs = []
    query = f"{city} {education} 招聘 site:zhipin.com OR site:zhaopin.com OR site:51job.com"
    url = f"https://cn.bing.com/search?q={requests.utils.quote(query)}&count=20"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        # 提取标题和链接
        pattern = r'<h2><a[^>]+href="([^"]+)"[^>]*>([^<]+)</a></h2>'
        matches = re.findall(pattern, resp.text)
        
        for link, title in matches[:15]:
            # 过滤黑名单
            if any(kw in title for kw in BLACKLIST_KEYWORDS):
                continue
            
            # 提取域名
            domain = ""
            if "http" in link:
                domain = link.split("/")[2] if len(link.split("/")) > 2 else ""
            
            jobs.append({
                "title": title.strip(),
                "url": link,
                "city": city,
                "source": domain
            })
    except Exception as e:
        print(f"[warn] Bing 搜索 {city} 失败: {e}")
    
    return jobs

def search_sogou(city, education):
    """使用搜狗搜索"""
    jobs = []
    query = f"{city} {education} 招聘"
    url = f"https://www.sogou.com/web?query={requests.utils.quote(query)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        # 提取结果
        pattern = r'<h3[^>]*>.*?<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>'
        matches = re.findall(pattern, resp.text, re.DOTALL)
        
        for link, title_html in matches[:10]:
            # 清理 HTML 标签
            title = re.sub(r'<[^>]+>', '', title_html).strip()
            
            if not any(kw in title for kw in ['招聘', '职位', '岗位', '人才']):
                continue
            if any(kw in title for kw in BLACKLIST_KEYWORDS):
                continue
            
            domain = ""
            if "http" in link:
                domain = link.split("/")[2] if len(link.split("/")) > 2 else ""
            
            jobs.append({
                "title": title,
                "url": link,
                "city": city,
                "source": domain or "搜狗"
            })
    except Exception as e:
        print(f"[warn] 搜狗搜索 {city} 失败: {e}")
    
    return jobs

def deduplicate(jobs):
    seen = set()
    unique = []
    for job in jobs:
        key = job['title'][:20]
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
        # 使用多个搜索引擎
        jobs1 = search_bing(city, EDUCATION)
        print(f"    Bing: {len(jobs1)} 条")
        jobs2 = search_sogou(city, EDUCATION)
        print(f"    搜狗: {len(jobs2)} 条")
        all_jobs.extend(jobs1)
        all_jobs.extend(jobs2)
    
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
