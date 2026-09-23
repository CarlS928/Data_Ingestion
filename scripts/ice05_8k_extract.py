"""
ICE 5.2 - Extracting Unstructured Data from an Earnings Press Release

Follows the ICE_Week05.md specification (MIS3060, Villanova University):
finds the most recent 8-K earnings filing (Item 2.02) for a chosen company on
SEC EDGAR, downloads its earnings press release exhibit, strips the HTML to
plain text, and uses simple keyword-proximity regexes to pull out revenue,
diluted EPS, net income, and a short guidance/outlook excerpt - a semi-
structured extraction, not a guaranteed-accurate one (see the debrief
questions in the exercise for why).

Before running for the assignment: replace YOUR_EMAIL below with your own
Villanova email - SEC EDGAR requires a real, identifying User-Agent on every
request and will reject ones that look generic or fake.

Run with:
    python scripts/ice05_8k_extract.py
Output:
    outputs/earnings_extract.csv   (company, ticker, period, revenue, eps_diluted, net_income, guidance_excerpt)
"""

import csv
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# --- Choose one company (per the exercise's table) ---------------------------------
COMPANY_CIKS = {
    "AAPL": ("Apple Inc.", "0000320193"),
    "MSFT": ("Microsoft Corporation", "0000789019"),
    "JPM": ("JPMorgan Chase & Co.", "0000019617"),
}
TICKER = "MSFT"
COMPANY_NAME, CIK = COMPANY_CIKS[TICKER]

# --- SEC EDGAR requires a real, identifying User-Agent on every request ------------
YOUR_EMAIL = "youremail@villanova.edu"  # <-- replace with your own Villanova email before running
USER_AGENT = f"MIS3060 Villanova {YOUR_EMAIL}"

SUBMISSIONS_URL = f"https://data.sec.gov/submissions/CIK{CIK}.json"
ARCHIVE_BASE = f"https://www.sec.gov/Archives/edgar/data/{int(CIK)}"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "outputs" / "earnings_extract.csv"


def sec_get(url):
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    resp.raise_for_status()
    return resp


def find_latest_earnings_8k():
    """Most recent 8-K filing whose Items include 2.02 (Results of Operations and Financial Condition)."""
    data = sec_get(SUBMISSIONS_URL).json()
    recent = data["filings"]["recent"]
    items_by_index = recent.get("items", [""] * len(recent["form"]))
    for i, form in enumerate(recent["form"]):
        if form == "8-K" and "2.02" in items_by_index[i].split(","):
            return {
                "accession": recent["accessionNumber"][i],
                "filing_date": recent["filingDate"][i],
                "period": recent["reportDate"][i],
            }
    raise RuntimeError(f"No 8-K filing with Item 2.02 found for {COMPANY_NAME}.")


def find_press_release_url(accession):
    """The filing index page lists each document's Type; the press release exhibit is typically EX-99.1."""
    accession_nodashes = accession.replace("-", "")
    index_url = f"{ARCHIVE_BASE}/{accession_nodashes}/{accession}-index.htm"
    soup = BeautifulSoup(sec_get(index_url).text, "html.parser")

    for row in soup.select("table.tableFile tr"):
        cells = [c.get_text(strip=True) for c in row.find_all("td")]
        if len(cells) < 4:
            continue
        doc_type, filename = cells[3], cells[2]
        if doc_type.upper().startswith("EX-99") or re.search(r"ex-?99", filename, re.I):
            link = row.find("a")
            if link and link.get("href"):
                return index_url, f"https://www.sec.gov{link['href']}"
    raise RuntimeError(f"No earnings press release exhibit (ex99/ex-99) found in filing {accession}.")


def html_to_text(url):
    resp = sec_get(url)
    resp.encoding = resp.apparent_encoding  # SEC serves UTF-8 without always declaring it
    soup = BeautifulSoup(resp.text, "html.parser")
    return " ".join(soup.get_text(separator=" ").split())


def dollar_amount_near(text, keywords, window=200):
    """First $ amount found within `window` characters after the first occurrence of any keyword."""
    for keyword in keywords:
        match = re.search(re.escape(keyword), text, re.I)
        if not match:
            continue
        snippet = text[match.end(): match.end() + window]
        amount = re.search(r"\$[\d,]+(?:\.\d+)?\s*(?:billion|million|thousand)?", snippet)
        if amount:
            return amount.group(0).strip()
    return None


def guidance_excerpt(text, max_sentences=2):
    """Up to two sentences mentioning outlook, guidance, or forward expectations."""
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z])", text)
    hits = [s.strip() for s in sentences if re.search(r"\boutlook\b|\bguidance\b|\bexpects\b", s, re.I)]
    return " ".join(hits[:max_sentences]) if hits else None


def save_csv_row(row, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        writer.writeheader()
        writer.writerow(row)


def main():
    print(f"Looking up {COMPANY_NAME}'s most recent 8-K with Item 2.02 (earnings) on SEC EDGAR...")
    filing = find_latest_earnings_8k()
    print(f"Found filing dated {filing['filing_date']} for the period ended {filing['period']}.")

    index_url, press_release_url = find_press_release_url(filing["accession"])
    print(f"Filing index: {index_url}")
    print(f"Press release exhibit: {press_release_url}")

    text = html_to_text(press_release_url)

    revenue = dollar_amount_near(text, ["revenue"])
    eps_diluted = dollar_amount_near(text, ["diluted earnings per share", "EPS"])
    net_income = dollar_amount_near(text, ["net income"])
    guidance = guidance_excerpt(text)

    print("\nExtracted values:")
    print(f"  Revenue:          {revenue}")
    print(f"  Diluted EPS:      {eps_diluted}")
    print(f"  Net income:       {net_income}")
    print(f"  Guidance excerpt: {guidance}")

    row = {
        "company": COMPANY_NAME,
        "ticker": TICKER,
        "period": filing["period"],
        "revenue": revenue,
        "eps_diluted": eps_diluted,
        "net_income": net_income,
        "guidance_excerpt": guidance,
    }
    save_csv_row(row, OUTPUT_PATH)
    print(f"\ndata/earnings_extract.csv saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
