from pydantic import BaseModel, Field
from typing import Optional, List
from src.agent_core.adk.tools import define_tool
from src.agent_core.tools.shell import ShellRunTool
from src.agent_core.adk.tracing import trace
from pathlib import Path

# 1. Define Pydantic Schema
class AzdArgs(BaseModel):
    command: str = Field(..., description="The azd command to execute (e.g., 'init', 'up').")
    template: Optional[str] = Field(None, description="The template name for azd init.")
    env_name: Optional[str] = Field(None, description="The environment name for azd.")

# 2. Instantiate Legacy Tool for execution
_workspace = Path("/Users/chepuriharikiran/Nova")
_allowlist = ["azd"]
_legacy_shell = ShellRunTool(workspace_dir=_workspace, allow_shell=True, allowlist=_allowlist)

# 3. Define ADK Typed Tool
@define_tool(
    name="azure.azd",
    description="Manage Azure Developer CLI operations. Use for initializing and deploying Azure templates.",
    schema=AzdArgs
)
def azd_tool(args: AzdArgs):
    """
    Executes azd commands with structured tracing.
    """
    full_command = f"azd {args.command}"
    if args.template:
        full_command += f" -t {args.template}"
    if args.env_name:
        full_command += f" -e {args.env_name}"
    
    # Force non-interactive for azd init if needed, although azd init -t usually is
    if args.command == "init" and args.template:
        # azd init -t template --no-prompt is often needed
        full_command += " --no-prompt"

    trace("tool_start", tool="azure.azd", command=full_command)
    
    try:
        result = _legacy_shell.execute({"command": full_command})
        trace("tool_end", tool="azure.azd", status="success", result=str(result)[:100])
        return result
    except Exception as e:
        trace("tool_end", tool="azure.azd", status="error", error=str(e))
        return {"error": str(e)}
