import requests
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Setup logging to file
logging.basicConfig(
    filename="request_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

URL = "https://podcastcharts.byspotify.com/api/charts/top?region=us"
TOTAL_REQUESTS = 5000
CONCURRENCY = 50  # number of parallel workers

# Worker function
def fetch(i, session):
    try:
        r = session.get(URL, timeout=5)
        if r.status_code == 429:
            msg = f"Request #{i} rate limited (429)"
            print(msg)
            logging.info(msg)
        elif r.status_code != 200:
            msg = f"Request #{i} failed: HTTP {r.status_code}"
            print(msg)
            logging.info(msg)
        return r.status_code
    except Exception as e:
        msg = f"Request #{i} error: {e}"
        print(msg)
        logging.error(msg)
        return None

# Main
if __name__ == "__main__":
    start = time.time()
    with requests.Session() as session:
        with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
            futures = [executor.submit(fetch, i, session) for i in range(1, TOTAL_REQUESTS + 1)]
            for _ in as_completed(futures):
                pass
    end = time.time()

    print(f"Completed {TOTAL_REQUESTS} requests in {end - start:.2f} seconds")
    print("Logs saved to request_log.txt")
