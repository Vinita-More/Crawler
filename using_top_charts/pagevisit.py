from playwright.sync_api import sync_playwright
import re
import time
import csv
import json
from datetime import datetime
import random

def scrape_podcast_details(page, podcast_url):
    """Scrape ratings and recent episode date from a specific podcast page"""
    try:
        print(f"  🔍 Visiting: {podcast_url}")
        page.goto(podcast_url, wait_until="networkidle", timeout=10000)
        time.sleep(random.uniform(1, 2))  # Random delay to be respectful
        
        podcast_data = {}
        
        # Try to get podcast rating
        try:
            # Look for rating elements (Apple uses different selectors)
            rating_selectors = [
                ".we-customer-ratings__averages__display",
                ".we-rating-stars",
                "[data-test-rating]",
                ".rating-value"
            ]
            
            rating = None
            for selector in rating_selectors:
                if page.locator(selector).count() > 0:
                    rating_element = page.locator(selector).first
                    rating_text = rating_element.inner_text().strip()
                    # Extract numeric rating
                    rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                    if rating_match:
                        rating = float(rating_match.group(1))
                        break
            
            podcast_data['rating'] = rating
        except Exception as e:
            print(f"      ⚠️ Could not get rating: {e}")
            podcast_data['rating'] = None
        
        # Try to get recent episode date
        try:
            # Look for episode dates (common selectors)
            date_selectors = [
                ".episode-date",
                ".release-date", 
                "[data-test-episode-date]",
                ".we-truncate time",
                "time[datetime]"
            ]
            
            recent_date = None
            for selector in date_selectors:
                elements = page.locator(selector)
                if elements.count() > 0:
                    # Get the first (most recent) episode date
                    first_element = elements.first
                    
                    # Try to get datetime attribute first
                    datetime_attr = first_element.get_attribute("datetime")
                    if datetime_attr:
                        recent_date = datetime_attr
                        break
                    
                    # Otherwise get text content
                    date_text = first_element.inner_text().strip()
                    if date_text:
                        recent_date = date_text
                        break
            
            podcast_data['recent_episode_date'] = recent_date
        except Exception as e:
            print(f"      ⚠️ Could not get recent episode date: {e}")
            podcast_data['recent_episode_date'] = None
        
        # Try to get podcast title for reference
        try:
            title_selectors = [
                "h1.product-header__title",
                ".we-truncate.we-truncate--single-line h1",
                "h1"
            ]
            
            title = None
            for selector in title_selectors:
                if page.locator(selector).count() > 0:
                    title = page.locator(selector).first.inner_text().strip()
                    break
            
            podcast_data['title'] = title
        except Exception as e:
            print(f"      ⚠️ Could not get title: {e}")
            podcast_data['title'] = None
        
        print(f"      ✅ Rating: {podcast_data['rating']}, Date: {podcast_data['recent_episode_date']}")
        return podcast_data
        
    except Exception as e:
        print(f"      ❌ Error scraping {podcast_url}: {e}")
        return {
            'rating': None,
            'recent_episode_date': None,
            'title': None,
            'error': str(e)
        }

def scrape_all_sections_with_details(country_code="us", max_podcasts_per_section=None):
    all_podcast_data = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Set to True for headless
        page = browser.new_page()
        
        # Set a reasonable timeout
        page.set_default_timeout(15000)

        charts_url = f"https://podcasts.apple.com/{country_code}/charts"  
        print(f"🌐 Starting scrape of {charts_url}")
        
        page.goto(charts_url, wait_until="networkidle")

        # Find all section buttons
        buttons = page.locator("button.title__button")
        button_count = buttons.count()

        print(f"🔍 Found {button_count} expandable sections")

        for section_idx in range(button_count):
            try:
                # Re-locate buttons as DOM might have changed
                buttons = page.locator("button.title__button")
                btn = buttons.nth(section_idx)
                section_title = btn.inner_text().strip()

                print(f"\n➡️ Processing section {section_idx + 1}/{button_count}: {section_title}")
                
                # Click to expand section
                btn.click()
                page.wait_for_selector("a[href*='/podcast/']", timeout=5000)
                time.sleep(1)

                # Get all podcast links in this section
                html = page.content()
                podcast_links = re.findall(r'href="([^"]*podcast/[^/]+/id\d+)"', html)
                
                # Remove duplicates and limit if specified
                unique_links = list(dict.fromkeys(podcast_links))
                if max_podcasts_per_section:
                    unique_links = unique_links[:max_podcasts_per_section]
                
                print(f"   📦 Found {len(unique_links)} unique podcast links in this section")

                # Visit each podcast page to get details
                for link_idx, podcast_link in enumerate(unique_links):
                    try:
                        # Extract podcast ID from link
                        id_match = re.search(r'id(\d+)', podcast_link)
                        podcast_id = id_match.group(1) if id_match else None
                        
                        # Make sure link is absolute
                        if podcast_link.startswith('/'):
                            full_url = f"https://podcasts.apple.com{podcast_link}"
                        else:
                            full_url = podcast_link
                        
                        print(f"   🎯 Processing podcast {link_idx + 1}/{len(unique_links)} (ID: {podcast_id})")
                        
                        # Scrape podcast details
                        podcast_data = scrape_podcast_details(page, full_url)
                        podcast_data['id'] = podcast_id
                        podcast_data['section'] = section_title
                        podcast_data['url'] = full_url
                        podcast_data['scraped_at'] = datetime.now().isoformat()
                        
                        all_podcast_data.append(podcast_data)
                        
                        # Small delay between podcasts
                        time.sleep(random.uniform(0.5, 1.5))
                        
                    except Exception as e:
                        print(f"      ❌ Error processing podcast {link_idx + 1}: {e}")
                        continue
                
                # Navigate back to charts page for next section
                print(f"   🔙 Returning to charts page...")
                page.goto(charts_url, wait_until="networkidle")
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Error processing section {section_idx + 1}: {e}")
                # Try to return to charts page
                try:
                    page.goto(charts_url, wait_until="networkidle")
                except:
                    pass
                continue

        browser.close()

    print(f"\n✅ Scraping complete! Collected data for {len(all_podcast_data)} podcasts")
    
    # Save to multiple formats
    save_results(all_podcast_data, country_code)
    
    return all_podcast_data

def save_results(data, country_code):
    """Save results in multiple formats"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save as JSON
    json_filename = f"podcast_data_{country_code}_{timestamp}.json"
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved JSON to: {json_filename}")
    
    # Save as CSV
    csv_filename = f"podcast_data_{country_code}_{timestamp}.csv"
    if data:
        fieldnames = ['id', 'title', 'rating', 'recent_episode_date', 'section', 'url', 'scraped_at', 'error']
        with open(csv_filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f"💾 Saved CSV to: {csv_filename}")
    
    # Save just IDs (for backward compatibility)
    ids_filename = f"podcast_ids_{country_code}_{timestamp}.txt"
    with open(ids_filename, "w", encoding="utf-8") as f:
        for item in data:
            if item.get('id'):
                f.write(item['id'] + "\n")
    print(f"💾 Saved IDs to: {ids_filename}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Scrape Apple Podcasts with detailed information")
    parser.add_argument("--country", default="us", help="Country code (us, uk, ca, etc.)")
    parser.add_argument("--max-per-section", type=int, help="Maximum podcasts to scrape per section")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    
    args = parser.parse_args()
    
    # Run the scraper
    scrape_all_sections_with_details(
        country_code=args.country,
        max_podcasts_per_section=args.max_per_section
    )