# AI 代码评测方案 (GitLab python_test)

## 目录结构
- `eval/humaneval_mbpp/`: 离线评测
- `eval/pass_at_k/`: 单元测试 pass@k
- `eval/llm_judge/`: 代码质量评审
- `eval/static_analysis/`: 静态分析
- `eval/online_metrics/`: 在线指标
- `eval/pipeline.py`: 统一流水线

## 快速开始
```bash
pip install -r requirements.txt
python eval/pipeline.py --smoke
```
