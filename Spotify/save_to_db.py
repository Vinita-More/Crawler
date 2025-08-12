# using same table to store all data about countries with and without categories
import mysql.connector
import requests
from datetime import datetime
import password
import time

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

# 20 categories
CATEGORIES_20 = [
    "top", "trending", "top_episodes", "arts", "business", "comedy", "education", "fiction", "history", "health%252520%2526%252520fitness",
    "leisure", "music", "news", "religion%252520%2526%252520spirituality", "science",
    "society%252520%2526%252520culture", "sports", "technology", "true%252520crime", "tv%252520%2526%252520film"]

# 3 categories
CATEGORIES_3 = ["top", "trending", "top_episodes"]

# 1 category
#CATEGORIES_1 = ["top"]

def fetch_items_with_retry(url, retries=3, delay=5):
    for attempt in range(retries):
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            data = r.json()
            if isinstance(data, dict):
                return data.get("items", [])
            if isinstance(data, list):
                return data
            return []
        except Exception as e:
            print(f"[WARN] Request failed (attempt {attempt+1}/{retries}): {e}")
            if attempt < retries - 1:
                time.sleep(delay)
    return None

def fetch_and_save():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password=password.Password,
        database="spotify"
    )
    cur = conn.cursor()

    insert_sql = """
    INSERT INTO spotify_podcast_charts_with_category
    (showId, showName, showPublisher, showImageUrl, showDescription,
     countryName, countryCode, category, chart_rank, created_at, updated_at)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """

    for country in sorted(set(Three + Seventeen)):
        if country in Seventeen:
            categories = CATEGORIES_20
        else:
            categories = CATEGORIES_3

        for category in categories:
            url = f"https://podcastcharts.byspotify.com/api/charts/{category}?region={country}"
            print(f"[INFO] Fetching {country.upper()} - {category} → {url}")

            items = fetch_items_with_retry(url)
            if items is None:
                print(f"[ERROR] Failed to fetch data after retries: {country.upper()} - {category}")
                continue

            for idx, item in enumerate(items):
                show_uri = item.get("showUri", "")
                show_id = show_uri.split(":")[-1] if show_uri else ""
                cur.execute(insert_sql, (
                    show_id,
                    item.get("showName", ""),
                    item.get("showPublisher", ""),
                    item.get("showImageUrl", ""),
                    item.get("showDescription", ""),
                    COUNTRY_NAMES.get(country, ""),
                    country,
                    category.replace("-", " ").title(),
                    idx + 1,  # rank
                    datetime.now(),
                    datetime.now()
                ))
            conn.commit()
            print(f"[OK] Inserted {len(items)} rows for {country.upper()} - {category}")

    cur.close()
    conn.close()

if __name__ == "__main__":
    fetch_and_save()


# def fetch_and_save():
#     conn = mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password=password.Password,
#         database="spotify"
#     )
#     cur = conn.cursor()

#     insert_sql = """
#     INSERT INTO spotify_podcast_charts_with_category
#     (showId, showName, showPublisher, showImageUrl, showDescription,
#      countryName, countryCode, category, chart_rank, created_at, updated_at)
#     VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
#     """

#     for country in sorted(set(Three + Seventeen)):
#         if country in Seventeen:
#             categories = CATEGORIES_20
       
#         else:
#             categories = CATEGORIES_3

#         for category in categories:
#             url = f"https://podcastcharts.byspotify.com/api/charts/{category}?region={country}"
#             print(f"[INFO] Fetching {country.upper()} - {category} → {url}")
#             try:
#                 r = requests.get(url, timeout=10)
#                 r.raise_for_status()
#                 items = r.json()

#                 if isinstance(items, dict):
#                     items = items.get("items", [])
#                 if not isinstance(items, list):
#                     items = []

#                 for idx, item in enumerate(items):
#                     show_uri = item.get("showUri", "")
#                     show_id = show_uri.split(":")[-1] if show_uri else ""
#                     cur.execute(insert_sql, (
#                         show_id,
#                         item.get("showName", ""),
#                         item.get("showPublisher", ""),
#                         item.get("showImageUrl", ""),
#                         item.get("showDescription", ""),
#                         COUNTRY_NAMES.get(country, ""),
#                         country,
#                         category.replace("-", " ").title(),
#                         idx + 1,  # rank
#                         datetime.now(),
#                         datetime.now()
#                     ))

#                 conn.commit()
#                 print(f"[OK] Inserted {len(items)} rows for {country.upper()} - {category}")

#             except Exception as e:
#                 print(f"[ERROR] {country.upper()} - {category} - {e}")

#     cur.close()
#     conn.close()