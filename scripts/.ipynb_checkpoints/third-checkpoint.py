import argparse
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
