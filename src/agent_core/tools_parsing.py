import json
import re
from typing import List, Optional, Dict, Any

def parse_tool_calls(text: str) -> List[Dict[str, Any]]:
    """Parse multiple tool calls from model output.
    
    Looks for JSON objects in the format:
    {"tool": "tool.name", "args": {"key": "value"}}
    
    Args:
        text: Model output text
        
    Returns:
        List of parsed tool call dicts
    """
    tool_calls = []
    current_idx = 0
    
    while True:
        # Find potential start of JSON
        match = re.search(r'\{\s*"tool"', text[current_idx:])
        if not match:
            break
        
        start_idx = current_idx + match.start()
        
        # Simple brace counting to find the end
        cnt = 0
        found_end = False
        for i in range(start_idx, len(text)):
            if text[i] == '{':
                cnt += 1
            elif text[i] == '}':
                cnt -= 1
                if cnt == 0:
                    try:
                        json_str = text[start_idx:i+1]
                        obj = json.loads(json_str)
                        if "tool" in obj and "args" in obj:
                            tool_calls.append(obj)
                        current_idx = i + 1
                        found_end = True
                        break
                    except json.JSONDecodeError:
                        # Continue searching if this wasn't valid JSON
                        pass
        
        if not found_end:
            # If we didn't find a valid end, skip this start brace
            current_idx = start_idx + 1
            
    return tool_calls

def detect_bad_tool_call(text: str) -> Optional[str]:
    """Detect if the model tried to call a tool with incorrect syntax.
    
    Returns:
        The suspected tool name if found, else None.
    """
    # Look for patterns like tool.name(...)
    # We look for word characters, dot, word characters, then parenthesis
    match = re.search(r'(\w+\.\w+)\s*\(', text)
    if match:
        return match.group(1)
    return None
