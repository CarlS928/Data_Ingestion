"""
Microsoft 8-K Report Downloader

Finds Microsoft's single most recent 8-K filing on SEC EDGAR (whatever it's
about - not necessarily an earnings release), pulls every HTML document
attached to it (the cover form plus any exhibits), extracts every data table
found in them, and stacks them into one CSV.

Not every 8-K reports quarterly results - only ones whose Items include 2.02
("Results of Operations and Financial Condition") do, and some exhibits (e.g.
investor-deck slides) are just images with no extractable tables at all. This
script says so plainly when that happens rather than writing a CSV of empty
boilerplate and calling it earnings data.

SEC EDGAR requires a descriptive User-Agent with contact info for programmatic
access (see https://www.sec.gov/os/webmaster-faq#developers) - replace the
placeholder in USER_AGENT below with your own name/email before relying on
this script.

Run with:
    python scripts/msft_8k_report.py
Output:
    outputs/msft_8k_report.csv
"""

import csv
import io
import re
from pathlib import Path

import pandas as pd
import requests

CIK = "0000789019"  # Microsoft Corporation
COMPANY = "Microsoft Corporation"
USER_AGENT = "BusinessIntelligence Data Ingestion research-script@example.com"  # replace with your own contact info
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "outputs" / "msft_8k_report.csv"

SUBMISSIONS_URL = f"https://data.sec.gov/submissions/CIK{CIK}.json"
ARCHIVE_BASE = f"https://www.sec.gov/Archives/edgar/data/{int(CIK)}"

# Documents to skip when looking for data tables: XBRL viewer render pages (R1.htm, R2.htm, ...),
# filing index pages, and non-HTML assets.
SKIP_PATTERNS = [re.compile(r"^R\d+\.htm$", re.I), re.compile(r"-index", re.I)]


def sec_get(url):
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    resp.raise_for_status()
    return resp


def find_latest_8k():
    """Return metadata for Microsoft's single most recent 8-K filing (EDGAR lists newest first)."""
    data = sec_get(SUBMISSIONS_URL).json()
    recent = data["filings"]["recent"]
    for i, form in enumerate(recent["form"]):
        if form == "8-K":
            return {
                "accession": recent["accessionNumber"][i],
                "filing_date": recent["filingDate"][i],
                "period": recent["reportDate"][i],
                "items": recent.get("items", [""] * len(recent["form"]))[i],
                "primary_document": recent["primaryDocument"][i],
            }
    raise RuntimeError("No 8-K filings found for this company.")


def list_filing_documents(accession):
    """Return the HTML documents inside a filing's folder (cover form + exhibits), skipping viewer/index pages."""
    accession_nodashes = accession.replace("-", "")
    folder_url = f"{ARCHIVE_BASE}/{accession_nodashes}"
    listing = sec_get(f"{folder_url}/index.json").json()

    docs = []
    for item in listing["directory"]["item"]:
        name = item["name"]
        if not name.lower().endswith((".htm", ".html")):
            continue
        if any(p.search(name) for p in SKIP_PATTERNS):
            continue
        docs.append((name, f"{folder_url}/{name}"))
    return docs


def extract_tables(doc_url):
    """Return every HTML table on a page as a list of DataFrames, or [] if none / unparsable."""
    content = sec_get(doc_url).content
    try:
        return pd.read_html(io.BytesIO(content), flavor="lxml")
    except ValueError:
        return []  # no <table> elements on this page


def write_report(meta, tables_by_doc, path):
    """One CSV: a metadata block, then every extracted table, each labeled with its source document."""
    path.parent.mkdir(parents=True, exist_ok=True)
    has_tables = any(tables for _, tables in tables_by_doc)

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Company", COMPANY])
        writer.writerow(["CIK", CIK])
        writer.writerow(["Form Type", "8-K"])
        writer.writerow(["Filing Date", meta["filing_date"]])
        writer.writerow(["Period of Report", meta["period"]])
        writer.writerow(["Items", meta["items"]])
        writer.writerow(["Accession Number", meta["accession"]])
        writer.writerow(["Filing Index URL", meta["index_url"]])
        if not has_tables:
            writer.writerow(["Note", "No extractable data tables were found in this filing's documents "
                                      "(exhibits may be image-only, e.g. a slide deck)."])
        writer.writerow([])

        for doc_name, tables in tables_by_doc:
            for i, table in enumerate(tables):
                writer.writerow([f"--- Source: {doc_name} | Table {i} ---"])
                writer.writerow(table.columns.tolist())
                writer.writerows(table.itertuples(index=False))
                writer.writerow([])


def main():
    print(f"Looking up {COMPANY}'s most recent 8-K on SEC EDGAR...")
    meta = find_latest_8k()
    meta["index_url"] = f"{ARCHIVE_BASE}/{meta['accession'].replace('-', '')}/{meta['accession']}-index.htm"
    print(f"Found: filed {meta['filing_date']}, period {meta['period']}, items {meta['items'] or '(none listed)'}")
    print(f"Filing index: {meta['index_url']}")

    if "2.02" not in meta["items"].split(","):
        print("Note: this filing's Items do not include 2.02 (Results of Operations and Financial Condition),")
        print("      so it may not be a quarterly-earnings release - it could be about another event entirely.")

    docs = list_filing_documents(meta["accession"])
    print(f"Found {len(docs)} document(s) to check for data tables: {', '.join(n for n, _ in docs)}")

    tables_by_doc = []
    for name, url in docs:
        tables = extract_tables(url)
        print(f"  {name}: {len(tables)} table(s)")
        tables_by_doc.append((name, tables))

    write_report(meta, tables_by_doc, OUTPUT_PATH)
    total_tables = sum(len(t) for _, t in tables_by_doc)
    print(f"\nSaved {total_tables} table(s) to {OUTPUT_PATH}")
    if total_tables == 0:
        print("No financial tables were found in this filing at all - see the CSV's Note field.")


if __name__ == "__main__":
    main()
