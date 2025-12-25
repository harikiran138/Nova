import unittest
from src.nova_agents.tools.registry import ToolRegistry
from src.nova_agents.core.policies import SafetyPolicy
from src.nova_agents.core.executor import ToolExecutor
from src.nova_agents.tools.custom.hello_world import HelloWorldTool

class TestArchitecture(unittest.TestCase):
    def test_tool_execution_flow(self):
        # 1. Setup Registry
        registry = ToolRegistry()
        hello_tool = HelloWorldTool()
        registry.register(hello_tool)
        
        # 2. Setup Policy
        policy = SafetyPolicy()
        
        # 3. Setup Executor
        executor = ToolExecutor(registry, policy)
        
        # 4. Execute via Executor
        print("\nTesting 'hello_world' tool via Executor...")
        result = executor.execute("hello_world", name="Nova")
        
        print(f"Result: {result}")
        self.assertEqual(result, "Hello, Nova!")
        
    def test_safety_blocking(self):
        # 1. Setup Registry
        registry = ToolRegistry()
        
        # Create a high risk tool
        class DangerousTool(HelloWorldTool):
            name = "dangerous_tool"
            risk_level = "HIGH"
            
        registry.register(DangerousTool())
        
        # 2. Setup Policy & Executor
        policy = SafetyPolicy()
        executor = ToolExecutor(registry, policy)
        
        # 3. Execute - Should be blocked
        print("\nTesting 'dangerous_tool' blocking...")
        result = executor.execute("dangerous_tool")
        
        print(f"Result: {result}")
        self.assertEqual(result["status"], "BLOCKED")

if __name__ == '__main__':
    unittest.main()
