'''
from playwright.sync_api import sync_playwright
import csv
import time

# ✅ Helper to select an item from dropdowns if value is provided
def select_dropdown(page, dropdown_holder_id, option_text):
    if not option_text:
        return  # Skip if no input was given

    dropdown_trigger = f"#{dropdown_holder_id} .choices"
    page.click(dropdown_trigger)
    page.wait_for_selector(f"#{dropdown_holder_id} .choices__list--dropdown", timeout=3000)

    option_selector = f'#{dropdown_holder_id} .choices__item--selectable'
    options = page.query_selector_all(option_selector)

    for option in options:
        if option.inner_text().strip().lower() == option_text.strip().lower():
            option.click()
            return

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://www.shl.com/solutions/products/product-catalog/", wait_until="domcontentloaded")

    # ✅ Optional dropdown filters (set one or more)
    job_family = "Safety"
    job_level = None
    industry = None
    language = None

    # Apply dropdown filters if given
    select_dropdown(page, "Form_FilteringForm_job_family_Holder", job_family)
    select_dropdown(page, "Form_FilteringForm_job_level_Holder", job_level)
    select_dropdown(page, "Form_FilteringForm_industry_Holder", industry)
    select_dropdown(page, "Form_FilteringForm_language_Holder", language)

    # 🔍 Submit the form
    page.click('#Form_FilteringForm_action_doFilteringForm')
    time.sleep(2)

    jobs = []

    # 🔁 Pagination loop
    while True:
        # Wait and collect job entries
        page.wait_for_selector('div.js-target-table-wrapper table tbody tr', timeout=5000)
        rows = page.query_selector_all('table tbody tr')

        for row in rows:
            title_el = row.query_selector('td a')
            title = title_el.inner_text().strip() if title_el else ''
            link = title_el.get_attribute('href') if title_el else ''

            cells = row.query_selector_all('td')
            remote_td = cells[1] if len(cells) > 1 else None
            adaptive_td = cells[2] if len(cells) > 2 else None

            remote = 'Yes' if remote_td and remote_td.query_selector('span.catalogue__circle.-yes') else 'No'
            adaptive = 'Yes' if adaptive_td and adaptive_td.query_selector('span.catalogue__circle.-yes') else 'No'

            key_spans = row.query_selector_all('span.product-catalogue__key')
            keys = ', '.join([span.inner_text().strip() for span in key_spans])

            jobs.append({
                'Job Title': title,
                'Link': link,
                'Remote Testing': remote,
                'Adaptive/IRT': adaptive,
                'Keys': keys
            })

        # Check if a next page exists
        next_btn = page.query_selector('li.-arrow.-next a.pagination__arrow')
        if next_btn:
            next_href = next_btn.get_attribute('href')
            full_url = "https://www.shl.com" + next_href
            print(f"➡️ Navigating to next page: {full_url}")
            page.goto(full_url, wait_until='domcontentloaded')
            time.sleep(2)
        else:
            print("✅ Reached last page.")
            break

    browser.close()

    # 💾 Save all results to CSV
    with open('results2026.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['Job Title', 'Link', 'Remote Testing', 'Adaptive/IRT', 'Keys'])
        writer.writeheader()
        writer.writerows(jobs)

    print(f"✅ Scraping finished. {len(jobs)} jobs saved to results2025.csv")
'''
import argparse
import csv
import os
import time
from playwright.sync_api import sync_playwright

# ✅ Helper to select an item from dropdowns if value is provided
def select_dropdown(page, dropdown_holder_id, option_text):
    if not option_text:
        return
    dropdown_trigger = f"#{dropdown_holder_id} .choices"
    page.click(dropdown_trigger)
    page.wait_for_selector(f"#{dropdown_holder_id} .choices__list--dropdown", timeout=3000)
    options = page.query_selector_all(f'#{dropdown_holder_id} .choices__item--selectable')
    for option in options:
        if option.inner_text().strip().lower() == option_text.strip().lower():
            option.click()
            return

# ✅ CLI Argument Parser
parser = argparse.ArgumentParser(description="SHL Catalog Scraper with Filters")
parser.add_argument("--job_family", help="Job Family filter (e.g. Safety)")
parser.add_argument("--job_level", help="Job Level filter")
parser.add_argument("--industry", help="Industry filter")
parser.add_argument("--language", help="Language filter")
parser.add_argument("--output", default="data/second.csv", help="CSV file path to save results")
args = parser.parse_args()

# ✅ Ensure output folder exists
os.makedirs(os.path.dirname(args.output), exist_ok=True)

jobs = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://www.shl.com/solutions/products/product-catalog/", wait_until="domcontentloaded")

    # ✅ Apply filters
    select_dropdown(page, "Form_FilteringForm_job_family_Holder", args.job_family)
    select_dropdown(page, "Form_FilteringForm_job_level_Holder", args.job_level)
    select_dropdown(page, "Form_FilteringForm_industry_Holder", args.industry)
    select_dropdown(page, "Form_FilteringForm_language_Holder", args.language)

    page.click('#Form_FilteringForm_action_doFilteringForm')
    time.sleep(2)

    # 🔁 Pagination loop
    while True:
        page.wait_for_selector('div.js-target-table-wrapper table tbody tr', timeout=5000)
        rows = page.query_selector_all('table tbody tr')

        for row in rows:
            title_el = row.query_selector('td a')
            title = title_el.inner_text().strip() if title_el else ''
            link = title_el.get_attribute('href') if title_el else ''

            cells = row.query_selector_all('td')
            remote_td = cells[1] if len(cells) > 1 else None
            adaptive_td = cells[2] if len(cells) > 2 else None

            remote = 'Yes' if remote_td and remote_td.query_selector('span.catalogue__circle.-yes') else 'No'
            adaptive = 'Yes' if adaptive_td and adaptive_td.query_selector('span.catalogue__circle.-yes') else 'No'
            key_spans = row.query_selector_all('span.product-catalogue__key')
            keys = ', '.join([span.inner_text().strip() for span in key_spans])

            jobs.append({
                'Job Title': title,
                'Link': link,
                'Remote Testing': remote,
                'Adaptive/IRT': adaptive,
                'Keys': keys
            })

        # ✅ Pagination handling
        next_btn = page.query_selector('li.-arrow.-next a.pagination__arrow')
        if next_btn:
            next_href = next_btn.get_attribute('href')
            if next_href:
                next_url = "https://www.shl.com" + next_href
                print(f"➡️ Going to next page: {next_url}")
                page.goto(next_url, wait_until='domcontentloaded')
                time.sleep(2)
            else:
                break
        else:
            print("✅ Reached last page.")
            break

    browser.close()

# ✅ Save to CSV
with open(args.output, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['Job Title', 'Link', 'Remote Testing', 'Adaptive/IRT', 'Keys'])
    writer.writeheader()
    writer.writerows(jobs)

print(f"✅ Done. {len(jobs)} records saved to {args.output}")
