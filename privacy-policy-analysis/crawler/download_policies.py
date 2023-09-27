import csv
from pathlib import Path
import re
import time

from pyvirtualdisplay import Display
import requests
from selenium import webdriver
import selenium


all_urls = dict()

with open("privacy_policy_urls.csv", newline="") as fin:
    reader = csv.DictReader(fin)

    for row in reader:
        url = row["privacy_policy_url"]

        if url not in all_urls:
            all_urls[url] = []

        all_urls[url].append(row["asin"])

with Display() as disp:
    outdir = Path("policies")
    outdir.mkdir(exist_ok=True)

    driver = webdriver.Chrome()

    for url, asin_list in all_urls.items():
        asin = asin_list[0]
        outpath = outdir / f"{asin}.html"

        if not outpath.is_file():
            print(f"Downloading {url} ...")

            m = re.match(r"https://docs.google.com/document/d/([^/]+)", url)

            if m:
                print("> Exporting Google Docs URL...")
                url = f"https://docs.google.com/feeds/download/documents/export/Export?id={m[1]}&exportFormat=html"
                req = requests.get(url)
                req.raise_for_status()
                html = req.text
            else:
                try:
                    driver.get("about:blank")
                    driver.set_page_load_timeout(10)
                    driver.get(url)
                    time.sleep(5)
                    html = driver.page_source
                except selenium.common.exceptions.WebDriverException:
                    print("> Error!!!")
                    continue

            with outpath.open("w") as fout:
                fout.write(html)

            print("> DONE, ASINs:", asin_list)

        if outpath.is_file():
            for asin in asin_list[1:]:
                linkpath = outdir / f"{asin}.html"
                if not linkpath.is_file():
                    linkpath.hardlink_to(outpath)

    driver.quit()
