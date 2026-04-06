from openai import AsyncOpenAI
import os
from dotenv import load_dotenv
from openai import RateLimitError


# load environment variables
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY is not set")

client = AsyncOpenAI(api_key=api_key)


# function to format logs
def format_logs(logs):
    if not logs:
        return "No logs available."

    logs_text = ""
    for log in logs:
        logs_text += (
            f"{log.created_at} | action={log.action} | "
            f"user={log.user_id} | data={log.extra_data}\n"
        )
    return logs_text



async def ask_ai(logs, question: str):
    try:
        logs_text = format_logs(logs)

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You analyze audit logs."},
                {"role": "user", "content": question},
            ],
        )

        return response.choices[0].message.content

    except RateLimitError:
        return "AI service unavailable due to quota limits. Please try later."


# 🔹 STREAM VERSION
async def ask_ai_stream(logs, question: str):
    logs_text = format_logs(logs)

    prompt = f"""
You are an AI assistant that analyzes organization audit logs.

Answer the question using ONLY the logs.

Logs:
{logs_text}

Question:
{question}
"""

    stream = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt},
        ],
        stream=True
    )

    async for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content