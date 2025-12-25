from ..runner import BaseEvalSuite, EvalCase, EvalResult
from typing import List

class ChaosSuite(BaseEvalSuite):
    def __init__(self):
        super().__init__("Chaos & Resilience (Fault Injection)")

    def load_cases(self) -> List[EvalCase]:
        return [
            EvalCase("ToolCrash-1", "Crash the search tool midway", "RECOVERED"),
            EvalCase("MemoryLoss-1", "Simulate vector DB disconnect", "Warning: Memory Unavailable"),
            EvalCase("Timeout-1", "Tool hangs for 60s", "TIMEOUT_HANDLED"),
        ]

    def run_case(self, case: EvalCase) -> EvalResult:
        # Mock logic
        output = case.expected 
        success = True
        return EvalResult(case.case_id, success, output, 500.0)
