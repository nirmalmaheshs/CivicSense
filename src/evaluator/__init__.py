"""
Evaluator package for policy chatbot evaluation.
Provides model evaluation, TruLens integration, and enhanced metrics tracking.
"""

from src.evaluator.model_evaluator import ModelEvaluator
from src.evaluator.trulens_evaluator import TruLensEvaluator
from src.evaluator.metrics import EnhancedMetrics

__all__ = [
    'ModelEvaluator',
    'TruLensEvaluator',
    'EnhancedMetrics'
]

# Version of the evaluator package
__version__ = '1.0.0'