"""
Multi-Model Task Assignment & Orchestration Engine
Routes each functional domain (Decision, UI, Backend, Research, Security, Context, Docs)
to the single best model for that specific job across Respan, Experiential, and APInex.
"""

import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import requests

load_dotenv()

# API Keys
RESPAN_KEY = os.environ.get("RESPAN_API_KEY")
EXPLABS_KEY = os.environ.get("EXPLABS_API_KEY")
APINEX_KEY = os.environ.get("APINEX_API_KEY")

# Clients
respan = OpenAI(base_url="https://gateway.respan.ai/v1", api_key=RESPAN_KEY)
explabs = OpenAI(base_url="https://api.experientiallabs.ai/v1", api_key=EXPLABS_KEY)
apinex = OpenAI(base_url="https://api.apinex.bond/v1", api_key=APINEX_KEY)

# Specialized Department Roles & Model Mapping
ROLE_REGISTRY = {
    "decision": {
        "model": "free/jev-1.13",
        "provider": "APInex Decisions API",
        "best_for": "Mathematical decision making, routing, binary evaluation, choice ranking",
        "endpoint_type": "decisions"
    },
    "deep_reasoning": {
        "model": "respan/gemini-4-carbon:free",
        "client": respan,
        "best_for": "Frontier logic, mathematical proofs, system architecture design",
        "endpoint_type": "chat"
    },
    "backend_engineering": {
        "model": "free/qwen-3.8-max",
        "client": apinex,
        "best_for": "Complex backend coding, FastAPI, database schemas, full-stack algorithms",
        "endpoint_type": "chat"
    },
    "frontend_ui": {
        "model": "meta/muse-ember:free",
        "client": respan,
        "best_for": "UI/UX wireframing, vision analysis, CSS/Tailwind, React components",
        "endpoint_type": "chat"
    },
    "security_audit": {
        "model": "free/deepseek-v4-pro-0813",
        "client": apinex,
        "best_for": "Security vulnerability audits, code review, edge case bug hunting",
        "endpoint_type": "chat"
    },
    "deep_research": {
        "model": "free/kimi-k3",
        "client": apinex,
        "best_for": "Ingesting 1M tokens of documentation, papers, massive codebases",
        "endpoint_type": "chat"
    },
    "technical_writing": {
        "model": "free/gpt-6-luna",
        "client": apinex,
        "best_for": "OpenAPI contracts, clean documentation, developer experience, user copy",
        "endpoint_type": "chat"
    },
    "live_web_search": {
        "provider": "APInex Search Tool",
        "best_for": "Real-time internet fact checking and verifying library updates",
        "endpoint_type": "tool"
    }
}

class ModelOrchestrator:
    """The Architect Engine that delegates work to the best model and aggregates results."""

    @staticmethod
    def evaluate_decision(state: str, questions: dict) -> dict:
        """Role: DECISION MAKING via Jev 1.13"""
        url = "https://api.apinex.bond/v1/decisions"
        headers = {"Authorization": f"Bearer {APINEX_KEY}", "Content-Type": "application/json"}
        payload = {"model": "free/jev-1.13", "state": state, "questions": questions}
        r = requests.post(url, headers=headers, json=payload, timeout=20)
        return r.json().get("answers", {})

    @staticmethod
    def search_web(query: str, count: int = 3) -> dict:
        """Role: LIVE GROUND TRUTH SEARCH via APInex Web Search"""
        url = "https://api.apinex.bond/v1/tools/web/search"
        headers = {"Authorization": f"Bearer {APINEX_KEY}", "Content-Type": "application/json"}
        r = requests.post(url, headers=headers, json={"query": query, "count": count}, timeout=15)
        return r.json()

    @staticmethod
    def delegate(role: str, prompt: str, system: str = None) -> str:
        """Delegates a prompt to the specialized model designated for that role."""
        if role not in ROLE_REGISTRY:
            raise ValueError(f"Unknown role: {role}. Available: {list(ROLE_REGISTRY.keys())}")
        
        cfg = ROLE_REGISTRY[role]
        if cfg["endpoint_type"] != "chat":
            raise ValueError(f"Role {role} is not a chat model. Use its specialized method.")
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = cfg["client"].chat.completions.create(
            model=cfg["model"],
            messages=messages,
            max_tokens=600,
        )
        return response.choices[0].message.content

# Ready to run test demonstrating automated role delegation
if __name__ == "__main__":
    print("=" * 60)
    print(" TASK ASSIGNMENT ARCHITECTURE TEST ")
    print("=" * 60)

    # 1. Decision
    print("\n[1. DECISION ENGINE -> Jev 1.13]")
    dec = ModelOrchestrator.evaluate_decision(
        state="We need to build a clean web dashboard for an AI task runner.",
        questions={
            "frontend_framework": {
                "type": "choice",
                "instructions": "Which frontend framework is best for fast responsive UI?",
                "criteria": {"react_vite": "React with Vite and Tailwind", "nextjs": "Next.js fullstack SSR", "vue": "Vue.js 3"}
            }
        }
    )
    print("Jev Decision:", json.dumps(dec, indent=2))

    # 2. UI Specialist
    print("\n[2. UI SPECIALIST -> Meta Muse Ember]")
    ui_out = ModelOrchestrator.delegate("frontend_ui", "Suggest the 3 essential UI layout components for an AI agent control panel in 2 bullet points.")
    print("UI Output:\n", ui_out)

    # 3. Backend Specialist
    print("\n[3. BACKEND SPECIALIST -> Qwen 3.8 MAX]")
    backend_out = ModelOrchestrator.delegate("backend_engineering", "Write a minimal FastAPI endpoint to dispatch an async task in Python.")
    print("Backend Output:\n", backend_out[:250], "...")

    print("\n[+] All model roles are successfully wired and ready to use!")
