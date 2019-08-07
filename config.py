import re


class Config(object):
    # Common
    BASE_URL = "https://www.ielts-practice.org/{}"
    BASE_CATEGORY_URL = "https://www.ielts-practice.org/category/{}/page/{}/"
    LABELS = [
        {
            "band": "9",
            "category": "band-9-ielts-essays"
        },
        {
            "band": "8",
            "category": "band-8-essay-samples"
        },
        {
            "band": "7.5",
            "category": "sample-essays"
        },
        {
            "band": "7",
            "category": "band-7-essay-samples"
        },
    ]
    FILE_NAME = "data.csv"
    LOG_FILE_NAME = "process.log"

    # Requests
    ERROR_THRESHOLD = 5
    SLEEP_BETWEEN_REQUESTS = 0.3
    USER_AGENT = "Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0"

    # Regular Expressions for crawling
    RE_EXTRACT_LINK_FROM_LIST = \
        re.compile('<a href="https://www.ielts-practice.org/(.*?)/" rel="bookmark" title="(.*)">(.*)</a>')

