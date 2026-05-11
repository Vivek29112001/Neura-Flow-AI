# 🤖 NeuraFlow — Multi-Agent AI Intelligence System

> Your AI-powered personal assistant for learning, jobs, research, and staying updated.

![Version](https://img.shields.io/badge/version-2.0.0-purple)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-brightgreen)

---

## 🧠 What is NeuraFlow?

**NeuraFlow** is a fully automated Multi-Agent AI Intelligence System that runs 24/7 on the cloud, powered by **NeuraCore** — a master orchestrator.

Every day at **7:00 AM IST**, NeuraFlow automatically activates specialized AI agents based on your goals:

- 📰 **NeuraNews** — Scrapes **20+ AI sources** for latest updates
- 💼 **NeuraJobs** — Finds AI/ML job opportunities tailored to you
- 🎓 **NeuraLearn** — Creates personalized learning roadmaps
- 💻 **NeuraCode** — Tracks GitHub trends and project ideas
- 🏢 **NeuraWatch** — Monitors AI companies & market intelligence
- 🚀 **NeuraForge** — Generates innovative project ideas
- 🧠 **NeuraCore** — Master orchestrator that decides which agents run
- 📧 Delivers **beautiful digests** to your Gmail inbox
- 📅 Adds **learning plans** to your Google Calendar
- ☁️ Runs **24/7 on Railway cloud** — even when your laptop is off!

---

## 🎯 Key Features

### 🤖 Multi-Agent Architecture
- **Specialized agents** for different domains (news, jobs, learning, coding, companies, ideas)
- **NeuraCore** — intelligent orchestrator that selects which agents to run
- **Goal-based execution** — runs agents based on YOUR personal goals

### 🗓️ Smart Scheduling
- **Day-based scheduling** — Different agents run on different days
- **Goal-based scheduling** — Choose "get_ai_job", "learn_ai", "ai_research", etc.
- **Automatic execution** — Runs every morning at 7:00 AM IST without user intervention

### 📧 Multi-Channel Delivery
- Gmail inbox notifications with beautifully formatted reports
- Google Calendar integration with actionable learning plans
- SQLite database for persistent tracking and history

### ⚡ Powered by Groq
- Ultra-fast AI processing using **Groq's LLaMA 3.1** model
- Sub-second response times for real-time insights
- Cost-effective cloud deployment

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| AI Brain | Groq API — LLaMA 3.1 |
| Orchestration | NeuraCore (Master Orchestrator) |
| Agents | Modular agent architecture (News, Jobs, Learning, Code, Watch, Forge) |
| Scheduler | APScheduler |
| Email | Gmail SMTP |
| Calendar | Google Calendar API |
| Database | SQLite + SQLAlchemy |
| News Sources | feedparser (RSS) + requests |
| API Server | FastAPI + Uvicorn |
| Logging | Custom Logger with decorators |
| Deployment | Railway.app |
| Language | Python 3.10+ |

---

## 📁 Project Structure

```
neura-flow/
├── app/
│   ├── agents/                    # Specialized AI agents
│   │   ├── news_agent.py         # Fetches AI news from 20+ sources
│   │   ├── job_agent.py          # Finds AI/ML job opportunities
│   │   ├── learning_agent.py     # Creates learning plans
│   │   ├── github_agent.py       # Tracks GitHub & code trends
│   │   ├── company_agent.py      # Monitors companies & market
│   │   └── project_agent.py      # Generates project ideas
│   ├── core/                      # Core utilities
│   │   ├── orchestrator.py       # NeuraCore - Master orchestrator
│   │   ├── logger.py             # Custom logging setup
│   │   └── decorators.py         # Retry, timer, safe_run decorators
│   ├── compose/
│   │   └── composer.py           # Result composition & formatting
│   ├── config/
│   │   └── user_config.json      # User preferences & goals
│   ├── logs/                      # Application logs
│   ├── database.py               # SQLite database setup
│   ├── scheduler.py              # Daily 7AM automation
│   ├── calendar_helper.py        # Google Calendar integration
│   ├── notifier.py               # Gmail email sender
│   └── test_pipeline.py          # Testing & debugging
├── railway.json                  # Railway deployment config
├── requirements.txt              # Python dependencies
├── .env                          # API keys (never commit!)
├── .gitignore
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Vivek29112001/NeuraFlow.git
cd NeuraFlow
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables

```bash
cp .env.example .env
# Fill in your API keys:
# - GROQ_API_KEY (from console.groq.com)
# - GMAIL_ADDRESS & GMAIL_APP_PASSWORD
# - GOOGLE_CREDENTIALS_PATH
# - GOOGLE_CALENDAR_ID
```

### 5. Setup Google Calendar Integration

```bash
# Place google_credentials.json in app/ folder
cd app
python calendar_helper.py
```

### 6. Configure User Goals

Edit `app/config/user_config.json`:

```json
{
  "user_goal": "get_ai_job",
  "preferences": {
    "learning_style": "practical",
    "preferred_companies": ["OpenAI", "DeepMind", "Meta"],
    "interests": ["LLMs", "Agents", "RAG"]
  }
}
```

### 7. Run NeuraFlow

```bash
cd app
python scheduler.py
```

NeuraFlow will run immediately and then automatically at 7:00 AM IST daily!

---

## 🔑 Environment Variables

Create a `.env` file in the root directory:

```bash
# Groq API
GROQ_API_KEY=your_groq_api_key_here

# Gmail
GMAIL_ADDRESS=your_email@gmail.com
GMAIL_APP_PASSWORD=your_app_password_here

# Google
GOOGLE_CREDENTIALS_PATH=app/google_credentials.json
GOOGLE_CALENDAR_ID=primary

# Optional
LOG_LEVEL=INFO
DEBUG=False
```

### Getting API Keys

| Variable | How to Get |
|---|---|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) → Create API key |
| `GMAIL_APP_PASSWORD` | [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) |
| `GOOGLE_CREDENTIALS_PATH` | [console.cloud.google.com](https://console.cloud.google.com) → Create OAuth 2.0 credentials |
| `GOOGLE_CALENDAR_ID` | Google Calendar settings → Calendar ID (use `primary` for default)

---

## 🤖 NeuraFlow Agents

### 📰 NeuraNews Agent
Fetches AI/ML news from **20+ premium sources**:
- **Research Papers**: arXiv, Papers With Code, IEEE Spectrum
- **AI Companies**: Hugging Face, OpenAI, Google AI, Anthropic, Meta AI, Microsoft AI, DeepMind, LangChain
- **AI News**: VentureBeat, MIT Tech Review, The Verge, Wired, TechCrunch, Towards Data Science
- **Community**: Reddit r/MachineLearning, r/LocalLLaMA, r/artificial

### 💼 NeuraJobs Agent
Tracks job opportunities in AI/ML from:
- LinkedIn jobs (filtered by skills)
- Hacker News jobs
- Indeed AI/ML roles
- Personalized recommendations based on your profile

### 🎓 NeuraLearn Agent
Creates personalized learning plans:
- Suggests daily learning topics
- Recommends courses & resources
- Tracks your learning progress
- Builds custom roadmaps based on goals

### 💻 NeuraCode Agent
Monitors GitHub & coding trends:
- Trending repositories
- Latest open-source projects
- Popular coding frameworks
- Developer insights & statistics

### 🏢 NeuraWatch Agent
Company & market intelligence:
- AI company news & funding rounds
- Startup developments
- Market trends & competitive analysis
- Industry reports

### 🚀 NeuraForge Agent
Generates innovative project ideas:
- AI project suggestions based on trends
- Starter projects for learning
- Production ideas based on your skills
- Hackathon ideas

---

## 🧠 NeuraCore — Master Orchestrator

NeuraCore intelligently decides which agents to run based on:

### 📅 Day-Based Schedule
```
Monday    → News, Jobs, Learning, Code, Watch, Forge
Tuesday   → News, Jobs
Wednesday → Learning, Code
Thursday  → News, Watch
Friday    → Jobs, Forge
Saturday  → Learning, News
Sunday    → News, Jobs, Learning
```

### 🎯 Goal-Based Agent Selection
```
get_ai_job       → Jobs, Learning, Code, Watch
learn_ai         → Learning, News, Forge
ai_research      → News, Learning, Code
build_startup    → Forge, News, Watch
stay_updated     → News, Watch, Code
freelancing      → Jobs, Forge, Code
```

The core reads your `user_config.json` and intelligently selects the best agents for your needs!

---

## 📧 Report Format

Each morning you receive multi-agent reports:

```
🤖 NEURAFLOW DAILY DIGEST
━━━━━━━━━━━━━━━━━━━━━━━━

📰 TOP 5 AI HEADLINES
   Latest breakthroughs and announcements

💼 JOB OPPORTUNITIES
   3-5 AI/ML roles matching your profile

🎓 TODAY'S LEARNING FOCUS
   Personalized topic with learning path

💻 TRENDING REPOSITORIES
   Hot open-source projects

🏢 COMPANY UPDATES
   News from AI leaders

🚀 PROJECT IDEAS
   Build ideas for your portfolio

🔗 MUST-READ LINKS
   Top real links from all agents
```

---

## ☁️ Deploy on Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app)

1. Fork this repository
2. Connect to Railway via GitHub
3. Add environment variables in Railway dashboard
4. Deploy!

---

## 🗺️ Roadmap

### Version 1.0 (Legacy) ✅
- [x] Single news agent
- [x] Basic email delivery
- [x] Google Calendar integration
- [x] Daily 7AM scheduler
- [x] Railway deployment

### Version 2.0 (Current) ✅
- [x] **NeuraCore** — Master Orchestrator
- [x] **NeuraNews** — News aggregation from 20+ sources
- [x] **NeuraJobs** — Job market tracking
- [x] **NeuraLearn** — Personalized learning plans
- [x] **NeuraCode** — GitHub trends & open source
- [x] **NeuraWatch** — Company intelligence
- [x] **NeuraForge** — Project idea generation
- [x] Goal-based agent orchestration
- [x] Day-based scheduling
- [x] user_config.json — Dynamic preferences
- [x] Core utilities (logger, decorators, retry logic)
- [x] Async/safe execution patterns
- [x] SQLite database for tracking

### Version 3.0 (Coming Soon) 🚧
- [ ] REST API endpoints for all agents
- [ ] Web dashboard (React/Next.js)
- [ ] Real-time notifications
- [ ] Advanced filtering & preferences
- [ ] Multi-user support with authentication
- [ ] Database migrations & backup
- [ ] Performance optimization & caching
- [ ] Advanced error handling & recovery

### Version 4.0 (Future) 🔮
- [ ] Mobile app (Android + iOS)
- [ ] WhatsApp/Telegram integration
- [ ] Slack workspace integration
- [ ] Premium subscription plans
- [ ] Community sharing & recommendations
- [ ] Collaborative features
- [ ] Advanced analytics & insights

---

## 🤝 Contributing

We welcome contributions! Whether it's:
- 🐛 Bug reports
- ✨ New features
- 📝 Documentation improvements
- 🧪 Tests & test cases
- 🎨 UI/UX improvements

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/YourFeatureName`)
3. Make your changes with clear commits
4. Write or update tests
5. Run tests locally: `python -m pytest`
6. Push to your fork (`git push origin feature/YourFeatureName`)
7. Create a Pull Request with a detailed description

### Code Guidelines

- Follow PEP 8 style guide
- Add docstrings to all functions/classes
- Include type hints where possible
- Write meaningful commit messages
- Add tests for new features
- Update README if adding new features

---

## 📄 License

Distributed under the MIT License. See `LICENSE` file for more information.

---

## 👤 Author

**Vivek Sharma**
- 🔗 GitHub: [@Vivek29112001](https://github.com/Vivek29112001/)
- 💼 LinkedIn: [viveksharma2911](https://www.linkedin.com/in/vivek2911/)
- 🌐 Portfolio: [viveksharma.dev](https://workwithvivek.netlify.app/)

---

## 💬 Support & Feedback

- 📧 Email: vivek15292001@gmail.com
- 🤝 Join our Discord community (coming soon)

---

## ⭐ Show Your Support

If NeuraFlow helped you stay updated with AI, please give it a ⭐ on GitHub!

---

*Built with ❤️ by Vivek Sharma*

*Powered by Groq LLaMA 3.1 | Deployed on Railway* 
