#!/usr/bin/env python3


import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

FEED_URL = sys.argv[1]         
MAX_ITEMS = int(sys.argv[2])    

def fetch(url: str) -> bytes:
   
    with urllib.request.urlopen(url) as resp:
        return resp.read()

def iso_to_pretty(date_str: str) -> str:
    
    try:
        
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except ValueError:
        try:
            dt = datetime.strptime(date_str[:25], "%a, %d %b %Y %H:%M:%S")
        except Exception:
            return date_str[:10]          
    return dt.strftime("%b %d, %Y")

def main() -> None:
    xml_bytes = fetch(FEED_URL)
    root = ET.fromstring(xml_bytes)

   
    entries = root.findall('.//item')
    if not entries:
        
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        entries = root.findall('.//atom:entry', ns)

    lines = []
    for e in entries[:MAX_ITEMS]:
        # Title
        title = e.findtext('title') or e.find('{http://www.w3.org/2005/Atom}title')
       
        link = e.findtext('link')
        if not link:
            link_el = e.find('{http://www.w3.org/2005/Atom}link')
            if link_el is not None:
                link = link_el.attrib.get('href')
        
        pub = e.findtext('pubDate') or e.find('{http://www.w3.org/2005/Atom}updated')
        pub_pretty = iso_to_pretty(pub) if pub else ""

        lines.append(f"- [{title}]({link}) — *{pub_pretty}*")

    t
    print("\n".join(lines))

if __name__ == "__main__":
    main()
