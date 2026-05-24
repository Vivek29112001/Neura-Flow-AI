from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import os
import re
import json
import base64
import pickle
import logging
import tempfile

SCOPES = ["https://www.googleapis.com/auth/calendar"]
logger = logging.getLogger("NeuraFlow")

# Detect headless / server environments (Railway, CI, Docker)
IS_HEADLESS = any([
    os.getenv("RAILWAY_ENVIRONMENT"),
    os.getenv("RAILWAY_PROJECT_ID"),
    os.getenv("RAILWAY_SERVICE_ID"),
    os.getenv("CI"),
    os.getenv("HEADLESS") == "true",
])


# ─────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────
def get_calendar_service():
    creds = None

    # Railway: Restore token from env variable
    if not os.path.exists("token.pickle"):
        token_b64 = os.getenv("GOOGLE_TOKEN_BASE64")
        if token_b64:
            with open("token.pickle", "wb") as f:
                f.write(base64.b64decode(token_b64))
            print("Token restored from environment!")

    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Refreshing expired Google token...")
            creds.refresh(Request())
            # Save refreshed token back to disk (for this session)
            with open("token.pickle", "wb") as token:
                pickle.dump(creds, token)
            logger.info("Token refreshed and saved!")
        else:
            # ── Headless server (Railway) — cannot open a browser ──
            if IS_HEADLESS:
                raise RuntimeError(
                    "Google Calendar: no valid token found on Railway.\n"
                    "Run 'python generate_token.py' locally, then set the printed\n"
                    "GOOGLE_TOKEN_BASE64 value as a Railway environment variable."
                )

            # ── Local: interactive browser OAuth flow ──
            creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
            if creds_json:
                tmp = tempfile.NamedTemporaryFile(
                    mode='w', suffix='.json', delete=False
                )
                tmp.write(creds_json)
                tmp.flush()
                creds_path = tmp.name
                tmp.close()
            else:
                creds_path = os.getenv(
                    "GOOGLE_CREDENTIALS_PATH",
                    "google_credentials.json"
                )

            flow = InstalledAppFlow.from_client_secrets_file(
                creds_path, SCOPES
            )
            creds = flow.run_local_server(port=0)

            with open("token.pickle", "wb") as token:
                pickle.dump(creds, token)

    return build("calendar", "v3", credentials=creds)


# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────
def _extract_urls(text: str) -> list:
    """Extract and clean real URLs from text"""
    urls = re.findall(r'https?://[^\s<>\'")\]\\]+', text)
    cleaned = [u.rstrip('.,;:)"\']') for u in urls]
    # Remove duplicates preserving order
    seen, unique = set(), []
    for u in cleaned:
        if u not in seen and "[link" not in u:
            seen.add(u)
            unique.append(u)
    return unique


def _clean_text(text: str, max_len: int = 500) -> str:
    """Remove URLs and markdown, limit length"""
    text = re.sub(r'https?://[^\s]+', '', text)
    text = re.sub(r'\*\*?(.*?)\*\*?', r'\1', text)
    text = re.sub(r'#{1,3}\s*', '', text)
    text = re.sub(r'\[link (unavailable|removed)\]', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()[:max_len]


def _extract_section(report: str, *keywords) -> str:
    """Extract section content by keyword"""
    for kw in keywords:
        pattern = rf"(?:#{1,3}\s*)?[^\n]*{kw}[^\n]*\n(.*?)(?=#{1,3}|\Z)"
        match = re.search(pattern, report, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()[:800]
    return ""


def _format_url_list(urls: list, label: str = "LINKS") -> str:
    """Format URLs as a clean readable list"""
    if not urls:
        return ""
    lines = [f"\n{'='*40}", f"{label}:\n"]
    for url in urls[:5]:
        domain = re.sub(r'https?://(www\.)?', '', url).split('/')[0]
        lines.append(f"* {domain}")
        lines.append(f"  {url}")
    return "\n".join(lines)


def _delete_old_events(service, prefix: str):
    """Delete old NeuraFlow events with given prefix"""
    try:
        today = datetime.now()
        result = service.events().list(
            calendarId   = "primary",
            timeMin      = today.strftime("%Y-%m-%dT00:00:00Z"),
            maxResults   = 100,
            singleEvents = True,
            orderBy      = "startTime"
        ).execute()

        deleted = 0
        for event in result.get("items", []):
            if prefix in event.get("summary", ""):
                service.events().delete(
                    calendarId = "primary",
                    eventId    = event["id"]
                ).execute()
                deleted += 1

        if deleted:
            print(f"Deleted {deleted} old '{prefix}' events")
    except Exception as e:
        print(f"Could not delete old events: {e}")


def _create_event(
    service,
    title: str,
    description: str,
    date: datetime,
    hour: int,
    duration_mins: int = 60,
    color_id: str = "1"
) -> bool:
    """Create a single Google Calendar event"""
    start = date.replace(hour=hour, minute=0, second=0, microsecond=0)
    end   = start + timedelta(minutes=duration_mins)

    event = {
        "summary":     title,
        "description": description,
        "colorId":     color_id,
        "start": {
            "dateTime": start.strftime("%Y-%m-%dT%H:%M:%S"),
            "timeZone": "Asia/Kolkata",
        },
        "end": {
            "dateTime": end.strftime("%Y-%m-%dT%H:%M:%S"),
            "timeZone": "Asia/Kolkata",
        },
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "popup", "minutes": 15},
                {"method": "email", "minutes": 30},
            ],
        },
    }

    try:
        service.events().insert(
            calendarId = "primary",
            body       = event
        ).execute()
        return True
    except Exception as e:
        print(f"Failed to create event '{title}': {e}")
        return False


# ─────────────────────────────────────────
# 1. LEARNING EVENTS — 9 AM (7 days)
# Color: Green (2)
# ─────────────────────────────────────────
def add_learning_events(report: str):
    """Add 7 daily learning tasks with real resource URLs"""
    service = get_calendar_service()
    today   = datetime.now()

    print(f"\nAdding LEARNING events for week of: {today.strftime('%Y-%m-%d')}")
    _delete_old_events(service, "NeuraLearn")

    days  = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    added = 0

    # Extract resource URLs from learning section
    learn_section = _extract_section(
        report,
        "YOUR LEARNING", "LEARNING MISSION",
        "THIS WEEK", "WEEK'S PLAN",
        "TOP RESOURCES"
    )
    global_urls = _extract_urls(learn_section)

    for i, day in enumerate(days):
        event_date = today + timedelta(days=i)

        # Try to extract day-specific task
        pattern = rf"{day}[:\s]+(.*?)(?=Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|\Z)"
        match   = re.search(pattern, report, re.IGNORECASE | re.DOTALL)

        if match:
            task_raw = match.group(1).strip()[:600]
        else:
            task_raw = learn_section[:400] if learn_section else "Review today's AI updates."

        # Get URLs from this specific day's task
        day_urls  = _extract_urls(task_raw)
        all_urls  = day_urls if day_urls else global_urls[:2]

        clean = _clean_text(task_raw, 400)
        short = clean[:55].replace('\n', ' ')

        # Build rich description
        desc  = f"NeuraFlow Learning — Day {i+1} of 7\n"
        desc += f"Week: {today.strftime('%B %d, %Y')}\n"
        desc += "=" * 40 + "\n\n"
        desc += "TASK:\n\n"
        desc += clean[:450] + "\n"
        desc += _format_url_list(all_urls, "LEARNING RESOURCES")
        desc += "\n\n" + "=" * 40 + "\n"
        desc += "Tip: Complete this task before 10 AM for best results!"
        desc += "\n\nGenerated by NeuraFlow AI Agent"

        title = f"NeuraLearn Day {i+1}: {short}..."

        if _create_event(
            service, title, desc,
            event_date, hour=9,
            duration_mins=60,
            color_id="2"
        ):
            added += 1
            print(f"  Added: {day} {event_date.strftime('%d/%m/%Y')} — {len(all_urls)} resource URLs")

    print(f"Learning events: {added}/7 added\n")
    return added


# ─────────────────────────────────────────
# 2. JOB EVENTS — 10 AM (daily)
# Color: Yellow (5)
# ─────────────────────────────────────────
def add_job_events(report: str):
    """Add daily job alert with real apply URLs"""
    service = get_calendar_service()
    today   = datetime.now()

    print(f"Adding JOB event for: {today.strftime('%Y-%m-%d')}")
    _delete_old_events(service, "NeuraJobs")

    job_section = _extract_section(
        report,
        "JOB MARKET", "HOT JOBS",
        "APPLY NOW", "JOB MARKET PULSE"
    )

    if not job_section:
        print("  No job section found — skipping")
        return 0

    urls  = _extract_urls(job_section)
    clean = _clean_text(job_section, 600)

    # Fallback URLs if none found
    fallback_urls = [
        "https://remoteok.com/remote-ai-jobs",
        "https://aijobs.net",
        "https://weworkremotely.com/categories/remote-programming-jobs",
    ]
    apply_urls = urls if urls else fallback_urls

    # Build rich description
    desc  = f"NeuraFlow Job Intelligence\n"
    desc += f"{today.strftime('%A, %B %d, %Y')}\n"
    desc += "=" * 40 + "\n\n"
    desc += "TODAY'S AI JOB OPPORTUNITIES:\n\n"
    desc += clean[:600] + "\n"
    desc += _format_url_list(apply_urls, "APPLY HERE")
    desc += "\n\n" + "=" * 40 + "\n"
    desc += "Tip: Apply within 24 hours for best response rates!"
    desc += "\n\nGenerated by NeuraFlow AI Agent"

    title = f"NeuraJobs {today.strftime('%a %b %d')} — {len(apply_urls)} AI Job Alerts"

    if _create_event(
        service, title, desc,
        today, hour=10,
        duration_mins=30,
        color_id="5"
    ):
        print(f"  Added: {today.strftime('%d/%m/%Y')} — {len(apply_urls)} job URLs\n")
        return 1

    return 0


# ─────────────────────────────────────────
# 3. NEWS EVENTS — 8 AM (daily)
# Color: Cyan (7)
# ─────────────────────────────────────────
def add_news_events(report: str):
    """Add daily AI news digest with real article URLs"""
    service = get_calendar_service()
    today   = datetime.now()

    print(f"Adding NEWS event for: {today.strftime('%Y-%m-%d')}")
    _delete_old_events(service, "NeuraNews")

    # Extract news sections
    news_section = _extract_section(
        report,
        "AI HIGHLIGHTS", "TOP HIGHLIGHTS",
        "TODAY'S TOP", "TODAY'S TOP AI"
    )
    mustread_section = _extract_section(report, "MUST-READ")

    if not news_section and not mustread_section:
        print("  No news section found — skipping")
        return 0

    # Collect URLs from both sections
    news_urls     = _extract_urls(news_section)
    mustread_urls = _extract_urls(mustread_section)
    all_urls      = list(dict.fromkeys(news_urls + mustread_urls))[:6]

    clean = _clean_text(news_section or mustread_section, 600)

    # Fallback URLs
    fallback_urls = [
        "https://venturebeat.com/category/ai",
        "https://arxiv.org/list/cs.AI/recent",
        "https://huggingface.co/blog",
    ]
    article_urls = all_urls if all_urls else fallback_urls

    # Build rich description
    desc  = f"NeuraFlow AI News Digest\n"
    desc += f"{today.strftime('%A, %B %d, %Y')}\n"
    desc += "=" * 40 + "\n\n"
    desc += "TODAY'S AI HIGHLIGHTS:\n\n"
    desc += clean[:600] + "\n"
    desc += _format_url_list(article_urls, "READ FULL ARTICLES")
    desc += "\n\n" + "=" * 40 + "\n"
    desc += "Tip: Read during your morning coffee for best retention!"
    desc += "\n\nGenerated by NeuraFlow AI Agent"

    title = f"NeuraNews {today.strftime('%a %b %d')} — {len(article_urls)} AI Updates"

    if _create_event(
        service, title, desc,
        today, hour=8,
        duration_mins=20,
        color_id="7"
    ):
        print(f"  Added: {today.strftime('%d/%m/%Y')} — {len(article_urls)} article URLs\n")
        return 1

    return 0


# ─────────────────────────────────────────
# MASTER FUNCTION
# ─────────────────────────────────────────
def add_all_events(report: str):
    """
    Master function — adds ALL 3 types of events:
    8 AM  — NeuraNews  (AI updates)
    9 AM  — NeuraLearn (7-day learning plan)
    10 AM — NeuraJobs  (job alerts)
    """
    print("\nNeuraFlow Calendar Update Starting...")
    print("=" * 50)

    news     = add_news_events(report)
    learning = add_learning_events(report)
    jobs     = add_job_events(report)

    total = learning + jobs + news
    print("=" * 50)
    print(f"Calendar Summary for {datetime.now().strftime('%B %d, %Y')}:")
    print(f"  8 AM  NeuraNews events:     {news}/1")
    print(f"  9 AM  NeuraLearn events:    {learning}/7")
    print(f"  10 AM NeuraJobs events:     {jobs}/1")
    print(f"  Total events added:         {total}")
    print("=" * 50)
    return total


# ─────────────────────────────────────────
# STANDALONE TEST
# ─────────────────────────────────────────
if __name__ == "__main__":
    test_report = """
## TODAY'S TOP AI HIGHLIGHTS
1. GPT-5 released by OpenAI https://openai.com/blog/gpt-5
2. LangChain v0.2 launched https://blog.langchain.dev/langchain-v02
3. Hugging Face releases new model https://huggingface.co/blog

## JOB MARKET PULSE
- Senior AI Engineer at Google
  APPLY: https://remoteok.com/remote-ai-jobs
- ML Engineer at Meta
  APPLY: https://weworkremotely.com/categories/remote-programming-jobs
- Data Scientist at Vercel
  APPLY: https://aijobs.net

## YOUR LEARNING MISSION TODAY
Focus on PyTorch fundamentals today.

Resource: PyTorch Tutorials
URL: https://pytorch.org/tutorials

Resource: fast.ai Course
URL: https://course.fast.ai

## THIS WEEK'S PLAN
Monday: PyTorch tensors https://pytorch.org/tutorials/beginner/basics/tensorqs_tutorial.html
Tuesday: Neural networks https://www.deeplearning.ai/courses
Wednesday: Kaggle practice https://www.kaggle.com/learn
Thursday: LangChain basics https://python.langchain.com/docs/get_started/introduction
Friday: Build a simple chatbot
Saturday: fast.ai deep learning https://course.fast.ai
Sunday: Review and practice https://www.kaggle.com/competitions

## MUST-READ TODAY
* OpenAI Blog: https://openai.com/blog
* Hugging Face: https://huggingface.co/blog
* Papers With Code: https://paperswithcode.com
"""
    add_all_events(test_report)