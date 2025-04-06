'''import argparse
import os
import csv
import time
from playwright.sync_api import sync_playwright

def select_dropdown(page, dropdown_holder_id, option_text):
    if not option_text:
        return
    trigger = f"#{dropdown_holder_id} .choices"
    page.click(trigger)
    page.wait_for_selector(f"#{dropdown_holder_id} .choices__list--dropdown", timeout=3000)
    options = page.query_selector_all(f"#{dropdown_holder_id} .choices__item--selectable")
    for option in options:
        if option.inner_text().strip().lower() == option_text.strip().lower():
            option.click()
            return

# 🧾 CLI parsing
parser = argparse.ArgumentParser(description="SHL Catalog by Job Category/Title")
parser.add_argument("--job_category", help="e.g. Management and Leadership")
parser.add_argument("--output", default="data/third.csv", help="CSV path")
args = parser.parse_args()

# 💾 Ensure directory
os.makedirs(os.path.dirname(args.output), exist_ok=True)

jobs = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://www.shl.com/solutions/products/product-catalog/job-title/", wait_until="domcontentloaded")

    # 🧭 Select job category
    select_dropdown(page, "Form_FilteringFormJobTitle_job_category_Holder", args.job_category)

    # ⏳ Wait for titles dropdown to populate (if needed)
    time.sleep(1)

    # 🔍 Submit form
    page.click("#Form_FilteringFormJobTitle_action_doFilteringForm")
    time.sleep(2)

    # 🔁 Pagination loop
    while True:
        page.wait_for_selector("div.js-target-table-wrapper table tbody tr", timeout=5000)
        rows = page.query_selector_all("table tbody tr")

        for row in rows:
            title_el = row.query_selector("td a")
            title = title_el.inner_text().strip() if title_el else ''
            link = title_el.get_attribute("href") if title_el else ''

            cells = row.query_selector_all("td")
            remote_td = cells[1] if len(cells) > 1 else None
            adaptive_td = cells[2] if len(cells) > 2 else None

            remote = "Yes" if remote_td and remote_td.query_selector("span.catalogue__circle.-yes") else "No"
            adaptive = "Yes" if adaptive_td and adaptive_td.query_selector("span.catalogue__circle.-yes") else "No"
            key_spans = row.query_selector_all("span.product-catalogue__key")
            keys = ", ".join([span.inner_text().strip() for span in key_spans])

            jobs.append({
                "Job Title": title,
                "Link": link,
                "Remote Testing": remote,
                "Adaptive/IRT": adaptive,
                "Keys": keys
            })

        # ➡️ Pagination
        next_btn = page.query_selector("li.-arrow.-next a.pagination__arrow")
        if next_btn:
            next_href = next_btn.get_attribute("href")
            if next_href:
                next_url = "https://www.shl.com" + next_href
                print(f"➡️ Next page: {next_url}")
                page.goto(next_url, wait_until="domcontentloaded")
                time.sleep(2)
            else:
                break
        else:
            print("✅ Last page reached.")
            break

    browser.close()

# 💾 Save CSV
with open(args.output, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["Job Title", "Link", "Remote Testing", "Adaptive/IRT", "Keys"])
    writer.writeheader()
    writer.writerows(jobs)

print(f"✅ Done. {len(jobs)} jobs saved to {args.output}")

import argparse
import os
import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ✅ Dropdown selector using Selenium
def select_dropdown(driver, dropdown_holder_id, option_text):
    if not option_text:
        return
    trigger_selector = f"#{dropdown_holder_id} .choices"
    driver.find_element(By.CSS_SELECTOR, trigger_selector).click()

    WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, f"#{dropdown_holder_id} .choices__list--dropdown"))
    )

    options = driver.find_elements(By.CSS_SELECTOR, f"#{dropdown_holder_id} .choices__item--selectable")
    for option in options:
        if option.text.strip().lower() == option_text.strip().lower():
            option.click()
            return

# 🧾 CLI parsing
parser = argparse.ArgumentParser(description="SHL Catalog by Job Category/Title")
parser.add_argument("--job_category", help="e.g. Management and Leadership")
parser.add_argument("--output", default="data/third.csv", help="CSV path")
args = parser.parse_args()

# 💾 Ensure directory
os.makedirs(os.path.dirname(args.output), exist_ok=True)

jobs = []

# ✅ Set up Selenium
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://www.shl.com/solutions/products/product-catalog/job-title/")
time.sleep(2)

# 🧭 Select job category
select_dropdown(driver, "Form_FilteringFormJobTitle_job_category_Holder", args.job_category)

# ⏳ Wait for titles dropdown to populate (if needed)
time.sleep(1)

# 🔍 Submit form
driver.find_element(By.ID, "Form_FilteringFormJobTitle_action_doFilteringForm").click()
time.sleep(2)

# 🔁 Pagination loop
while True:
    WebDriverWait(driver, 5).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.js-target-table-wrapper table tbody tr"))
    )
    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")

    for row in rows:
        try:
            title_el = row.find_element(By.CSS_SELECTOR, "td a")
            title = title_el.text.strip()
            link = title_el.get_attribute("href")
        except:
            title, link = '', ''

        cells = row.find_elements(By.CSS_SELECTOR, "td")
        remote_td = cells[1] if len(cells) > 1 else None
        adaptive_td = cells[2] if len(cells) > 2 else None

        remote = "Yes" if remote_td and remote_td.find_elements(By.CSS_SELECTOR, "span.catalogue__circle.-yes") else "No"
        adaptive = "Yes" if adaptive_td and adaptive_td.find_elements(By.CSS_SELECTOR, "span.catalogue__circle.-yes") else "No"

        key_spans = row.find_elements(By.CSS_SELECTOR, "span.product-catalogue__key")
        keys = ", ".join([span.text.strip() for span in key_spans])

        jobs.append({
            "Job Title": title,
            "Link": link,
            "Remote Testing": remote,
            "Adaptive/IRT": adaptive,
            "Keys": keys
        })

    # ➡️ Pagination
    try:
        next_btn = driver.find_element(By.CSS_SELECTOR, "li.-arrow.-next a.pagination__arrow")
        next_href = next_btn.get_attribute("href")
        if next_href:
            next_url = "https://www.shl.com" + next_href
            print(f"➡️ Next page: {next_url}")
            driver.get(next_url)
            time.sleep(2)
        else:
            break
    except:
        print("✅ Last page reached.")
        break

driver.quit()

# 💾 Save CSV
with open(args.output, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["Job Title", "Link", "Remote Testing", "Adaptive/IRT", "Keys"])
    writer.writeheader()
    writer.writerows(jobs)

print(f"✅ Done. {len(jobs)} jobs saved to {args.output}")
'''
import argparse
import os
import csv
import asyncio
from playwright.sync_api import sync_playwright
from playwright.__main__ import main as playwright_main

# Install browsers if not already installed (for Render compatibility)
try:
    playwright_main(["install", "--with-deps"])
except Exception:
    pass

def parse_args():
    parser = argparse.ArgumentParser(description="SHL Catalog by Job Category/Title using Playwright")
    parser.add_argument("--job_category", help="e.g. Management and Leadership")
    parser.add_argument("--output", default="data/third.csv", help="CSV path")
    return parser.parse_args()

def ensure_output_directory(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def select_dropdown(page, dropdown_holder_id, option_text):
    if not option_text:
        return
    trigger_selector = f"#{dropdown_holder_id} .choices"
    page.click(trigger_selector)
    page.wait_for_selector(f"#{dropdown_holder_id} .choices__list--dropdown", timeout=3000)

    options = page.query_selector_all(f"#{dropdown_holder_id} .choices__item--selectable")
    for option in options:
        if option.inner_text().strip().lower() == option_text.strip().lower():
            option.click()
            break

def scrape_catalog(args):
    jobs = []
    ensure_output_directory(args.output)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://www.shl.com/solutions/products/product-catalog/job-title/", timeout=60000)

        select_dropdown(page, "Form_FilteringFormJobTitle_job_category_Holder", args.job_category)
        page.click("#Form_FilteringFormJobTitle_action_doFilteringForm")
        page.wait_for_timeout(2000)

        while True:
            page.wait_for_selector("div.js-target-table-wrapper table tbody tr", timeout=5000)
            rows = page.query_selector_all("table tbody tr")

            for row in rows:
                try:
                    title_el = row.query_selector("td a")
                    title = title_el.inner_text().strip()
                    link = title_el.get_attribute("href")
                except:
                    title, link = '', ''

                cells = row.query_selector_all("td")
                remote_td = cells[1] if len(cells) > 1 else None
                adaptive_td = cells[2] if len(cells) > 2 else None

                remote = "Yes" if remote_td and remote_td.query_selector("span.catalogue__circle.-yes") else "No"
                adaptive = "Yes" if adaptive_td and adaptive_td.query_selector("span.catalogue__circle.-yes") else "No"

                key_spans = row.query_selector_all("span.product-catalogue__key")
                keys = ", ".join([span.inner_text().strip() for span in key_spans])

                jobs.append({
                    "Job Title": title,
                    "Link": link,
                    "Remote Testing": remote,
                    "Adaptive/IRT": adaptive,
                    "Keys": keys
                })

            try:
                next_btn = page.query_selector("li.-arrow.-next a.pagination__arrow")
                if next_btn:
                    next_href = next_btn.get_attribute("href")
                    if next_href:
                        page.goto("https://www.shl.com" + next_href)
                        page.wait_for_timeout(2000)
                        continue
            except:
                pass

            break

        browser.close()

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Job Title", "Link", "Remote Testing", "Adaptive/IRT", "Keys"])
        writer.writeheader()
        writer.writerows(jobs)

    print(f"Done. {len(jobs)} jobs saved to {args.output}")

if __name__ == "__main__":
    scrape_catalog(parse_args())
