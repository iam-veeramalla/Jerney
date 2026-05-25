"""
analyzer.py
Sends failing pod details to Google Gemini (FREE).
Get your key at: https://aistudio.google.com/app/apikey
"""
from __future__ import annotations
import json
import google.generativeai as genai
from healer.config import GEMINI_API_KEY
from healer.watcher import PodEvent

# Connect to Gemini with your API key
genai.configure(api_key=GEMINI_API_KEY)

# Create the AI model with context about Jerney
# The system_instruction is like telling the AI its job before any conversation
_model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",   # free model, fast, very capable
    system_instruction="""You are KubeHealer, an expert Kubernetes SRE AI for the Jerney Blog Platform.

Jerney runs in namespace `jerney` with 3 deployments:
- jerney-db       → PostgreSQL 16, port 5432, EBS PVC, secret: jerney-db-secret
- jerney-backend  → Node.js/Express, port 5000, health: /api/health
- jerney-frontend → React/Nginx, port 8080

Common failures to know about:
- jerney-backend CrashLoopBackOff → usually DB not ready or app crash
- jerney-db Pending               → EBS PVC not bound yet (WaitForFirstConsumer)
- OOMKilled on frontend           → nginx needs more than 128Mi memory
- ImagePullBackOff                → wrong image tag on ghcr.io
- HighRestartCount on backend     → DB connection pool exhausted

You MUST respond with ONLY valid JSON, absolutely no markdown, no extra text:
{
  "root_cause": "<one clear sentence explaining what went wrong>",
  "severity": "low|medium|high|critical",
  "component_affected": "database|backend|frontend|unknown",
  "actions": [
    {
      "type": "restart_pod|scale_deployment|patch_resources|patch_env|describe_event|no_action",
      "reason": "<why this action fixes the problem>",
      "params": {}
    }
  ],
  "prevention": "<one tip to stop this happening again>"
}

Action params examples:
- patch_resources  → {"memory_limit": "256Mi", "cpu_limit": "500m"}
- scale_deployment → {"replicas": 2}
- patch_env        → {"DB_HOST": "jerney-db"}"""
)


def analyze(event: PodEvent) -> dict:
    """
    Send pod failure info to Gemini, get back a heal plan as a Python dict.
    """
    try:
        response = _model.generate_content(
            f"Analyze this Jerney pod failure:\n\n{event.summary()}"
        )
        raw = response.text.strip()

        # Gemini sometimes wraps JSON in ```json ``` — strip that out
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        return json.loads(raw)

    except Exception as e:
        # If AI fails for any reason, return a safe fallback
        return {
            "root_cause": f"AI analysis failed: {e}",
            "severity": "medium",
            "component_affected": event.component,
            "actions": [{"type": "describe_event", "reason": str(e), "params": {}}],
            "prevention": "Check your GEMINI_API_KEY and internet connectivity.",
        }
