import json
import uuid
from typing import List, Dict, Any, Optional, Generator
from pydantic import BaseModel

from ..models.ollama import OllamaClient
from ..memory.memory import MemorySystem
from ..tools.base import BaseTool
from ..config import config

class Agent:
    """Nova v2 Agent Engine implementing ReAct pattern."""
    
    def __init__(self, 
                 client: OllamaClient = None, 
                 memory: MemorySystem = None,
                 tools: List[BaseTool] = None):
        self.client = client or OllamaClient()
        self.memory = memory or MemorySystem()
        self.tools = {t.name: t for t in tools or []}
        self.system_prompt = self._build_system_prompt()
        
    def _build_system_prompt(self) -> str:
        """Construct the system prompt with tool definitions."""
        tool_schemas = [t.to_schema() for t in self.tools.values()]
        
        prompt = """You are Nova, an advanced local AI agent.
You have access to the following tools:

{tools_json}

To use a tool, you MUST respond with a JSON object in this format:
{{"tool": "tool_name", "args": {{...}}}}

If you don't need to use a tool, just respond normally.
Think step-by-step.
""".format(tools_json=json.dumps(tool_schemas, indent=2))
        return prompt

    def chat(self, user_input: str, session_id: str = None) -> Generator[str, None, None]:
        """Run the agent loop."""
        if not session_id:
            session_id = str(uuid.uuid4())
            
        # Add user message to memory
        self.memory.add_message(session_id, "user", user_input)
        
        # Get history
        history = self.memory.get_history(session_id)
        messages = [{"role": m["role"], "content": m["content"]} for m in history]
        
        # Prepend system prompt
        messages.insert(0, {"role": "system", "content": self.system_prompt})
        
        # Agent Loop (Max 5 turns)
        for _ in range(5):
            # Generate response (non-streaming for tool decision)
            response_text = self.client.generate(messages, stream=False)
            
            if not response_text:
                yield "Error: Failed to generate response."
                return

            # Check for tool call
            tool_call = self._parse_tool_call(response_text)
            
            if tool_call:
                tool_name = tool_call.get("tool")
                tool_args = tool_call.get("args", {})
                
                yield f"🔧 Calling tool: {tool_name}...\n"
                
                if tool_name in self.tools:
                    try:
                        result = self.tools[tool_name].run(**tool_args)
                        observation = f"Tool Output: {result}"
                    except Exception as e:
                        observation = f"Tool Error: {str(e)}"
                else:
                    observation = f"Error: Tool {tool_name} not found."
                
                # Add to history
                self.memory.add_message(session_id, "assistant", response_text)
                self.memory.add_message(session_id, "user", f"Observation: {observation}")
                
                messages.append({"role": "assistant", "content": response_text})
                messages.append({"role": "user", "content": f"Observation: {observation}"})
                
            else:
                # Final response
                self.memory.add_message(session_id, "assistant", response_text)
                yield response_text
                return

    def _parse_tool_call(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse JSON tool call from text."""
        try:
            # Look for JSON object
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1:
                json_str = text[start:end+1]
                data = json.loads(json_str)
                if "tool" in data and "args" in data:
                    return data
        except:
            pass
        return None
