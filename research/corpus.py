"""Fictional sources for research/research_agent.py. Lumen Bay does not exist.

Planted on purpose:
- AGREEMENT: 12,000 tonnes diverted appears in a web source AND an internal doc
  -> should be reported as well-established.
- CONFLICT 1: household participation 41% (council sign-up data) vs 34%
  (institute survey) - two credible sources, different methods. Both must survive.
- CONFLICT 2: cost per household $18 (blog, Nov 2025, 2024 budget) vs $21
  (council report, Jan 2026, 2025 budget) - explained by date, still both kept.
- TIMEOUT: reading "hauler-contract-memo" times out when SIMULATE_TIMEOUT is on.
"""

WEB_PAGES = [
    {
        "url": "https://lumenbay-gazette.example/2026/03/composting-milestone",
        "source_name": "Lumen Bay Gazette",
        "publication_date": "2026-03-10",
        "keywords": ["composting", "participation", "diversion", "households", "landfill"],
        "text": "Lumen Bay's curbside composting program reached 41% of households in 2025, "
                "according to city sign-up figures, and diverted roughly 12,000 tonnes of food "
                "waste from the Harrow Point landfill.",
    },
    {
        "url": "https://coastal-sustainability.example/reports/lumen-bay-2025",
        "source_name": "Coastal Sustainability Institute",
        "publication_date": "2026-02-01",
        "keywords": ["composting", "participation", "survey", "households"],
        "text": "Our door-to-door survey of 1,200 Lumen Bay households found that 34% "
                "actively used their compost bins at least twice a month in 2025. Sign-up "
                "counts overstate active use because many registered households never "
                "set a bin out.",
    },
    {
        "url": "https://greenledger-blog.example/posts/lumen-bay-compost-costs",
        "source_name": "GreenLedger (blog)",
        "publication_date": "2025-11-05",
        "keywords": ["composting", "cost", "budget", "households"],
        "text": "Based on the 2024 municipal budget, Lumen Bay's composting program costs "
                "about $18 per household per year.",
    },
]

DOCUMENTS = {
    "council-waste-report-2025": {
        "title": "Lumen Bay City Council - Annual Waste Report 2025",
        "publication_date": "2026-01-15",
        "text": "Section 3. Organics. Registered participation: 41% of households "
                "(sign-ups as of Dec 2025). Food waste diverted from landfill: 12,000 tonnes. "
                "Program cost (2025 budget): $21 per household per year, up from 2024 due to "
                "a new collection route.",
    },
    "resident-survey-summary": {
        "title": "Resident Services Survey - Summary of Results",
        "publication_date": "2026-02-20",
        "text": "72% of composting participants rated the program 'satisfied' or 'very "
                "satisfied'. Most common complaint: odour from bins in summer (cited by 22%).",
    },
    "hauler-contract-memo": {
        "title": "Memo: Organics Hauler Contract Renewal",
        "publication_date": "2026-03-02",
        "text": "The hauler contract renewal adds a second weekly pickup from July 2026, "
                "raising projected cost to $24 per household per year.",
    },
}

TIMEOUT_DOC = "hauler-contract-memo"
