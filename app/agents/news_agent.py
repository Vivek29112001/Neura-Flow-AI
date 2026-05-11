import feedparser
import requests
import hashlib
import logging
import os
import sys
from groq import Groq
from datetime import datetime, timezone
from dotenv import load_dotenv
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import Session, Article

load_dotenv()
logger = logging.getLogger("NeuraFlow")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

BASE_FEEDS = {
    "arXiv AI":         "https://arxiv.org/rss/cs.AI",
    "arXiv ML":         "https://arxiv.org/rss/cs.LG",
    "Hugging Face":     "https://huggingface.co/blog/feed.xml",
    "OpenAI Blog":      "https://openai.com/blog/rss.xml",
    "Google AI Blog":   "https://blog.research.google/feeds/posts/default",
    "LangChain Blog":   "https://blog.langchain.dev/rss/",
    "Anthropic Blog":   "https://www.anthropic.com/rss.xml",
    "VentureBeat AI":   "https://venturebeat.com/category/ai/feed/",
    "MIT Tech Review":  "https://www.technologyreview.com/feed/",
    "IEEE Spectrum AI": "https://spectrum.ieee.org/feeds/topic/artificial-intelligence.rss",
    "Reddit ML":        "https://www.reddit.com/r/MachineLearning/.rss",
    "Reddit LocalLLaMA":"https://www.reddit.com/r/LocalLLaMA/.rss",
}

def run_news_agent(config: dict = {}) -> str:
    logger.info("NeuraNews fetching articles...")
    session = Session()
    articles = []
    headers = {"User-Agent": "Mozilla/5.0 (compatible; NeuraFlow/1.0)"}

    for source, url in BASE_FEEDS.items():
        try:
            response = requests.get(url, headers=headers, timeout=10)
            feed = feedparser.parse(response.content)
            for entry in feed.entries[:5]:
                if not hasattr(entry, "link"):
                    continue
                if not entry.link.startswith("http"):
                    continue
                article_id = hashlib.md5(entry.link.encode()).hexdigest()
                exists = session.query(Article).filter_by(id=article_id).first()
                if exists:
                    continue
                article = Article(
                    id=article_id,
                    title=entry.title if hasattr(entry, "title") else "No title",
                    source=source,
                    url=entry.link,
                    summary=entry.get("summary", "")[:500],
                    fetched_at=datetime.now(timezone.utc)
                )
                session.add(article)
                articles.append({
                    "title": article.title,
                    "source": source,
                    "url": entry.link,
                    "summary": article.summary
                })
            logger.info(f"Fetched from {source}")
        except Exception as e:
            logger.warning(f"Skipped {source}: {e}")

    session.commit()
    session.close()
    logger.info(f"Total new articles: {len(articles)}")

    if not articles:
        return "No new AI articles found today."

    article_text = ""
    for i, a in enumerate(articles[:20], 1):
        article_text += f"{i}. [{a['source']}] {a['title']}\n"
        article_text += f"   URL: {a['url']}\n"
        article_text += f"   Summary: {a['summary'][:200]}\n\n"

    prompt = (
        "Summarize these AI articles into 5 key highlights.\n"
        "For each: title, 2-line explanation, and EXACT URL from the list.\n"
        "Only use URLs explicitly provided below.\n\n"
        + article_text
    )

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )
    return response.choices[0].message.content



    