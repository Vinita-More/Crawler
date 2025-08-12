import time
import requests
from datetime import datetime, timedelta
from collections import deque
import json
from typing import Optional, Dict, Any

class APIRateLimiter:
    def __init__(self, api_url: str = "https://podcastcharts.byspotify.com/api/charts/top?region=us"):
        self.api_url = api_url
        self.request_times = deque()  # Store timestamps of requests
        self.start_time = time.time()
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.rate_limited_requests = 0
        
    def clean_old_requests(self, window_seconds: int = 60):
        """Remove request timestamps older than the specified window"""
        current_time = time.time()
        while self.request_times and current_time - self.request_times[0] > window_seconds:
            self.request_times.popleft()
    
    def get_current_rate_per_minute(self) -> float:
        """Calculate current requests per minute in the last 60 seconds"""
        self.clean_old_requests(60)
        return len(self.request_times)
    
    def get_current_rate_per_second(self) -> float:
        """Calculate current requests per second in the last 60 seconds"""
        return self.get_current_rate_per_minute() / 60.0
    
    def get_average_rate_per_minute(self) -> float:
        """Calculate average requests per minute since start"""
        elapsed_time = time.time() - self.start_time
        if elapsed_time < 60:
            return (self.total_requests / elapsed_time) * 60
        return (self.total_requests / elapsed_time) * 60
    
    def get_average_rate_per_second(self) -> float:
        """Calculate average requests per second since start"""
        elapsed_time = time.time() - self.start_time
        return self.total_requests / elapsed_time if elapsed_time > 0 else 0
    
    def make_request(self, params: Optional[Dict[str, Any]] = None, 
                    headers: Optional[Dict[str, str]] = None) -> requests.Response:
        """Make a request and track timing/success"""
        current_time = time.time()
        self.request_times.append(current_time)
        self.total_requests += 1
        
        try:
            # Default headers
            if headers is None:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'application/json'
                }
            
            response = requests.get(self.api_url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                self.successful_requests += 1
            elif response.status_code == 429:
                self.rate_limited_requests += 1
                print(f"⚠️  Rate limited! Status: {response.status_code}")
                # Check for Retry-After header
                retry_after = response.headers.get('Retry-After')
                if retry_after:
                    print(f"   Retry after: {retry_after} seconds")
            else:
                self.failed_requests += 1
                print(f"❌ Request failed with status: {response.status_code}")
            
            return response
            
        except requests.RequestException as e:
            self.failed_requests += 1
            print(f"❌ Request exception: {e}")
            raise
    
    def print_stats(self):
        """Print current statistics"""
        elapsed_time = time.time() - self.start_time
        print(f"\n📊 API Rate Statistics:")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"⏰ Running time: {elapsed_time:.1f} seconds")
        print(f"📈 Total requests: {self.total_requests}")
        print(f"✅ Successful: {self.successful_requests}")
        print(f"❌ Failed: {self.failed_requests}")
        print(f"⚠️  Rate limited: {self.rate_limited_requests}")
        print(f"")
        print(f"🏃 Current rate (last 60s): {self.get_current_rate_per_minute():.1f} req/min ({self.get_current_rate_per_second():.2f} req/s)")
        print(f"📊 Average rate: {self.get_average_rate_per_minute():.1f} req/min ({self.get_average_rate_per_second():.2f} req/s)")
        
        if self.total_requests > 0:
            success_rate = (self.successful_requests / self.total_requests) * 100
            print(f"✨ Success rate: {success_rate:.1f}%")

def test_rate_limits(delay_seconds: float = 1.0, max_requests: int = 100):
    """Test the API with a specific delay between requests"""
    limiter = APIRateLimiter()
    
    print(f"🚀 Starting API rate test...")
    print(f"⏱️  Delay between requests: {delay_seconds} seconds")
    print(f"🎯 Max requests: {max_requests}")
    print(f"🔗 API URL: {limiter.api_url}")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    try:
        for i in range(max_requests):
            print(f"Request {i+1}/{max_requests}...", end=" ")
            
            try:
                response = limiter.make_request()
                print(f"Status: {response.status_code}")
                
                # Print stats every 10 requests
                if (i + 1) % 10 == 0:
                    limiter.print_stats()
                    
            except Exception as e:
                print(f"Error: {e}")
            
            # Stop if we hit rate limits multiple times
            if limiter.rate_limited_requests >= 3:
                print(f"\n⛔ Stopping after {limiter.rate_limited_requests} rate limit hits")
                break
            
            time.sleep(delay_seconds)
            
    except KeyboardInterrupt:
        print(f"\n⏹️  Test interrupted by user")
    
    limiter.print_stats()
    return limiter

def find_optimal_rate():
    """Try different request rates to find the optimal one"""
    print("🔍 Finding optimal request rate...")
    
    # Test different delays (requests per second)
    test_delays = [0.1, 0.2, 0.5, 1.0, 2.0]  # 10, 5, 2, 1, 0.5 req/sec
    
    results = {}
    
    for delay in test_delays:
        print(f"\n🧪 Testing {1/delay:.1f} req/sec (delay: {delay}s)")
        limiter = test_rate_limits(delay_seconds=delay, max_requests=20)
        
        results[delay] = {
            'req_per_sec': 1/delay,
            'success_rate': (limiter.successful_requests / limiter.total_requests) * 100 if limiter.total_requests > 0 else 0,
            'rate_limited': limiter.rate_limited_requests
        }
        
        print(f"Results: {limiter.successful_requests}/{limiter.total_requests} successful, {limiter.rate_limited_requests} rate limited")
        
        # If we get rate limited, try slower rates
        if limiter.rate_limited_requests > 0:
            print("Rate limited detected - testing slower rates...")
        
        time.sleep(2)  # Brief pause between tests
    
    print(f"\n📋 Summary of rate tests:")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    for delay, result in results.items():
        status = "✅" if result['rate_limited'] == 0 else "⚠️"
        print(f"{status} {result['req_per_sec']:.1f} req/sec: {result['success_rate']:.1f}% success, {result['rate_limited']} rate limited")

if __name__ == "__main__":
    print("🎯 Spotify Podcast Charts API Rate Limiter")
    print("═══════════════════════════════════════════")
    
    # You can run different tests:
    
    # 1. Test with 1 request per second
    print("\n1️⃣ Testing 1 request per second for 30 requests:")
    test_rate_limits(delay_seconds=1.0, max_requests=30)
    
    #2. Find optimal rate
    print("\n2️⃣ Finding optimal request rate:")
    find_optimal_rate()
    
    #3. Custom test
    limiter = APIRateLimiter()
    response = limiter.make_request({'region': 'us'})
    print(f"Single request status: {response.status_code}")
    limiter.print_stats()






# import requests
# import time

# URL = "https://podcastcharts.byspotify.com/api/charts/trending?region=it"
# TIMEOUT = 5
# START_DELAY = 1.0     # Start with 1 request/sec
# MIN_DELAY = 0.05      # Fastest we'll try (0.05 sec = 20/sec)
# DELAY_STEP = 0.1      # How much to reduce delay per round

# def test_rate(delay):
#     """Send requests at a given delay until failure."""
#     count = 0
#     start = time.time()
#     while True:
#         try:
#             r = requests.get(URL, timeout=TIMEOUT)
#             if r.status_code != 200:
#                 print(f"Non-200 status: {r.status_code}")
#                 return False, count
#             count += 1
#         except Exception as e:
#             print(f"Error after {count} requests: {e}")
#             return False, count
        
#         elapsed = time.time() - start
#         if elapsed > 60:  # Test for one minute
#             return True, count
#         time.sleep(delay)

# def find_limit():
#     delay = START_DELAY
#     last_good = None
#     while delay >= MIN_DELAY:
#         print(f"\nTesting delay: {delay:.2f}s between requests")
#         success, count = test_rate(delay)
#         if success:
#             print(f"✅ Passed: {count} requests in 1 minute at {delay:.2f}s delay")
#             last_good = (delay, count)
#             delay -= DELAY_STEP  # Try faster
#         else:
#             print(f"❌ Failed at delay {delay:.2f}s — stopping.")
#             break
#     return last_good

# if __name__ == "__main__":
#     result = find_limit()
#     if result:
#         delay, rpm = result
#         print(f"\nSafe limit: ~{rpm} requests/minute (delay {delay:.2f}s)")
#     else:
#         print("No safe limit found — server is blocking aggressively.")
# =========================================
# import requests
# import time

# url = "https://podcastcharts.byspotify.com/api/charts/top?region=us"

# count = 0
# while True:
#     count += 1
#     r = requests.get(url)
#     if r.status_code == 200:
#         print(f"{count}: OK")
#     elif r.status_code == 429:
#         retry_after = r.headers.get("Retry-After", "unknown")
#         print(f"RATE LIMIT HIT after {count} requests! Retry after {retry_after} seconds")
#         break
#     else:
#         print(f"{count}: ERROR {r.status_code}")
#         break
