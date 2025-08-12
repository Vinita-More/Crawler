# Enhanced Spotify podcast scraper with comprehensive logging
import mysql.connector
import requests
from datetime import datetime
import logging
import json
import time
import sys
import traceback
from typing import Dict, List, Any
import password

# Setup comprehensive logging
def setup_logging():
    """Setup multiple log files for different types of information"""
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    simple_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # Error log file
    error_handler = logging.FileHandler('spotify_errors.log')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    logger.addHandler(error_handler)
    
    # Detailed activity log
    debug_handler = logging.FileHandler('spotify_detailed.log')
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(detailed_formatter)
    logger.addHandler(debug_handler)
    
    # Success log
    success_handler = logging.FileHandler('spotify_success.log')
    success_handler.setLevel(logging.INFO)
    success_handler.setFormatter(simple_formatter)
    logger.addHandler(success_handler)
    
    return logger

# Initialize logging
logger = setup_logging()

# Country mapping
COUNTRY_NAMES = {
    "ad": "Andorra", "ae": "United Arab Emirates", "al": "Albania", "ar": "Argentina", "at": "Austria", "au": "Australia",
    "az": "Azerbaijan", "ba": "Bosnia and Herzegovina", "be": "Belgium", "bg": "Bulgaria", "bh": "Bahrain", "bo": "Bolivia",
    "br": "Brazil", "bw": "Botswana", "ca": "Canada", "ch": "Switzerland", "cl": "Chile", "co": "Colombia", "cr": "Costa Rica",
    "cy": "Cyprus", "cz": "Czechia", "de": "Germany", "dk": "Denmark", "do": "Dominican Republic", "dz": "Algeria",
    "ec": "Ecuador", "ee": "Estonia", "eg": "Egypt", "es": "Spain", "fi": "Finland", "fr": "France", "gb": "United Kingdom",
    "ge": "Georgia", "gh": "Ghana", "gr": "Greece", "gt": "Guatemala", "hk": "Hong Kong", "hn": "Honduras", "hr": "Croatia",
    "hu": "Hungary", "id": "Indonesia", "ie": "Ireland", "il": "Israel", "in": "India", "is": "Iceland", "it": "Italy",
    "jm": "Jamaica", "jo": "Jordan", "jp": "Japan", "ke": "Kenya", "kh": "Cambodia", "kr": "South Korea", "kw": "Kuwait",
    "lb": "Lebanon", "lt": "Lithuania", "lu": "Luxembourg", "lv": "Latvia", "ma": "Morocco", "mk": "North Macedonia",
    "mt": "Malta", "mu": "Mauritius", "mw": "Malawi", "mx": "Mexico", "my": "Malaysia", "mz": "Mozambique", "na": "Namibia",
    "ng": "Nigeria", "ni": "Nicaragua", "nl": "Netherlands", "no": "Norway", "np": "Nepal", "nz": "New Zealand", "om": "Oman",
    "pa": "Panama", "pe": "Peru", "ph": "Philippines", "pl": "Poland", "pt": "Portugal", "py": "Paraguay", "qa": "Qatar",
    "ro": "Romania", "rs": "Serbia", "rw": "Rwanda", "sa": "Saudi Arabia", "se": "Sweden", "sg": "Singapore", "si": "Slovenia",
    "sk": "Slovakia", "sn": "Senegal", "sv": "El Salvador", "th": "Thailand", "tn": "Tunisia", "tr": "Turkey",
    "tt": "Trinidad and Tobago", "tw": "Taiwan", "tz": "Tanzania", "ua": "Ukraine", "us": "United States",
    "uy": "Uruguay", "uz": "Uzbekistan", "vn": "Vietnam", "za": "South Africa", "zm": "Zambia", "zw": "Zimbabwe"
}

# Country groups
Three = ["ar", "at", "ca", "cl", "co", "dk", "fi", "fr", "in", "id", "ie", "it", "jp", "nz", "no", "ph", "es", "nl"]
Seventeen = ["au", "us", "gb", "br", "de", "mx", "se"]
One = [
    "al", "ad", "ae", "az", "ba", "be", "bg", "bh", "bo", "br", "bw", "ch", "cr", "cy", "cz", "do",
    "dz", "ec", "ee", "eg", "es", "fi", "fr", "gb", "ge", "gh", "gr", "gt", "hk", "hn", "hr", "hu",
    "id", "ie", "il", "in", "is", "jm", "jo", "jp", "ke", "kh", "kr", "kw", "lb", "lt", "lu", "lv",
    "ma", "mk", "mt", "mu", "mw", "mx", "my", "mz", "na", "ng", "ni", "np", "om", "pa", "pe", "ph",
    "pl", "pt", "py", "qa", "ro", "rs", "rw", "sa", "se", "sg", "si", "sk", "sn", "sv", "th", "tn",
    "tr", "tt", "tw", "tz", "ua", "uy", "uz", "vn", "za", "zm", "zw"
]

# Categories
CATEGORIES_20 = [
    "top", "trending", "top_episodes", "arts", "business", "comedy", "education", "fiction", "history", 
    "health%252520%2526%252520fitness", "leisure", "music", "news", "religion%252520%2526%252520spirituality", 
    "science", "society%252520%2526%252520culture", "sports", "technology", "true%252520crime", "tv%252520%2526%252520film"
]

CATEGORIES_3 = ["top", "trending", "top_episodes"]
CATEGORIES_1 = ["top"]

class SpotifyScrapingStats:
    """Track comprehensive scraping statistics"""
    def __init__(self):
        self.start_time = time.time()
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.rate_limited_requests = 0
        self.timeout_requests = 0
        self.database_errors = 0
        self.total_items_inserted = 0
        self.countries_processed = 0
        self.categories_processed = 0
        self.request_times = []
        
    def log_request(self, success: bool, response_time: float, error_type: str = None):
        """Log individual request statistics"""
        self.total_requests += 1
        self.request_times.append(response_time)
        
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
            if error_type == "rate_limit":
                self.rate_limited_requests += 1
            elif error_type == "timeout":
                self.timeout_requests += 1
    
    def log_database_error(self):
        """Log database error"""
        self.database_errors += 1
    
    def log_items_inserted(self, count: int):
        """Log items inserted"""
        self.total_items_inserted += count
    
    def get_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary statistics"""
        elapsed_time = time.time() - self.start_time
        avg_response_time = sum(self.request_times) / len(self.request_times) if self.request_times else 0
        requests_per_minute = (self.total_requests / elapsed_time) * 60 if elapsed_time > 0 else 0
        
        return {
            "total_runtime_seconds": round(elapsed_time, 2),
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "rate_limited_requests": self.rate_limited_requests,
            "timeout_requests": self.timeout_requests,
            "database_errors": self.database_errors,
            "success_rate_percent": round((self.successful_requests / self.total_requests * 100) if self.total_requests > 0 else 0, 2),
            "average_response_time_ms": round(avg_response_time * 1000, 2),
            "requests_per_minute": round(requests_per_minute, 2),
            "total_items_inserted": self.total_items_inserted,
            "countries_processed": self.countries_processed,
            "categories_processed": self.categories_processed
        }

# Global stats tracker
stats = SpotifyScrapingStats()

def make_api_request(url: str, country: str, category: str, timeout: int = 5) -> tuple:
    """Make API request with detailed logging and error handling"""
    
    request_start_time = time.time()
    
    try:
        logger.debug(f"Making request to: {url}")
        
        headers = {
            'User-Agent': 'SpotifyPodcastScraper/1.0',
            'Accept': 'application/json',
            'Connection': 'keep-alive'
        }
        
        response = requests.get(url, timeout=timeout, headers=headers)
        response_time = time.time() - request_start_time
        
        # Log detailed request info
        request_info = {
            'url': url,
            'country': country,
            'category': category,
            'status_code': response.status_code,
            'response_time_ms': round(response_time * 1000, 2),
            'response_size_bytes': len(response.content),
            'timestamp': datetime.now().isoformat()
        }
        
        # Write request details to JSON log
        with open('api_requests.json', 'a') as f:
            f.write(json.dumps(request_info) + '\n')
        
        if response.status_code == 200:
            stats.log_request(True, response_time)
            logger.info(f"✅ SUCCESS {country.upper()}-{category}: {response.status_code} in {response_time*1000:.0f}ms")
            return True, response.json(), None
            
        elif response.status_code == 429:
            stats.log_request(False, response_time, "rate_limit")
            retry_after = response.headers.get('Retry-After', 'Unknown')
            error_msg = f"Rate limited. Retry after: {retry_after}"
            logger.error(f"🚫 RATE LIMITED {country.upper()}-{category}: {error_msg}")
            return False, None, error_msg
            
        else:
            stats.log_request(False, response_time)
            error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
            logger.error(f"❌ HTTP ERROR {country.upper()}-{category}: {error_msg}")
            return False, None, error_msg
            
    except requests.exceptions.Timeout:
        response_time = time.time() - request_start_time
        stats.log_request(False, response_time, "timeout")
        error_msg = f"Request timeout after {timeout}s"
        logger.error(f"⏰ TIMEOUT {country.upper()}-{category}: {error_msg}")
        return False, None, error_msg
        
    except requests.exceptions.ConnectionError as e:
        response_time = time.time() - request_start_time
        stats.log_request(False, response_time)
        error_msg = f"Connection error: {str(e)[:200]}"
        logger.error(f"🔌 CONNECTION ERROR {country.upper()}-{category}: {error_msg}")
        return False, None, error_msg
        
    except Exception as e:
        response_time = time.time() - request_start_time
        stats.log_request(False, response_time)
        error_msg = f"Unexpected error: {str(e)[:200]}"
        logger.error(f"💥 UNEXPECTED ERROR {country.upper()}-{category}: {error_msg}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False, None, error_msg

def insert_to_database(cur, conn, items: List[Dict], country: str, category: str) -> bool:
    """Insert items to database with detailed error logging"""
    
    insert_sql = """
    INSERT INTO spotify_podcast_charts_with_category
    (showId, showName, showPublisher, showImageUrl, showDescription,
     countryName, countryCode, category, chart_rank, created_at, updated_at)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    
    try:
        inserted_count = 0
        
        for idx, item in enumerate(items):
            try:
                show_uri = item.get("showUri", "")
                show_id = show_uri.split(":")[-1] if show_uri else ""
                
                # Log item details
                item_info = {
                    'country': country,
                    'category': category,
                    'rank': idx + 1,
                    'show_id': show_id,
                    'show_name': item.get("showName", "")[:100],  # Truncate for logging
                    'show_publisher': item.get("showPublisher", "")[:100]
                }
                
                cur.execute(insert_sql, (
                    show_id,
                    item.get("showName", ""),
                    item.get("showPublisher", ""),
                    item.get("showImageUrl", ""),
                    item.get("showDescription", ""),
                    COUNTRY_NAMES.get(country, ""),
                    country,
                    category.replace("-", " ").title(),
                    idx + 1,
                    datetime.now(),
                    datetime.now()
                ))
                
                inserted_count += 1
                
                # Log every 10th item for detailed tracking
                if (idx + 1) % 10 == 0:
                    logger.debug(f"Inserted item #{idx + 1} for {country.upper()}-{category}")
                
            except mysql.connector.Error as db_error:
                stats.log_database_error()
                logger.error(f"🗃️ DATABASE ERROR inserting item #{idx + 1} for {country.upper()}-{category}: {db_error}")
                logger.error(f"Item data: {json.dumps(item_info, indent=2)}")
                continue
                
            except Exception as item_error:
                stats.log_database_error()
                logger.error(f"💥 ITEM PROCESSING ERROR #{idx + 1} for {country.upper()}-{category}: {item_error}")
                logger.error(f"Full traceback: {traceback.format_exc()}")
                continue
        
        # Commit the transaction
        conn.commit()
        stats.log_items_inserted(inserted_count)
        
        logger.info(f"💾 DATABASE SUCCESS {country.upper()}-{category}: {inserted_count}/{len(items)} items inserted")
        return True
        
    except mysql.connector.Error as db_error:
        stats.log_database_error()
        logger.error(f"🗃️ DATABASE COMMIT ERROR {country.upper()}-{category}: {db_error}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        
        try:
            conn.rollback()
            logger.info(f"🔄 Transaction rolled back for {country.upper()}-{category}")
        except:
            logger.error(f"❌ Failed to rollback transaction for {country.upper()}-{category}")
        
        return False
    
    except Exception as e:
        stats.log_database_error()
        logger.error(f"💥 UNEXPECTED DATABASE ERROR {country.upper()}-{category}: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False

def fetch_and_save():
    """Enhanced main function with comprehensive logging"""
    
    logger.info("🚀 STARTING SPOTIFY PODCAST CHART SCRAPING")
    logger.info("=" * 80)
    
    # Database connection
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=password.Password,
            database="trial"
        )
        cur = conn.cursor()
        logger.info("✅ Database connection established")
        
    except mysql.connector.Error as db_error:
        logger.error(f"🗃️ DATABASE CONNECTION FAILED: {db_error}")
        return
    
    # Process all countries
    all_countries = sorted(set(One + Three + Seventeen))
    total_combinations = sum([
        len(CATEGORIES_20) if country in Seventeen else
        len(CATEGORIES_3) if country in Three else
        len(CATEGORIES_1)
        for country in all_countries
    ])
    
    logger.info(f"📊 SCRAPING PLAN:")
    logger.info(f"   • Countries to process: {len(all_countries)}")
    logger.info(f"   • Total API calls: {total_combinations}")
    logger.info(f"   • Seventeen countries (20 categories): {len(Seventeen)}")
    logger.info(f"   • Three countries (3 categories): {len(Three)}")
    logger.info(f"   • One countries (1 category): {len(One)}")
    logger.info("=" * 80)
    
    processed_combinations = 0
    
    for country in all_countries:
        try:
            stats.countries_processed += 1
            
            # Determine categories for this country
            if country in Seventeen:
                categories = CATEGORIES_20
                logger.info(f"🌟 Processing {country.upper()} ({COUNTRY_NAMES.get(country)}) - 20 categories")
            elif country in Three:
                categories = CATEGORIES_3
                logger.info(f"🥉 Processing {country.upper()} ({COUNTRY_NAMES.get(country)}) - 3 categories")
            else:
                categories = CATEGORIES_1
                logger.info(f"🥇 Processing {country.upper()} ({COUNTRY_NAMES.get(country)}) - 1 category")
            
            country_start_time = time.time()
            country_success = 0
            country_failures = 0
            
            for category in categories:
                stats.categories_processed += 1
                processed_combinations += 1
                
                url = f"https://podcastcharts.byspotify.com/api/charts/{category}?region={country}"
                
                progress_percent = (processed_combinations / total_combinations) * 100
                logger.info(f"📡 [{processed_combinations}/{total_combinations}] ({progress_percent:.1f}%) Fetching {country.upper()}-{category}")
                
                # Make API request
                success, data, error = make_api_request(url, country, category)
                
                if success and data:
                    # Process response data
                    items = data if isinstance(data, list) else data.get("items", [])
                    
                    if not isinstance(items, list):
                        items = []
                        logger.warning(f"⚠️ Unexpected data format for {country.upper()}-{category}")
                    
                    logger.info(f"📊 Retrieved {len(items)} items for {country.upper()}-{category}")
                    
                    # Insert to database
                    if items:
                        db_success = insert_to_database(cur, conn, items, country, category)
                        if db_success:
                            country_success += 1
                        else:
                            country_failures += 1
                    else:
                        logger.warning(f"⚠️ No items to insert for {country.upper()}-{category}")
                        country_success += 1  # Still count as success
                else:
                    country_failures += 1
                    logger.error(f"❌ Failed to fetch {country.upper()}-{category}: {error}")
                
                # Small delay between requests to be respectful
                time.sleep(0.1)
            
            # Country summary
            country_duration = time.time() - country_start_time
            logger.info(f"📋 COUNTRY SUMMARY {country.upper()}: {country_success}/{len(categories)} successful in {country_duration:.1f}s")
            
        except Exception as country_error:
            logger.error(f"💥 COUNTRY PROCESSING ERROR {country.upper()}: {country_error}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            continue
    
    # Cleanup
    try:
        cur.close()
        conn.close()
        logger.info("✅ Database connection closed")
    except Exception as cleanup_error:
        logger.error(f"❌ Error closing database: {cleanup_error}")
    
    # Final comprehensive report
    print_final_report()

def print_final_report():
    """Print comprehensive final scraping report"""
    
    summary = stats.get_summary()
    
    logger.info(f"\n{'='*80}")
    logger.info(f"🎯 SPOTIFY PODCAST SCRAPING - FINAL REPORT")
    logger.info(f"{'='*80}")
    
    logger.info(f"⏱️ TIMING STATISTICS:")
    logger.info(f"   • Total Runtime: {summary['total_runtime_seconds']} seconds")
    logger.info(f"   • Average Response Time: {summary['average_response_time_ms']}ms")
    logger.info(f"   • Requests Per Minute: {summary['requests_per_minute']}")
    logger.info(f"")
    
    logger.info(f"📊 REQUEST STATISTICS:")
    logger.info(f"   • Total API Requests: {summary['total_requests']:,}")
    logger.info(f"   • Successful Requests: {summary['successful_requests']:,}")
    logger.info(f"   • Failed Requests: {summary['failed_requests']:,}")
    logger.info(f"   • Rate Limited: {summary['rate_limited_requests']:,}")
    logger.info(f"   • Timeouts: {summary['timeout_requests']:,}")
    logger.info(f"   • Success Rate: {summary['success_rate_percent']}%")
    logger.info(f"")
    
    logger.info(f"🗃️ DATABASE STATISTICS:")
    logger.info(f"   • Total Items Inserted: {summary['total_items_inserted']:,}")
    logger.info(f"   • Database Errors: {summary['database_errors']:,}")
    logger.info(f"   • Countries Processed: {summary['countries_processed']:,}")
    logger.info(f"   • Categories Processed: {summary['categories_processed']:,}")
    logger.info(f"")
    
    logger.info(f"📁 LOG FILES CREATED:")
    logger.info(f"   • spotify_errors.log (errors only)")
    logger.info(f"   • spotify_detailed.log (all activity)")
    logger.info(f"   • spotify_success.log (successful operations)")
    logger.info(f"   • api_requests.json (structured API data)")
    
    logger.info(f"{'='*80}")
    
    # Also save summary to JSON
    with open('scraping_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    logger.info(f"💾 Summary saved to scraping_summary.json")

if __name__ == "__main__":
    try:
        fetch_and_save()
    except KeyboardInterrupt:
        logger.info("\n⚠️ Scraping interrupted by user")
        print_final_report()
    except Exception as e:
        logger.error(f"💥 CRITICAL ERROR: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        print_final_report()