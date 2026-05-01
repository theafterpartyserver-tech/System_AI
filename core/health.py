# core/health.py

import os
import json


def compute_health_score():
    log_path = os.path.join("logs", "events.log")

    exec_times = []
    failures = 0

    if not os.path.exists(log_path):
        return {"health_score": 100, "avg_latency": 0, "failures": 0}

    with open(log_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)

            if event.get("phase") == "executor":
                exec_times.append(event.get("duration_ms", 0))

            if "reject" in event.get("phase", ""):
                failures += 1

        except (json.JSONDecodeError, KeyError):
            continue

    avg_latency = sum(exec_times) / len(exec_times) if exec_times else 0

    score = 100

    if avg_latency > 500:
        score -= 20

    if failures > 3:
        score -= 30

    return {
        "health_score": score,
        "avg_latency": avg_latency,
        "failures": failures,
    }


def get_routing_bias():
    health = compute_health_score()

    # Later you can wire this into state.json too, but for now just compute.
    if health["health_score"] < 50:
        return "conservative"
    elif health["avg_latency"] > 300:
        return "fast_mode"
    else:
        return "balanced"
