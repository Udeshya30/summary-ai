import re

def calculate_risk_score(summary_text):
    score = 0
    
    # Weighted scoring (enterprise logic)
    weights = {"High": 3, "Medium": 2, "Low": 1}

    for level, w in weights.items():
        score += len(re.findall(level, summary_text)) * w

    return score

def estimate_financial_impact(summary_text):
    amounts = re.findall(r"[₹Rs\. ]([0-9,]+)", summary_text)
    values = [int(x.replace(",", "")) for x in amounts if x.replace(",", "").isdigit()]
    return sum(values) if values else 0
