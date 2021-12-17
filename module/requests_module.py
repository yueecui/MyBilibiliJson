import logging
import requests
from .chrome_cookies import get_bilibili_cookies


COOKIES = get_bilibili_cookies()
if COOKIES is None:
    raise ValueError("没有正确获得bilibli.com的cookies")

POST_HEADERS = {
    # ":method": "POST",
    # ":authority": "api.bilibili.com",
    # ":scheme": "https",
    # ":path": "/x/activity/mission/task/reward/receive",
    # "content-length": "124",
    "sec-ch-ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"96\", \"Google Chrome\";v=\"96\"",
    "accept": "application/json, text/plain, */*",
    "content-type": "application/x-www-form-urlencoded",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    "sec-ch-ua-platform": "\"Windows\"",
    "origin": "https://www.bilibili.com",
    "sec-fetch-site": "same-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.bilibili.com/",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "zh-CN,zh;q=0.9",
}

MAX_TRY = 3


def requests_get(url: str, **kwargs):
    retry_count = 0
    while retry_count < MAX_TRY:
        response = requests.get(url, cookies=COOKIES, **kwargs)
        if response.status_code == 200:
            return response
        retry_count += 1
        logging.info(f'GET <{url}>失败，状态码：{response.status_code}，第{retry_count}次重试')
    return None


def requests_post(url: str, **kwargs):
    retry_count = 0
    while retry_count < MAX_TRY:
        response = requests.post(url, **kwargs, headers=POST_HEADERS, cookies=COOKIES)
        if response.status_code == 200:
            return response
        retry_count += 1
        logging.info(f'POST <{url}>失败，状态码：{response.status_code}，第{retry_count}次重试')
    return None
