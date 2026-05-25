import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY    = os.getenv("GEMINI_API_KEY", "")
NAMESPACE         = os.getenv("NAMESPACE", "jerney")
AUTO_HEAL         = os.getenv("AUTO_HEAL", "true").lower() == "true"
POLL_INTERVAL     = int(os.getenv("POLL_INTERVAL", "30"))
MAX_RESTART_COUNT = int(os.getenv("MAX_RESTART_COUNT", "5"))
API_PORT          = int(os.getenv("API_PORT", "8080"))

# These are the exact error states Kubernetes reports
# when a pod/container is in trouble
UNHEALTHY_REASONS = {
    "CrashLoopBackOff",       # container keeps crashing and restarting
    "OOMKilled",              # container used too much memory, OS killed it
    "Error",                  # generic error exit
    "ImagePullBackOff",       # can't download the Docker image
    "ErrImagePull",           # same as above, different stage
    "Pending",                # pod stuck, not scheduled to any node yet
    "Evicted",                # pod kicked off a node (low disk/memory on node)
    "CreateContainerConfigError",  # bad config, env var or secret missing
    "RunContainerError",      # container failed to start
    "ContainerCannotRun",     # similar to above
}
