# PrivacyPolicyScraper

Privacy policies for 263 Australian organisations: ASX 200 companies, 20 MNCs operating in Australia, and 20 Australian Government entities.

Scraping is already done. The zip contains the database, extracted text, screenshots, and raw HTML files for all organisations.

---

## Setup

**Requirements:** Python 3.10+

1. Download and unzip the shared folder — you should have a `PrivacyPolicyScraper/` directory.

2. Open a terminal inside that directory:

```bash
cd PrivacyPolicyScraper
```

3. Create a virtual environment and install dependencies:

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install --prefer-binary -r requirements.txt
```

4. Start the dashboard:

```bash
python main.py serve
```

Open **http://localhost:5000** in your browser.

---

## What the dashboard shows

- All 263 organisations with scraping status, filterable by type (ASX200 / MNC / Government)
- Live search by company name, sector, or ASX code
- Per-company detail page: extracted policy text, links to raw HTML, screenshot, and PDF
- `GET /api/status` — JSON summary of scraping counts

---

## Accessing the data directly

No dashboard needed — all files are on disk:

| Path | Contents |
|------|----------|
| `data/output/companies.csv` | Company metadata: name, website, sector, type, ASX code |
| `data/output/privacy_policies.csv` | Policy URLs, content type, extracted text, scrape status |
| `data/db/privacy_scraper.db` | SQLite database — open with [DB Browser for SQLite](https://sqlitebrowser.org) or any SQLite client |
| `storage/companies/<slug>/` | Raw files per company: `privacy_policy.html`, `screenshot.png`, `extracted_text.txt`, `privacy_policy.pdf` |

---

## Re-running or extending the scraper

Only needed if you want to refresh or add organisations. Requires one extra step to install the browser used for screenshots:

```bash
playwright install chromium
```

```bash
# Scrape all organisations
python main.py scrape

# Scrape a subset
python main.py scrape --type ASX200
python main.py scrape --type MNC
python main.py scrape --type GOVERNMENT

# Scrape a single company by name or ASX code
python main.py scrape --company CBA
python main.py scrape --company "Commonwealth Bank"

# Force re-scrape already-done companies
python main.py scrape --force

# Regenerate CSVs after scraping
python main.py export
```
