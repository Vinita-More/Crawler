import mysql.connector
import requests
import time
from datetime import datetime
import password

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

Three = [
    "ar", "at", "ca", "cl", "co", "dk", "fi", "fr", "in", "id",
    "ie", "it", "jp", "nz", "no", "ph", "es", "nl"
]

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


failed = []

# Before your for-loop
start_time = time.time()
request_count = 0

for code in COUNTRY_CODES:
    url = f"https://podcastcharts.byspotify.com/api/charts/top?region={code}"
    print(f"[INFO] Fetching {code} → {url}")

    try:
        r = requests.get(url, timeout=10)
        request_count += 1  # count every request attempt
        r.raise_for_status()
        # ... rest of your parsing + DB insert ...
    except Exception as e:
        print(f"[ERROR] {code} - {e}")
        failed.append(url)

# After loop ends
end_time = time.time()
elapsed = end_time - start_time
if elapsed > 0:
    rps = request_count / elapsed
else:
    rps = 0

print(f"\n[STATS] Sent {request_count} requests in {elapsed:.2f} seconds.")
print(f"[STATS] Average speed: {rps:.2f} requests per second.")
