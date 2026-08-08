import pandas as pd
import re
from Levenshtein import distance
from urllib.parse import urlparse
import tldextract


def get_url_length(url):
    return len(url)

def suspicious_words(url):
    sus_words = ["login", "account", "content", "include", "online", "sites", "admin", "email", "secur", "update", "verify"]
    flag = False
    
    for i in sus_words:
        if i in url:
            flag = True

    return flag
    
def check_for_ip_address(url):
    if re.search(r"\d+\.\d+\.\d+\.\d+", url):
        return True
    else:
        return False

def check_typosquatting(url):
    brands = ["Apple", "Microsoft", "Google", "Amazon", "Samsung", "Coca Cola", "Toyota", "Mercedes Benz", "McDonald's", "Disney",
           "Louis Vuitton", "Gucci", "Chanel", "Hermès", "Rolex", "Prada", "Dior", "Zara", "H&M", "Uniqlo", "Starbucks", "Pepsi",
           "Nestlé", "KFC", "Domino's", "Heineken", "Budweiser", "Red Bull", "Subway", "Nescafé", "Intel", "Dell", "Lenovo", "HP",
           "Sony", "LG", "Huawei", "Adobe", "Nvidia", "Cisco", "BMW", "Honda", "Audi", "Ford", "Volkswagen", "Porsche", "Ferrari",
           "Hyundai", "Lexus", "Jeep", "Nike", "Adidas", "Puma", "Under Armour", "New Balance", "Reebok", "Vans", "Converse", "The North Face",
           "Patagonia", "Netflix", "Warner Bros", "Spotify", "YouTube", "TikTok", "ESPN", "BBC", "Hulu", "Paramount", "Visa", "Mastercard", "PayPal",
           "American Express", "JPMorgan Chase", "Bank of America", "HSBC", "Goldman Sachs", "Citi", "Allianz", "Ikea", "DHL", "Tesla"]
           #extracted from https://brandyhq.com/blog/best-brands-of-the-world/
    track = 100000

    extracted = tldextract.extract(url)
    domain_name = extracted.domain
    domain_name = domain_name.lower()

    for i in brands:
        i = i.lower()
        calculated_distance = distance(i, domain_name)
        if calculated_distance < track:
            track = calculated_distance
           
    if track != 0 and track <= 2:
        return True
    else:
        return False


phistank_df = pd.read_csv("https://data.phishtank.com/data/online-valid.csv")

phistank_url = phistank_df['url']

tranco_df = pd.read_csv("https://tranco-list.eu/top-1m.csv.zip", compression="zip", header=None, names=["rank", "domain"])
prepend = "https://" + tranco_df["domain"]

phistank_sample = phistank_url.sample(n=5001)
tranco_sample = prepend.sample(n=5001)

phising_df = pd.DataFrame({
    "Url": phistank_sample, 
    "label": 1
})


legit_df = pd.DataFrame({
    "Url": tranco_sample,
    "label": 0
})


combined_df = pd.concat([phising_df,legit_df], ignore_index=True)

combined_df["url_length"] = combined_df["Url"].apply(get_url_length)
combined_df["contains_suspicious_words"] = combined_df["Url"].apply(suspicious_words)
combined_df["ip_address"] = combined_df["Url"].apply(check_for_ip_address)
combined_df["checking_typosquatting"] = combined_df["Url"].apply(check_typosquatting)
