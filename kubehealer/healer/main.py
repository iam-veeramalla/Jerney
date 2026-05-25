"""
main.py
Entry point for KubeHealer.
Two things happen when you run this:
  1. A background thread runs healing_loop() every 30s
  2. FastAPI web server starts so you can see events at http://localhost:9090
"""
from __future__ import annotations
import logging
import threading
import time
from collections import deque
from datetime import datetime

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from healer import config
from healer.watcher  import get_unhealthy_pods
from healer.analyzer import analyze
from healer.healer   import execute

# Set up logging — you'll see these in kubectl logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
)
log = logging.getLogger("kubehealer.main")

# Store last 300 healing events in memory (shown on dashboard)
HISTORY: deque[dict] = deque(maxlen=300)

app = FastAPI(title="KubeHealer – Jerney")


@app.get("/healthz")
def healthz():
    """Kubernetes uses this to check if KubeHealer itself is alive."""
    return {"status": "ok", "namespace": config.NAMESPACE}


@app.get("/events")
def events():
    """Returns all healing events as JSON — useful for scripting."""
    return list(HISTORY)


@app.get("/", response_class=HTMLResponse)
def dashboard():
    """The live web dashboard — auto-refreshes every 15 seconds."""
    SEV_COLOR = {
        "low":      "#4ade80",   # green
        "medium":   "#facc15",   # yellow
        "high":     "#fb923c",   # orange
        "critical": "#f87171",   # red
    }
    ICON = {"database": "🗄", "backend": "⚙️", "frontend": "🌐"}

    rows = "".join(
        f"<tr>"
        f"<td class=m>{e['time']}</td>"
        f"<td>{ICON.get(e.get('component',''), '❓')} {e.get('component','?')}</td>"
        f"<td class=m>{e['pod']}</td>"
        f"<td><span class=tag>{e['reason']}</span></td>"
        f"<td style='color:{SEV_COLOR.get(e.get('severity','low'),'#fff')};font-weight:700'>"
        f"{e.get('severity','?').upper()}</td>"
        f"<td>{e.get('root_cause','')}</td>"
        f"<td class=act>{'<br>'.join(e.get('actions',[]))}</td>"
        f"</tr>"
        for e in reversed(HISTORY)
    ) or '<tr><td colspan=7 class=empty>✅ All Jerney pods are healthy right now</td></tr>'

    return f"""<!DOCTYPE html>
<html><head>
<meta charset=UTF-8>
<meta http-equiv=refresh content=15>
<title>KubeHealer – Jerney</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: #060b14; color: #cbd5e1; font-family: system-ui; }}
  header {{ background: linear-gradient(135deg, #0ea5e9, #6366f1); padding: 1.2rem 2rem; }}
  header h1 {{ color: #fff; font-size: 1.5rem; }}
  header p  {{ color: rgba(255,255,255,.7); font-size: .85rem; margin-top: .2rem; }}
  .meta {{ display: flex; gap: 2rem; padding: .8rem 2rem;
           background: #0d1826; font-size: .8rem; color: #64748b; }}
  .meta b {{ color: #38bdf8; }}
  main {{ padding: 1.5rem 2rem; }}
  table {{ width: 100%; border-collapse: collapse; font-size: .82rem; }}
  th {{ background: #0d1826; color: #7dd3fc; padding: .6rem .8rem;
        text-align: left; text-transform: uppercase;
        font-size: .72rem; letter-spacing: .05em; }}
  td {{ padding: .5rem .8rem; border-bottom: 1px solid #0d1826; vertical-align: top; }}
  tr:hover td {{ background: #0d1826; }}
  .m   {{ font-family: monospace; color: #94a3b8; font-size: .78rem; }}
  .tag {{ background: #1e293b; border-radius: 3px; padding: .1rem .4rem;
          font-size: .74rem; font-family: monospace; color: #f472b6; }}
  .act {{ font-family: monospace; font-size: .74rem; color: #a3e635; }}
  .empty {{ text-align: center; padding: 3rem; color: #334155; }}
</style>
</head><body>
<header>
  <h1>⚡ KubeHealer</h1>
  <p>Gemini AI self-healing · Jerney Blog Platform · watching namespace: <b>{config.NAMESPACE}</b></p>
</header>
<div class=meta>
  <span>Auto-Heal: <b>{"ON ✓" if config.AUTO_HEAL else "DRY-RUN (safe mode)"}</b></span>
  <span>Poll interval: <b>every {config.POLL_INTERVAL}s</b></span>
  <span>Events recorded: <b>{len(HISTORY)}</b></span>
  <span>Page auto-refresh: <b>15s</b></span>
</div>
<main>
  <table>
    <thead>
      <tr>
        <th>Time (UTC)</th>
        <th>Component</th>
        <th>Pod</th>
        <th>K8s Reason</th>
        <th>Severity</th>
        <th>AI Root Cause</th>
        <th>Actions Taken</th>
      </tr>
    </thead>
    <tbody>{rows}</tbody>
  </table>
</main>
</body></html>"""


def healing_loop():
    """
    Runs forever in a background thread.
    Every POLL_INTERVAL seconds:
      1. Get list of unhealthy pods
      2. For each sick pod → ask Gemini AI what to do
      3. Execute the fix (or just log it in dry-run mode)
      4. Save to HISTORY so dashboard can show it
    """
    log.info("🚀 KubeHealer started | namespace=%s | auto_heal=%s | poll=%ss",
             config.NAMESPACE, config.AUTO_HEAL, config.POLL_INTERVAL)

    while True:
        try:
            unhealthy_pods = get_unhealthy_pods()

            if not unhealthy_pods:
                log.info("✅ All Jerney pods are healthy")
            else:
                for ev in unhealthy_pods:
                    log.warning("🔴 UNHEALTHY: pod=%s component=%s reason=%s restarts=%d",
                                ev.name, ev.component, ev.reason, ev.restart_count)

                    # Ask Gemini AI for analysis and action plan
                    plan = analyze(ev)

                    # Execute or dry-run based on AUTO_HEAL setting
                    if config.AUTO_HEAL:
                        actions = execute(ev, plan)
                    else:
                        # DRY-RUN: just show what WOULD happen
                        actions = [
                            f"[DRY-RUN] would do '{a['type']}': {a.get('reason', '')}"
                            for a in plan.get("actions", [])
                        ]

                    # Save to history for dashboard
                    HISTORY.append({
                        "time":       datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                        "pod":        ev.name,
                        "namespace":  ev.namespace,
                        "deployment": ev.deployment,
                        "component":  ev.component,
                        "reason":     ev.reason,
                        "severity":   plan.get("severity", "?"),
                        "root_cause": plan.get("root_cause", ""),
                        "prevention": plan.get("prevention", ""),
                        "actions":    actions,
                    })

        except Exception as e:
            log.error("Healing loop error: %s", e, exc_info=True)

        time.sleep(config.POLL_INTERVAL)


if __name__ == "__main__":
    # Start healing loop in background thread (daemon=True means it stops when main stops)
    healing_thread = threading.Thread(target=healing_loop, daemon=True)
    healing_thread.start()

    # Start web dashboard (this blocks — runs until you Ctrl+C)
    uvicorn.run(app, host="0.0.0.0", port=config.API_PORT, log_level="warning")
