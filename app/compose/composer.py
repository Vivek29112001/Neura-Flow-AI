import os
import re
import requests
import smtplib
import logging
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Optional
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
logger = logging.getLogger("NeuraFlow")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


class NeuraCompose:
    """
    NeuraCompose — Report Composer of NeuraFlow
    Takes all agent results → merges → sends via email + calendar + whatsapp
    """

    SECTION_ICONS = {
        "NeuraNews":  "📰",
        "NeuraJobs":  "💼",
        "NeuraLearn": "🎓",
        "NeuraCode":  "💻",
        "NeuraWatch": "🏢",
        "NeuraForge": "🔨",
    }

    def __init__(
        self,
        results: Dict[str, Optional[str]],
        config: dict,
        day: str
    ):
        self.results  = results
        self.config   = config
        self.day      = day
        self.user     = config.get("user", {})
        self.channels = config.get("channels", {})
        self.report: str = ""
        logger.info(f"NeuraCompose initialized with {len(results)} agent results")

    # ─────────────────────────────────────────
    # STEP 1: COMBINE ALL AGENT RESULTS
    # ─────────────────────────────────────────
    def _build_combined_context(self) -> str:
        """Combines all agent results into one context for AI"""
        combined = ""
        for agent_name, result in self.results.items():
            if result:
                icon = self.SECTION_ICONS.get(agent_name, "📌")
                combined += f"\n\n{'='*50}\n"
                combined += f"{icon} {agent_name.upper()} REPORT:\n"
                combined += f"{'='*50}\n"
                combined += result
        return combined

    # ─────────────────────────────────────────
    # STEP 2: GENERATE UNIFIED REPORT
    # ─────────────────────────────────────────
    def _generate_unified_report(self, combined: str) -> str:
        """Uses Groq AI to generate one beautiful unified report"""
        user_name  = self.user.get("name", "User")
        user_level = self.user.get("level", "Intermediate")
        user_goals = self.user.get("goals", [])

        prompt = f"""
        You are NeuraCompose for NeuraFlow AI system.

        User: Name={user_name}, Level={user_level}, Goals={', '.join(user_goals)}

        Agent Reports (with REAL URLs — preserve ALL of them):
        {combined}

        Write a unified daily report with these sections.
        For Job Market Pulse: include EVERY job URL exactly as "APPLY: [url]"
        For Learning Mission: include resource URLs exactly as shown
        For Must-Read: only use URLs from the reports above

        ## TODAY'S TOP AI HIGHLIGHTS
        (5 key updates — simple explanations)

        ## JOB MARKET PULSE
        (For each job mention the title AND its APPLY URL exactly as given)
        Format:
        - Job Title at Company
        APPLY: https://exact-url-from-report

        ## YOUR LEARNING MISSION TODAY
        (Today's focus task — include the resource name AND URL)
        Format:
        Resource: [Name]
        URL: https://exact-url-from-report

        ## THIS WEEK'S PLAN
        (Day by day — Monday to Sunday)

        ## TRENDING IN TECH
        (GitHub repos with their exact URLs)

        ## COMPANY WATCH
        (Company news with article URLs)

        ## BUILD THIS WEEKEND
        (One project idea — no URL needed)

        ## MUST-READ TODAY
        (Top 3 — only URLs from agent reports above)
        Format:
        - [Title]: https://exact-url

        CRITICAL RULES:
        - Copy ALL job APPLY URLs exactly as given in reports
        - Copy ALL learning resource URLs exactly as given
        - NEVER generate or guess any URL
        - If no URL available, write (no link) — never make one up
        """
        
        logger.info("Generating unified report with Groq AI...")
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=3000
        )
        return response.choices[0].message.content

    # ─────────────────────────────────────────
    # STEP 2.5: VALIDATE URLs
    # ─────────────────────────────────────────
    def _validate_urls(self, report: str) -> str:
        """Validate all URLs — remove unreachable/fake ones"""

        def check_url(match):
            url = match.group(0).rstrip('.,;:)"\']')
            try:
                res = requests.head(
                    url,
                    timeout=5,
                    allow_redirects=True,
                    headers={"User-Agent": "Mozilla/5.0"}
                )
                if res.status_code < 400:
                    logger.info(f"URL OK: {url}")
                    return url
                else:
                    logger.warning(f"URL dead ({res.status_code}): {url}")
                    return "[link unavailable]"
            except Exception as e:
                logger.warning(f"URL failed: {url} — {e}")
                return "[link unavailable]"

        url_pattern = r'https?://[^\s<>\'")\]\\]+'
        return re.sub(url_pattern, check_url, report)

    # ─────────────────────────────────────────
    # STEP 3A: EMAIL
    # ─────────────────────────────────────────
    def _send_email(self, report: str):
        """Sends the unified report via Gmail"""
        if not self.channels.get("email", False):
            logger.info("Email channel disabled — skipping")
            return

        sender   = os.getenv("GMAIL_ADDRESS")
        password = os.getenv("GMAIL_APP_PASSWORD")
        receiver = os.getenv("GMAIL_ADDRESS")

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"NeuraFlow Daily Report — {datetime.now().strftime('%A, %b %d')}"
        msg["From"]    = f"NeuraFlow <{sender}>"
        msg["To"]      = receiver

        msg.attach(MIMEText(report, "plain"))
        msg.attach(MIMEText(self._format_html(report), "html"))

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender, password)
                server.sendmail(sender, receiver, msg.as_string())
            logger.info("Email sent successfully!")
        except Exception as e:
            logger.error(f"Email failed: {e}")

    def _format_html(self, report: str) -> str:
        """Converts report to beautiful HTML email with URL cards"""
        today_str = datetime.now().strftime('%A, %B %d, %Y')
        user_name = self.user.get('name', 'User')

        def make_url_card(match):
            url    = match.group(0).rstrip('.,;:)"\']')
            domain = re.sub(r'https?://(www\.)?', '', url).split('/')[0]
            return (
                f'<a href="{url}" target="_blank" '
                f'style="display:inline-block;margin:4px 0;padding:8px 14px;'
                f'background:#eef2ff;border:1px solid #c7d2fe;border-radius:8px;'
                f'color:#4338ca;text-decoration:none;font-size:13px;'
                f'font-weight:500;">'
                f'🔗 {domain}</a>'
            )

        def format_section(text):
            text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
            text = re.sub(r'\*(.*?)\*', r'<em style="color:#666;">\1</em>', text)
            text = re.sub(
                r'#{1,3}\s*(.*)',
                r'</div><div class="section"><h3 style="color:#1e1b4b;'
                r'font-size:15px;font-weight:600;margin:0 0 12px;'
                r'padding:10px 14px;background:#f5f3ff;border-left:4px solid '
                r'#6366f1;border-radius:4px;">\1</h3>',
                text
            )
            text = re.sub(
                r'^[-•*]\s+(.+)$',
                r'<div style="display:flex;gap:8px;margin:6px 0;">'
                r'<span style="color:#6366f1;font-weight:bold;margin-top:1px;">▸</span>'
                r'<span>\1</span></div>',
                text, flags=re.MULTILINE
            )
            text = re.sub(
                r'^(\d+)\.\s+(.+)$',
                r'<div style="display:flex;gap:8px;margin:8px 0;">'
                r'<span style="background:#6366f1;color:white;border-radius:50%;'
                r'width:22px;height:22px;display:inline-flex;align-items:center;'
                r'justify-content:center;font-size:11px;font-weight:bold;'
                r'flex-shrink:0;">\1</span><span>\2</span></div>',
                text, flags=re.MULTILINE
            )
            text = re.sub(r'https?://[^\s<>\'")\]\\]+', make_url_card, text)
            text = text.replace('\n', '<br>')
            return text

        formatted = format_section(report)

        return f"""
        <html>
        <body style="font-family:'Segoe UI',Arial,sans-serif;max-width:680px;
                     margin:auto;padding:0;background:#f4f4f8;">

            <div style="background:linear-gradient(135deg,#1e1b4b 0%,#312e81 50%,#4338ca 100%);
                        padding:40px 30px;text-align:center;">
                <div style="font-size:32px;margin-bottom:8px;">🧠</div>
                <h1 style="color:white;margin:0;font-size:26px;font-weight:700;letter-spacing:1px;">
                    NeuraFlow
                </h1>
                <p style="color:#a5b4fc;margin:6px 0 0;font-size:13px;">Daily Intelligence Report</p>
                <p style="color:#818cf8;margin:4px 0 0;font-size:12px;">{today_str}</p>
            </div>

            <div style="background:#4338ca;padding:14px 30px;text-align:center;">
                <p style="color:white;margin:0;font-size:15px;font-weight:600;">
                    Good Morning, {user_name}! Your AI briefing is ready 🚀
                </p>
            </div>

            <div style="background:white;padding:14px 20px;
                        border-bottom:1px solid #e5e7eb;text-align:center;">
                <span style="background:#e0f2fe;color:#0369a1;padding:5px 10px;
                             border-radius:20px;font-size:11px;margin:3px;
                             display:inline-block;">📰 NeuraNews</span>
                <span style="background:#dcfce7;color:#166534;padding:5px 10px;
                             border-radius:20px;font-size:11px;margin:3px;
                             display:inline-block;">💼 NeuraJobs</span>
                <span style="background:#fef3c7;color:#92400e;padding:5px 10px;
                             border-radius:20px;font-size:11px;margin:3px;
                             display:inline-block;">🎓 NeuraLearn</span>
                <span style="background:#f3e8ff;color:#6b21a8;padding:5px 10px;
                             border-radius:20px;font-size:11px;margin:3px;
                             display:inline-block;">💻 NeuraCode</span>
                <span style="background:#fee2e2;color:#991b1b;padding:5px 10px;
                             border-radius:20px;font-size:11px;margin:3px;
                             display:inline-block;">🏢 NeuraWatch</span>
                <span style="background:#fff7ed;color:#9a3412;padding:5px 10px;
                             border-radius:20px;font-size:11px;margin:3px;
                             display:inline-block;">🔨 NeuraForge</span>
            </div>

            <div style="background:white;padding:30px 30px 10px;">
                <div class="section">
                    {formatted}
                </div>
            </div>

            {self._build_url_summary(report)}

            <div style="background:#1e1b4b;padding:24px;text-align:center;margin-top:0;">
                <p style="color:#818cf8;margin:0;font-size:14px;font-weight:600;">
                    NeuraFlow Intelligence System
                </p>
                <p style="color:#4f46e5;margin:6px 0 0;font-size:12px;">
                    Powered by NeuraCore + 6 AI Agents
                </p>
                <p style="color:#3730a3;margin:4px 0 0;font-size:11px;">
                    {datetime.now().strftime('%Y-%m-%d %H:%M')} IST
                </p>
            </div>
        </body>
        </html>
        """

    def _build_url_summary(self, report: str) -> str:
        """Build a dedicated URL cards section at the bottom of email"""
        all_urls = re.findall(r'https?://[^\s<>\'")\]\\]+', report)
        all_urls = [u.rstrip('.,;:)"\']') for u in all_urls]

        seen       = set()
        unique_urls = []
        for url in all_urls:
            if url not in seen and "[link" not in url:
                seen.add(url)
                unique_urls.append(url)

        if not unique_urls:
            return ""

        categories = {
            "📰 Articles & News":    [],
            "💼 Job Listings":       [],
            "🎓 Learning Resources": [],
            "💻 GitHub Repos":       [],
            "🔗 Other Links":        [],
        }

        for url in unique_urls:
            if any(x in url for x in ["arxiv", "venturebeat", "techcrunch",
                                       "technologyreview", "openai.com/blog",
                                       "anthropic.com", "deepmind", "reddit",
                                       "huggingface.co/blog", "langchain.dev/blog"]):
                categories["📰 Articles & News"].append(url)
            elif any(x in url for x in ["remoteok", "weworkremotely", "indeed",
                                         "linkedin", "aijobs", "ycombinator.com/jobs"]):
                categories["💼 Job Listings"].append(url)
            elif any(x in url for x in ["course", "learn", "tutorial", "kaggle",
                                         "youtube", "deeplearning", "fast.ai",
                                         "pytorch", "tensorflow", "huggingface.co/learn",
                                         "docs.python", "realpython", "cookbook",
                                         "cs50", "developers.google"]):
                categories["🎓 Learning Resources"].append(url)
            elif "github.com" in url:
                categories["💻 GitHub Repos"].append(url)
            else:
                categories["🔗 Other Links"].append(url)

        html  = '<div style="background:#f8f7ff;padding:24px 30px;border-top:2px solid #e0e7ff;">'
        html += '<h3 style="color:#1e1b4b;font-size:16px;margin:0 0 16px;font-weight:700;">'
        html += "🔗 All Links from Today's Report</h3>"

        for category, urls in categories.items():
            if not urls:
                continue
            html += f'<div style="margin-bottom:16px;">'
            html += f'<p style="color:#4338ca;font-size:13px;font-weight:600;margin:0 0 8px;">{category}</p>'

            for url in urls[:5]:
                domain     = re.sub(r'https?://(www\.)?', '', url).split('/')[0]
                short_path = '/'.join(url.split('/')[:5])
                if len(short_path) > 60:
                    short_path = short_path[:57] + '...'

                html += (
                    f'<a href="{url}" target="_blank" '
                    f'style="display:block;padding:10px 14px;margin:4px 0;'
                    f'background:white;border:1px solid #e0e7ff;border-radius:8px;'
                    f'color:#4338ca;text-decoration:none;font-size:13px;'
                    f'border-left:3px solid #6366f1;">'
                    f'<span style="font-weight:600;">{domain}</span>'
                    f'<span style="color:#6b7280;font-size:11px;display:block;margin-top:2px;">'
                    f'{short_path}</span></a>'
                )
            html += '</div>'

        html += '</div>'
        return html

    # ─────────────────────────────────────────
    # STEP 3B: CALENDAR
    # ─────────────────────────────────────────
    def _send_calendar(self, report: str):
        """Adds ALL events — learning + jobs + news"""
        if not self.channels.get("calendar", False):
            logger.info("Calendar disabled — skipping")
            return
        try:
            from calendar_helper import add_all_events
            add_all_events(report)
            logger.info("All calendar events added!")
        except Exception as e:
            logger.error(f"Calendar failed: {e}")

    # ─────────────────────────────────────────
    # STEP 3C: WHATSAPP
    # ─────────────────────────────────────────
    def _send_whatsapp(self, report: str):
        """Send WhatsApp alerts for all agents that ran"""
        if not self.channels.get("whatsapp", False):
            logger.info("WhatsApp channel disabled — skipping")
            return
        try:
            from notifiers.whatsapp_notifier import send_all_whatsapp_alerts
            agents_run = list(self.results.keys())
            sent = send_all_whatsapp_alerts(report, agents_run)
            logger.info(f"WhatsApp: {sent} alerts sent!")
        except Exception as e:
            logger.error(f"WhatsApp failed: {e}")

    # ─────────────────────────────────────────
    # MAIN PIPELINE
    # ─────────────────────────────────────────
    def compose_and_send(self):
        """Main method — compose report and deliver to all channels"""
        logger.info("NeuraCompose starting...")

        if not self.results:
            logger.warning("No agent results to compose!")
            return

        # Step 1: Combine all agent results
        combined = self._build_combined_context()
        logger.info(f"Combined {len(self.results)} agent reports")

        # Step 2: Generate unified AI report
        self.report = self._generate_unified_report(combined)
        logger.info("Unified report generated!")

        # Step 2.5: Validate all URLs
        logger.info("Validating URLs...")
        self.report = self._validate_urls(self.report)
        logger.info("URL validation done!")

        # Step 3: Deliver to all channels
        logger.info("Delivering to channels...")
        self._send_email(self.report)
        self._send_calendar(self.report)
        self._send_whatsapp(self.report)

        logger.info("NeuraCompose done! All channels delivered!")
        return self.report