"""
pass@k 计算模块
===============
实现 Chen et al. (2021) 论文中定义的无偏 pass@k 估计量：

    pass@k = 1 - C(n-c, k) / C(n, k)

其中:
  n = 每题总采样次数
  c = 通过的次数
  k = 评估的 k 值（如 1, 10, 100）

同时提供 pytest 插件风格的 collector，可在 pytest 运行后自动统计 pass@k。
"""

from __future__ import annotations

import json
import math
import os
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence


# ---------------------------------------------------------------------------
# 核心数学公式
# ---------------------------------------------------------------------------

def _comb(n: int, k: int) -> float:
    """组合数 C(n, k)，支持大数（用 math.comb）。"""
    if k < 0 or k > n:
        return 0.0
    return float(math.comb(n, k))


def pass_at_k(n: int, c: int, k: int) -> float:
    """无偏 pass@k 估计。

    Args:
        n: 总采样次数
        c: 通过的样本数
        k: top-k 的 k 值

    Returns:
        pass@k 概率值，范围 [0, 1]
    """
    if n < k:
        raise ValueError(f"n={n} 必须 >= k={k}")
    if c == 0:
        return 0.0
    if n - c < k:
        return 1.0
    return 1.0 - _comb(n - c, k) / _comb(n, k)


def pass_at_k_batch(
    results: list[dict],
    k_values: Sequence[int] = (1, 10, 100),
) -> dict[str, float]:
    """批量计算多个 k 值的 pass@k。

    Args:
        results: 每个元素包含 {"n": int, "c": int} 的列表
        k_values: 要计算的 k 值列表

    Returns:
        {"pass@1": 0.xx, "pass@10": 0.xx, ...}
    """
    metrics: dict[str, float] = {}
    for k in k_values:
        valid = [r for r in results if r["n"] >= k]
        if not valid:
            metrics[f"pass@{k}"] = 0.0
            continue
        scores = [pass_at_k(r["n"], r["c"], k) for r in valid]
        metrics[f"pass@{k}"] = sum(scores) / len(scores)
    return metrics


# ---------------------------------------------------------------------------
# pytest 多次采样执行器
# ---------------------------------------------------------------------------

@dataclass
class SamplingResult:
    test_file: str
    n_runs: int
    n_passed: int
    pass_rate: float
    pass_at_1: float
    pass_at_k_values: dict[str, float]


def run_test_n_times(
    test_path: str,
    n: int = 10,
    k_values: Sequence[int] = (1, 5, 10),
    extra_args: list[str] | None = None,
) -> SamplingResult:
    """对单个测试文件执行 n 次，统计 pass@k。

    每次运行视为一次独立采样（适用于随机性测试或多次补全的场景）。

    Args:
        test_path: pytest 测试文件路径
        n:         采样次数
        k_values:  计算哪些 k
        extra_args: 传递给 pytest 的额外参数

    Returns:
        SamplingResult
    """
    passed_count = 0
    extra_args = extra_args or []

    for i in range(n):
        cmd = [
            sys.executable, "-m", "pytest",
            test_path, "-q", "--tb=no", "--no-header",
        ] + extra_args
        result = subprocess.run(cmd, capture_output=True, text=True)  # noqa: S603
        if result.returncode == 0:
            passed_count += 1

    pass_rate = passed_count / n
    raw = [{"n": n, "c": passed_count}]
    metrics = pass_at_k_batch(raw, k_values)

    return SamplingResult(
        test_file=test_path,
        n_runs=n,
        n_passed=passed_count,
        pass_rate=pass_rate,
        pass_at_1=metrics.get("pass@1", 0.0),
        pass_at_k_values=metrics,
    )


def run_test_suite_n_times(
    test_dir: str = ".",
    n: int = 10,
    k_values: Sequence[int] = (1, 5, 10),
    pattern: str = "test_*.py",
) -> dict:
    """对目录中所有测试文件分别执行 n 次，汇总 pass@k 报告。"""
    test_files = list(Path(test_dir).glob(pattern))
    if not test_files:
        print(f"[WARN] 未找到匹配 {pattern} 的测试文件")
        return {}

    all_results = []
    for tf in test_files:
        print(f"  采样测试: {tf.name} (n={n}) ...", flush=True)
        r = run_test_n_times(str(tf), n=n, k_values=k_values)
        all_results.append(asdict(r))
        print(f"    通过 {r.n_passed}/{n} | " + " | ".join(f"{k}={v:.3f}" for k, v in r.pass_at_k_values.items()))

    # 全局汇总
    raw_for_global = [{"n": r["n_runs"], "c": r["n_passed"]} for r in all_results]
    global_metrics = pass_at_k_batch(raw_for_global, k_values)

    report = {
        "summary": global_metrics,
        "per_file": all_results,
    }
    return report


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="pass@k 测试采样评测")
    parser.add_argument("--test-dir", default=".", help="测试目录")
    parser.add_argument("--n", type=int, default=10, help="每个测试文件的采样次数")
    parser.add_argument("--k", nargs="+", type=int, default=[1, 5, 10], help="计算 pass@k 的 k值")
    parser.add_argument("--output", default="reports/pass_at_k.json")
    args = parser.parse_args()

    print(f"\n=== pass@k 评测 | n={args.n} | k={args.k} ===")
    report = run_test_suite_n_times(args.test_dir, n=args.n, k_values=args.k)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] 报告已保存至 {args.output}")
    print("全局指标:", json.dumps(report.get("summary", {}), indent=2))


if __name__ == "__main__":
    main()
