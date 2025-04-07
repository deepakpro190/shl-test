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


import argparse
import csv
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ✅ Helper to select an item from dropdowns if value is provided
def select_dropdown(driver, dropdown_holder_id, option_text):
    if not option_text:
        return

    dropdown_trigger = driver.find_element(By.CSS_SELECTOR, f"#{dropdown_holder_id} .choices")
    dropdown_trigger.click()

    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, f"#{dropdown_holder_id} .choices__list--dropdown"))
    )

    options = driver.find_elements(By.CSS_SELECTOR, f'#{dropdown_holder_id} .choices__item--selectable')
    for option in options:
        if option.text.strip().lower() == option_text.strip().lower():
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

# ✅ Setup Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
driver.get("https://www.shl.com/solutions/products/product-catalog/")

# ✅ Apply filters
select_dropdown(driver, "Form_FilteringForm_job_family_Holder", args.job_family)
select_dropdown(driver, "Form_FilteringForm_job_level_Holder", args.job_level)
select_dropdown(driver, "Form_FilteringForm_industry_Holder", args.industry)
select_dropdown(driver, "Form_FilteringForm_language_Holder", args.language)

driver.find_element(By.ID, "Form_FilteringForm_action_doFilteringForm").click()
time.sleep(2)

# 🔁 Pagination loop
while True:
    WebDriverWait(driver, 5).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.js-target-table-wrapper table tbody tr'))
    )
    rows = driver.find_elements(By.CSS_SELECTOR, 'table tbody tr')

    for row in rows:
        try:
            title_el = row.find_element(By.CSS_SELECTOR, 'td a')
            title = title_el.text.strip()
            link = title_el.get_attribute('href')
        except:
            title, link = '', ''

        cells = row.find_elements(By.CSS_SELECTOR, 'td')
        remote_td = cells[1] if len(cells) > 1 else None
        adaptive_td = cells[2] if len(cells) > 2 else None

        remote = 'Yes' if remote_td and remote_td.find_elements(By.CSS_SELECTOR, 'span.catalogue__circle.-yes') else 'No'
        adaptive = 'Yes' if adaptive_td and adaptive_td.find_elements(By.CSS_SELECTOR, 'span.catalogue__circle.-yes') else 'No'

        key_spans = row.find_elements(By.CSS_SELECTOR, 'span.product-catalogue__key')
        keys = ', '.join([span.text.strip() for span in key_spans])

        jobs.append({
            'Job Title': title,
            'Link': link,
            'Remote Testing': remote,
            'Adaptive/IRT': adaptive,
            'Keys': keys
        })

    # ✅ Pagination handling
    try:
        next_btn = driver.find_element(By.CSS_SELECTOR, 'li.-arrow.-next a.pagination__arrow')
        next_href = next_btn.get_attribute('href')
        if next_href:
            next_url = "https://www.shl.com" + next_href
            print(f"➡️ Going to next page: {next_url}")
            driver.get(next_url)
            time.sleep(2)
        else:
            break
    except:
        print("✅ Reached last page.")
        break

driver.quit()

# ✅ Save to CSV
with open(args.output, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['Job Title', 'Link', 'Remote Testing', 'Adaptive/IRT', 'Keys'])
    writer.writeheader()
    writer.writerows(jobs)

print(f"✅ Done. {len(jobs)} records saved to {args.output}")
'''
import argparse
import csv
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Function to select dropdown option by visible text (using Choices.js)
def select_dropdown(driver, wait, holder_id, option_text):
    if not option_text:
        return

    # Click to open the dropdown
    container = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"#{holder_id} .choices")))
    container.click()

    # Wait for dropdown options
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f"#{holder_id} .choices__list--dropdown")))

    # Find and click the matching option
    options = driver.find_elements(By.CSS_SELECTOR, f"#{holder_id} .choices__item--selectable")
    for option in options:
        if option.text.strip().lower() == option_text.strip().lower():
            option.click()
            break

# Main scraper function
def main():
    parser = argparse.ArgumentParser(description="SHL Catalog Scraper with Filters (Selenium)")
    parser.add_argument("--job_family", help="Job Family filter (e.g. Safety)")
    parser.add_argument("--job_level", help="Job Level filter")
    parser.add_argument("--industry", help="Industry filter")
    parser.add_argument("--language", help="Language filter")
    parser.add_argument("--output", default="data/second.csv", help="CSV file path to save results")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    jobs = []

    # Setup headless browser
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 10)

    driver.get("https://www.shl.com/solutions/products/product-catalog/")

    try:
        select_dropdown(driver, wait, "Form_FilteringForm_job_family_Holder", args.job_family)
        select_dropdown(driver, wait, "Form_FilteringForm_job_level_Holder", args.job_level)
        select_dropdown(driver, wait, "Form_FilteringForm_industry_Holder", args.industry)
        select_dropdown(driver, wait, "Form_FilteringForm_language_Holder", args.language)

        driver.find_element(By.ID, "Form_FilteringForm_action_doFilteringForm").click()
        time.sleep(2)

        while True:
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.js-target-table-wrapper table tbody tr")))
            rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")

            for row in rows:
                try:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    title_el = cells[0].find_element(By.TAG_NAME, "a") if cells else None
                    title = title_el.text.strip() if title_el else ''
                    link = title_el.get_attribute("href") if title_el else ''
                except:
                    title, link = '', ''

                remote = 'Yes' if len(cells) > 1 and cells[1].find_elements(By.CSS_SELECTOR, 'span.catalogue__circle.-yes') else 'No'
                adaptive = 'Yes' if len(cells) > 2 and cells[2].find_elements(By.CSS_SELECTOR, 'span.catalogue__circle.-yes') else 'No'
                key_spans = row.find_elements(By.CSS_SELECTOR, 'span.product-catalogue__key')
                keys = ', '.join([span.text.strip() for span in key_spans])

                jobs.append({
                    'Job Title': title,
                    'Link': link,
                    'Remote Testing': remote,
                    'Adaptive/IRT': adaptive,
                    'Keys': keys
                })

            try:
                next_btn = driver.find_element(By.CSS_SELECTOR, "li.-arrow.-next a.pagination__arrow")
                next_href = next_btn.get_attribute("href")
                if next_href:
                    next_url = "https://www.shl.com" + next_href
                    print(f"➡️ Going to next page: {next_url}")
                    driver.get(next_url)
                    time.sleep(2)
                else:
                    break
            except:
                print("✅ Reached last page.")
                break

    finally:
        driver.quit()

    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['Job Title', 'Link', 'Remote Testing', 'Adaptive/IRT', 'Keys'])
        writer.writeheader()
        writer.writerows(jobs)

    print(f"✅ Done. {len(jobs)} records saved to {args.output}")

if __name__ == "__main__":
    main()
