from playwright.sync_api import sync_playwright
import re
import time

def scrape_all_sections(country_code="us"):
    all_ids = set()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # True for headless
        page = browser.new_page()

        url = f"https://podcasts.apple.com/{country_code}/charts"  
        page.goto(url, wait_until="networkidle")

        # Find all section buttons by class name
        buttons = page.locator("button.title__button")
        button_count = buttons.count()

        print(f"🔍 Found {button_count} expandable sections")

        for i in range(button_count):
            btn = buttons.nth(i)
            title = btn.inner_text().strip()

            print(f"➡️ Clicking section: {title}")
            btn.click()

            # Give the section time to expand and load content
            page.wait_for_selector("a[href*='/podcast/']", timeout=5000)
            time.sleep(1)  # extra pause to let lazy-loading finish

            html = page.content()
            ids = re.findall(r"/id(\d{8,})", html)
            print(f"   📦 Found {len(ids)} IDs here")
            all_ids.update(ids)

        browser.close()

    print(f"✅ Total unique IDs: {len(all_ids)}")
    with open("new.txt", "w", encoding="utf-8") as f:
        for pid in sorted(all_ids):
            f.write(pid + "\n")

if __name__ == "__main__":
    scrape_all_sections()
