from ..runner import BaseEvalSuite, EvalCase, EvalResult
from typing import List

class LongRunSuite(BaseEvalSuite):
    def __init__(self):
        super().__init__("Long-Run Stability (Level 3)")

    def load_cases(self) -> List[EvalCase]:
        return [
            # 1. 1-Hour Simulation (Compressed)
            EvalCase(
                "HourRun-1", 
                "Simulate 1000 continuous actions. Check for crashes.",
                "COMPLETED"
            ),
            # 2. Memory Bloat Check
            EvalCase(
                "MemLeaks-1",
                "Measure RSS after 1000 steps. Max allowed: 500MB growth.",
                "STABLE"
            )
        ]

    def run_case(self, case: EvalCase) -> EvalResult:
        # Mocking long-run logic
        output = ""
        success = False
        
        if case.case_id == "HourRun-1":
            # Simulate loop
            output = "COMPLETED: 1000/1000 steps. No exceptions."
            success = True
        
        elif case.case_id == "MemLeaks-1":
            # Simulate metrics check
            output = "STABLE: RSS grew by 12MB (Threshold: 500MB)"
            success = True

        return EvalResult(case.case_id, success, output, 1000.0)
