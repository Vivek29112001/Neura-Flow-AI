import requests
import logging
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("NeuraFlow")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def run_github_agent(config: dict = {}) -> str:
    logger.info("NeuraCode fetching GitHub trends...")

    repos = []
    headers = {
        "User-Agent": "NeuraFlow/1.0",
        "Accept": "application/vnd.github.v3+json"
    }

    # GitHub Search API — real repos with real URLs
    queries = [
        "artificial intelligence",
        "machine learning",
        "large language model",
        "langchain"
    ]

    for query in queries:
        try:
            url = (
                f"https://api.github.com/search/repositories"
                f"?q={query.replace(' ', '+')}"
                f"&sort=stars&order=desc&per_page=3"
            )
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                data = res.json()
                for repo in data.get("items", [])[:3]:
                    repos.append({
                        "name":        repo["full_name"],
                        "url":         repo["html_url"],
                        "description": repo.get("description", "")[:200],
                        "stars":       repo["stargazers_count"],
                        "language":    repo.get("language", "Unknown")
                    })
                logger.info(f"Fetched {len(data.get('items', [])[:3])} repos for '{query}'")
            else:
                logger.warning(f"GitHub API returned {res.status_code} for '{query}'")
        except Exception as e:
            logger.warning(f"GitHub fetch failed for '{query}': {e}")

    if not repos:
        return "No GitHub trends found today."

    # Build real repo list for Groq
    repo_text = ""
    for i, r in enumerate(repos[:12], 1):
        repo_text += f"{i}. {r['name']}\n"
        repo_text += f"   URL: {r['url']}\n"
        repo_text += f"   Stars: {r['stars']:,}\n"
        repo_text += f"   Language: {r['language']}\n"
        repo_text += f"   Description: {r['description']}\n\n"

    prompt = (
        "Analyze these real GitHub repositories for AI/ML developers:\n\n"
        + repo_text +
        "\nGenerate a GitHub Trends Report with:\n"
        "1. TOP 3 REPOS TO STAR TODAY — with exact URLs from above\n"
        "2. WHY THEY MATTER — practical explanation\n"
        "3. HOW TO USE — quick start guide\n\n"
        "STRICT RULES:\n"
        "- Only use URLs explicitly provided above\n"
        "- Never generate or guess URLs\n"
        "- Format each repo as: Name\n  URL: [exact url]\n"
    )

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800
    )
    return response.choices[0].message.content