import feedparser
import requests
import logging
import os
import sys
import smtplib
import re
from groq import Groq
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("NeuraFlow")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

JOB_FEEDS = {
    # Indeed India
    "Indeed AI Jobs":        "https://in.indeed.com/rss?q=artificial+intelligence&l=India",
    "Indeed ML Jobs":        "https://in.indeed.com/rss?q=machine+learning&l=India",
    "Indeed Data Science":   "https://in.indeed.com/rss?q=data+scientist&l=India",
    "Indeed Python":         "https://in.indeed.com/rss?q=python+developer&l=India",
    "Indeed LLM":            "https://in.indeed.com/rss?q=LLM+engineer&l=India",

    # Remote Jobs
    "RemoteOK AI":           "https://remoteok.com/remote-ai-jobs.rss",
    "RemoteOK ML":           "https://remoteok.com/remote-machine-learning-jobs.rss",
    "RemoteOK Data":         "https://remoteok.com/remote-data-science-jobs.rss",
    "WeWorkRemotely":        "https://weworkremotely.com/categories/remote-programming-jobs.rss",

    # AI Specific
    "AI Jobs Board":         "https://aijobs.net/feed/",
    "HackerNews Jobs":       "https://news.ycombinator.com/jobs.rss",
}

def _fetch_jobs(config: dict) -> list:
    """Fetch jobs from all RSS feeds"""
    jobs = []
    headers = {"User-Agent": "Mozilla/5.0 (compatible; NeuraFlow/1.0)"}

    # Get user preferences
    locations = config.get("jobs", {}).get("locations", ["India", "Remote"])
    roles = config.get("jobs", {}).get("roles", ["AI Engineer"])

    for source, url in JOB_FEEDS.items():
        try:
            response = requests.get(url, headers=headers, timeout=10)
            feed = feedparser.parse(response.content)
            count = 0

            for entry in feed.entries[:5]:
                if not hasattr(entry, "link"):
                    continue
                if not entry.link.startswith("http"):
                    continue

                jobs.append({
                    "title":   entry.title if hasattr(entry, "title") else "No title",
                    "source":  source,
                    "url":     entry.link,
                    "summary": entry.get("summary", "")[:300]
                })
                count += 1

            logger.info(f"Fetched {count} jobs from {source}")
        except Exception as e:
            logger.warning(f"Skipped {source}: {e}")

    logger.info(f"Total jobs fetched: {len(jobs)}")
    return jobs


def _analyze_jobs(jobs: list, config: dict) -> str:
    if not jobs:
        return "No jobs found today."

    user       = config.get("user", {})
    job_config = config.get("jobs", {})

    job_text = ""
    for i, j in enumerate(jobs[:25], 1):
        job_text += f"{i}. {j['title']}\n"
        job_text += f"   Company/Source: {j['source']}\n"
        job_text += f"   APPLY URL: {j['url']}\n"
        job_text += f"   Details: {j['summary'][:150]}\n\n"

    prompt = (
        f"You are an AI career coach.\n\n"
        f"User: Level={user.get('level','Intermediate')}, "
        f"Roles={', '.join(job_config.get('roles',['AI Engineer']))}\n\n"
        f"Job listings with APPLY URLs:\n{job_text}\n\n"
        f"Write a Job Market Report. For EVERY job you mention, "
        f"you MUST include its APPLY URL exactly as shown above.\n\n"
        f"Format each job EXACTLY like this:\n"
        f"- [Job Title] at [Company]\n"
        f"  APPLY: [exact URL from above]\n\n"
        f"Also include:\n"
        f"- TOP IN-DEMAND SKILLS this week\n"
        f"- SALARY RANGE if mentioned\n"
        f"- MARKET TREND\n\n"
        f"RULES: Only use URLs from the list above. Never make up URLs."
    )

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500
    )
    return response.choices[0].message.content

def _send_job_email(report: str):
    """Send job report via email"""
    sender   = os.getenv("GMAIL_ADDRESS")
    password = os.getenv("GMAIL_APP_PASSWORD")
    receiver = os.getenv("GMAIL_ADDRESS")

    if not sender or not password:
        logger.warning("Email credentials missing — skipping job email")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"💼 NeuraJobs Report — {datetime.now().strftime('%A, %b %d')}"
    msg["From"]    = f"NeuraFlow <{sender}>"
    msg["To"]      = receiver

    # Make URLs clickable
    def make_clickable(text):
        url_pattern = r'(https?://[^\s<>]+)'
        return re.sub(
            url_pattern,
            r'<a href="\1" style="color:#6366f1;">\1</a>',
            text
        )

    formatted = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', report)
    formatted  = make_clickable(formatted)
    formatted  = formatted.replace('\n', '<br>')

    html = f"""
    <html>
    <body style="font-family:Arial,sans-serif;max-width:680px;
                 margin:auto;background:#f4f4f8;padding:0;">
        <div style="background:linear-gradient(135deg,#1a1a2e,#16213e);
                    padding:30px;text-align:center;">
            <h1 style="color:white;margin:0;font-size:24px;">
                NeuraJobs Daily Report
            </h1>
            <p style="color:#a0aec0;margin:8px 0 0;font-size:13px;">
                {datetime.now().strftime('%A, %B %d, %Y')}
            </p>
        </div>
        <div style="background:#6366f1;padding:12px 30px;text-align:center;">
            <p style="color:white;margin:0;font-size:14px;font-weight:bold;">
                Today's AI Job Market Intelligence
            </p>
        </div>
        <div style="background:white;padding:30px;
                    line-height:1.8;font-size:15px;color:#2c2c2c;">
            {formatted}
        </div>
        <div style="background:#1a1a2e;padding:20px;text-align:center;">
            <p style="color:#6366f1;margin:0;font-size:13px;">
                NeuraFlow — NeuraJobs Agent
            </p>
            <p style="color:#718096;margin:4px 0 0;font-size:11px;">
                {datetime.now().strftime('%Y-%m-%d %H:%M')} IST
            </p>
        </div>
    </body>
    </html>
    """

    msg.attach(MIMEText(report, "plain"))
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
        logger.info("Job report email sent!")
    except Exception as e:
        logger.error(f"Job email failed: {e}")


def run_job_agent(config: dict = {}) -> str:
    """
    Main entry point — called by NeuraCore
    Returns job market report as string
    """
    logger.info("NeuraJobs starting...")

    # Step 1: Fetch jobs
    jobs = _fetch_jobs(config)

    # Step 2: Analyze with AI
    report = _analyze_jobs(jobs, config)

    logger.info("NeuraJobs analysis done!")
    return report


if __name__ == "__main__":
    # Standalone test
    import json
    with open("../config/user_config.json") as f:
        config = json.load(f)
    report = run_job_agent(config)
    print(report)