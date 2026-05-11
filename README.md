<<<<<<< HEAD
# 🤖 NeuraFlow — Personal AI Learning Intelligence System

> Stay updated with AI every day. Automatically.

![Version](https://img.shields.io/badge/version-1.0.0-purple)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-brightgreen)

---

## 🧠 What is NeuraFlow?

**NeuraFlow** is a fully automated Personal AI Learning Intelligence System that runs 24/7 on the cloud.

Every morning at **7:00 AM IST**, NeuraFlow automatically:

- 📰 Scrapes **20+ sources** — arXiv, IEEE Spectrum, Hugging Face, OpenAI, LangChain, Reddit, VentureBeat & more
- 🤖 Uses **Groq's LLaMA 3.1** to generate a personalized daily AI learning report
- 📧 Delivers a **beautiful digest** to your Gmail inbox
- 📅 Adds a **7-day learning plan** to your Google Calendar
- ☁️ Runs **24/7 on Railway cloud** — even when your laptop is off!

---

## ❌ The Problem

AI and technology is evolving faster than ever.
New models, new tools, new research papers — every single day.
Most of us struggle to keep up and end up falling behind without even realizing it.

## ✅ The Solution

NeuraFlow is an AI Agent that stays updated with the latest technology — and keeps YOU updated too!

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| AI Brain | Groq API — LLaMA 3.1 |
| Scheduler | APScheduler |
| Email | Gmail SMTP |
| Calendar | Google Calendar API |
| Database | SQLite + SQLAlchemy |
| News Sources | feedparser (RSS) |
| Deployment | Railway.app |
| Language | Python 3.10+ |

---

## 📁 Project Structure

```
ai-learning-agent/
├── app/
│   ├── database.py          # SQLite database setup
│   ├── fetcher.py           # RSS feed scraper (20+ sources)
│   ├── summarizer.py        # Groq AI report generator
│   ├── notifier.py          # Gmail email sender
│   ├── calendar_helper.py   # Google Calendar integration
│   └── scheduler.py         # Daily 7AM automation
├── .env                     # API keys (never commit!)
├── .gitignore
├── railway.json             # Railway deployment config
├── requirements.txt         # Python dependencies
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
# Fill in your API keys in .env
```

### 5. Setup Google Calendar

```bash
# Place your google_credentials.json inside app/ folder
# Then run to authenticate:
cd app
python calendar_helper.py
```

### 6. Run NeuraFlow

```bash
cd app
python scheduler.py
```

---

## 🔑 Environment Variables

See [`.env.example`](.env.example) for all required variables.

| Variable | Description | How to Get |
|---|---|---|
| `GROQ_API_KEY` | Groq AI API key | [console.groq.com](https://console.groq.com) |
| `GMAIL_ADDRESS` | Your Gmail address | Your Google account |
| `GMAIL_APP_PASSWORD` | Gmail App Password | [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) |
| `GOOGLE_CREDENTIALS_PATH` | Path to Google credentials JSON | Google Cloud Console |
| `GOOGLE_CALENDAR_ID` | Calendar ID (use `primary`) | Google Calendar settings |

---

## 📰 News Sources

NeuraFlow fetches from **20+ sources** daily:

**Research Papers**
- arXiv AI, ML, CV, NLP
- Papers With Code
- IEEE Spectrum AI

**AI Companies**
- Hugging Face Blog
- OpenAI Blog
- Google AI Blog
- Anthropic Blog
- Meta AI Blog
- Microsoft AI Blog
- DeepMind Blog
- LangChain Blog

**AI News**
- VentureBeat AI
- MIT Technology Review
- The Verge AI
- Wired AI
- TechCrunch AI
- Towards Data Science

**Community**
- Reddit r/MachineLearning
- Reddit r/LocalLLaMA
- Reddit r/artificial

---

## 📧 Daily Report Format

Each morning you receive:

```
📰 TOP 5 HIGHLIGHTS
   Most important AI updates of the day

🧠 WHAT THIS MEANS FOR YOU
   Practical impact on your learning journey

📚 TODAY'S LEARNING FOCUS
   One topic to study today with resources

📅 THIS WEEK'S LEARNING PLAN
   Day 1 → Day 7 learning roadmap

🔗 MUST-READ LINKS
   Top 3 real links to check today
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

### Version 1.0 (Current) ✅
- [x] News fetching from 20+ sources
- [x] AI-powered daily report generation
- [x] Gmail email delivery
- [x] Google Calendar integration
- [x] Daily 7AM scheduler
- [x] Railway cloud deployment

### Version 2.0 (Coming Soon) 🚧
- [ ] NeuraCore — Master Orchestrator
- [ ] NeuraJobs — Job Market Agent
- [ ] NeuraLearn — Personalized Learning Agent
- [ ] NeuraCode — GitHub Trends Agent
- [ ] NeuraWatch — Company Intelligence Agent
- [ ] NeuraForge — Project Ideas Agent
- [ ] user_config.json — Dynamic preferences
- [ ] Web dashboard

### Version 3.0 (Future) 🔮
- [ ] Mobile app (Android + iOS)
- [ ] WhatsApp notifications
- [ ] Subscription plans
- [ ] Multi-user support

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 👤 Author

**Vivek Sharma**
- GitHub: [@Vivek29112001](https://github.com/Vivek29112001)
- LinkedIn: [viveksharma2911](https://linkedin.com/in/viveksharma2911)

---

## ⭐ Show Your Support

If this project helped you, please give it a ⭐ on GitHub!

---

*Built with ❤️ by Vivek Sharma | Powered by Groq LLaMA & NeuraFlow*
=======
>>>>>>> 8c2bdbc8a64d3752144cba59e9c9d82ff82fe6d2
"# Neura-Flow-AI" 
