import subprocess
from typing import Dict, Optional

class OfflineDocs:
    """Retrieves offline documentation for tools and languages."""
    
    COMMON_TOOLS = {
        "git": "git --help",
        "python": "python3 --help",
        "pip": "pip --help",
        "docker": "docker --help",
        "grep": "man grep",
        "find": "man find",
        "ls": "man ls",
    }

    def get_doc(self, query: str) -> Optional[str]:
        """Get documentation for a query."""
        query = query.lower().strip()
        
        # Check for exact tool match
        if query in self.COMMON_TOOLS:
            cmd = self.COMMON_TOOLS[query]
            return self._run_help(cmd)
            
        # Check for "how to X in Y"
        if "git" in query:
            return self._run_help("git --help")
            
        return None

    def _run_help(self, command: str) -> str:
        try:
            # Use 'man' or '--help'
            parts = command.split()
            if parts[0] == "man":
                # man pages might be interactive, use cat or col -b
                # For simplicity, just try running it, but man usually pages.
                # Better to use --help for most CLI tools in automation
                return "Man pages are interactive. Try --help."
            
            result = subprocess.run(parts, capture_output=True, text=True, timeout=5)
            return result.stdout[:2000] + "\n... (truncated)"
        except Exception as e:
            return f"Error retrieving docs: {e}"
