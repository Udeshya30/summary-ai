from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()  # loads .env variables

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_summary(text: str, prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": text}
        ],
        max_tokens=1000,
        temperature=0.2  # low = more factual (important for audit)
    )
    return response.choices[0].message.content


def generate_long_summary(text, prompt):
    chunks = list(chunk_text(text))
    partial_summaries = []

    for chunk in chunks:
        summary = generate_summary(chunk, prompt)
        partial_summaries.append(summary)

    # final merge summary
    final = generate_summary("\n".join(partial_summaries), prompt)
    return final
