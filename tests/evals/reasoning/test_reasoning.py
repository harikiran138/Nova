import time
from typing import List
from ..runner import BaseEvalSuite, EvalCase, EvalResult
# from datasets import load_dataset  # Keep commented until we actually add dependency

class ReasoningSuite(BaseEvalSuite):
    def __init__(self):
        super().__init__("Core Reasoning (GSM8K)")

    def load_cases(self) -> List[EvalCase]:
        # For now, manually defining a few GSM8K-style cases to verify the harness
        # In a real scenario, we would use: dataset = load_dataset("gsm8k", "main", split="test")
        return [
            EvalCase(
                case_id="GSM8K-1",
                input_data="Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May?",
                expected="72"
            ),
            EvalCase(
                case_id="GSM8K-2",
                input_data="Weng earns $12 an hour for babysitting. Yesterday, she just did 50 minutes of babysitting. How much did she earn?",
                expected="$10"
            ),
            EvalCase(
                case_id="Logic-1",
                input_data="If all cats are mammals and all mammals have kidneys, do all cats have kidneys?",
                expected="Yes"
            )
        ]

    def run_case(self, case: EvalCase) -> EvalResult:
        start_time = time.time()
        
        # TODO: Replace with actual Nova Agent Generation
        # from src.nova_agents.agent_loop import AgentLoop
        # response = agent_loop.process(case.input_data)
        
        # MOCKING RESPONSE FOR SCAFFOLD VERIFICATION
        mock_thinking_time = 0.5
        time.sleep(mock_thinking_time)
        
        # Simple heuristic mock for demonstration
        result_output = ""
        if "72" in case.expected:
            result_output = "Natalia sold 48 in April. Half of 48 is 24. 48 + 24 = 72."
        elif "$10" in case.expected:
            result_output = "50 minutes is 5/6 of an hour. 12 * 5/6 = 10. She earned $10."
        else:
            result_output = "Yes, by transitive property."
            
        success = case.expected in result_output
        latency = (time.time() - start_time) * 1000
        
        return EvalResult(case.case_id, success, result_output, latency)
