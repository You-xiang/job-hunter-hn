# -*- coding: utf-8 -*-
"""招聘简报微信推送"""
import os
import datetime
import requests

DOCS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs")

def main():
    jobs_path = os.path.join(DOCS, "jobs.txt")
    if not os.path.exists(jobs_path):
        print("[skip] 未找到 jobs.txt")
        return

    with open(jobs_path, encoding="utf-8") as f:
        content = f.read()

    date_str = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime("%m-%d")
    title = f"招聘信息简报 {date_str}"
    body = content[:3000]

    sendkey = os.environ.get("SC_KEY", "").strip()
    if sendkey:
        try:
            r = requests.post(f"https://sctapi.ftqq.com/{sendkey}.send", data={"title": title, "desp": body}, timeout=30)
            print(f"[push] ok -> {r.text[:200]}")
        except Exception as exc:
            print(f"[warn] push failed: {exc}")
    else:
        print("[skip] 未配置 SC_KEY")

if __name__ == "__main__":
    main()
