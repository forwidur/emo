import json
import os
import sys

from bs4 import BeautifulSoup
from langdetect import detect
import plyvel

def process_raw_html(html):
    soup = BeautifulSoup(html, 'html.parser')

    if soup.h1 != None:
        title = soup.h1.get_text("\r\n", strip=True)
    else:
        title = soup.title.get_text("\r\n", strip=True)
        if title.endswith(' – Medium'):
            title = title[:-len(' – Medium')]

    body = ''
    body_elements = []
    # TODO this selector sometimes still leave certain titles in the body text
    # example at https://medium.com/@giftangelahamisi/my-grandmas-fight-with-ovarian-cancer-is-saving-my-life-90ea906d9f09
    for element in soup.select('div.section-content p'):
        body_elements.append(element.get_text("\r\n", strip=True))
    body = '\r\n'.join(body_elements)

    return {'title': title, 'body': body}

def process_raw_path(raw_path, out_db):
    print("Processing %s. " % (raw_path), end='')
    raw_db = plyvel.DB(raw_path)

    total = 0
    eng = 0
    long_enough = 0
    for url, raw_post in raw_db:
        post = process_raw_html(raw_post)
        total = total + 1
        if len(post["body"]) < 500:
            continue
        long_enough = long_enough + 1
        try:
            if detect(post["body"]) == "en":
                out_db.put(url, json.dumps(post, separators=(',',':')).encode())
                eng = eng + 1
        except:
            print(url, post)

    print("Total: %d, long enough: %d, English: %d" % (total, long_enough, eng))

def main():
    raw_days_path = sys.argv[1]
    output_path = sys.argv[2]

    if not os.path.exists(output_path):
        os.makedirs(output_path)
    out_db = plyvel.DB(output_path, create_if_missing=True)

    for x in os.walk(raw_days_path):
        raw_path = x[0]
        if raw_path == raw_days_path:  # Filter out the top dir.
            continue
        process_raw_path(raw_path, out_db)

    out_db.close()

if __name__== "__main__":
    main()
