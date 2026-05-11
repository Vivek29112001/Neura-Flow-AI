import logging
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("NeuraFlow")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def run_project_agent(config: dict = {}) -> str:
    logger.info("NeuraForge generating project ideas...")

    user    = config.get("user", {})
    topics  = config.get("topics", {})
    level   = user.get("level", "Intermediate")
    primary = topics.get("primary", ["AI", "ML"])
    goals   = user.get("goals", [])

    prompt = (
        f"Generate detailed project ideas for an AI developer.\n\n"
        f"Profile:\n"
        f"- Level: {level}\n"
        f"- Topics: {', '.join(primary)}\n"
        f"- Goals: {', '.join(goals)}\n\n"
        f"For each project provide:\n"
        f"1. WEEKEND PROJECT (2 days)\n"
        f"   - Project name and description\n"
        f"   - Tech stack (Python libraries only)\n"
        f"   - 5 implementation steps\n\n"
        f"2. PORTFOLIO PROJECT (1-2 weeks)\n"
        f"   - Project name and description\n"
        f"   - Tech stack\n"
        f"   - Why it impresses employers\n\n"
        f"3. LEARNING PROJECT (ongoing)\n"
        f"   - Project name and description\n"
        f"   - What skills it builds\n\n"
        f"IMPORTANT: Do NOT include any URLs or links.\n"
        f"Focus only on project descriptions and tech stacks.\n"
    )

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )
    return response.choices[0].message.content