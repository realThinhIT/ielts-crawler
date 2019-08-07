import logging
import csv
import time

import requests
from requests_html import HTMLSession

from config import Config

headers = {
    "User-Agent":
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36",
    "Upgrade-Insecure-Requests": "1",
    "DNT": "1",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate"
}


def try_to_req_with_html(post_url):
    sleep_req()

    session = HTMLSession()
    req = session.get(post_url, headers=headers)

    return return_req(req, post_url, req_instance=session)


def try_to_req(req_url):
    sleep_req()

    req = requests.get(req_url, headers=headers)

    return return_req(req, req_url, req_instance=requests)


def return_req(req, url, req_instance):
    if not req.ok:
        for i in range(1, Config.ERROR_THRESHOLD):
            sleep_req()
            req = req_instance.get(url, headers=headers)

            if req.ok:
                break

    if not req.ok:
        log("[Req] Request to {} failed after max tries.".format(url))

    return req


def res(response):
    return response.decode('utf-8')


def log(content):
    logging.basicConfig(filename=Config.LOG_FILE_NAME, level=logging.DEBUG)
    print(content)
    logging.info(content)


def write_csv(row):
    with open(Config.FILE_NAME, "a") as write_file:
        writer = csv.writer(write_file)
        writer.writerow(row)

    write_file.close()


def sleep_req():
    time.sleep(Config.SLEEP_BETWEEN_REQUESTS)


def check_topic(topic_name):
    return "Here is a band" in topic_name \
            or "Essay topic" in topic_name \
            or "essay topic" in topic_name \
            or "following essay" in topic_name \
            or "following topic" in topic_name \
            or "IELTS" in topic_name \
            or "writing sample" in topic_name \
            or "appeared in" in topic_name


def check_divider(content):
    return "Band" in content and (
        "essay" in content
        or "Essay" in content
    )
