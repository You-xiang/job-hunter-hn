# -*- coding: utf-8 -*-
"""
鎷涜仒淇℃伅妫€绱㈣剼鏈?- 婀栧崡鐪佸叏鐪?v2
浣跨敤 Bing 鎼滅储寮曟搸妫€绱㈡嫑鑱樹俊鎭紙瑙ｅ喅 GitHub Actions 鏃犳硶璁块棶涓浗鏀垮簻缃戠珯鐨勯棶棰橈級
"""
import os
import re
import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

CITIES = [
    "闀挎矙", "鏍床", "婀樻江", "琛￠槼", "閭甸槼", "宀抽槼", "甯稿痉",
    "寮犲鐣?, "鐩婇槼", "閮村窞", "姘稿窞", "鎬€鍖?, "濞勫簳", "婀樿タ"
]

BLACKLIST_KEYWORDS = [
    "鍒峰崟", "鎵撳瓧", "鎵嬪伐", "鏃ョ粨", "鏈堝叆杩囦竾", "淇濆簳",
    "浠ｇ悊", "鍔犵洘", "寰晢", "娣樺疂鍒峰崟", "缃戠粶鍏艰亴", "娓告垙浠ｇ粌",
    "褰╃エ", "鍗氬僵", "鑹叉儏", "璧屽崥", "璐锋", "淇＄敤鍗?, "鐐掕偂",
    "鏈熻揣", "澶栨眹", "铏氭嫙璐у竵", "鍖哄潡閾炬嫑鑱?
]

def search_bing(query, count=10):
    """浣跨敤 Bing 鎼滅储"""
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
        print(f"    Bing 鎼滅储寮傚父: {e}")
    return []

def fetch_jobs():
    """妫€绱㈡嫑鑱樹俊鎭?""
    all_jobs = []
    seen_urls = set()

    search_queries = [
        "婀栧崡 鎷涜仒 澶т笓 2026",
        "闀挎矙 鎷涜仒 澶т笓瀛﹀巻",
        "婀栧崡 浜嬩笟鍗曚綅 鎷涜仒 澶т笓",
        "婀栧崡 浼佷笟鎷涜仒 澶т笓",
        "鏍床 婀樻江 琛￠槼 鎷涜仒 澶т笓",
        "宀抽槼 甯稿痉 鐩婇槼 鎷涜仒 澶т笓",
        "閮村窞 姘稿窞 鎬€鍖?鎷涜仒 澶т笓",
        "閭甸槼 濞勫簳 婀樿タ 寮犲鐣?鎷涜仒 澶т笓",
    ]

    for query in search_queries:
        print(f"  鎼滅储: {query}")
        results = search_bing(query, count=10)
        print(f"    鎵惧埌 {len(results)} 鏉＄粨鏋?)
        for r in results:
            url_clean = r['url'].split('?')[0].rstrip('/')
            if url_clean not in seen_urls:
                seen_urls.add(url_clean)
                all_jobs.append({
                    'title': r['title'],
                    'url': r['url'],
                    'snippet': r.get('snippet', ''),
                    'source': 'Bing鎼滅储'
                })

    return all_jobs

def filter_jobs(jobs):
    """杩囨护榛戜腑浠嬪拰涓嶇浉鍏充俊鎭?""
    filtered = []
    for job in jobs:
        text = job.get('title', '') + ' ' + job.get('snippet', '')
        if any(kw in text for kw in BLACKLIST_KEYWORDS):
            continue
        # 杩囨护鎺夋槑鏄句笉鐩稿叧鐨勭粨鏋滐紙濡傜函鏂伴椈銆佽棰戠瓑锛?        skip = False
        for pattern in ['youtube.com', 'bilibili.com', 'tiktok.com', 'douyin.com']:
            if pattern in job.get('url', ''):
                skip = True
                break
        if skip:
            continue
        filtered.append(job)
    return filtered

def format_jobs(jobs):
    """鏍煎紡鍖栬緭鍑?""
    today = datetime.date.today()
    if not jobs:
        return f"馃搵 婀栧崡鐪佹嫑鑱樹俊鎭眹鎬伙紙{today}锛塡n\n浠婃棩鏆傛湭妫€绱㈠埌绗﹀悎鏉′欢鐨勬嫑鑱樹俊鎭紝璇锋槑澶╁啀璇曘€?

    lines = [f"馃搵 婀栧崡鐪佹嫑鑱樹俊鎭眹鎬伙紙{today}锛?, ""]
    lines.append(f"馃搷 鑼冨洿锛氭箹鍗楃渷鍏ㄧ渷锛坽', '.join(CITIES)}锛?)
    lines.append(f"馃帗 瀛﹀巻锛氬ぇ涓撳強浠ヤ笂")
    lines.append(f"鉁?鍏辨绱㈠埌 {len(jobs)} 鏉℃湁鏁堜俊鎭?)
    lines.append("")

    for i, job in enumerate(jobs[:20], 1):
        lines.append(f"{i}. {job['title']}")
        if job.get('snippet'):
            snippet = job['snippet'][:120]
            lines.append(f"   馃摑 {snippet}")
        lines.append(f"   馃敆 {job['url']}")
        lines.append("")

    lines.append("馃挕 鎻愮ず锛氫互涓婁俊鎭潵鑷叕寮€鎼滅储寮曟搸锛岃娉ㄦ剰鐢勫埆淇℃伅鐪熷疄鎬э紝璀︽儠榛戜腑浠嬨€?)
    return "\n".join(lines)

def main():
    print("[1/3] 妫€绱㈡嫑鑱樹俊鎭?..")
    all_jobs = fetch_jobs()
    print(f"  鍏辨绱㈠埌 {len(all_jobs)} 鏉″師濮嬩俊鎭?)

    print("[2/3] 杩囨护榛戜腑浠?..")
    filtered = filter_jobs(all_jobs)
    print(f"  杩囨护鍚庡墿浣?{len(filtered)} 鏉?)

    print("[3/3] 鏍煎紡鍖栬緭鍑?..")
    content = format_jobs(filtered)

    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "jobs.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"done -> {output_file}")

if __name__ == "__main__":
    main()
