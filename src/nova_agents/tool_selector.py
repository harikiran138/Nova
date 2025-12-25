from typing import List, Dict, Any
import fnmatch

class ToolSelector:
    """Selects appropriate tools based on agent profile and goal."""
    
    def __init__(self, profiles: Dict[str, Any]):
        self.profiles = profiles
        
    def select_tools(self, profile_name: str, available_tools: List[str]) -> List[str]:
        """Select tools allowed for the given profile."""
        if profile_name not in self.profiles:
            # Default to all tools if profile not found
            return available_tools
            
        allowed_patterns = self.profiles[profile_name].get("allowed_tools", ["*"])
        
        selected_tools = []
        for tool in available_tools:
            for pattern in allowed_patterns:
                if fnmatch.fnmatch(tool, pattern):
                    selected_tools.append(tool)
                    break
                    
        return selected_tools

    def get_profile(self, profile_name: str) -> Dict[str, Any]:
        """Get profile details."""
        return self.profiles.get(profile_name, self.profiles.get("general", {}))
