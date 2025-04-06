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
import os
import asyncio
from playwright.async_api import async_playwright

# ✅ Parse CLI arguments
parser = argparse.ArgumentParser(description="SHL Crawler - Keyword Search")
parser.add_argument("keywords", nargs="+", help="List of keywords to search (e.g., manager engineer analyst)")
args = parser.parse_args()

# ✅ Ensure output directory exists
os.makedirs("data", exist_ok=True)

async def main():
    all_jobs = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        for keyword in args.keywords:
            print(f"🔍 Searching for: {keyword}")
            await page.goto("https://www.shl.com/solutions/products/product-catalog/", timeout=60000)

            try:
                # Fill in the search input
                await page.fill('input[name="keyword"]', keyword)
                await page.click('#Form_FilteringFormKeywords_action_doFilteringForm')
                await page.wait_for_selector("table tbody tr", timeout=10000)

                rows = await page.query_selector_all("table tbody tr")

                for row in rows:
                    title_el = await row.query_selector("td a")
                    title = await title_el.inner_text() if title_el else ""
                    link = await title_el.get_attribute("href") if title_el else ""

                    tds = await row.query_selector_all("td")
                    remote = adaptive = "No"

                    if len(tds) > 1:
                        remote_yes = await tds[1].query_selector("span.catalogue__circle.-yes")
                        remote = "Yes" if remote_yes else "No"

                    if len(tds) > 2:
                        adaptive_yes = await tds[2].query_selector("span.catalogue__circle.-yes")
                        adaptive = "Yes" if adaptive_yes else "No"

                    key_spans = await row.query_selector_all("span.product-catalogue__key")
                    keys = ", ".join([await span.inner_text() for span in key_spans])

                    all_jobs.append({
                        'Job Title': title,
                        'Link': link,
                        'Remote Testing': remote,
                        'Adaptive/IRT': adaptive,
                        'Keys': keys
                    })

            except Exception as e:
                print(f"⚠️ Error retrieving data for keyword '{keyword}': {str(e)}")

        await browser.close()

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

# ✅ Run the script
asyncio.run(main())
