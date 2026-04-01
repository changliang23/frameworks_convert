"""
静态分析模块 — Lint + 复杂度
============================
对 Python 代码文件进行静态分析，整合:
  - flake8  : PEP8 风格 + 语法检查
  - pylint  : 深度代码 quality 分析（可选）
  - radon   : 圈复杂度（Cyclomatic Complexity）+ 可维护性指数
  - bandit  : 安全漏洞扫描

用法:
  python eval/static_analysis/analyzer.py \\
      --target test_api_demo.py test_selenium_demo.py \\
      --output reports/static_analysis.json
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class FlakeIssue:
    file: str
    line: int
    col: int
    code: str
    message: str


@dataclass
class ComplexityResult:
    file: str
    function: str
    complexity: int
    rank: str
    lineno: int = 0


@dataclass
class BanditIssue:
    file: str
    line: int
    severity: str
    confidence: str
    test_id: str
    issue_text: str


@dataclass
class FileAnalysis:
    file: str
    flake8_issues: list = field(default_factory=list)
    flake8_issue_count: int = 0
    complexity_results: list = field(default_factory=list)
    max_complexity: int = 0
    avg_complexity: float = 0.0
    maintainability_index: float = 0.0
    bandit_issues: list = field(default_factory=list)
    bandit_high_severity: int = 0
    pylint_score: float = -1.0


def _run(cmd: list) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True)  # noqa: S603


def run_flake8(file_path: str) -> list[FlakeIssue]:
    cmd = [
        sys.executable, "-m", "flake8",
        "--format=%(path)s:%(row)d:%(col)d: %(code)s %(text)s",
        "--max-line-length=120",
        file_path,
    ]
    result = _run(cmd)
    issues = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line: continue
        try:
            parts = line.split(":", 4)
            if len(parts) < 5: continue
            f, row, col, rest = parts[0], int(parts[1]), int(parts[2]), parts[4].strip()
            code_msg = rest.split(" ", 1)
            code = code_msg[0]
            msg = code_msg[1] if len(code_msg) > 1 else ""
            issues.append(FlakeIssue(file=f, line=row, col=col, code=code, message=msg))
        except (ValueError, IndexError): continue
    return issues


def run_radon_cc(file_path: str) -> list[ComplexityResult]:
    cmd = [sys.executable, "-m", "radon", "cc", "-j", file_path]
    result = _run(cmd)
    if not result.stdout.strip(): return []
    try: data = json.loads(result.stdout)
    except json.JSONDecodeError: return []
    results = []
    for fpath, blocks in data.items():
        for block in blocks:
            results.append(ComplexityResult(
                file=fpath, function=block.get("name", ""),
                complexity=block.get("complexity", 0),
                rank=block.get("rank", "?"), lineno=block.get("lineno", 0),
            ))
    return results


def run_radon_mi(file_path: str) -> float:
    cmd = [sys.executable, "-m", "radon", "mi", "-j", file_path]
    result = _run(cmd)
    if not result.stdout.strip(): return -1.0
    try:
        data = json.loads(result.stdout)
        for _, val in data.items():
            if isinstance(val, (int, float)): return float(val)
            if isinstance(val, dict): return float(val.get("mi", -1))
    except (json.JSONDecodeError, KeyError, TypeError): pass
    return -1.0


def run_bandit(file_path: str) -> list[BanditIssue]:
    cmd = [sys.executable, "-m", "bandit", "-f", "json", "-q", file_path]
    result = _run(cmd)
    if not result.stdout.strip(): return []
    try: data = json.loads(result.stdout)
    except json.JSONDecodeError: return []
    issues = []
    for r in data.get("results", []):
        issues.append(BanditIssue(
            file=r.get("filename", file_path), line=r.get("line_number", 0),
            severity=r.get("issue_severity", ""), confidence=r.get("issue_confidence", ""),
            test_id=r.get("test_id", ""), issue_text=r.get("issue_text", ""),
        ))
    return issues

def run_pylint(file_path: str) -> float:
    cmd = [sys.executable, "-m", "pylint", "--output-format=json", file_path]
    result = _run(cmd)
    for line in reversed(result.stdout.splitlines()):
        if "Your code has been rated" in line:
            try:
                score_str = line.split("at ")[1].split("/")[0]
                return float(score_str)
            except (IndexError, ValueError): pass
    return -1.0

def analyze_file(file_path: str, run_pylint_check: bool = False) -> FileAnalysis:
    print(f"  analyzing {Path(file_path).name} ...", flush=True)
    analysis = FileAnalysis(file=file_path)
    analysis.flake8_issues = [asdict(i) for i in run_flake8(file_path)]
    analysis.flake8_issue_count = len(analysis.flake8_issues)
    cc_results = run_radon_cc(file_path)
    analysis.complexity_results = [asdict(r) for r in cc_results]
    if cc_results:
        complexities = [r.complexity for r in cc_results]
        analysis.max_complexity = max(complexities)
        analysis.avg_complexity = sum(complexities) / len(complexities)
    analysis.maintainability_index = run_radon_mi(file_path)
    bandit_issues = run_bandit(file_path)
    analysis.bandit_issues = [asdict(i) for i in bandit_issues]
    analysis.bandit_high_severity = sum(1 for i in bandit_issues if i.severity.upper() == "HIGH")
    if run_pylint_check: analysis.pylint_score = run_pylint(file_path)
    return analysis

def analyze_files(file_paths: list[str], run_pylint_check: bool = False) -> dict:
    results = [asdict(analyze_file(fp, run_pylint_check)) for fp in file_paths if Path(fp).exists()]
    total_flake = sum(r["flake8_issue_count"] for r in results)
    total_bandit = sum(len(r["bandit_issues"]) for r in results)
    avg_cc = sum(r["avg_complexity"] for r in results) / len(results) if results else 0.0
    avg_mi = sum(r["maintainability_index"] for r in results if r["maintainability_index"] >= 0) / max(1, sum(1 for r in results if r["maintainability_index"] >= 0))
    return {
        "summary": {
            "total_files": len(results), "total_flake8_issues": total_flake,
            "total_bandit_issues": total_bandit, "avg_cyclomatic_complexity": round(avg_cc, 2),
            "avg_maintainability_index": round(avg_mi, 2),
        }, "files": results,
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", nargs="+", required=True)
    parser.add_argument("--output", default="reports/static_analysis.json")
    parser.add_argument("--pylint", action="store_true")
    args = parser.parse_args()
    report = analyze_files(args.target, run_pylint_check=args.pylint)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f: json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] 报告已保存至 {args.output}")

if __name__ == "__main__": main()
