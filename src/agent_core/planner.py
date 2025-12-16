import json
import uuid
from typing import List, Optional
from .model_client import OllamaClient
from .tasks import Task
from .tools import ToolRegistry
import re

class Planner:
    """Planner for generating structured task plans."""
    
    def __init__(self, client: OllamaClient, tools: ToolRegistry, profile_name: str = "general"):
        self.client = client
        self.tools = tools
        self.profile_name = profile_name
        
        # Filter tools for planning
        from .config import Config
        config = Config.from_env()
        profiles = config.load_profiles()
        
        from .tool_selector import ToolSelector
        selector = ToolSelector(profiles)
        self.active_tool_names = selector.select_tools(profile_name, list(tools.tools.keys()))
        
    def plan_task(self, goal: str) -> Task:
        """Generate a plan for the given goal."""
        task_id = str(uuid.uuid4())[:8]
        task = Task(id=task_id, goal=goal, status="planning")
        
        # Get descriptions of ONLY active tools
        active_descriptions = []
        for name in self.active_tool_names:
            if name in self.tools.tools:
                active_descriptions.append(self.tools.tools[name].description)
                
        tool_descriptions = "\n".join(active_descriptions)
        
        prompt = f"""GOAL: {goal}

AVAILABLE TOOLS:
{tool_descriptions}

You are the Supervisor Agent.
Create a step-by-step plan to achieve the goal using ONLY the available tools.
Assign a specialized agent role for each step: "coder", "researcher", "reviewer", or "general".

Return a JSON object with a "steps" key containing a list of steps.
Each step should have:
- "id": number
- "description": string
- "tool": string (name of the tool to use, or null if no tool needed)
- "args": object (arguments for the tool)
- "role": string (coder, researcher, reviewer, general)

Example format:
{{
  "steps": [
    {{
      "description": "Research Python libraries",
      "tool": "net.search",
      "args": {{ "query": "python libraries" }},
      "role": "researcher"
    }}
  ]
}}
"""
        response = self.client.generate(
            messages=[{"role": "user", "content": prompt}],
            system_prompt="You are a precise planner. Output valid JSON only. Do not include markdown formatting."
        )
        
        if not response:
            task.add_step("Analyze the goal and decide next steps manually")
            return task
            
        try:
            # Clean response
            json_str = response.strip()
            # Remove markdown code blocks if present
            if "```" in json_str:
                json_str = re.sub(r'```json\s*|\s*```', '', json_str)
            
            plan_data = json.loads(json_str)
            steps = plan_data.get("steps", [])
            
            for step in steps:
                task.add_step(
                    description=step.get("description", "Unknown step"),
                    tool=step.get("tool"),
                    args=step.get("args"),
                    role=step.get("role", "general")
                )
                
        except Exception as e:
            # Fallback on error
            task.add_step(f"Failed to parse plan: {str(e)}. Proceed manually.")
            
        task.status = "pending"
        return task
