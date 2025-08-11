
import requests
import time

URL = "https://podcastcharts.byspotify.com/api/charts/trending?region=it"
TIMEOUT = 5
START_DELAY = 1.0     # Start with 1 request/sec
MIN_DELAY = 0.05      # Fastest we'll try (0.05 sec = 20/sec)
DELAY_STEP = 0.1      # How much to reduce delay per round

def test_rate(delay):
    """Send requests at a given delay until failure."""
    count = 0
    start = time.time()
    while True:
        try:
            r = requests.get(URL, timeout=TIMEOUT)
            if r.status_code != 200:
                print(f"Non-200 status: {r.status_code}")
                return False, count
            count += 1
        except Exception as e:
            print(f"Error after {count} requests: {e}")
            return False, count
        
        elapsed = time.time() - start
        if elapsed > 60:  # Test for one minute
            return True, count
        time.sleep(delay)

def find_limit():
    delay = START_DELAY
    last_good = None
    while delay >= MIN_DELAY:
        print(f"\nTesting delay: {delay:.2f}s between requests")
        success, count = test_rate(delay)
        if success:
            print(f"✅ Passed: {count} requests in 1 minute at {delay:.2f}s delay")
            last_good = (delay, count)
            delay -= DELAY_STEP  # Try faster
        else:
            print(f"❌ Failed at delay {delay:.2f}s — stopping.")
            break
    return last_good

if __name__ == "__main__":
    result = find_limit()
    if result:
        delay, rpm = result
        print(f"\nSafe limit: ~{rpm} requests/minute (delay {delay:.2f}s)")
    else:
        print("No safe limit found — server is blocking aggressively.")

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
