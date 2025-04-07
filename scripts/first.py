import argparse
import csv
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ✅ Parse CLI arguments
parser = argparse.ArgumentParser(description="SHL Crawler - Keyword Search (Selenium)")
parser.add_argument("keywords", nargs="+", help="List of keywords to search (e.g., manager engineer analyst)")
args = parser.parse_args()

# ✅ Ensure output directory exists
os.makedirs("data", exist_ok=True)

# ✅ Configure headless browser
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 10)

all_jobs = []

for keyword in args.keywords:
    print(f"🔍 Searching for: {keyword}")
    driver.get("https://www.shl.com/solutions/products/product-catalog/")

    try:
        search_input = wait.until(EC.presence_of_element_located((By.NAME, "keyword")))
        search_input.clear()
        search_input.send_keys(keyword)

        search_button = driver.find_element(By.ID, "Form_FilteringFormKeywords_action_doFilteringForm")
        search_button.click()

        # Wait for table rows to load
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.js-target-table-wrapper table tbody tr")))
        rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")

        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            title_el = cells[0].find_element(By.TAG_NAME, "a") if cells else None
            title = title_el.text.strip() if title_el else ''
            link = title_el.get_attribute("href") if title_el else ''

            remote = 'No'
            adaptive = 'No'

            if len(cells) > 1:
                if cells[1].find_elements(By.CSS_SELECTOR, "span.catalogue__circle.-yes"):
                    remote = 'Yes'
            if len(cells) > 2:
                if cells[2].find_elements(By.CSS_SELECTOR, "span.catalogue__circle.-yes"):
                    adaptive = 'Yes'

            key_spans = row.find_elements(By.CSS_SELECTOR, "span.product-catalogue__key")
            keys = ', '.join([span.text.strip() for span in key_spans])

            all_jobs.append({
                'Job Title': title,
                'Link': link,
                'Remote Testing': remote,
                'Adaptive/IRT': adaptive,
                'Keys': keys
            })

    except Exception as e:
        print(f"⚠️ Error retrieving data for keyword '{keyword}': {str(e)}")

driver.quit()

# ✅ Write results to file
if all_jobs:
    output_file = "data/first.csv"
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=['Job Title', 'Link', 'Remote Testing', 'Adaptive/IRT', 'Keys'])
        writer.writeheader()
        writer.writerows(all_jobs)
    print(f"✅ Saved {len(all_jobs)} results to {output_file}")
else:
    print("❌ No results found.")
