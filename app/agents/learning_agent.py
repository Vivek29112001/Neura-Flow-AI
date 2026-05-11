import logging
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("NeuraFlow")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# 100% Real verified URLs — never hallucinated
VERIFIED_RESOURCES = [
    ("fast.ai Practical Deep Learning",        "https://course.fast.ai"),
    ("Google ML Crash Course",                 "https://developers.google.com/machine-learning/crash-course"),
    ("Kaggle Learn",                           "https://www.kaggle.com/learn"),
    ("Hugging Face NLP Course",                "https://huggingface.co/learn/nlp-course"),
    ("LangChain Docs",                         "https://python.langchain.com/docs/get_started/introduction"),
    ("OpenAI Cookbook",                        "https://cookbook.openai.com"),
    ("Real Python",                            "https://realpython.com"),
    ("Python Official Tutorial",               "https://docs.python.org/3/tutorial"),
    ("Andrej Karpathy Neural Nets Zero2Hero",  "https://www.youtube.com/playlist?list=PLAqhIrjkxbuWI23v9cThsA9GvCAUhRvKZ"),
    ("StatQuest with Josh Starmer",            "https://www.youtube.com/@statquest"),
    ("Kaggle Competitions",                    "https://www.kaggle.com/competitions"),
    ("Papers With Code",                       "https://paperswithcode.com"),
    ("DeepLearning.AI Courses",                "https://www.deeplearning.ai/courses"),
    ("CS50 AI Harvard",                        "https://cs50.harvard.edu/ai"),
    ("PyTorch Tutorials",                      "https://pytorch.org/tutorials"),
    ("TensorFlow Tutorials",                   "https://www.tensorflow.org/tutorials"),
    ("Scikit-learn User Guide",                "https://scikit-learn.org/stable/user_guide.html"),
    ("arXiv CS.AI Latest",                     "https://arxiv.org/list/cs.AI/recent"),
    ("Towards Data Science",                   "https://towardsdatascience.com"),
    ("Machine Learning Mastery",               "https://machinelearningmastery.com"),
]

def run_learning_agent(config: dict = {}) -> str:
    logger.info("NeuraLearn generating learning path...")

    user    = config.get("user", {})
    topics  = config.get("topics", {})
    goals   = user.get("goals", ["learn_ai"])
    level   = user.get("level", "Intermediate")
    primary = topics.get("primary", ["AI", "ML"])

    # Step 1: Pick best resources FIRST (no hallucination possible)
    resource_names = [name for name, url in VERIFIED_RESOURCES]
    pick_prompt = (
        f"From this numbered list, pick the TOP 3 most relevant for:\n"
        f"Level: {level}, Topics: {', '.join(primary)}, Goals: {', '.join(goals)}\n\n"
        + "\n".join([f"{i+1}. {name}" for i, name in enumerate(resource_names)])
        + "\n\nReply with ONLY 3 numbers separated by commas. Example: 1,5,12"
    )

    pick_response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": pick_prompt}],
        max_tokens=15
    )

    # Parse numbers safely
    picked_text = pick_response.choices[0].message.content.strip()
    picked_nums = []
    for part in picked_text.replace(" ", "").split(","):
        try:
            n = int(part.strip()) - 1
            if 0 <= n < len(VERIFIED_RESOURCES):
                picked_nums.append(n)
        except:
            pass

    if not picked_nums:
        picked_nums = [0, 2, 12]  # Fallback: fast.ai, Kaggle, DeepLearning.AI

    # Step 2: Build resource section with REAL URLs
    resources_text = "TOP RESOURCES FOR YOU:\n"
    resources_with_urls = []
    for n in picked_nums[:3]:
        name, url = VERIFIED_RESOURCES[n]
        resources_text    += f"- {name}: {url}\n"
        resources_with_urls.append((name, url))

    # Step 3: Generate learning plan (NO URLs in prompt — we add them ourselves)
    plan_prompt = (
        f"Create a 7-day learning plan (no URLs needed):\n"
        f"Level: {level}\n"
        f"Goals: {', '.join(goals)}\n"
        f"Topics: {', '.join(primary)}\n\n"
        f"Format EXACTLY like this:\n\n"
        f"YOUR LEARNING MISSION TODAY:\n"
        f"[One sentence about what to focus on today]\n\n"
        f"THIS WEEK'S PLAN:\n"
        f"Monday: [task]\n"
        f"Tuesday: [task]\n"
        f"Wednesday: [task]\n"
        f"Thursday: [task]\n"
        f"Friday: [task]\n"
        f"Saturday: [task]\n"
        f"Sunday: [task]\n\n"
        f"PRACTICE TASK:\n"
        f"[One hands-on coding exercise]\n\n"
        f"Do NOT include any URLs."
    )

    plan_response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": plan_prompt}],
        max_tokens=800
    )
    plan = plan_response.choices[0].message.content

    # Step 4: Combine plan + real URLs
    final = plan + "\n\n" + resources_text
    logger.info(f"NeuraLearn done! Resources: {[n for n, u in resources_with_urls]}")
    return final