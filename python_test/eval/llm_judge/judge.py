"""
LLM Judge — 代码质量评测
========================
使用 LLM 作为裁判，从多个维度对 AI 生成代码进行质量打分。

评测维度（每项 0-10 分）:
  - correctness  : 逻辑正确性
  - readability  : 可读性与注释
  - efficiency   : 时间/空间复杂度
  - style        : PEP8 / 代码风格
  - test_coverage: 测试覆盖完整性（针对测试代码）

用法:
  python eval/llm_judge/judge.py \
      --input reports/offline_eval.json \
      --model gpt-4o \
      --output reports/llm_judge.json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import textwrap
from dataclasses import asdict, dataclass, field
from pathlib import Path


# ---------------------------------------------------------------------------
# 评分维度
# ---------------------------------------------------------------------------

DIMENSIONS = [
    "correctness",
    "readability",
    "efficiency",
    "style",
    "test_coverage",
]

JUDGE_SYSTEM_PROMPT = textwrap.dedent("""
    You are an expert code reviewer. Evaluate the given Python code snippet
    across the following dimensions and respond ONLY with valid JSON.

    Dimensions (score 0-10 each):
      - correctness   : logical correctness, handles edge cases
      - readability   : naming, comments, structure clarity
      - efficiency    : time/space complexity appropriateness
      - style         : PEP8 compliance, idiomatic Python
      - test_coverage : breadth and quality of test cases

    Response format (strict JSON, no markdown):
    {
      "correctness": <int 0-10>,
      "readability": <int 0-10>,
      "efficiency":  <int 0-10>,
      "style":       <int 0-10>,
      "test_coverage": <int 0-10>,
      "overall": <float, weighted average>,
      "comments": "<one paragraph summary in Chinese>"
    }
""").strip()


# ---------------------------------------------------------------------------
# 数据结构
# ---------------------------------------------------------------------------

@dataclass
class JudgeScore:
    task_id: str
    code_snippet: str
    correctness: float = 0.0
    readability: float = 0.0
    efficiency: float = 0.0
    style: float = 0.0
    test_coverage: float = 0.0
    overall: float = 0.0
    comments: str = ""
    raw_response: str = ""


# ---------------------------------------------------------------------------
# LLM 调用
# ---------------------------------------------------------------------------

def _call_llm(
    code: str,
    model: str,
    api_base: str,
    api_key: str,
    context: str = "",
) -> str:
    """向 LLM 发送评审请求，返回原始响应文本。"""
    try:
        from openai import OpenAI  # type: ignore
    except ImportError:
        raise ImportError("请先安装 openai: pip install openai")

    client = OpenAI(api_key=api_key, base_url=api_base)
    user_msg = f"{context}\n\n```python\n{code}\n```" if context else f"```python\n{code}\n```"
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.0,
    )
    return resp.choices[0].message.content or ""


def _parse_scores(raw: str, task_id: str, code: str) -> JudgeScore:
    """解析 LLM 返回的 JSON 评分。"""
    score = JudgeScore(task_id=task_id, code_snippet=code, raw_response=raw)
    # 去掉可能的 markdown 代码块包装
    cleaned = re.sub(r"```[a-z]*\n?", "", raw).strip().rstrip("`").strip()
    try:
        data = json.loads(cleaned)
        score.correctness = float(data.get("correctness", 0))
        score.readability = float(data.get("readability", 0))
        score.efficiency = float(data.get("efficiency", 0))
        score.style = float(data.get("style", 0))
        score.test_coverage = float(data.get("test_coverage", 0))
        score.overall = float(data.get("overall", 0))
        score.comments = str(data.get("comments", ""))
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        score.comments = f"[解析失败] {e} | raw: {raw[:200]}"
    return score


# ---------------------------------------------------------------------------
# 评测入口
# ---------------------------------------------------------------------------

def judge_code(
    code: str,
    task_id: str = "unknown",
    context: str = "",
    model: str = "gpt-4o",
    api_base: str = "https://api.openai.com/v1",
    api_key: str = "",
) -> JudgeScore:
    """对单段代码进行 LLM 评审，返回 JudgeScore。"""
    print(f"  judging {task_id} ...", end=" ", flush=True)
    raw = _call_llm(code, model, api_base, api_key, context)
    score = _parse_scores(raw, task_id, code)
    print(f"overall={score.overall:.1f}")
    return score


def judge_from_eval_report(
    report_path: str,
    model: str = "gpt-4o",
    api_base: str = "https://api.openai.com/v1",
    api_key: str = "",
    max_items: int = 50,
) -> list[JudgeScore]:
    """从离线评测报告中读取补全代码，批量进行 LLM 评审。"""
    with open(report_path, encoding="utf-8") as f:
        report = json.load(f)

    details = report.get("details", [])
    scores: list[JudgeScore] = []

    for item in details[:max_items]:
        task_id = item.get("task_id", "unknown")
        completions = item.get("completions", [])
        if not completions:
            continue
        # 取第一条补全评审（代表性样本）
        s = judge_code(
            code=completions[0],
            task_id=task_id,
            model=model,
            api_base=api_base,
            api_key=api_key,
        )
        scores.append(s)

    return scores


def judge_local_files(
    file_paths: list[str],
    model: str = "gpt-4o",
    api_base: str = "https://api.openai.com/v1",
    api_key: str = "",
) -> list[JudgeScore]:
    """对本地 Python 文件列表进行 LLM 评审。"""
    scores: list[JudgeScore] = []
    for fp in file_paths:
        code = Path(fp).read_text(encoding="utf-8")
        s = judge_code(
            code=code,
            task_id=Path(fp).name,
            model=model,
            api_base=api_base,
            api_key=api_key,
        )
        scores.append(s)
    return scores


def save_report(scores: list[JudgeScore], output: str) -> None:
    """保存 LLM Judge 报告。"""
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    avg_overall = sum(s.overall for s in scores) / len(scores) if scores else 0.0
    dim_avgs = {}
    for dim in DIMENSIONS:
        vals = [getattr(s, dim) for s in scores]
        dim_avgs[dim] = sum(vals) / len(vals) if vals else 0.0

    report = {
        "summary": {"avg_overall": avg_overall, "dimension_averages": dim_avgs},
        "details": [asdict(s) for s in scores],
    }
    with open(output, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] LLM Judge 报告已保存至 {output}")
    print(f"平均综合分: {avg_overall:.2f} / 10")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="LLM Judge 代码质量评测")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    # 模式 1：从离线评测报告评审
    p_report = subparsers.add_parser("from-report", help="从离线评测报告中评审代码")
    p_report.add_argument("--input", required=True, help="离线评测 JSON 报告路径")
    p_report.add_argument("--max", type=int, default=50)

    # 模式 2：评审本地文件
    p_files = subparsers.add_parser("from-files", help="评审指定 Python 文件")
    p_files.add_argument("files", nargs="+", help="Python 文件路径")

    for p in [p_report, p_files]:
        p.add_argument("--model", default="gpt-4o")
        p.add_argument("--api-base", default=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1"))
        p.add_argument("--api-key", default=os.getenv("OPENAI_API_KEY", ""))
        p.add_argument("--output", default="reports/llm_judge.json")

    args = parser.parse_args()
    print(f"\n=== LLM Judge | model={args.model} ===")

    if args.mode == "from-report":
        scores = judge_from_eval_report(args.input, args.model, args.api_base, args.api_key, args.max)
    else:
        scores = judge_local_files(args.files, args.model, args.api_base, args.api_key)

    save_report(scores, args.output)


if __name__ == "__main__":
    main()
