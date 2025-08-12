# # # storing only top podcast data from every country 

import mysql.connector
import requests
import time
from datetime import datetime
import password

# Country names mapping
COUNTRY_NAMES = {
    "ad": "Andorra", "ae": "United Arab Emirates", "al": "Albania", "ar": "Argentina", "at": "Austria", "au": "Australia",
    "az": "Azerbaijan", "ba": "Bosnia and Herzegovina", "be": "Belgium", "bg": "Bulgaria", "bh": "Bahrain", "bo": "Bolivia",
    "br": "Brazil", "bw": "Botswana", "ca": "Canada", "ch": "Switzerland", "cl": "Chile", "co": "Colombia", "cr": "Costa Rica",
    "cy": "Cyprus", "cz": "Czechia", "de": "Germany", "dk": "Denmark", "do": "Dominican Republic", "dz": "Algeria", "ec": "Ecuador",
    "ee": "Estonia", "eg": "Egypt", "es": "Spain", "fi": "Finland", "fr": "France", "gb": "United Kingdom", "ge": "Georgia",
    "gh": "Ghana", "gr": "Greece", "gt": "Guatemala", "hk": "Hong Kong", "hn": "Honduras", "hr": "Croatia", "hu": "Hungary",
    "id": "Indonesia", "ie": "Ireland", "il": "Israel", "in": "India", "is": "Iceland", "it": "Italy", "jm": "Jamaica",
    "jo": "Jordan", "jp": "Japan", "ke": "Kenya", "kh": "Cambodia", "kr": "South Korea", "kw": "Kuwait", "lb": "Lebanon",
    "lt": "Lithuania", "lu": "Luxembourg", "lv": "Latvia", "ma": "Morocco", "mk": "North Macedonia", "mt": "Malta", "mu": "Mauritius", 
    "mw": "Malawi", "mx": "Mexico", "my": "Malaysia", "mz": "Mozambique", "na": "Namibia", "ng": "Nigeria", "ni": "Nicaragua", 
    "nl": "Netherlands", "no": "Norway", "np": "Nepal", "nz": "New Zealand", "om": "Oman", "pa": "Panama",
    "pe": "Peru", "ph": "Philippines", "pl": "Poland", "pt": "Portugal", "py": "Paraguay", "qa": "Qatar", "ro": "Romania",
    "rs": "Serbia", "rw": "Rwanda", "sa": "Saudi Arabia", "se": "Sweden", "sg": "Singapore", "si": "Slovenia", "sk": "Slovakia",
    "sn": "Senegal", "sv": "El Salvador", "th": "Thailand", "tn": "Tunisia", "tr": "Turkey", "tt": "Trinidad and Tobago", "tw": "Taiwan",
    "tz": "Tanzania", "ua": "Ukraine", "us": "United States", "uy": "Uruguay", "uz": "Uzbekistan", "vn": "Vietnam", "za": "South Africa",
    "zm": "Zambia", "zw": "Zimbabwe"
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

# Merge & deduplicate
COUNTRY_CODES = sorted(set(Three + Seventeen + One))

def fetch_data(url, retries=3, delay=2):
    """Fetch JSON from API with retry mechanism."""
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.RequestException as e:
            print(f"[RETRY] Attempt {attempt} failed: {e}")
            time.sleep(delay * attempt)  # exponential backoff
    return None

def fetch_and_save():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password=password.Password,
        database="trial"
    )
    cur = conn.cursor()

    insert_sql = """
    INSERT INTO spotify_podcast_top_charts
    (showId, showName, showPublisher, showImageUrl, showDescription,
    countryName, countryCode, category, chart_rank, created_at, updated_at)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)   
    """

    for code in COUNTRY_CODES:
        url = f"https://podcastcharts.byspotify.com/api/charts/top?region={code}"
        print(f"[INFO] Fetching {code} → {url}")

        items = fetch_data(url)
        if not items:
            print(f"[ERROR] Failed to fetch {code} after retries")
            continue

        if isinstance(items, dict):
            items = items.get("items", [])
        if not isinstance(items, list):
            items = []

        for idx, item in enumerate(items, start=1):
            show_uri = item.get("showUri", "")
            show_id = show_uri.split(":")[-1] if show_uri else ""
            cur.execute(insert_sql, (
                show_id,
                item.get("showName", ""),
                item.get("showPublisher", ""),
                item.get("showImageUrl", ""),
                item.get("showDescription", ""),
                COUNTRY_NAMES.get(code, ""),
                code,
                "Top Podcasts",
                idx,
                datetime.now(),
                datetime.now()
            ))

        conn.commit()
        print(f"[OK] Inserted {len(items)} rows for {code}")
        time.sleep(1)  # <-- slow down to 1 req/sec

    cur.close()
    conn.close()

if __name__ == "__main__":
    fetch_and_save()




# import mysql.connector
# import requests
# import time
# from datetime import datetime
# import password

# COUNTRY_NAMES = {
#     "ad": "Andorra", "ae": "United Arab Emirates", "al": "Albania", "ar": "Argentina", "at": "Austria", "au": "Australia",
#     "az": "Azerbaijan", "ba": "Bosnia and Herzegovina", "be": "Belgium", "bg": "Bulgaria", "bh": "Bahrain", "bo": "Bolivia",
#     "br": "Brazil", "bw": "Botswana", "ca": "Canada", "ch": "Switzerland", "cl": "Chile", "co": "Colombia", "cr": "Costa Rica",
#     "cy": "Cyprus", "cz": "Czechia", "de": "Germany", "dk": "Denmark", "do": "Dominican Republic", "dz": "Algeria", "ec": "Ecuador",
#     "ee": "Estonia", "eg": "Egypt", "es": "Spain", "fi": "Finland", "fr": "France", "gb": "United Kingdom", "ge": "Georgia",
#     "gh": "Ghana", "gr": "Greece", "gt": "Guatemala", "hk": "Hong Kong", "hn": "Honduras", "hr": "Croatia", "hu": "Hungary",
#     "id": "Indonesia", "ie": "Ireland", "il": "Israel", "in": "India", "is": "Iceland", "it": "Italy", "jm": "Jamaica",
#     "jo": "Jordan", "jp": "Japan", "ke": "Kenya", "kh": "Cambodia", "kr": "South Korea", "kw": "Kuwait", "lb": "Lebanon",
#     "lt": "Lithuania", "lu": "Luxembourg", "lv": "Latvia", "ma": "Morocco", "mk": "North Macedonia", "mt": "Malta", "mu": "Mauritius", 
#     "mw": "Malawi", "mx": "Mexico", "my": "Malaysia", "mz": "Mozambique", "na": "Namibia", "ng": "Nigeria", "ni": "Nicaragua", 
#     "nl": "Netherlands", "no": "Norway", "np": "Nepal", "nz": "New Zealand", "om": "Oman", "pa": "Panama",
#     "pe": "Peru", "ph": "Philippines", "pl": "Poland", "pt": "Portugal", "py": "Paraguay", "qa": "Qatar", "ro": "Romania",
#     "rs": "Serbia", "rw": "Rwanda", "sa": "Saudi Arabia", "se": "Sweden", "sg": "Singapore", "si": "Slovenia", "sk": "Slovakia",
#     "sn": "Senegal", "sv": "El Salvador", "th": "Thailand", "tn": "Tunisia", "tr": "Turkey", "tt": "Trinidad and Tobago", "tw": "Taiwan",
#     "tz": "Tanzania", "ua": "Ukraine", "us": "United States", "uy": "Uruguay", "uz": "Uzbekistan", "vn": "Vietnam", "za": "South Africa",
#     "zm": "Zambia", "zw": "Zimbabwe"
# }

# Three = [
#     "ar", "at", "ca", "cl", "co", "dk", "fi", "fr", "in", "id",
#     "ie", "it", "jp", "nz", "no", "ph", "es", "nl"
# ]

# Seventeen = ["au", "us", "gb", "br", "de", "mx", "se"]

# One = [
#     "al", "ad", "ae", "az", "ba", "be", "bg", "bh", "bo", "br", "bw", "ch", "cr", "cy", "cz", "do",
#     "dz", "ec", "ee", "eg", "es", "fi", "fr", "gb", "ge", "gh", "gr", "gt", "hk", "hn", "hr", "hu",
#     "id", "ie", "il", "in", "is", "jm", "jo", "jp", "ke", "kh", "kr", "kw", "lb", "lt", "lu", "lv",
#     "ma", "mk", "mt", "mu", "mw", "mx", "my", "mz", "na", "ng", "ni", "np", "om", "pa", "pe", "ph",
#     "pl", "pt", "py", "qa", "ro", "rs", "rw", "sa", "se", "sg", "si", "sk", "sn", "sv", "th", "tn",
#     "tr", "tt", "tw", "tz", "ua", "uy", "uz", "vn", "za", "zm", "zw"
# ]

# # Merge & deduplicate
# COUNTRY_CODES = sorted(set(Three + Seventeen + One))

# def fetch_and_save():
#     conn = mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password=password.Password,
#         database="trial"
#     )
#     cur = conn.cursor()

#     insert_sql = """
#     INSERT INTO spotify_podcast_top_charts
#     (showId, showName, showPublisher, showImageUrl, showDescription,
#     countryName, countryCode, category, chart_rank, created_at, updated_at)
#     VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)   
#     """
#     failed = []

#     for code in COUNTRY_CODES:
#         url = f"https://podcastcharts.byspotify.com/api/charts/top?region={code}"
#         print(f"[INFO] Fetching {code} → {url}")
       
#         try:
#             r = requests.get(url, timeout=10)
#             r.raise_for_status()
#             items = r.json()

#             if isinstance(items, dict):
#                 items = items.get("items", [])
#             if not isinstance(items, list):
#                 items = []

#             for idx, item in enumerate(items, start=1):
#                 show_uri = item.get("showUri", "")
#                 show_id = show_uri.split(":")[-1] if show_uri else ""
#                 cur.execute(insert_sql, (
#                     show_id,
#                     item.get("showName", ""),
#                     item.get("showPublisher", ""),
#                     item.get("showImageUrl", ""),
#                     item.get("showDescription", ""),
#                     COUNTRY_NAMES.get(code, ""),
#                     code,
#                     "Top Podcasts",  # category
#                     idx,  
#                     datetime.now(),
#                     datetime.now()
#                 ))

#             conn.commit()
#             print(f"[OK] Inserted {len(items)} rows for {code}")

#         except Exception as e:
#             print(f"[ERROR] {code} - {e}")
#             failed.append(url)


#     for url in failed:
#         try:
#             r = requests.get(url, timeout=10)
#             r.raise_for_status()
#             items = r.json()

#             if isinstance(items, dict):
#                 items = items.get("items", [])
#             if not isinstance(items, list):
#                 items = []

#             for idx, item in enumerate(items, start=1):
#                 show_uri = item.get("showUri", "")
#                 show_id = show_uri.split(":")[-1] if show_uri else ""
#                 cur.execute(insert_sql, (
#                     show_id,
#                     item.get("showName", ""),
#                     item.get("showPublisher", ""),
#                     item.get("showImageUrl", ""),
#                     item.get("showDescription", ""),
#                     COUNTRY_NAMES.get(code, ""),
#                     code,
#                     "Top Podcasts",  # category
#                     idx,  
#                     datetime.now(),
#                     datetime.now()
#                 ))
#         except Exception as e:
#                     print(f"[ERROR] {code} - {e}")
#         conn.commit()
#         print(f"[OK] Inserted {len(items)} rows for {code}")

#     cur.close()
#     conn.close()

# if __name__ == "__main__":
#     fetch_and_save()