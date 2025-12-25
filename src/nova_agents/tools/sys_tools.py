import os
import psutil
import platform
from typing import Dict, Any

class SysEnvTool:
    name = "sys.env"
    description = "Get environment variables."
    
    def execute(self, key: str = None) -> Dict[str, Any]:
        if key:
            return {"value": os.environ.get(key)}
        return {"env": dict(os.environ)}

class SysUsageTool:
    name = "sys.usage"
    description = "Get system resource usage (CPU, RAM)."
    
    def execute(self) -> Dict[str, Any]:
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": dict(psutil.virtual_memory()._asdict()),
            "platform": platform.platform()
        }
