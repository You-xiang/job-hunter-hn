# -*- coding: utf-8 -*-
"""
招聘信息检索脚本 - 湖南省全省 v3
使用 Bing 搜索引擎检索招聘信息
修复去重逻辑：按标题去重而非 URL
"""
import os
import re
import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

CITIES = [
    "长沙", "株洲", "湘潭", "衡阳", "邵阳", "岳阳", "常德",
    "张家界", "益阳", "郴州", "永州", "怀化", "娄底", "湘西"
]

BLACKLIST_KEYWORDS = [
    "刷单", "打字", "手工", "日结", "月入过万", "保底",
    "代理", "加盟", "微商", "淘宝刷单", "网络兼职", "游戏代练",
    "彩票", "博彩", "色情", "赌博", "贷款", "信用卡", "炒股",
    "期货", "外汇", "虚拟货币", "区块链招聘"
]

def search_bing(query, count=10):
    """使用 Bing 搜索"""
    url = f"https://www.bing.com/search?q={quote(query)}&count={count}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            results = []
            for item in soup.find_all('li', class_='b_algo'):
                h2 = item.find('h2')
                if h2:
                    a = h2.find('a')
                    if a:
                        title = a.get_text(strip=True)
                        link = a.get('href', '')
                        snippet_tag = item.find('div', class_='b_caption')
                        snippet = ''
                        if snippet_tag:
                            p = snippet_tag.find('p')
                            if p:
                                snippet = p.get_text(strip=True)
                        if link and title:
                            results.append({
                                'title': title,
                                'url': link,
                                'snippet': snippet
                            })
            return results[:count]
    except Exception as e:
        print(f"    Bing 搜索异常: {e}")
    return []

def fetch_jobs():
    """检索招聘信息"""
    all_jobs = []
    seen_titles = set()

    search_queries = [
        "湖南 招聘 大专 2026",
        "长沙 招聘 大专学历",
        "湖南 事业单位 招聘 大专",
        "湖南 企业招聘 大专",
        "株洲 湘潭 衡阳 招聘 大专",
        "岳阳 常德 益阳 招聘 大专",
        "郴州 永州 怀化 招聘 大专",
        "邵阳 娄底 湘西 张家界 招聘 大专",
    ]

    for query in search_queries:
        print(f"  搜索: {query}")
        results = search_bing(query, count=10)
        print(f"    找到 {len(results)} 条结果")
        for r in results:
            title_clean = r['title'].strip()
            if title_clean not in seen_titles:
                seen_titles.add(title_clean)
                all_jobs.append({
                    'title': r['title'],
                    'url': r['url'],
                    'snippet': r.get('snippet', ''),
                    'source': 'Bing搜索'
                })

    return all_jobs

def filter_jobs(jobs):
    """过滤黑中介和不相关信息"""
    filtered = []
    for job in jobs:
        text = job.get('title', '') + ' ' + job.get('snippet', '')
        if any(kw in text for kw in BLACKLIST_KEYWORDS):
            continue
        skip = False
        for pattern in ['youtube.com', 'bilibili.com', 'tiktok.com', 'douyin.com']:
            if pattern in job.get('url', ''):
                skip = True
                break
        if skip:
            continue
        filtered.append(job)
    return filtered

def format_jobs(jobs):
    """格式化输出 - 纯文字版，无链接"""
    today = datetime.date.today()
    if not jobs:
        return f"湖南省招聘信息汇总（{today}）\n\n今日暂未检索到符合条件的招聘信息，请明天再试。"

    lines = [f"湖南省招聘信息汇总（{today}）", ""]
    lines.append(f"范围：湖南省全省（{', '.join(CITIES)}）")
    lines.append(f"学历：大专及以上")
    lines.append(f"共检索到 {len(jobs)} 条有效信息")
    lines.append("")

    for i, job in enumerate(jobs[:20], 1):
        lines.append(f"{i}. {job['title']}")
        # 整理 snippet 内容，提取关键信息
        if job.get('snippet'):
            snippet = job['snippet']
            # 清理 snippet，去掉多余空格和特殊字符
            snippet = re.sub(r'\s+', ' ', snippet).strip()
            # 如果 snippet 包含有用信息，分行显示
            if len(snippet) > 20:
                lines.append(f"   {snippet}")
        lines.append("")

    lines.append("提示：以上信息来自公开搜索引擎，请注意甄别信息真实性，警惕黑中介。")
    return "\n".join(lines)

def main():
    print("[1/3] 检索招聘信息...")
    all_jobs = fetch_jobs()
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
