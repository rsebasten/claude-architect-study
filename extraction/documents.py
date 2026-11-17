"""Fictional invoice documents with ground truth, for extraction/pipeline.py.

SAMPLES are hand-written edge cases (each one tests a specific behavior).
make_batch_docs() generates 100 templated docs for the Message Batches demo.
All vendors, numbers and people are made up.
"""

import random

# Each sample: id, doc_type (the layout, used for accuracy-by-type analysis),
# text, expected (ground truth for the scored fields), and what it tests.
SAMPLES = [
    {
        "id": "table-001",
        "doc_type": "table",
        "tests": "clean tabular invoice; every field present",
        "text": """NORTHWIND CLOUD SERVICES
Invoice No: NW-2026-0412        Date: 2026-03-14
PO Reference: PO-7781

| Item                         | Amount (USD) |
|------------------------------|-------------:|
| Platform licence (annual)    |     4,800.00 |
| Premium support              |     1,200.00 |
|------------------------------|-------------:|
| TOTAL DUE                    |     6,000.00 |
""",
        "expected": {"vendor_name": "Northwind Cloud Services", "invoice_number": "NW-2026-0412",
                     "invoice_date": "2026-03-14", "currency": "USD", "category": "software",
                     "total": 6000.0},
    },
    {
        "id": "email-002",
        "doc_type": "narrative",
        "tests": "prose email with no invoice number or date: both must be null, not invented",
        "text": """From: Dana Ortiz <dana@bluepeak-training.example>
Subject: Workshop fees

Hi team, thanks again for having us. As agreed, the two-day facilitation
workshop comes to EUR 3,000 for the sessions plus EUR 450 for printed
materials, so EUR 3,450 in total. I'll send a formal invoice once our new
billing system is live - for now please treat this email as the request.
Best, Dana (Bluepeak Training)
""",
        "expected": {"vendor_name": "Bluepeak Training", "invoice_number": None,
                     "invoice_date": None, "currency": "EUR", "category": "services",
                     "total": 3450.0},
    },
    {
        "id": "receipt-003",
        "doc_type": "receipt",
        "tests": "currency outside the enum: must use 'other' + currency_detail",
        "text": """ALPENBLICK HOTEL ZERMATT
Receipt #A-55190   08.02.2026
2 nights Superior Room ..... CHF 560.00
City tax ................... CHF  14.00
TOTAL ...................... CHF 574.00
Paid by card. Thank you!
""",
        "expected": {"vendor_name": "Alpenblick Hotel Zermatt", "invoice_number": "A-55190",
                     "invoice_date": "2026-02-08", "currency": "other", "category": "travel",
                     "total": 574.0},
    },
    {
        "id": "table-004",
        "doc_type": "table",
        "tests": "source error: line items sum to 1,900 but the total says 2,100. "
                 "A retry cannot fix this - it must go to human review",
        "text": """GREYSTONE HARDWARE SUPPLY
Invoice GH-88213 | Issued 2026-01-30

Qty  Description            Line total (USD)
 4   Rack shelf kit               1,200.00
 2   Rail mounting set              700.00
                       TOTAL      2,100.00
""",
        "expected": {"vendor_name": "Greystone Hardware Supply", "invoice_number": "GH-88213",
                     "invoice_date": "2026-01-30", "currency": "USD", "category": "hardware",
                     "total": 2100.0},
    },
    {
        "id": "narrative-005",
        "doc_type": "narrative",
        "tests": "category outside the enum (catering): 'other' + category_detail",
        "text": """Statement from Harbor Lane Catering, ref HLC-3021, dated the 3rd of March 2026.
For the quarterly all-hands we provided lunch for 80 guests at GBP 18 per head
(GBP 1,440) and an afternoon coffee service (GBP 260). Amount payable: GBP 1,700.
""",
        "expected": {"vendor_name": "Harbor Lane Catering", "invoice_number": "HLC-3021",
                     "invoice_date": "2026-03-03", "currency": "GBP", "category": "other",
                     "total": 1700.0},
    },
    {
        "id": "receipt-006",
        "doc_type": "receipt",
        "tests": "smudged scan: no vendor name legible, no total - low confidence, review",
        "text": """[scan - top of page torn]
...ware Licence renewal ...... USD 99.00
...onal seats x3 ............. USD [illegible]
Date: 2026-02-1?
""",
        "expected": {"vendor_name": None, "invoice_number": None, "invoice_date": None,
                     "currency": "USD", "category": "software", "total": None},
    },
]

SCORED_FIELDS = ["vendor_name", "invoice_number", "invoice_date", "currency", "category", "total"]

_VENDORS = [
    ("Copperleaf Software", "software", "USD"), ("Riverbend Couriers", "services", "USD"),
    ("Orbital Desk Supply", "hardware", "EUR"), ("Skyline Air Travel", "travel", "GBP"),
    ("Maple & Finch Legal", "services", "USD"), ("Tidewater Data Tools", "software", "EUR"),
]


def make_batch_docs(n: int = 100, seed: int = 7) -> list[dict]:
    """Templated docs for the batch demo. One is deliberately oversized."""
    rng = random.Random(seed)
    docs = []
    for i in range(n):
        vendor, category, currency = rng.choice(_VENDORS)
        items = [(f"Service line {k + 1}", round(rng.uniform(50, 900), 2))
                 for k in range(rng.randint(1, 4))]
        total = round(sum(a for _, a in items), 2)
        number = f"INV-{1000 + i}"
        date = f"2026-0{rng.randint(1, 9)}-{rng.randint(10, 28)}"
        lines = "\n".join(f"{d:<30} {currency} {a:>10,.2f}" for d, a in items)
        if i == 37:  # oversized: forces the chunk-and-resubmit path
            lines += "\n" + "\n".join(
                f"Usage detail {k:04d}: 1 unit @ {currency} 0.00" for k in range(1500))
        docs.append({
            "id": f"doc-{i:03d}",
            "doc_type": "table",
            "text": f"{vendor.upper()}\nInvoice {number}   Date {date}\n\n{lines}\n"
                    f"{'TOTAL':<30} {currency} {total:>10,.2f}\n",
            "expected": {"vendor_name": vendor, "invoice_number": number, "invoice_date": date,
                         "currency": currency, "category": category, "total": total},
        })
    return docs
