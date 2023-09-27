#!/usr/bin/env python3

import csv
from pathlib import Path
import sys

import lxml.html as lh


skill_page_dir, = sys.argv[1:]


with open("privacy_policy_urls.csv", "w", newline="") as fout:
    writer = csv.DictWriter(fout, fieldnames=["asin", "publisher", "privacy_policy_url"])
    writer.writeheader()

    for f in Path(skill_page_dir).glob("*.html"):
        doc = lh.parse(str(f)).getroot()
        asin = f.name[:-5]
        publisher = ""

        for item in doc.cssselect("#a2s-product-info span.a-size-base"):
            text = item.text.strip()
            if text.startswith("by "):
                publisher = item.text.strip()[3:]

        for item in doc.cssselect("#a2s-skill-details a.a-link-normal"):
            link_text = item.text.strip()
            url = item.get("href")

            if url != "#" and link_text == "Developer Privacy Policy":
                writer.writerow(dict(asin=asin, publisher=publisher, privacy_policy_url=url))
