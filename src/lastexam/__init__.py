"""LastExam: task loading and deterministic evaluation for AI agents."""
from .core import evaluate, grade, load_suite, public_task

__version__ = "0.1.0"
__all__ = ["evaluate", "grade", "load_suite", "public_task", "__version__"]
