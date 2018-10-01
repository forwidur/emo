from datetime import date, timedelta
import os
import sys

import plyvel
import requests
import xml.etree.ElementTree as ET

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 ' +
                  '(KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
}

def post_links_for_date(date):
    sitemap = 'https://medium.com/sitemap/posts/%s/posts-%s.xml' % (date.split('-')[0], date)

    response = requests.get(sitemap, headers=headers)
    root = ET.fromstring(response.content)

    res = []
    for child in root:
        for grandchild in child:
            if grandchild.tag == '{http://www.sitemaps.org/schemas/sitemap/0.9}loc':
                res.append(grandchild.text)

    return res


def main():
    db_path = sys.argv[1]

    yesterday = (date.today() - timedelta(1)).strftime('%Y-%m-%d')
    posts = post_links_for_date(yesterday)

    print(len(posts))

    if not os.path.exists(db_path):
        os.makedirs(db_path)
    db = plyvel.DB(db_path + yesterday, create_if_missing=True)

    for url in posts:
        print(url)
        p = requests.get(url, headers)
        db.put(url.encode(), p.content)

    db.close()

if __name__== "__main__":
    main()
