import pandas as pd
import io

def generate_excel(summary, findings, risk_score, exposure):
    output = io.BytesIO()

    # Sheet 1 - Overview
    summary_data = {
        "Metric": ["Risk Score Index", "Total Financial Exposure"],
        "Value": [risk_score, exposure]
    }
    df_summary = pd.DataFrame(summary_data)

    # Sheet 2 - Findings Table
    df_findings = pd.DataFrame(findings)

    # Sheet 3 - Risk Category Breakdown
    risk_count = df_findings["risk"].value_counts()
    risk_sheet = pd.DataFrame({
        "Risk Level": risk_count.index,
        "Occurrences": risk_count.values
    })

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_summary.to_excel(writer, index=False, sheet_name="Summary")
        df_findings.to_excel(writer, index=False, sheet_name="Findings")
        risk_sheet.to_excel(writer, index=False, sheet_name="Risk Distribution")

    output.seek(0)
    return output
