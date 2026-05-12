# PrivacyPolicyScraper

Scrapes and stores privacy policies for 263 Australian organisations: ASX 200 companies, 20 MNCs operating in Australia, and 20 Australian Government entities.

For each organisation it finds the privacy policy URL, downloads the full HTML (+ screenshot) or PDF, and extracts plain text. Everything is stored in SQLite and a local folder structure. A minimal Flask dashboard lets you browse and read policies.

---

## Setup

**Requirements:** Python 3.10+

```bash
git clone https://github.com/<you>/PrivacyPolicyScraper.git
cd PrivacyPolicyScraper

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install --prefer-binary -r requirements.txt
playwright install chromium
```

---

## Usage

```bash
# Scrape all 263 organisations (takes ~45 min on first run)
python main.py scrape

# Scrape a subset
python main.py scrape --type ASX200
python main.py scrape --type MNC
python main.py scrape --type GOVERNMENT

# Scrape a single company by name or ASX code
python main.py scrape --company CBA
python main.py scrape --company "Commonwealth Bank"

# Re-scrape companies that were already done
python main.py scrape --force

# Export to CSV  (data/output/)
python main.py export

# Start dashboard  → http://localhost:5000
python main.py serve
```

---

## Output

| Path | Contents |
|------|----------|
| `data/db/privacy_scraper.db` | SQLite database |
| `data/output/companies.csv` | Company metadata |
| `data/output/privacy_policies.csv` | Policy URLs, status, extracted text |
| `storage/companies/<slug>/` | Per-company files (html, png, txt, pdf) |

Raw files are accessible without the dashboard — open any `.html` in a browser, `.png` in an image viewer, or `.txt` in any editor.

---

## Dashboard

`python main.py serve` starts a local Flask server at `http://127.0.0.1:5000`.

- Filter companies by type (ASX200 / MNC / Government)
- Live search by name, sector, or ASX code
- Per-company detail page with extracted text and links to raw files
- `GET /api/status` returns JSON counts by scraping status
