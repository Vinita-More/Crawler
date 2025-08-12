import requests
import time
import concurrent.futures
import logging

# Setup logging to file
logging.basicConfig(filename="err.log", level=logging.ERROR, 
                    format="%(asctime)s - %(message)s")

URL = "https://podcastcharts.byspotify.com/api/charts/top?region=us"
TOTAL_REQUESTS = 10000
TIME_WINDOW = 60  # seconds
timeout_seconds = 30

def make_request(i):
    try:
        r = requests.get(URL, timeout=timeout_seconds)
        if r.status_code != 200:
            logging.error(f"Request #{i} failed with status code: {r.status_code}")
        return (i, r.status_code)
    except requests.exceptions.RequestException as e:
        logging.error(f"Request #{i} encountered error: {e}")
        return (i, f"ERROR: {e}")

def stress_test():
    start_time = time.time()
    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
        futures = [executor.submit(make_request, i) for i in range(1, TOTAL_REQUESTS + 1)]
        for future in concurrent.futures.as_completed(futures):
            req_num, status = future.result()
            elapsed = time.time() - start_time
            print(f"[REQ #{req_num}] Status: {status} | Time elapsed: {elapsed:.2f}s")
            results.append((req_num, status))

            if status == 429:
                print(f"\n🚫 Rate limit hit at request #{req_num} after {elapsed:.2f} seconds.")
                break

    total_elapsed = time.time() - start_time
    print(f"\nSent {len(results)} requests in {total_elapsed:.2f} seconds.")
    print("All errors are logged in err.log")

if __name__ == "__main__":
    stress_test()