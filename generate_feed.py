#!/usr/bin/env python3

import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime

FEED_URLS = sys.argv[1:-1]
MAX_ITEMS = int(sys.argv[-1])

ATOM_NS = {'atom': 'http://www.w3.org/2005/Atom'}

def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as resp:
        return resp.read()

def parse_date(date_str: str):
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except ValueError:
        pass
    try:
        return parsedate_to_datetime(date_str)
    except Exception:
        pass
    try:
        return datetime.strptime(date_str[:25], "%a, %d %b %Y %H:%M:%S")
    except Exception:
        return None

def collect_items(feed_url: str):
    root = ET.fromstring(fetch(feed_url))
    entries = root.findall('.//item')
    if not entries:
        entries = root.findall('.//atom:entry', ATOM_NS)

    items = []
    for e in entries:
        title = e.findtext('title') or e.findtext('{http://www.w3.org/2005/Atom}title')
        link = e.findtext('link')
        if not link:
            link_el = e.find('{http://www.w3.org/2005/Atom}link')
            if link_el is not None:
                link = link_el.attrib.get('href')
        pub = e.findtext('pubDate') or e.findtext('{http://www.w3.org/2005/Atom}updated')
        dt = parse_date(pub)
        items.append({'title': title or '(untitled)', 'link': link or '', 'dt': dt})
    return items

def main() -> None:
    all_items = []
    for url in FEED_URLS:
        try:
            all_items.extend(collect_items(url))
        except Exception as exc:
            print(f'<!-- skipped feed {url}: {exc} -->', file=sys.stderr)

    dated = [i for i in all_items if i['dt'] is not None]
    undated = [i for i in all_items if i['dt'] is None]
    dated.sort(key=lambda i: i['dt'], reverse=True)
    all_items = dated + undated

    lines = []
    for i in all_items[:MAX_ITEMS]:
        pub_pretty = i['dt'].strftime('%b %d, %Y') if i['dt'] else ''
        suffix = f' (*{pub_pretty}*)' if pub_pretty else ''
        lines.append(f"- [{i['title']}]({i['link']}){suffix}")

    print("\n".join(lines))

if __name__ == '__main__':
    main()
