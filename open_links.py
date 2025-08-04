genre_ids = [
    1301,  # Arts
    1302,  # Business
    1303,  # Comedy
    1304,  # Education
    1305,  # Kids & Family
    1306, #Food
    1309,  # TV & Film
    1310,  # Music
    1314,  # Religion & Spirituality
    1318,  # Technology
    1320,  # Places and Travel
    1321,  # Business
    1324,  # Society and culture
    1545,  #sports
    1488,  # True Crime
    1502,  # Leisure
    1487, #history
    1498, #Language learning
    1512, #Health and fitness
    1544, #Relationships
    1500, #Self improvement
    1533, #science
    1543, #Documentry
    1503, # Automotive
    1504, #Aviation 
    1505, #hobbies
    1506, #Crafts
    1507, #Games
    1508, #Homes and Garden
    1509, #Video games
    1510, #Animation and Manga
    1511, #Government
    1546,#Soccer
    1547, #football
    1548, #basketball
    1549, #baseball
    1550, #hockey
    1551, # Running
    1552,#rugby
    1553, #golf

]
country_codes = [
    "us", "gb", "ca", "au", "in", "de", "fr", "jp", "kr", "br", "mx", "cn", "it", "es",
    "ru", "nl", "se", "no", "fi", "dk", "ie", "nz", "za", "sg", "hk", "tw", "be", "ch",
    "at", "pl", "tr", "sa", "ae", "ar", "cl", "co", "cz", "gr", "hu", "id", "il", "my",
    "ph", "pt", "ro", "sk", "th", "ua", "ve", "vn"
]

#Generating links
def generate_apple_podcast_links(genre_ids, country_codes):
    base_url = "https://podcasts.apple.com/{country}/genre/{genre_id}"
    links = []

    for country in country_codes:
        for genre_id in genre_ids:
            url = base_url.format(country=country, genre_id=genre_id)
            links.append(url)
    
    return links

links = generate_apple_podcast_links(genre_ids, country_codes)

