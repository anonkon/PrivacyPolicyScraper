# PrivacyPolicyScraper

Privacy policies for 263 Australian organisations: ASX 200 companies, 20 MNCs operating in Australia, and 20 Australian Government entities.

**Scraping is already done.** The database, extracted text, screenshots, and raw HTML/PDFs are included in this repository. You only need to run the scraper again if you want to refresh or extend the data.

---

## Quickstart — browse the data

```bash
git clone https://github.com/<you>/PrivacyPolicyScraper.git
cd PrivacyPolicyScraper

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install --prefer-binary -r requirements.txt

python main.py serve
```

Open **http://localhost:5000** in your browser.

The dashboard lets you:
- Browse all 263 organisations, filter by type (ASX200 / MNC / Government)
- Search by name, sector, or ASX code
- View extracted policy text per company
- Open raw HTML, PNG screenshot, or download PDF

---

## Data without the dashboard

All data is also accessible directly:

| Path | Contents |
|------|----------|
| `data/output/companies.csv` | Company metadata (name, website, sector, type, ASX code) |
| `data/output/privacy_policies.csv` | Policy URLs, status, extracted text |
| `data/db/privacy_scraper.db` | SQLite database (open with DB Browser or any SQLite client) |
| `storage/companies/<slug>/` | Per-company files: `privacy_policy.html`, `screenshot.png`, `extracted_text.txt`, `privacy_policy.pdf` |

---

## Re-running or extending the scraper

```bash
# One-time: install Playwright browser (only needed for screenshots)
playwright install chromium

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
