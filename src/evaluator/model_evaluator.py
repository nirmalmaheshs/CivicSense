import time
import pandas as pd
import streamlit as st
from typing import List, Dict
from snowflake.cortex import Complete

class ModelEvaluator:
    def __init__(self):
        # Initialize test cases with ground truth answers
        self.test_cases = self.get_test_cases()

        # Initialize evaluation results and configurations in session state
        if 'evaluation_results' not in st.session_state:
            st.session_state.evaluation_results = []
        if 'model_configurations' not in st.session_state:
            st.session_state.model_configurations = []

    def get_test_cases(self):
        """Get the list of test questions with ground truth answers"""
        return [
            {
                "question": "What are the eligibility requirements for healthcare benefits?",
                "ground_truth": "To be eligible for healthcare benefits, you must be a U.S. citizen or legal resident, meet income requirements based on the Federal Poverty Level, and not have access to affordable employer-sponsored coverage. Additional requirements may include age, disability status, and household size."
            },
            # ... other test cases ...
        ]

    def evaluate_answer_similarity(self, model_answer: str, ground_truth: str) -> float:
        """Evaluate semantic similarity between model answer and ground truth"""
        prompt = f"""
        Model Answer: {model_answer}
        Ground Truth: {ground_truth}

        On a scale from 0 to 1, evaluate the semantic similarity and factual accuracy of the model's answer 
        compared to the ground truth. Consider:
        - Key information coverage
        - Factual accuracy
        - Completeness
        - Relevant details

        Provide only the numerical score.
        """

        try:
            response = Complete("mistral-large2", prompt)
            score = float(response.strip())
            return min(max(score, 0), 1)
        except:
            return 0.0

    # ... other evaluation methods ...

    def get_evaluation_summary(self, config_name: str = None) -> Dict:
        """Get summary of evaluation results for a specific configuration or all"""
        if not st.session_state.evaluation_results:
            return {}

        df = pd.DataFrame(st.session_state.evaluation_results)
        if config_name:
            df = df[df['config_name'] == config_name]

        metrics = [
            'answer_similarity', 'factual_accuracy', 'context_relevance',
            'response_relevance', 'completion_quality', 'response_conciseness'
        ]

        summary = {
            'total_evaluations': len(df),
            'latest_run': df['timestamp'].max(),
            'metrics': {
                metric: {
                    'mean': df[metric].mean(),
                    'std': df[metric].std(),
                    'min': df[metric].min(),
                    'max': df[metric].max()
                } for metric in metrics
            },
            'avg_latency_ms': df['latency_ms'].mean()
        }

        return summary