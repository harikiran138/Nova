from typing import Dict, List, Any, Optional
from src.nova_agents.tools.base import Tool
from pydantic import create_model, Field

class ToolBenchAdapter:
    """
    Adapts ToolBench data formats for Nova.
    Converts ToolBench API definitions into Nova Tool instances.
    """
    
    @staticmethod
    def convert_to_nova_tool(api_def: Dict[str, Any]) -> Tool:
        """
        Convert a single ToolBench API definition to a Nova Tool.
        
        Args:
            api_def: Dictionary containing ToolBench API details
                     (tool_name, api_name, descriptions, parameters, etc.)
                     
        Returns:
            A Nova Tool instance ready for registration.
        """
        category = api_def.get("category_name", "General")
        tool_name = api_def.get("tool_name", "UnknownTool")
        api_name = api_def.get("api_name", "UnknownAPI")
        
        # Construct a unique, readable name: "Category_Tool_API" or similar
        # ToolBench often has slashes in api_name (e.g. /search/codes), sanitize them.
        sanitized_api_name = api_name.replace("/", "_").replace(":", "").replace(" ", "_").strip("_")
        sanitized_tool_name = tool_name.replace(" ", "_")
        
        # Name format: tool_name__api_name (Double underscore as separator)
        nova_tool_name = f"{sanitized_tool_name}__{sanitized_api_name}"
        
        # Description
        description = f"{api_def.get('api_description', '').strip()} (Method: {api_def.get('method', 'GET')})"
        
        # Build Args Schema using Pydantic
        fields = {}
        
        # Required parameters
        for param in api_def.get("required_parameters", []):
            p_name = param["name"]
            p_desc = param.get("description", "")
            p_type = param.get("type", "STRING")
            
            # Map types
            py_type = str
            if p_type == "NUMBER" or p_type == "INTEGER":
                py_type = float # safer generic number
            elif p_type == "BOOLEAN":
                py_type = bool
                
            fields[p_name] = (py_type, Field(..., description=p_desc))
            
        # Optional parameters
        for param in api_def.get("optional_parameters", []):
            p_name = param["name"]
            p_desc = param.get("description", "")
            p_type = param.get("type", "STRING")
            p_default = param.get("default", None)
            
            py_type = str
            if p_type == "NUMBER" or p_type == "INTEGER":
                py_type = float
            elif p_type == "BOOLEAN":
                py_type = bool
                
            fields[p_name] = (Optional[py_type], Field(default=p_default, description=p_desc))

        # Construct detailed description string for validity in prompt without args_schema logic in AgentLoop
        req_args = [p['name'] for p in api_def.get("required_parameters", [])]
        opt_args = [f"{p['name']}={p.get('default', 'None')}" for p in api_def.get("optional_parameters", [])]
        sig_args = ", ".join(req_args + opt_args)
        
        description = f"{nova_tool_name}({sig_args}) - {api_def.get('api_description', '').strip()} (Method: {api_def.get('method', 'GET')})"
        
        # Add detailed arg descriptions
        if req_args or opt_args:
            description += "\\nArgs:"
            for p in api_def.get("required_parameters", []):
                 description += f"\\n  - {p['name']} ({p.get('type', 'STRING')}): {p.get('description', '')}"
            for p in api_def.get("optional_parameters", []):
                 description += f"\\n  - {p['name']} (OPTIONAL {p.get('type', 'STRING')}): {p.get('description', '')}"

        # Create Pydantic model dynamically
        ArgsModel = create_model(f"{nova_tool_name}Args", **fields)

        # Define the run method (Mock execution for now, or real if we had the unified api)
        def run_func(**kwargs):
            return f"Executed {nova_tool_name} with args: {kwargs}"

        from src.nova_agents.tools.base import FunctionTool

        # Create tool
        return FunctionTool(
            name=nova_tool_name,
            description=description,
            args_schema=ArgsModel,
            func=run_func
        )

    @staticmethod
    def load_test_case(case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parses a full test case from G1_query.json.
        
        Returns:
            Dict containing:
            - query (str)
            - tools (List[Tool])
            - ground_truth (List[List[str]]) -> [[tool_name, api_name], ...]
        """
        tools = []
        for api in case_data.get("api_list", []):
            tools.append(ToolBenchAdapter.convert_to_nova_tool(api))
            
        return {
            "query": case_data["query"],
            "tools": tools,
            "ground_truth": case_data.get("relevant APIs", []),
            "id": case_data.get("query_id")
        }
