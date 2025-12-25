from src.nova_agents.tools.base import Tool

class HelloWorldTool(Tool):
    name = "hello_world"
    description = "A simple hello world tool for verification."
    risk_level = "LOW"

    def execute(self, name: str = "World") -> str:
        return f"Hello, {name}!"
