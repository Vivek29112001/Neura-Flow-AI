import feedparser
import requests
import logging
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("NeuraFlow")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

COMPANY_FEEDS = {
    "OpenAI":    "https://openai.com/blog/rss.xml",
    "Anthropic": "https://www.anthropic.com/rss.xml",
    "Google AI": "https://blog.research.google/feeds/posts/default",
    "Meta AI":   "https://ai.meta.com/blog/feed/",
    "Microsoft": "https://blogs.microsoft.com/ai/feed/",
    "DeepMind":  "https://deepmind.google/blog/rss.xml",
}

def run_company_agent(config: dict = {}) -> str:
    logger.info("NeuraWatch fetching company updates...")

    updates = []
    headers = {"User-Agent": "Mozilla/5.0 (compatible; NeuraFlow/1.0)"}

    for company, url in COMPANY_FEEDS.items():
        try:
            response = requests.get(url, headers=headers, timeout=10)
            feed = feedparser.parse(response.content)
            for entry in feed.entries[:2]:
                if hasattr(entry, "link") and entry.link.startswith("http"):
                    updates.append({
                        "company": company,
                        "title": entry.title if hasattr(entry, "title") else "Update",
                        "url": entry.link,
                        "summary": entry.get("summary", "")[:200]
                    })
            logger.info(f"Fetched from {company}")
        except Exception as e:
            logger.warning(f"Skipped {company}: {e}")

    if not updates:
        return "No company updates found today."

    updates_text = ""
    for u in updates[:12]:
        updates_text += f"[{u['company']}] {u['title']}\n"
        updates_text += f"URL: {u['url']}\n"
        updates_text += f"Summary: {u['summary']}\n\n"

    prompt = (
        "Summarize these AI company updates:\n\n"
        + updates_text +
        "\nInclude:\n"
        "1. BIGGEST ANNOUNCEMENT this week\n"
        "2. COMPANY SPOTLIGHT — most active company\n"
        "3. WHAT TO WATCH — upcoming releases\n"
        "Only use URLs explicitly provided above."
    )

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800
    )
    return response.choices[0].message.content