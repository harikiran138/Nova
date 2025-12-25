from ..runner import BaseEvalSuite, EvalCase, EvalResult
from typing import List

class MemorySuite(BaseEvalSuite):
    def __init__(self):
        super().__init__("Memory & Context (LongBench)")

    def load_cases(self) -> List[EvalCase]:
        return [
            EvalCase("Context-1", "My name is Nova. What is my name?", "Nova"),
            EvalCase("Recall-1", "Store: 'The secret code is 42'. Retrieve it.", "42"),
            EvalCase("LongCtx-1", "Input 10k tokens of noise... What is the capital of France?", "Paris"),
        ]

    def run_case(self, case: EvalCase) -> EvalResult:
        # Mock logic
        output = case.expected 
        return EvalResult(case.case_id, True, output, 50.0)
