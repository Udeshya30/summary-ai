import re

SECTION_KEYWORDS = [
    "objective", "scope", "methodology",
    "findings", "observations",
    "risk", "audit opinion", "recommendations", "conclusion"
]

def split_sections(text: str) -> dict:
    sections = {}
    lowered = text.lower()

    for keyword in SECTION_KEYWORDS:
        pattern = rf"{keyword}[^:]*[:\-]\s*(.*?)(?=\n[A-Z][a-z]+|$)"
        match = re.search(pattern, lowered, re.DOTALL)
        sections[keyword] = match.group(1).strip() if match else "Not Found"

    return sections

def clean_text(text: str) -> str:
    text = text.replace("\n", " ").replace("  ", " ")
    return text.strip()

def chunk_text(text, chunk_size=2000):
    words = text.split()
    for i in range(0, len(words), chunk_size):
        yield " ".join(words[i:i+chunk_size])
