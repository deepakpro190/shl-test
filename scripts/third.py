import argparse
import os
import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def parse_args():
    parser = argparse.ArgumentParser(description="SHL Catalog by Job Category/Title using Selenium")
    parser.add_argument("--job_category", help="e.g. Management and Leadership")
    parser.add_argument("--output", default="data/third.csv", help="CSV path")
    return parser.parse_args()

def ensure_output_directory(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def select_dropdown(driver, wait, holder_id, option_text):
    if not option_text:
        return

    trigger_selector = f"#{holder_id} .choices"
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, trigger_selector))).click()
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f"#{holder_id} .choices__list--dropdown")))
    
    options = driver.find_elements(By.CSS_SELECTOR, f"#{holder_id} .choices__item--selectable")
    for option in options:
        if option.text.strip().lower() == option_text.strip().lower():
            option.click()
            break

def scrape_catalog(args):
    jobs = []
    ensure_output_directory(args.output)

    # Setup Selenium headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 10)

    driver.get("https://www.shl.com/solutions/products/product-catalog/job-title/")

    try:
        select_dropdown(driver, wait, "Form_FilteringFormJobTitle_job_category_Holder", args.job_category)
        driver.find_element(By.ID, "Form_FilteringFormJobTitle_action_doFilteringForm").click()
        time.sleep(2)

        while True:
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table tbody tr")))
            rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")

            for row in rows:
                try:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    title_el = cells[0].find_element(By.TAG_NAME, "a") if cells else None
                    title = title_el.text.strip() if title_el else ''
                    link = title_el.get_attribute("href") if title_el else ''
                except:
                    title, link = '', ''

                remote = "Yes" if len(cells) > 1 and cells[1].find_elements(By.CSS_SELECTOR, "span.catalogue__circle.-yes") else "No"
                adaptive = "Yes" if len(cells) > 2 and cells[2].find_elements(By.CSS_SELECTOR, "span.catalogue__circle.-yes") else "No"
                key_spans = row.find_elements(By.CSS_SELECTOR, "span.product-catalogue__key")
                keys = ", ".join([span.text.strip() for span in key_spans])

                jobs.append({
                    "Job Title": title,
                    "Link": link,
                    "Remote Testing": remote,
                    "Adaptive/IRT": adaptive,
                    "Keys": keys
                })

            # Check and go to next page
            try:
                next_btn = driver.find_element(By.CSS_SELECTOR, "li.-arrow.-next a.pagination__arrow")
                next_href = next_btn.get_attribute("href")
                if next_href:
                    next_url = "https://www.shl.com" + next_href
                    print(f"➡️ Navigating to: {next_url}")
                    driver.get(next_url)
                    time.sleep(2)
                    continue
            except:
                break

    finally:
        driver.quit()

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Job Title", "Link", "Remote Testing", "Adaptive/IRT", "Keys"])
        writer.writeheader()
        writer.writerows(jobs)

    print(f"✅ Done. {len(jobs)} jobs saved to {args.output}")

if __name__ == "__main__":
    scrape_catalog(parse_args())
