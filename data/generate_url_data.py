import re
import requests
import pandas as pd

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


phistank_df = pd.read_csv("https://data.phishtank.com/data/online-valid.csv")

phistank_url = phistank_df['url']
#print(phistank_url.head(6))
#print(len(phistank_url))

tranco_df = pd.read_csv("https://tranco-list.eu/top-1m.csv.zip", compression="zip", header=None, names=["rank", "domain"])
prepend = "https://" + tranco_df["domain"]
#print(prepend.head(6))

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
#print(combined_df)

combined_df["url_length"] = combined_df["Url"].apply(get_url_length)
combined_df["contains_suspicious_words"] = combined_df["Url"].apply(suspicious_words)
combined_df["ip_address"] = combined_df["Url"].apply(check_for_ip_address)

#print(combined_df.head(6000))

print(combined_df["contains_suspicious_words"].value_counts())
print(combined_df["ip_address"].value_counts())