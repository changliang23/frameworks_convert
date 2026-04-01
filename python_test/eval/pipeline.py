"""
统一评测 Pipeline
================
"""

import argparse
import json
import os
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))

@dataclass
class PipelineConfig:
    model: str = "gpt-4o"
    smoke: bool = False
    output_dir: str = "reports"

def run_pipeline(cfg):
    Path(cfg.output_dir).mkdir(parents=True, exist_ok=True)
    print(f"\n=== Running Pipeline (smoke={cfg.smoke}) ===")
    from eval.humaneval_mbpp.runner import run_evaluation, save_report
    res = run_evaluation(model=cfg.model, use_canonical=cfg.smoke)
    save_report(res, f"{cfg.output_dir}/offline_eval.json")
    from eval.static_analysis.analyzer import analyze_files
    targets = [str(ROOT / "test_api_demo.py"), str(ROOT / "test_selenium_demo.py")]
    s_report = analyze_files([t for t in targets if Path(t).exists()])
    with open(f"{cfg.output_dir}/static_analysis.json", "w") as f: json.dump(s_report, f, indent=2)
    print("\n=== Pipeline Finished ===")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--model", default="gpt-4o")
    args = parser.parse_args()
    run_pipeline(PipelineConfig(model=args.model, smoke=args.smoke))
