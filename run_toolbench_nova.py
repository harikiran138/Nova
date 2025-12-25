import json
import os
import sys
from typing import List, Dict, Any

# Ensure src is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.nova_agents.core.agent_loop import AgentLoop
from src.nova_agents.tools.registry import ToolRegistry
from src.nova_agents.benchmarks.toolbench_adapter import ToolBenchAdapter
from src.nova_shared.config import Config

def load_dataset(path: str) -> List[Dict[str, Any]]:
    with open(path, 'r') as f:
        return json.load(f)

def run_evaluation(limit: int = 5):
    # Enforce Benchmark Mode
    os.environ["BENCHMARK_MODE"] = "true"
    os.environ["BENCHMARK_TASK_TYPE"] = "toolbench"
    
    from src.nova_ai.model_client import OllamaClient

    # Initialize Agent
    config = Config.from_env()
    registry = ToolRegistry(workspace_dir=".")
    
    # Initialize Client
    client = OllamaClient(
        base_url=config.ollama_base_url,
        model=config.ollama_model
    )
    
    # Initialize AgentLoop
    agent = AgentLoop(client=client, tools=registry)
    
    # Load Data
    dataset_path = "../ToolBench/data_example/instruction/G1_query.json"
    print(f"Loading dataset from {dataset_path}...")
    data = load_dataset(dataset_path)
    
    results = []
    
    print(f"Running evaluation on {limit} tasks...")
    
    from src.nova_agents.tools_parsing import parse_tool_calls

    for i, item in enumerate(data[:limit]):
        case = ToolBenchAdapter.load_test_case(item)
        query = case["query"]
        ground_truth_apis = case["ground_truth"] # [[tool, api], ...]
        
        print(f"\n--- Task {i+1} ---")
        print(f"Query: {query[:100]}...")
        
        # 1. Setup Registry
        registry.clear_ephemeral_tools()
        for tool in case["tools"]:
            registry.register_ephemeral_tool(tool)
            
        print(f"Registered {len(case['tools'])} tools.")
        
        # 2. Run Agent
        # Clear history to ensure fresh start
        agent.reset_conversation()
        
        try:
            # We only care about the first few steps usually, but let's let it run
            # The run might behave differently with mock tools.
            # We intercept the response to check tool calls.
            response = agent.process_input(query)
            
            # 3. Analyze History for Tool Calls
            # Look for recent assistant messages with tool_calls
            tool_calls_made = []
            
            # AgentLoop stores history in self.conversation_history
            # History is [{"role": "...", "content": "..."}]
            for msg in agent.conversation_history:
                if msg.get('role') == 'assistant':
                    content = msg.get('content', '')
                    parsed_calls = parse_tool_calls(content)
                    if parsed_calls:
                         for call in parsed_calls:
                             tool_calls_made.append(call['tool'])
            
            print(f"Agent called: {tool_calls_made}")
            
            # 4. Verify
            # Ground truth format: [['Category', 'APIName'], ['Category', 'APIName']]
            # Our tool names: Category_Tool__APIName (normalized)
            
            # We need to fuzzy match or normalize ground truth to our tool names
            # Adapter logic: f"{sanitized_tool_name}__{sanitized_api_name}"
            # Let's reconstruct expected names from ground truth
            
            expected_tools = []
            for gt in ground_truth_apis:
                # gt is [ToolName, APIName] usually
                # Need to match Adapter's sanitization logic
                t_name, a_name = gt[0], gt[1]
                sanitized_api = a_name.replace("/", "_").replace(":", "").replace(" ", "_").strip("_")
                sanitized_tool = t_name.replace(" ", "_")
                expected_name = f"{sanitized_tool}__{sanitized_api}"
                expected_tools.append(expected_name)
            
            print(f"Expected: {expected_tools}")
            
            # Simple Strict Match: Did we call ANY of the expected tools?
            # Or ALL? ToolBench usually checks if the sequence is correct.
            # Let's check for "Recall" - did we retrieve the right tools?
            
            matches = [t for t in tool_calls_made if t in expected_tools]
            success = len(matches) > 0
            
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"Result: {status}")
            
            results.append({
                "id": case["id"],
                "success": success,
                "called": tool_calls_made,
                "expected": expected_tools
            })
            
        except Exception as e:
            print(f"Error executing task: {e}")
            results.append({"id": case["id"], "success": False, "error": str(e)})

    # Summary
    passed = sum(1 for r in results if r["success"])
    print(f"\nFinal Score: {passed}/{len(results)} ({passed/len(results)*100:.1f}%)")

if __name__ == "__main__":
    run_evaluation(limit=5)
