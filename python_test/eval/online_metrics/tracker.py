"""
在线指标追踪模块 — 修复率 / 采纳率
====================================
追踪 AI 代码建议在真实开发场景中的在线表现指标。
"""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

@dataclass
class SuggestionEvent:
    session_id: str
    task_id: str
    timestamp: float = field(default_factory=time.time)
    suggested: bool = True
    accepted: bool = False
    retained: bool = False
    fixed: bool = False
    fix_time_seconds: float = -1.0
    model: str = ""
    language: str = "python"

def append_event(event: SuggestionEvent, events_file: str = "reports/online_events.jsonl"):
    Path(events_file).parent.mkdir(parents=True, exist_ok=True)
    with open(events_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(event), ensure_ascii=False) + "\n")

def load_events(events_file: str) -> list[dict]:
    path = Path(events_file)
    if not path.exists(): return []
    events = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip(): events.append(json.loads(line))
    return events

def _safe_rate(n, d): return round(n / d, 4) if d > 0 else 0.0

def generate_report(events_file: str) -> dict:
    events = load_events(events_file)
    if not events: return {"metrics": {}}
    n = len(events)
    acc = sum(1 for e in events if e.get("accepted"))
    fix = sum(1 for e in events if e.get("fixed"))
    ret = sum(1 for e in events if e.get("retained"))
    return {
        "metrics": {
            "total_suggestions": n, "accept_rate": _safe_rate(acc, n),
            "fix_rate": _safe_rate(fix, n), "retention_rate": _safe_rate(ret, acc),
        }
    }

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="cmd", required=True)
    p_log = subparsers.add_parser("log")
    p_log.add_argument("--session-id", required=True)
    p_log.add_argument("--task-id", required=True)
    p_log.add_argument("--accepted", action="store_true")
    p_log.add_argument("--fixed", action="store_true")
    p_rep = subparsers.add_parser("report")
    p_rep.add_argument("--input", default="reports/online_events.jsonl")
    p_rep.add_argument("--output", default="reports/online_metrics.json")
    args = parser.parse_args()
    if args.cmd == "log":
        append_event(SuggestionEvent(session_id=args.session_id, task_id=args.task_id, accepted=args.accepted, fixed=args.fixed))
    elif args.cmd == "report":
        report = generate_report(args.input)
        with open(args.output, "w") as f: json.dump(report, f, indent=2)

if __name__ == "__main__": main()
