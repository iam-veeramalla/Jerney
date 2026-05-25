"""
healer.py
Executes the AI's recommended fix on the live Kubernetes cluster.
Each action type corresponds to a specific Kubernetes API call.
"""
from __future__ import annotations
import logging
from kubernetes import client, config as k8s_config
from healer.watcher import PodEvent

log = logging.getLogger("kubehealer.healer")


def _load():
    try:
        k8s_config.load_incluster_config()
    except Exception:
        k8s_config.load_kube_config()


def execute(event: PodEvent, plan: dict) -> list[str]:
    """
    Loops through every action the AI recommended and runs it.
    Returns a list of result messages (shown on dashboard).
    """
    _load()
    results = []

    for action in plan.get("actions", []):
        atype  = action.get("type", "no_action")
        params = action.get("params", {})
        reason = action.get("reason", "")

        log.info("EXECUTING action=%s on pod=%s", atype, event.name)

        try:
            if atype in ("restart_pod", "delete_pod"):
                result = _restart_pod(event)

            elif atype == "scale_deployment":
                result = _scale(event, params)

            elif atype == "patch_resources":
                result = _patch_resources(event, params)

            elif atype == "patch_env":
                result = _patch_env(event, params)

            elif atype == "describe_event":
                # AI says: just alert, don't touch anything
                result = f"🔔 ALERT [{event.component.upper()}] {event.name}: {reason}"

            else:
                # no_action: AI says pod is self-healing, just watch
                result = f"👁 WATCHING {event.name} — {reason}"

        except Exception as exc:
            result = f"❌ ERROR running {atype} on {event.name}: {exc}"

        log.info(result)
        results.append(result)

    return results


# ── The actual fix functions ──────────────────────────────────────────────────

def _restart_pod(event: PodEvent) -> str:
    """
    Deletes the broken pod.
    Kubernetes automatically creates a fresh one from the Deployment template.
    This fixes: CrashLoopBackOff, stuck states, temporary app crashes.
    """
    client.CoreV1Api().delete_namespaced_pod(
        name=event.name, namespace=event.namespace)
    return f"✅ RESTARTED {event.name} — Deployment will create a fresh pod"


def _scale(event: PodEvent, params: dict) -> str:
    """
    Changes how many replicas (copies) of a deployment are running.
    Example: scale jerney-backend from 1 to 2 if one is unhealthy.
    """
    replicas = int(params.get("replicas", 1))
    client.AppsV1Api().patch_namespaced_deployment_scale(
        name=event.deployment,
        namespace=event.namespace,
        body={"spec": {"replicas": replicas}})
    return f"✅ SCALED {event.deployment} → {replicas} replicas"


def _patch_resources(event: PodEvent, params: dict) -> str:
    """
    Updates memory and CPU limits on a deployment's container.
    Used when OOMKilled happens — the container ran out of memory.
    For example: jerney-frontend gets more than the default 128Mi.
    """
    mem = params.get("memory_limit", "256Mi")
    cpu = params.get("cpu_limit", "500m")
    patch = {
        "spec": {
            "template": {
                "spec": {
                    "containers": [{
                        "name": event.container_name,
                        "resources": {
                            "limits":   {"memory": mem, "cpu": cpu},
                            "requests": {"memory": mem, "cpu": cpu},
                        },
                    }]
                }
            }
        }
    }
    client.AppsV1Api().patch_namespaced_deployment(
        name=event.deployment, namespace=event.namespace, body=patch)
    return f"✅ PATCHED {event.deployment}: memory={mem} cpu={cpu}"


def _patch_env(event: PodEvent, params: dict) -> str:
    """
    Adds or updates environment variables on a deployment.
    Used if the AI detects a wrong config value causing crashes.
    Example: wrong DB_HOST pointing to wrong service name.
    """
    patch = {
        "spec": {
            "template": {
                "spec": {
                    "containers": [{
                        "name": event.container_name,
                        "env": [{"name": k, "value": v} for k, v in params.items()],
                    }]
                }
            }
        }
    }
    client.AppsV1Api().patch_namespaced_deployment(
        name=event.deployment, namespace=event.namespace, body=patch)
    return f"✅ PATCHED env vars {list(params.keys())} on {event.deployment}"
