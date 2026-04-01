"""
离线评测模块 — HumanEval + MBPP
================================
支持通过 OpenAI 兼容接口调用模型，对 HumanEval / MBPP 标准数据集进行离线批量评测。

流程:
  1. 加载本地 JSONL 格式的数据集（HumanEval / MBPP）
  2. 向目标模型发送 prompt，获取代码补全结果（支持多次采样用于 pass@k）
  3. 在沙箱环境中执行代码 + 测试用例
  4. 汇总 pass rate，输出 JSON 报告

用法:
  python eval/humaneval_mbpp/runner.py \\
      --dataset humaneval \\
      --model gpt-4o \\
      --n 10 \\
      --output reports/humaneval_result.json
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import sys
import textwrap
import time
import traceback
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# 内置轻量演示数据集（无需网络）
# ---------------------------------------------------------------------------

HUMANEVAL_SAMPLES: list[dict] = [
    {
        "task_id": "HumanEval/0",
        "prompt": "from typing import List\n\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\n    \"\"\"Check if any two numbers in list are closer than threshold.\n    >>> has_close_elements([1.0, 2.0, 3.0], 0.5)\n    False\n    >>> has_close_elements([1.0, 2.8, 3.0], 0.3)\n    True\n    \"\"\"\n",
        "canonical_solution": "    for idx, elem in enumerate(numbers):\n        for idx2, elem2 in enumerate(numbers):\n            if idx != idx2:\n                distance = abs(elem - elem2)\n                if distance < threshold:\n                    return True\n    return False\n",
        "test": "def check(candidate):\n    assert candidate([1.0, 2.0, 3.9, 4.0, 5.0, 2.2], 0.3) == True\n    assert candidate([1.0, 2.0, 3.9, 4.0, 5.0, 2.2], 0.05) == False\n    assert candidate([1.0, 2.0, 5.9, 4.0, 5.0], 0.95) == True\n",
        "entry_point": "has_close_elements",
    },
    {
        "task_id": "HumanEval/1",
        "prompt": "from typing import List\n\ndef separate_paren_groups(paren_string: str) -> List[str]:\n    \"\"\"Separate balanced paren groups from input string.\n    >>> separate_paren_groups('( ) (( )) (( )( ))')\n    ['()', '(())', '(()())']\n    \"\"\"\n",
        "canonical_solution": "    result = []\n    current_string = []\n    current_depth = 0\n    for c in paren_string:\n        if c == '(':\n            current_depth += 1\n            current_string.append(c)\n        elif c == ')':\n            current_depth -= 1\n            current_string.append(c)\n            if current_depth == 0:\n                result.append(''.join(current_string))\n                current_string = []\n    return result\n",
        "test": "def check(candidate):\n    assert candidate('(()()) ((())) () ((())()())') == ['(()())', '((()))', '()', '((())()())']\n",
        "entry_point": "separate_paren_groups",
    },
]

MBPP_SAMPLES: list[dict] = [
    {
        "task_id": "MBPP/1",
        "text": "Write a function to find the minimum cost path to reach (m, n) from (0, 0) for the given cost matrix cost[][] and a position (m, n) in cost[][].",
        "code": "R = 3\nC = 3\ndef min_cost(cost, m, n):\n    tc = [[0 for x in range(C)] for x in range(R)]\n    tc[0][0] = cost[0][0]\n    for i in range(1, m+1):\n        tc[i][0] = tc[i-1][0] + cost[i][0]\n    for j in range(1, n+1):\n        tc[0][j] = tc[0][j-1] + cost[0][j]\n    for i in range(1, m+1):\n        for j in range(1, n+1):\n            tc[i][j] = min(tc[i-1][j-1], tc[i-1][j], tc[i][j-1]) + cost[i][j]\n    return tc[m][n]\n",
        "test_list": [
            "assert min_cost([[1, 2, 3], [4, 8, 2], [1, 5, 3]], 2, 2) == 8",
            "assert min_cost([[2, 3, 4], [5, 9, 3], [2, 6, 4]], 2, 2) == 12",
        ],
    },
]


# ---------------------------------------------------------------------------
# 数据加载
# ---------------------------------------------------------------------------

def load_dataset(dataset: str, data_path: str | None = None) -> list[dict]:
    """加载 HumanEval 或 MBPP 数据集。
    若提供 data_path，则从本地 JSONL 文件读取；否则使用内置演示样本。
    """
    if data_path and Path(data_path).exists():
        samples = []
        with open(data_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    samples.append(json.loads(line))
        return samples

    print(f"[INFO] 未找到本地数据集文件，使用内置演示样本 ({dataset})")
    return HUMANEVAL_SAMPLES if dataset == "humaneval" else MBPP_SAMPLES


# ---------------------------------------------------------------------------
# 沙箱执行
# ---------------------------------------------------------------------------

def _exec_code(code: str, timeout: int = 10) -> tuple[bool, str]:
    """在受限命名空间中执行代码，返回 (passed, error_message)。"""
    stdout_buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(stdout_buf):
            exec(compile(code, "<eval>", "exec"), {"__builtins__": __builtins__})  # noqa: S102
        return True, ""
    except Exception:  # noqa: BLE001
        return False, traceback.format_exc()


def evaluate_humaneval(sample: dict, completions: list[str]) -> list[bool]:
    """对 HumanEval 格式样本逐条执行，返回每条是否通过。"""
    results = []
    for completion in completions:
        full_code = (
            sample["prompt"]
            + completion
            + "\n"
            + sample["test"]
            + f"\ncheck({sample['entry_point']})\n"
        )
        passed, _ = _exec_code(full_code)
        results.append(passed)
    return results


def evaluate_mbpp(sample: dict, completions: list[str]) -> list[bool]:
    """对 MBPP 格式样本逐条执行，返回每条是否通过。"""
    results = []
    for completion in completions:
        test_block = "\n".join(sample["test_list"])
        full_code = completion + "\n" + test_block + "\n"
        passed, _ = _exec_code(full_code)
        results.append(passed)
    return results


# ---------------------------------------------------------------------------
# 模型调用（OpenAI 兼容）
# ---------------------------------------------------------------------------

def call_model(
    prompt: str,
    model: str,
    n: int,
    api_base: str,
    api_key: str,
    temperature: float = 0.8,
) -> list[str]:
    """调用 OpenAI 兼容接口，返回 n 条代码补全。"""
    try:
        from openai import OpenAI  # type: ignore
    except ImportError:
        raise ImportError("请先安装 openai: pip install openai")

    client = OpenAI(api_key=api_key, base_url=api_base)
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        n=n,
        temperature=temperature,
    )
    return [c.message.content or "" for c in resp.choices]


# ---------------------------------------------------------------------------
# 主评测逻辑
# ---------------------------------------------------------------------------

@dataclass
class EvalResult:
    task_id: str
    dataset: str
    n_samples: int
    n_passed: int
    pass_rate: float
    completions: list[str] = field(default_factory=list)


def run_evaluation(
    dataset: str = "humaneval",
    model: str = "gpt-4o",
    n: int = 1,
    api_base: str = "https://api.openai.com/v1",
    api_key: str = "",
    data_path: str | None = None,
    use_canonical: bool = False,
) -> list[EvalResult]:
    """执行完整评测流程，返回每个任务的 EvalResult。

    Args:
        use_canonical: 若为 True，直接使用标准答案执行（用于验证沙箱和测试用例）。
    """
    samples = load_dataset(dataset, data_path)
    results: list[EvalResult] = []

    for sample in samples:
        task_id = sample.get("task_id", "unknown")
        print(f"  evaluating {task_id} ...", end=" ", flush=True)

        if use_canonical:
            # 验证模式：用标准答案
            if dataset == "humaneval":
                completions = [sample["canonical_solution"]] * n
            else:
                completions = [sample["code"]] * n
        else:
            prompt = sample.get("prompt", sample.get("text", ""))
            completions = call_model(prompt, model, n, api_base, api_key)

        if dataset == "humaneval":
            passed_list = evaluate_humaneval(sample, completions)
        else:
            passed_list = evaluate_mbpp(sample, completions)

        n_passed = sum(passed_list)
        pass_rate = n_passed / len(passed_list) if passed_list else 0.0
        print(f"{n_passed}/{len(passed_list)} passed")

        results.append(
            EvalResult(
                task_id=task_id,
                dataset=dataset,
                n_samples=len(completions),
                n_passed=n_passed,
                pass_rate=pass_rate,
                completions=completions,
            )
        )

    return results


def save_report(results: list[EvalResult], output: str) -> None:
    """将评测结果保存为 JSON 报告。"""
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    data = {
        "summary": {
            "total": len(results),
            "avg_pass_rate": sum(r.pass_rate for r in results) / len(results) if results else 0,
        },
        "details": [asdict(r) for r in results],
    }
    with open(output, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] 报告已保存至 {output}")


# ---------------------------------------------------------------------------
# CLI 入口
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="HumanEval / MBPP 离线评测")
    parser.add_argument("--dataset", choices=["humaneval", "mbpp"], default="humaneval")
    parser.add_argument("--model", default="gpt-4o")
    parser.add_argument("--n", type=int, default=1, help="每题采样次数")
    parser.add_argument("--api-base", default=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1"))
    parser.add_argument("--api-key", default=os.getenv("OPENAI_API_KEY", ""))
    parser.add_argument("--data-path", default=None, help="本地 JSONL 数据集路径")
    parser.add_argument("--output", default="reports/offline_eval.json")
    parser.add_argument("--use-canonical", action="store_true", help="用标准答案验证（冒烟测试）")
    args = parser.parse_args()

    print(f"\n=== 离线评测: {args.dataset.upper()} | model={args.model} | n={args.n} ===")
    results = run_evaluation(
        dataset=args.dataset,
        model=args.model,
        n=args.n,
        api_base=args.api_base,
        api_key=args.api_key,
        data_path=args.data_path,
        use_canonical=args.use_canonical,
    )
    save_report(results, args.output)

    avg = sum(r.pass_rate for r in results) / len(results) if results else 0
    print(f"平均通过率: {avg:.2%} ({len(results)} tasks)")


if __name__ == "__main__":
    main()
