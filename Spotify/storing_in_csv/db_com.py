import mysql.connector
import pandas as pd
from datetime import date, timedelta

# ------------------
# DB Connection
# ------------------
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password=password.Password,
    database="yourdb"
)
cursor = conn.cursor(dictionary=True)

# ------------------
# Config
# ------------------
COUNTRY_NAMES = {
    "ar": "Argentina", "at": "Austria", "au": "Australia",
    "br": "Brazil", "ca": "Canada", "cl": "Chile",
    "co": "Colombia", "de": "Germany", "dk": "Denmark",
    "es": "Spain", "fi": "Finland", "fr": "France",
    "gb": "United Kingdom", "id": "Indonesia", "ie": "Ireland",
    "in": "India", "it": "Italy", "jp": "Japan",
    "mx": "Mexico", "nl": "Netherlands", "no": "Norway",
    "nz": "New Zealand", "ph": "Philippines", "se": "Sweden",
    "us": "United States"
}

THREE = ["ar", "at", "ca", "cl", "co", "dk", "fi", "fr", "in", "id", "ie", "it", "jp", "nz", "no", "ph", "es", "nl"]
SEVENTEEN = ["au", "us", "gb", "br", "de", "mx", "se"]

CATEGORIES_20 = [
    "top", "trending", "top_episodes", "arts", "business", "comedy", "education", "fiction", "history", "health%252520%2526%252520fitness",
    "leisure", "music", "news", "religion%252520%2526%252520spirituality", "science",
    "society%252520%2526%252520culture", "sports", "technology", "true%252520crime", "tv%252520%2526%252520film"
]

CATEGORIES_3 = ["top", "trending", "top_episodes"]

# ------------------
# Dates
# ------------------
today = date.today()
yesterday = today - timedelta(days=1)

# ------------------
# Main comparison loop
# ------------------
results = []

for country in COUNTRY_NAMES.keys():
    categories = CATEGORIES_20 if country in SEVENTEEN else CATEGORIES_3
    
    for category in categories:
        # JOIN query to compare today and yesterday
        query = f"""
            SELECT 
                t_today.ShowID,
                t_today.Rank AS today_rank,
                t_yest.Rank AS yesterday_rank,
                t_today.ShowName
            FROM charts_table t_today
            LEFT JOIN charts_table t_yest
                ON t_today.ShowID = t_yest.ShowID
                AND t_today.CountryCode = t_yest.CountryCode
                AND t_today.Category = t_yest.Category
                AND t_yest.Date = '{yesterday}'
            WHERE t_today.Date = '{today}'
              AND t_today.CountryCode = %s
              AND t_today.Category = %s
        """
        cursor.execute(query, (country, category))
        rows = cursor.fetchall()

        for row in rows:
            if row['yesterday_rank'] is None:
                movement = "NEW"
                diff = None
            else:
                diff = row['yesterday_rank'] - row['today_rank']
                if diff > 0:
                    movement = f"UP {diff}"
                elif diff < 0:
                    movement = f"DOWN {abs(diff)}"
                else:
                    movement = "SAME"

            results.append({
                "Country": COUNTRY_NAMES[country],
                "Category": category,
                "ShowID": row['ShowID'],
                "ShowName": row['ShowName'],
                "Today Rank": row['today_rank'],
                "Yesterday Rank": row['yesterday_rank'],
                "Movement": movement
            })

# ------------------
# Save to CSV
# ------------------
df = pd.DataFrame(results)
df.to_csv("rank.csv", index=False, encoding="utf-8")
print("✅ CSV saved: rank_changes.csv")
