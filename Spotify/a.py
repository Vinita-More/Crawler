# import requests
# import time
# import concurrent.futures
# import logging

# # Setup logging to file
# logging.basicConfig(filename="err.txt", level=logging.ERROR, 
#                     format="%(asctime)s - %(message)s")

# URL = "https://podcastcharts.byspotify.com/api/charts/top?region=us"
# TOTAL_REQUESTS = 10000
# TIME_WINDOW = 60  # seconds
# timeout_seconds = 10

# def make_request(i):
#     try:
#         r = requests.get(URL, timeout=timeout_seconds)
#         if r.status_code != 200:
#             logging.error(f"Request #{i} failed with status code: {r.status_code}")
#         return (i, r.status_code)
#     except requests.exceptions.RequestException as e:
#         logging.error(f"Request #{i} encountered error: {e}")
#         return (i, f"ERROR: {e}")

# def stress_test():
#     start_time = time.time()
#     results = []

#     with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
#         futures = [executor.submit(make_request, i) for i in range(1, TOTAL_REQUESTS + 1)]
#         for future in concurrent.futures.as_completed(futures):
#             req_num, status = future.result()
#             elapsed = time.time() - start_time
#             print(f"[REQ #{req_num}] Status: {status} | Time elapsed: {elapsed:.2f}s")
#             results.append((req_num, status))

#             if status == 429:
#                 print(f"\n🚫 Rate limit hit at request #{req_num} after {elapsed:.2f} seconds.")
#                 break

#     total_elapsed = time.time() - start_time
#     print(f"\nSent {len(results)} requests in {total_elapsed:.2f} seconds.")
#     print("All errors are logged in err.txt")

# if __name__ == "__main__":
#     stress_test()
import requests
import time
import concurrent.futures
import logging
from logging.handlers import RotatingFileHandler

# Logging setup
error_handler = RotatingFileHandler("errors.log", maxBytes=5*1024*1024, backupCount=3)
error_handler.setLevel(logging.ERROR)
info_handler = RotatingFileHandler("requests.log", maxBytes=5*1024*1024, backupCount=3)
info_handler.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
error_handler.setFormatter(formatter)
info_handler.setFormatter(formatter)

logger = logging.getLogger("StressTest")
logger.setLevel(logging.DEBUG)
logger.addHandler(error_handler)
logger.addHandler(info_handler)

URL = "https://podcastcharts.byspotify.com/api/charts/top?region=us"
TOTAL_REQUESTS = 10000
MAX_WORKERS = 100  # Adjustable concurrency
TIMEOUT_SECONDS = 10

def make_request(i):
    try:
        r = requests.get(URL, timeout=TIMEOUT_SECONDS)
        logger.info(f"Request #{i} status: {r.status_code}")
        if r.status_code != 200:
            logger.error(f"Request #{i} failed with status code: {r.status_code}")
        return (i, r.status_code)
    except requests.exceptions.RequestException as e:
        logger.error(f"Request #{i} encountered error: {e}")
        return (i, f"ERROR: {e}")

def stress_test():
    start_time = time.time()
    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
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
    print("✅ All requests logged in requests.log")
    print("⚠️ Errors logged in errors.log")

if __name__ == "__main__":
    stress_test()
