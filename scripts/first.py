'''
# Step 2: Import required modules
from playwright.sync_api import sync_playwright
import csv
# Step 3: Start the Playwright session
with sync_playwright() as p:
    # Launch a headless Chromium browser
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # Go to the SHL job catalog page
    page.goto("https://www.shl.com/solutions/products/product-catalog/")

    # Fill the search input with the keyword "manager"
    page.fill('input[name="keyword"]', 'manager')

    # Click the search button
    page.click('#Form_FilteringFormKeywords_action_doFilteringForm')

    # Optional: short delay to let JS kick in
    import time
    time.sleep(2)

# ✅ Wait for actual rows to load (this is the most solid indicator)
    page.wait_for_selector('div.js-target-table-wrapper table tbody tr')
    # Select all rows in the results table
    rows = page.query_selector_all('table tbody tr')

    # Create a list to hold the job data
    jobs = []

    # Loop through each row and extract data
    for row in rows:
        title_el = row.query_selector('td a')  # Title and link
        title = title_el.inner_text().strip() if title_el else ''
        link = title_el.get_attribute('href') if title_el else ''
            # Get all <td> elements (columns) from this row
        cells = row.query_selector_all('td')
    
        # Remote testing and Adaptive/IRT are assumed to be in fixed positions (e.g. 1st and 2nd "custom__table-heading__general")
        remote_td = cells[1] if len(cells) > 1 else None
        adaptive_td = cells[2] if len(cells) > 2 else None
    
        remote = 'Yes' if remote_td and remote_td.query_selector('span.catalogue__circle.-yes') else 'No'
        adaptive = 'Yes' if adaptive_td and adaptive_td.query_selector('span.catalogue__circle.-yes') else 'No'
        key_spans = row.query_selector_all('span.product-catalogue__key')  # Tags/keys
        keys = ', '.join([span.inner_text().strip() for span in key_spans])

        # Add the job info to the list
        jobs.append({
            'Job Title': title,
            'Link': link,
            'Remote Testing' : remote,
            'Adaptive/IRT' : adaptive,
            'Keys': keys
        })

    # Close the browser
    browser.close()

    # Save data to a CSV file
    with open('results.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['Job Title', 'Link','Remote Testing' , 'Adaptive/IRT' , 'Keys'])
        writer.writeheader()
        writer.writerows(jobs)

    print("✅ CSV created: results.csv")
'''
'''
import argparse
import csv
import time
import os
from playwright.sync_api import sync_playwright

# ✅ Parse CLI arguments
parser = argparse.ArgumentParser(description="SHL Crawler - Keyword Search")
parser.add_argument("keywords", nargs="+", help="List of keywords to search (e.g., manager engineer analyst)")
args = parser.parse_args()

# ✅ Ensure output directory exists
os.makedirs("data", exist_ok=True)

all_jobs = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    for keyword in args.keywords:
        print(f"🔍 Searching for: {keyword}")
        page.goto("https://www.shl.com/solutions/products/product-catalog/")
        page.fill('input[name="keyword"]', keyword)
        page.click('#Form_FilteringFormKeywords_action_doFilteringForm')
        time.sleep(2)

        try:
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

                all_jobs.append({
                    'Job Title': title,
                    'Link': link,
                    'Remote Testing': remote,
                    'Adaptive/IRT': adaptive,
                    'Keys': keys
                })

        except Exception as e:
            print(f"⚠️ Error retrieving data for keyword '{keyword}': {str(e)}")

    browser.close()

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
'''
import argparse
import csv
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ✅ Parse CLI arguments
parser = argparse.ArgumentParser(description="SHL Crawler - Keyword Search")
parser.add_argument("keywords", nargs="+", help="List of keywords to search (e.g., manager engineer analyst)")
args = parser.parse_args()

# ✅ Ensure output directory exists
os.makedirs("data", exist_ok=True)

all_jobs = []

# ✅ Setup Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

for keyword in args.keywords:
    print(f"🔍 Searching for: {keyword}")
    driver.get("https://www.shl.com/solutions/products/product-catalog/")
    time.sleep(2)

    try:
        search_input = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.NAME, "keyword"))
        )
        search_input.clear()
        search_input.send_keys(keyword)

        search_button = driver.find_element(By.ID, "Form_FilteringFormKeywords_action_doFilteringForm")
        search_button.click()

        time.sleep(2)
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
