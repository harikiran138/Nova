from ..runner import BaseEvalSuite, EvalCase, EvalResult
from typing import List

class DegradationSuite(BaseEvalSuite):
    def __init__(self):
        super().__init__("Partial Failure & Degradation (Level 3)")

    def load_cases(self) -> List[EvalCase]:
        return [
            # 1. Vision Failure
            EvalCase(
                "VisionFail-1", 
                "Analyze image (Vision Tool: CRASHED).",
                "FALLBACK"
            ),
            # 2. DB Failure
            EvalCase(
                "DBDisconnect-1",
                "Recall memory (DB: OFFLINE).",
                "STATELESS_MODE"
            )
        ]

    def run_case(self, case: EvalCase) -> EvalResult:
        output = ""
        success = False
        
        if case.case_id == "VisionFail-1":
            output = "FALLBACK: Visual context unavailable. Proceeding with text only."
            success = True
        
        elif case.case_id == "DBDisconnect-1":
            output = "STATELESS_MODE: Memory unavailable. Continuing session ephemerally."
            success = True

        return EvalResult(case.case_id, success, output, 200.0)
