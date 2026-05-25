from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from kubernetes import client, config as k8s_config
from healer.config import NAMESPACE, UNHEALTHY_REASONS, MAX_RESTART_COUNT


@dataclass
class PodEvent:
    """
    One sick pod. Holds everything we know about it —
    name, which component it is, why it failed, and its logs.
    This gets sent to the AI for analysis.
    """
    name: str
    namespace: str
    deployment: str      # jerney-db | jerney-backend | jerney-frontend
    component: str       # database | backend | frontend
    reason: str          # e.g. CrashLoopBackOff
    message: str         # K8s description of the problem
    restart_count: int
    container_name: str
    node: Optional[str]
    logs: str = ""       # last 100 lines of container output
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def summary(self) -> str:
        """Formats all pod info into one string to send to Gemini."""
        return (
            f"App: Jerney Blog Platform | Namespace: {self.namespace}\n"
            f"Component: {self.component} | Deployment: {self.deployment}\n"
            f"Pod: {self.name} | Container: {self.container_name} | Node: {self.node}\n"
            f"Failure: {self.reason} | Restarts: {self.restart_count}\n"
            f"K8s Message: {self.message}\n\n"
            f"Logs (last 100 lines):\n{self.logs[-3000:]}"
        )


def _load_k8s():
    """
    Try to load Kubernetes credentials.
    Inside cluster → uses the mounted ServiceAccount token automatically.
    On your laptop → uses your ~/.kube/config file.
    """
    try:
        k8s_config.load_incluster_config()
    except Exception:
        k8s_config.load_kube_config()


def _fetch_logs(v1, pod, ns, container):
    """Get the last 100 lines of a container's output."""
    try:
        return v1.read_namespaced_pod_log(
            name=pod, namespace=ns,
            container=container, tail_lines=100, timestamps=True)
    except Exception as e:
        return f"[logs unavailable: {e}]"


def _deployment_of(pod_name: str):
    """
    Figures out which Jerney deployment a pod belongs to.
    Pod names look like: jerney-backend-7d4f9b-xkz2p
    We check the prefix to know it's the backend deployment.
    """
    for dep, comp in {
        "jerney-db":       "database",
        "jerney-backend":  "backend",
        "jerney-frontend": "frontend",
    }.items():
        if pod_name.startswith(dep):
            return dep, comp
    return pod_name.rsplit("-", 2)[0], "unknown"


def get_unhealthy_pods() -> List[PodEvent]:
    """
    Main function: scans all pods in jerney namespace.
    Returns only the ones that are sick.
    Called every POLL_INTERVAL seconds from main.py.
    """
    _load_k8s()
    v1 = client.CoreV1Api()
    events = []

    for pod in v1.list_namespaced_pod(namespace=NAMESPACE).items:
        name = pod.metadata.name
        ns   = pod.metadata.namespace
        node = pod.spec.node_name
        dep, comp = _deployment_of(name)

        # Case 1: Pod has no container statuses yet (very early failure or stuck Pending)
        if not pod.status or not pod.status.container_statuses:
            phase  = (pod.status.phase if pod.status else "Unknown") or "Unknown"
            reason = (pod.status.reason or phase) if pod.status else phase
            msg    = (pod.status.message or "") if pod.status else ""
            if phase in ("Pending", "Failed") or reason in UNHEALTHY_REASONS:
                events.append(PodEvent(
                    name=name, namespace=ns, deployment=dep, component=comp,
                    reason=reason, message=msg, restart_count=0,
                    container_name="unknown", node=node))
            continue

        # Case 2: Pod has containers — check each container's state
        for cs in pod.status.container_statuses:
            cname    = cs.name
            restarts = cs.restart_count or 0
            reason = message = ""

            if cs.state.waiting:      # container is stuck waiting to start
                reason  = cs.state.waiting.reason  or ""
                message = cs.state.waiting.message or ""
            elif cs.state.terminated: # container ran and exited (possibly crashed)
                reason  = cs.state.terminated.reason  or ""
                message = cs.state.terminated.message or ""

            # Flag as sick if: known bad reason OR too many restarts
            if reason in UNHEALTHY_REASONS or restarts >= MAX_RESTART_COUNT:
                events.append(PodEvent(
                    name=name, namespace=ns, deployment=dep, component=comp,
                    reason=reason or "HighRestartCount", message=message,
                    restart_count=restarts, container_name=cname,
                    node=node, logs=_fetch_logs(v1, name, ns, cname)))
    return events
