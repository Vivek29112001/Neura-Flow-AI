import json
import sys
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

from core.logger import setup_logger
from core.decorators import log_execution, retry, timer, safe_run

load_dotenv()
logger = setup_logger()


class NeuraCore:
    """
    NeuraCore — Master Orchestrator of NeuraFlow
    Reads user goals → decides which agents to run → collects results
    """

    CONFIG_PATH = "config/user_config.json"

    # Day of week → which agents run
    DAY_SCHEDULE = {
        "Monday":    ["NeuraNews", "NeuraJobs", "NeuraLearn",
                      "NeuraCode", "NeuraWatch", "NeuraForge"],
        "Tuesday":   ["NeuraNews", "NeuraJobs"],
        "Wednesday": ["NeuraLearn", "NeuraCode"],
        "Thursday":  ["NeuraNews", "NeuraWatch"],
        "Friday":    ["NeuraJobs", "NeuraForge"],
        "Saturday":  ["NeuraLearn", "NeuraNews"],
        "Sunday":    ["NeuraNews", "NeuraJobs", "NeuraLearn"],
    }

    # User goal → required agents
    GOAL_AGENTS = {
        "get_ai_job":    ["NeuraJobs", "NeuraLearn", "NeuraCode", "NeuraWatch"],
        "learn_ai":      ["NeuraLearn", "NeuraNews", "NeuraForge"],
        "ai_research":   ["NeuraNews", "NeuraLearn", "NeuraCode"],
        "build_startup": ["NeuraForge", "NeuraNews", "NeuraWatch"],
        "stay_updated":  ["NeuraNews", "NeuraWatch", "NeuraCode"],
        "freelancing":   ["NeuraJobs", "NeuraForge", "NeuraCode"],
    }

    def __init__(self):
        self.config = self._load_config()
        self.today = datetime.now().strftime("%A")
        self.results: Dict[str, Optional[str]] = {}
        logger.info(f"🧠 NeuraCore initialized | Day: {self.today} | User: {self.config['user']['name']}")

    def _load_config(self) -> dict:
        """Load and validate user_config.json"""
        try:
            with open(self.CONFIG_PATH, "r") as f:
                config = json.load(f)
            logger.info("✅ Config loaded successfully")
            return config
        except FileNotFoundError:
            logger.error(f"❌ Config not found: {self.CONFIG_PATH}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in config: {e}")
            raise

    def _decide_agents(self) -> List[str]:
        """
        Smart agent selection:
        Priority 1 — User goals
        Priority 2 — Day of week schedule
        Priority 3 — Enabled in config
        """
        enabled = [
            name for name, active
            in self.config.get("agents", {}).items()
            if active
        ]

        # Collect agents from user goals
        goal_agents = set()
        for goal in self.config.get("user", {}).get("goals", []):
            for key, agents in self.GOAL_AGENTS.items():
                if key in goal.lower():
                    goal_agents.update(agents)

        # Day schedule agents
        day_agents = set(self.DAY_SCHEDULE.get(self.today, ["NeuraNews"]))

        # Final selection
        if goal_agents:
            final = goal_agents & set(enabled)
        else:
            final = day_agents & set(enabled)

        # NeuraNews always runs (minimum)
        final.add("NeuraNews")

        logger.info(f"📋 Agents to run today: {sorted(final)}")
        return sorted(final)

    @safe_run
    def _run_agent(self, agent_name: str) -> Optional[str]:
        """Safely runs one agent"""
        agent_map = {
            "NeuraNews":  self._run_news,
            "NeuraJobs":  self._run_jobs,
            "NeuraLearn": self._run_learn,
            "NeuraCode":  self._run_code,
            "NeuraWatch": self._run_watch,
            "NeuraForge": self._run_forge,
        }
        runner = agent_map.get(agent_name)
        if not runner:
            logger.warning(f"⚠ Unknown agent: {agent_name}")
            return None
        return runner()

    @log_execution("NeuraNews")
    @retry(max_attempts=3, delay=2.0)
    def _run_news(self) -> str:
        from agents.news_agent import run_news_agent
        return run_news_agent(self.config)

    @log_execution("NeuraJobs")
    @retry(max_attempts=3, delay=2.0)
    def _run_jobs(self) -> str:
        from agents.job_agent import run_job_agent
        return run_job_agent(self.config)

    @log_execution("NeuraLearn")
    @retry(max_attempts=2, delay=1.0)
    def _run_learn(self) -> str:
        from agents.learning_agent import run_learning_agent
        return run_learning_agent(self.config)

    @log_execution("NeuraCode")
    @retry(max_attempts=2, delay=1.0)
    def _run_code(self) -> str:
        from agents.github_agent import run_github_agent
        return run_github_agent(self.config)

    @log_execution("NeuraWatch")
    @retry(max_attempts=2, delay=1.0)
    def _run_watch(self) -> str:
        from agents.company_agent import run_company_agent
        return run_company_agent(self.config)

    @log_execution("NeuraForge")
    @retry(max_attempts=2, delay=1.0)
    def _run_forge(self) -> str:
        from agents.project_agent import run_project_agent
        return run_project_agent(self.config)

    @timer
    def run(self) -> Dict[str, Optional[str]]:
        """Main pipeline — call this to run everything"""
        logger.info("=" * 55)
        logger.info("🚀 NeuraFlow pipeline starting...")
        logger.info(f"👤 User   : {self.config['user']['name']}")
        logger.info(f"🎯 Goals  : {self.config['user']['goals']}")
        logger.info(f"📅 Day    : {self.today}")
        logger.info("=" * 55)

        agents_to_run = self._decide_agents()

        for agent_name in agents_to_run:
            logger.info(f"\n── Running {agent_name} ──")
            result = self._run_agent(agent_name)
            if result:
                self.results[agent_name] = result

        logger.info(f"\n✅ {len(self.results)}/{len(agents_to_run)} agents completed")

        # Send to NeuraCompose
        self._compose_and_deliver()

        return self.results

    def _compose_and_deliver(self):
        """Passes all results to NeuraCompose for final report"""
        from compose.composer import NeuraCompose
        composer = NeuraCompose(
            results=self.results,
            config=self.config,
            day=self.today
        )
        composer.compose_and_send()


if __name__ == "__main__":
    core = NeuraCore()
    core.run()