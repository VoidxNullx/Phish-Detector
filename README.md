# Phishing URL Detector

A machine learning classifier that detects phishing URLs using real-world data from PhishTank and Tranco, trained on four hand-engineered features extracted directly from URL text.

## What this project does

Traditional phishing protection relies on blocklists — reactive systems that only catch URLs someone has already reported. This project explores whether a small set of *structural* features extracted from a URL's text (no blocklist lookups, no external reputation checks) can meaningfully separate phishing from legitimate URLs.

1. Pulls ~5,000 real, verified phishing URLs from [PhishTank](https://phishtank.org)
2. Pulls ~5,000 real legitimate domains from [Tranco](https://tranco-list.eu), a research-grade top-domains list
3. Extracts four features from each URL
4. Trains a Random Forest classifier and evaluates it on held-out data

## The four features

| Feature | What it measures |
|---|---|
| `url_length` | Character count of the full URL |
| `contains_suspicious_words` | Presence of common phishing-related keywords (login, verify, account, etc.) |
| `ip_address` | Whether the URL uses a raw IP address instead of a domain name |
| `checking_typosquatting` | Edit-distance similarity to a list of ~80 well-known brand names — catches near-identical domain spoofing (e.g. `paypa1.com` vs `paypal.com`) |

## Results

**83% accuracy** on held-out real-world data (2,001 test URLs).

```
              precision    recall  f1-score
   legitimate     0.78      0.92      0.84
     phishing     0.91      0.75      0.82
```

The precision/recall split is the more honest story here: the model is very *confident* when it flags something as phishing (91% precision), but it misses roughly **1 in 4 actual phishing URLs** (75% recall). That gap is directly explained by feature coverage — `contains_suspicious_words` fires on only ~4.6% of real URLs, `ip_address` on ~0.3%, and `checking_typosquatting` on ~7%, meaning `url_length` alone is doing most of the work for a large share of the dataset.

## Bugs found and fixed

**Case-sensitivity in typosquatting detection.** The initial implementation compared domains against brand names without normalizing case — `distance("google", "Google")` returns `1`, not `0`, because the Levenshtein distance function is case-sensitive. This meant Google's *real, legitimate* domain was being flagged as a typosquat purely due to capitalization, while genuine typosquats (like `paypa1.com`) were sometimes scored as *less* suspicious than they should have been. Fixed by lowercasing both sides of every comparison. See commit history for the before/after.

## Known limitations

- **Keyword-matching is weak on modern phishing.** Research on a 2019 PhishTank dataset found that even the most common suggestive word ("login") appears in only ~13% of real phishing URLs — keyword-stuffing has fallen out of favor as blocklists got better at catching it. This project's own data confirms it: under 5% hit rate.
- **Typosquatting detection is biased toward short domains.** Edit distance is naturally easier to satisfy for short strings — a 3-4 character domain has a much higher chance of coincidentally landing within distance 2 of *some* brand in the list, without any real relationship to that brand. Spot-checking flagged results showed several short legitimate domains (`hk.net`, `sfs.ch`) incorrectly flagged this way.
- **Only ~80 brands are checked against.** A production system would need a much larger, regularly updated brand list to catch typosquatting of less globally-famous but still commonly-targeted sites (regional banks, smaller SaaS products, etc.)

## Project structure

```
Phish-Detector/
├── data/
│   └── generate_url_data.py   # data fetching, feature extraction, training
├── models/
│   └── RFC.joblib              # trained model (generated, not committed)
├── requirements.txt
└── README.md
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows
pip install -r requirements.txt
python data/generate_url_data.py
```

## What I learned building this

- Real-world data behaves very differently from intuition — my hand-picked suspicious keyword list barely fired on actual phishing URLs, which led me to find published research instead of guessing
- Edit distance is a genuinely useful tool for catching brand impersonation, but it has a real bias toward short strings that's worth checking for, not assuming away
- A subtle type mismatch (comparing case-sensitive strings) can silently produce wrong results without throwing any error
- Precision and recall tell more useful information than accuracy alone, especially for security applications where the cost of a false negative (missed phishing) and a false positive (blocked legitimate site) are very different

## Next steps

- Add character-based features (hyphen count, subdomain depth, digit ratio)
- Scale the typosquatting distance threshold based on domain length, to reduce short-domain false positives
- Expand the brand list significantly, or use a dynamically updated source
- Try a domain-age/WHOIS-based feature for a stronger real-world signal

## Author

Built by [Tarun](https://github.com/VoidxNullx), as part of an AI + Cybersecurity project series, alongside hands-on pentesting practice via TryHackMe and PortSwigger Web Security Academy.
