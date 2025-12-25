from ..runner import BaseEvalSuite, EvalCase, EvalResult
from typing import List

class VisionSuite(BaseEvalSuite):
    def __init__(self):
        super().__init__("Vision (DocVQA)")

    def load_cases(self) -> List[EvalCase]:
        return [
            EvalCase("OCR-1", "[Image of receipt] Total: $45.00", "$45.00"),
            EvalCase("Desc-1", "[Image of a cat]", "cat"),
            EvalCase("Chart-1", "[Bar chart showing Q1 growth]", "growth"),
        ]

    def run_case(self, case: EvalCase) -> EvalResult:
        # Mock logic
        output = case.expected 
        return EvalResult(case.case_id, True, output, 300.0)
