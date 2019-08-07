import re
import os

from config import Config
from utils import res, log, write_csv, try_to_req_with_html, try_to_req, check_topic, check_divider


LINK_LISTS = {
    "9": [],
    "8": [],
    "7.5": [],
    "7": []
}
CRAWLED_LINK = []
TOTAL_POSTS_COUNTER = 0


def crawl_links(label):
    band = label["band"]
    category = label["category"]

    failed_counter = 0
    for page in range(1, 1000):
        log("Trying to fetch page {} of band {}".format(page, band))
        req_url = Config.BASE_CATEGORY_URL.format(category, page)

        # Make a request
        req = try_to_req(req_url)

        # If request failed, add it to the threshold
        if not req.ok:
            failed_counter = failed_counter + 1

            if failed_counter == Config.ERROR_THRESHOLD:
                log("Discovered {} links from band {}.".format(len(LINK_LISTS[band]), band))
                break

        # If request is okay
        else:
            # Decode response
            response = res(req.content)

            # Extract links from page
            links = Config.RE_EXTRACT_LINK_FROM_LIST.findall(response)

            # Add to crawl links list
            if links:
                for link in links:
                    if link[0] is not None:
                        LINK_LISTS[band].append(link[0])


def crawl_post_data(band):
    global TOTAL_POSTS_COUNTER
    links = LINK_LISTS[band]

    # Crawl posts
    log("Starting to crawl {} links from band {}.".format(len(LINK_LISTS[band]), band))

    for post_url in links:
        # Check if this link has been crawled
        if post_url in CRAWLED_LINK:
            continue

        CRAWLED_LINK.append(post_url)

        # Get content and create a HTML session
        req = try_to_req_with_html(Config.BASE_URL.format(post_url))

        # Decide if divider is h2 or h3
        divider = "h2"
        h2_element = req.html.find('.entry-inner h2')
        h3_element = req.html.find('.entry-inner h3')

        # Find all p elements
        p_elements = req.html.find(".entry-inner p")

        if h2_element is not None:
            if len(h2_element) == 1:
                divider = "h2"
            elif len(h2_element) == 2:
                divider = "h2:nth-of-type(2)"
        if h3_element is not None:
            if len(h3_element) == 1:
                divider = "h3"
            elif len(h3_element) == 2:
                divider = "h3:nth-of-type(2)"
        if len(h2_element) == 0 and len(h3_element) == 0:
            n_th_element = None
            p_counter = 0

            for p in p_elements:
                if check_divider(p.text):
                    n_th_element = p_counter
                p_counter = p_counter + 1

            if n_th_element is None:
                n_th_element = 2

            divider = "p:nth-of-type({})".format(n_th_element + 1)

        # Find all paragraphs
        after_h2_p_elements = req.html.find(".entry-inner {} ~ p".format(divider))

        # If only p before h2 then that's the topic
        p_before_h2 = len(p_elements) - len(after_h2_p_elements)

        # Select topic
        topic = ""

        if p_before_h2 > 1:
            topic_element = req.html.find(".entry-inner p", first=True)

            if topic_element is not None:
                if check_topic(topic_element.text):
                    topic_element = req.html.find(".entry-inner p")[1]

                topic = topic_element.text
        elif p_before_h2 == 1:
            topic = req.html.find(".entry-inner p", first=True).text

        # Select paragraphs
        paragraph_counter = 1
        essay_content = ""
        paragraphs = req.html.find(".entry-inner {} ~ p".format(divider))

        if paragraphs:
            for paragraph in paragraphs:
                # Exclude related posts
                if paragraph.text != "Related posts:" and "Do you have an essay on this topic" not in paragraph.text:
                    # No new line with the first paragraph
                    if paragraph_counter > 1:
                        essay_content = essay_content + "\n"

                    essay_content = essay_content + paragraph.text

                    paragraph_counter = paragraph_counter + 1

        # Check if all are valid
        if topic != "" and essay_content != "":
            log("[Band {}] Topic: {}".format(band, topic))

            TOTAL_POSTS_COUNTER = TOTAL_POSTS_COUNTER + 1
            write_csv([TOTAL_POSTS_COUNTER, topic, essay_content, band, post_url])

        # If this does not met
        else:
            log("[Band {}] URL {} failed to crawl.".format(band, post_url))
            log("With topic = {} \n& content = {} \n& divider = {}".format(topic, essay_content, divider))


if __name__ == "__main__":
    # Remove files
    write_csv(['id', 'topic', 'essay', 'grade', 'url'])

    for _label in Config.LABELS:
        crawl_links(_label)
        crawl_post_data(_label["band"])
