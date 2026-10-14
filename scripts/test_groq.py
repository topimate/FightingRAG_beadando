
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

if not api_key:
    raise ValueError("Nem található a GROQ_API_KEY a .env fájlban!")

client = Groq(api_key=api_key)

response = client.chat.completions.create(
    model=model,
    messages=[
        {
            "role": "system",
            "content": (
                "You are an assistant specializing in combat sports rules. "
                "You answer questions about MMA, Muay Thai, and Kickboxing. "
                "Always distinguish between sports and governing organizations. "
                "If you are uncertain, clearly state your uncertainty."
            ),
        },
        {
            "role": "user",
            "content": "Is ground fighting allowed in Muay Thai?",
        },
    ],
    temperature=0,
    max_completion_tokens=400,
)

print("Model:", model)
print("Question: Is ground fighting allowed in Muay Thai?")
print("\nAnswer:")
print(response.choices[0].message.content)
