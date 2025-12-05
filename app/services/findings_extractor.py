from openai import OpenAI
client = OpenAI()

def extract_findings(text: str):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": 
                "Extract audit findings as structured JSON:\n"
                "Format:\n"
                "[{\"finding\":\"...\",\"risk_level\":\"High/Medium/Low\",\"recommendation\":\"...\"}]"
            },
            {"role": "user", "content": text}
        ],
        temperature=0.1
    )
    return response.choices[0].message.content
