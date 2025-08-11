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
        print(f"    🔍 Visiting: {podcast_url}")
        page.goto(podcast_url, wait_until="networkidle", timeout=10000)
        time.sleep(random.uniform(1, 2))  # Random delay to be respectful
        
        podcast_data = {}
        
        
    #Try to get podcast rating
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
            #Look for episode dates (common selectors)
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
                    #Get the first (most recent) episode date
                    first_element = elements.first
                    
                    #Try to get datetime attribute first
                    datetime_attr = first_element.get_attribute("datetime")
                    if datetime_attr:
                        recent_date = datetime_attr
                        break
                    
                    #Otherwise get text content
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
    seen_ids = set()  # Track seen IDs to avoid duplicates
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Set to True for headless
        page = browser.new_page()
        
        #Set a reasonable timeout
        page.set_default_timeout(15000)

        charts_url = f"https://podcasts.apple.com/{country_code}/charts"  
        print(f"🌐 Starting scrape of {charts_url}")
        
       # First, get all section titles to process
        page.goto(charts_url, wait_until="networkidle")
        time.sleep(2)  # Give page time to fully load
        
        #Get all section titles first
        buttons = page.locator("button.title__button")
        button_count = buttons.count()
        
        section_titles = []
        for i in range(button_count):
            try:
                title = buttons.nth(i).inner_text().strip()
                section_titles.append(title)
            except:
                section_titles.append(f"Section {i+1}")
        
        print(f"🔍 Found {len(section_titles)} expandable sections: {section_titles}")

        #Process each section by title (more reliable than index)
        for section_idx, expected_title in enumerate(section_titles):
            try:
                #Always start fresh from charts page
                print(f"\n🔄 Navigating to charts page for section {section_idx + 1}/{len(section_titles)}")
                page.goto(charts_url, wait_until="networkidle")
                time.sleep(2)
                
                #Re-locate all buttons
                buttons = page.locator("button.title__button")
                current_button_count = buttons.count()
                
                if current_button_count != len(section_titles):
                    print(f"⚠️ Button count changed! Expected {len(section_titles)}, found {current_button_count}")
                
                #Find the button with matching title
                target_button = None
                actual_title = None
                
                for i in range(min(current_button_count, len(section_titles))):
                    try:
                        btn = buttons.nth(i)
                        title = btn.inner_text().strip()
                        if title == expected_title or i == section_idx:
                            target_button = btn
                            actual_title = title
                            break
                    except Exception as e:
                        print(f"      ⚠️ Error checking button {i}: {e}")
                        continue
                
                if not target_button:
                    print(f"❌ Could not find button for section: {expected_title}")
                    continue
                
                print(f"➡️ Processing section {section_idx + 1}/{len(section_titles)}: {actual_title}")
                
                #Click to expand section
                target_button.click()
                time.sleep(2)  # Wait for expansion
                
                #Wait for podcast links to appear
                try:
                    # Scroll to load more podcasts
                    seen_count = 0
                    max_scroll_attempts = 20  # safety limit
                    scroll_attempts = 0

                    while True:
                        # Get current links
                        html = page.content()
                        current_links = re.findall(r'href="([^"]*podcast/[^/]+/id\d+)"', html)
                        current_count = len(set(current_links))

                        # Stop if:
                        # - no new items loaded after scrolling, OR
                        # - reached the hard limit of 200
                        if current_count == seen_count or current_count >= 200:
                            break

                        seen_count = current_count
                        scroll_attempts += 1
                        if scroll_attempts > max_scroll_attempts:
                            break

                        # Scroll down a bit
                        page.mouse.wheel(0, 2000)
                        time.sleep(1.5)  # wait for new content to load

                except Exception as e:
                    print(f"   ⚠️ No podcast links found in section: {actual_title} - {e}")
                    continue
                
                time.sleep(1)  # Additional wait for content to load

                #Get all podcast links in this section
                html = page.content()
                podcast_links = re.findall(r'href="([^"]*podcast/[^/]+/id\d+)"', html)
                
                #Remove duplicates and limit if specified
                unique_links = list(dict.fromkeys(podcast_links))
                if max_podcasts_per_section:
                    unique_links = unique_links[:max_podcasts_per_section]
                
                print(f"   📦 Found {len(unique_links)} unique podcast links in this section")
                
                if not unique_links:
                    print(f"   ⚠️ No podcast links found in section: {actual_title}")
                    continue

                #Visit each podcast page to get details
                for link_idx, podcast_link in enumerate(unique_links):
                    try:
                        #Extract podcast ID from link
                        id_match = re.search(r'id(\d+)', podcast_link)
                        podcast_id = id_match.group(1) if id_match else None
                        
                        if not podcast_id:
                            print(f"      ⚠️ Could not extract ID from: {podcast_link}")
                            continue
                        
                        #Skip if we've already seen this ID
                        if podcast_id in seen_ids:
                            print(f"      ⏭️ Skipping duplicate ID: {podcast_id}")
                            continue
                        
                        #Make sure link is absolute
                        if podcast_link.startswith('/'):
                            full_url = f"https://podcasts.apple.com{podcast_link}"
                        else:
                            full_url = podcast_link
                        
                        print(f"   🎯 Processing podcast {link_idx + 1}/{len(unique_links)} (ID: {podcast_id})")
                        
                       # Scrape podcast details
                        podcast_data = scrape_podcast_details(page, full_url)
                        podcast_data['id'] = podcast_id
                        podcast_data['section'] = actual_title
                        podcast_data['url'] = full_url
                        podcast_data['scraped_at'] = datetime.now().isoformat()
                        
                        #Add to our data and mark as seen
                        all_podcast_data.append(podcast_data)
                        seen_ids.add(podcast_id)
                        
                        #Small delay between podcasts
                        time.sleep(random.uniform(0.5, 1.5))
                        
                    except Exception as e:
                        print(f"      ❌ Error processing podcast {link_idx + 1}: {e}")
                        continue
                
                print(f"   ✅ Completed section: {actual_title} ({len([d for d in all_podcast_data if d['section'] == actual_title])} podcasts)")
                
            except Exception as e:
                print(f"❌ Error processing section {section_idx + 1} ({expected_title}): {e}")
                continue

        browser.close()

    print(f"\n✅ Scraping complete! Collected data for {len(all_podcast_data)} podcasts")
    
    #Save to multiple formats
    save_results(all_podcast_data, country_code)
    
    return all_podcast_data

def save_results(data, country_code):
    """Save results in multiple formats"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    #Save as JSON
    json_filename = f"podcast_data_{country_code}_{timestamp}.json"
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved JSON to: {json_filename}")
    
    #Save as CSV
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
    
    #Run the scraper
    scrape_all_sections_with_details(
        country_code=args.country,
        max_podcasts_per_section=args.max_per_section
    )
# import requests
# import re
# import time
# import random
# from selectolax.parser import HTMLParser

# # Country list (ISO 2-letter codes)
# countries = ["us", "in", "gb", "au", "ca", "de"]

# headers = {
#     "User-Agent": "Mozilla/5.0"
# }

# # Storage
# country_room_links = {}
# all_podcast_ids = set()
# failed_urls = []

# room_pattern = re.compile(r'^https://podcasts\.apple\.com/([a-z]{2})/room/\d+$')
# id_pattern = re.compile(r'/id(\d+)')

# def fetch_and_parse(url):
#     """Fetch a URL and return an HTMLParser tree or None if failed."""
#     try:
#         r = requests.get(url, headers=headers, timeout=10)
#         if r.status_code != 200:
#             print(f"❌ Failed {url}: Status {r.status_code}")
#             failed_urls.append(url)
#             return None
#         return HTMLParser(r.text)
#     except Exception as e:
#         print(f"⚠ Error fetching {url}: {e}")
#         failed_urls.append(url)
#         return None

# def scrape_page_for_ids_and_rooms(tree, country=None):
#     """Extract all podcast IDs and room links (if country provided)."""
#     if not tree:
#         return

#     for node in tree.css("a"):
#         href = node.attributes.get("href", "")
#         if not href:
#             continue

#         # Absolute link if relative
#         if href.startswith("/"):
#             href = "https://podcasts.apple.com" + href

#         # Extract podcast ID
#         match_id = id_pattern.search(href)
#         if match_id:
#             all_podcast_ids.add(match_id.group(1))

#         # Extract room links (only for browse page)
#         if country:
#             match_room = room_pattern.match(href)
#             if match_room and match_room.group(1) == country:
#                 country_room_links[country].add(href)

# # ====== PHASE 1: Browse pages ======
# for country in countries:
#     url = f"https://podcasts.apple.com/{country}/browse"
#     print(f"\n📄 Fetching browse page for {country}: {url}")

#     country_room_links[country] = set()

#     tree = fetch_and_parse(url)
#     scrape_page_for_ids_and_rooms(tree, country=country)

#     print(f"✅ Found {len(country_room_links[country])} room links for {country}")
#     time.sleep(random.uniform(2, 4))  # polite delay

# # ====== PHASE 2: Room pages ======
# for country, links in country_room_links.items():
#     for link in links:
#         print(f"🔍 Scraping room page: {link}")
#         tree = fetch_and_parse(link)
#         scrape_page_for_ids_and_rooms(tree)
#         time.sleep(random.uniform(2, 5))

# # ====== RETRY FAILED ======
# if failed_urls:
#     print(f"\n🔄 Retrying {len(failed_urls)} failed URLs...")
#     retry_list = failed_urls.copy()
#     failed_urls.clear()
#     for url in retry_list:
#         print(f"🔁 Retrying: {url}")
#         tree = fetch_and_parse(url)
#         scrape_page_for_ids_and_rooms(tree)
#         time.sleep(random.uniform(2, 5))

# # ====== Save results ======
# with open("all_podcast_ids.txt", "w", encoding="utf-8") as f:
#     for pid in sorted(all_podcast_ids):
#         f.write(pid + "\n")

# with open("room_links_per_country.txt", "w", encoding="utf-8") as f:
#     for country, links in country_room_links.items():
#         for link in links:
#             f.write(f"{country},{link}\n")

# print("\n📊 Summary:")
# print(f"Total podcast IDs found: {len(all_podcast_ids)}")
# print(f"Failed URLs (after retry): {len(failed_urls)}")
