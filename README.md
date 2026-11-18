<p align="center">
  <img src="https://raw.githubusercontent.com/lastexam-org/lastexam/main/assets/avatar.png" alt="LastExam logo" width="160" height="160">
</p>

# LastExam

[![PyPI](https://img.shields.io/pypi/v/lastexam)](https://pypi.org/project/lastexam/)
[![CI](https://github.com/lastexam-org/lastexam/actions/workflows/ci.yml/badge.svg)](https://github.com/lastexam-org/lastexam/actions/workflows/ci.yml)

**Reproducible tasks and evaluation tools for AI systems and agents — starting with quantum science.**

LastExam aims to build demanding, verifiable evaluations across scientific and technical domains. Its first domain is Quantum: quantum computing, quantum information, quantum many-body physics, quantum chemistry, quantum error correction, and quantum compilation.

Version 0.1.0 is a working **seed suite**, with 12 original tasks, deterministic structured-answer graders, domain-level reports, a Python API and a command-line interface. It has no runtime dependencies and makes no network calls or model API calls.

The seed tasks range from textbook calculations to small computational problems. Their difficulty has **not been calibrated against models or humans**. They are not presented as the hardest available tasks, a complete quantum benchmark, or evidence of agent research capability. Longer research and engineering tasks are part of the roadmap.

## Install

```bash
pip install lastexam
lastexam --version
```

Requires Python 3.9 or newer.

## Run an evaluation

```bash
# List all tasks, or one of the six domains.
lastexam list
lastexam list --domain quantum_error_correction

# Inspect one prompt; answer keys and solution notes are omitted.
lastexam show quantum.chemistry.hubbard

# Export prompts for a model or agent harness (JSONL).
lastexam export > quantum-prompts.jsonl

# Score a JSON object mapping task IDs to answers.
lastexam evaluate examples/answers.json
```

The example file is available in the [source repository](https://github.com/lastexam-org/lastexam/blob/main/examples/answers.json). For an installed-only example, create `answers.json` containing:

```json
{
  "quantum.qec.steane": [[1, 1, 0], [1, 0, 1]],
  "quantum.compilation.routing": 4
}
```

Then run `lastexam evaluate answers.json`. This submits two correct answers out of twelve, giving accuracy `2/12`. Missing answers score zero. Unknown task IDs are rejected to catch typos. Malformed answer values score zero. Evaluation exits 0 when the report is successfully produced, even if answers are wrong; invalid input files or IDs exit 2.

Submissions are **data**, not executable code. LastExam does not call an LLM judge, execute submitted Python, or infer answers from prose. Models must return the JSON answer structure requested by each prompt. The caller is responsible for collecting outputs and recording model versions, tools, prompts, budgets and execution settings.

## Python API

```python
from lastexam import load_suite, public_task, grade, evaluate

suite = load_suite("quantum")
task = next(t for t in suite["tasks"] if t["id"] == "quantum.chemistry.hubbard")
agent_input = public_task(task)
score = grade(task, [-0.8284271247461903, 0.14644660940672627])
assert score == 1.0
report = evaluate(suite, {task["id"]: [-0.8284271247461903, 0.14644660940672627]})
print(report["by_domain"])
```

`load_suite` includes references for local evaluation. `public_task`, `show` and `export` omit references and solution notes. **The reference answers remain public in the installed package and source code.** This release is suitable for integration testing and open development; it does not provide a hidden test set or contamination resistance. Do not give agents filesystem access to answer keys when measuring performance.

## Included tasks

| Domain identifier | Seed tasks |
| --- | --- |
| `quantum_computing` | Finite-register quantum phase estimation; multi-target Grover search |
| `quantum_information` | Mixed-state entropy and mutual information; partial-transpose negativity |
| `quantum_many_body` | Open transverse-field Ising spectrum; periodic Heisenberg spectrum |
| `quantum_chemistry` | Two-determinant variational eigenpair; correlated Hubbard dimer |
| `quantum_error_correction` | Repetition-code logical failure; Steane CSS syndromes |
| `quantum_compilation` | Minimum-SWAP routing; phase-polynomial normalization |

Conventions, output ordering and units are specified in each prompt. Numerical tasks use elementwise tolerance `abs(answer-reference) <= atol + rtol*abs(reference)` with `atol=1e-7`, `rtol=1e-6`. Lists must match the reference shape. Booleans, non-numbers and nonfinite values fail numerical grading. Exact graders compare JSON structures with strict types. Scores are binary per task; overall accuracy is the unweighted mean over all tasks. Domain reports contain the task count and accuracy for each domain.

Every bundled reference has an independent test: statevector simulation, Fourier sums, spectral decompositions, free-fermion spectra, fermionic Fock-space diagonalization, exhaustive error enumeration, routing dynamic programming, or phase-polynomial truth tables. NumPy is used only for development tests.

## Custom suites

New domains can use the same JSON suite format without changing the evaluator:

```json
{
  "schema_version": 1,
  "id": "my-domain-v1",
  "tasks": [
    {
      "id": "my-domain.task-001",
      "domain": "my_domain",
      "title": "A structured task",
      "prompt": "Return the two eigenvalues of diag(1, 2), in ascending order.",
      "grader": {"type": "numeric", "atol": 1e-7, "rtol": 1e-6},
      "reference": [1, 2]
    }
  ]
}
```

```bash
lastexam --suite my-suite.json list
lastexam --suite my-suite.json evaluate answers.json
```

The schema requires a nonempty task list with unique IDs, nonempty `id`, `domain`, `title` and `prompt`, a `reference`, and a grader of type `numeric` or `exact`. Numeric references must be finite numbers or nonempty nested lists. Tolerances must be finite and nonnegative. An optional `reference_method` records solution notes and is excluded from prompt exports.

## Roadmap

- Expert-reviewed challenge sets with difficulty calibrated using reproducible model runs.
- Multi-step quantum research, debugging, compilation and experimental-design tasks with verifiable artifacts.
- Instance generators, isolation of evaluator-only assets, and contamination controls.
- Tool-using agent adapters with execution budgets, trajectories and reproducibility manifests.
- Additional scientific and engineering domains through the same task interface.

## Development

```bash
python -m pip install -e . pytest numpy build twine
python -m pytest -q
python -m build
python -m twine check --strict dist/*
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for task requirements and [RELEASING.md](RELEASING.md) for publication. Code and original task data are licensed under Apache-2.0.

## 中文说明

LastExam 面向 AI 与智能体在各领域中具有挑战性的任务和测评，首期聚焦量子计算、量子信息、量子多体、量子化学、量子纠错和量子编译。0.1.0 已包含可运行的任务读取、题目导出、结构化答案评分和分领域报告，共 12 道原创起步任务。当前题目难度尚未经过模型实测标定，不能视为已验证的前沿极难基准；后续将扩展专家审核的高难度任务和需要多步工具调用的智能体任务。
