#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import hashlib
import os
import requests
import re
from datetime import datetime

# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
# 把你的企业微信 webhook 完整粘到这里！必须改！
WECOM_WEBHOOK = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=7ae4adaf-ac5a-4cc1-a478-687ff0527e83"
# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←

URL = "https://yst-info.zjcaee.com/html/infor/infor.html?sub=0&v=1764651891988"
STATE_FILE = "/app/seen.txt"   # Koyeb 里用的路径

def send(title, url):
    try:
        requests.post(WECOM_WEBHOOK, json={
            "msgtype": "news",
            "news": {"articles": [{"title": title, "url": url, "description": "乐数通最新公告"}]}
        }, timeout=10)
        print(f"已推送 → {title}")
    except:
        print("推送失败")

seen = set()
if os.path.exists(STATE_FILE):
    seen = set(open(STATE_FILE).read().splitlines())

first_run = len(seen) == 0
if first_run:
    send("【乐数通公告监控已在 Koyeb 云端启动】以后只推新公告", URL)

while True:
    try:
        r = requests.get(URL, timeout=15)
        r.encoding = 'utf-8'
        # 直接用正则暴力提取（实测当前页面有效）
        items = re.findall(r'"title":"(.*?)".*?"createTime":"(\d{4}-\d{2}-\d{2})".*?"url":"(.*?)"', r.text)
        
        for title, date, url_path in items:
            date = date.replace("-", ".")
            link = "https://yst-info.zjcaee.com" + url_path if url_path.startswith("/") else url_path
            key = hashlib.md5((title + link).encode()).hexdigest()
            
            if key not in seen:
                seen.add(key)
                full = f"{date} {title}"
                if not first_run:
                    send(full, link)
                else:
                    print(f"标记旧公告：{full}")
        
        if items:
            open(STATE_FILE, "w").write("\n".join(seen))
            
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M')} 检查完成，已记录 {len(seen)} 条")
        
    except Exception as e:
        print("出错继续跑：", e)
    
    time.sleep(180)  # 3 分钟一次
