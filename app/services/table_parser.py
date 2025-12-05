import re

def parse_findings(summary: str):
    rows = []
    # Get only the table region (between ==== or after heading)
    table_match = re.search(r"\|(.|\n)*", summary)
    if not table_match: 
        return []

    table_text = table_match.group(0).strip()
    lines = [l for l in table_text.split("\n") if l.strip().startswith("|")]

    for line in lines[1:]:  # skip header row
        cols = [c.strip() for c in line.split("|")[1:-1]]

        if len(cols) < 4:
            continue

        issue = cols[0]
        amount = re.sub(r"[^\d]", "", cols[1]) or "0"
        risk = cols[2]
        root = cols[3]

        rows.append({
            "issue": issue,
            "impact": int(amount),
            "risk": risk,
            "root_cause": root
        })

    return rows
