import time
from pathlib import Path
from src.agent_core.tools.registry import ToolRegistry

registry = ToolRegistry(Path("test_workspace"))
registry.file.mkdir(".") # Ensure workspace exists

def log(msg):
    print(f"[AGENT] {msg}")

def run_step(name, tool, args):
    log(f"Executing {tool}...")
    res = registry.execute(tool, args)
    if isinstance(res, str) and "Error" in res and "not found" not in res:
        print(f"❌ {name} Failed: {res}")
        return False
    print(f"✅ {name} Output: {str(res)[:100]}...")
    return True

try:
    # 1. File System: Create a target file
    run_step("Create Target", "file.write", {"path": "targets.txt", "content": "example.com"})
    
    # 2. Git: Track it
    run_step("Git Init", "kali.run", {"command": "git init"}) # Using Kali to run git? No, use git tool.
    # Wait, GitTool uses subprocess on host.
    run_step("Git Status", "git.status", {})
    run_step("Git Add", "git.add", {"files": ["targets.txt"]})
    run_step("Git Commit", "git.commit", {"message": "Add target"})
    
    # 3. Kali: Start Session
    run_step("Start Session", "kali.start_session", {})
    
    # 4. Kali: Install Tool (curl)
    run_step("Install curl", "kali.install", {"packages": "curl"})
    
    # 5. Kali: Use Tool (curl)
    # We'll fetch the target from the file we created? 
    # The workspace is mounted at /workspace.
    # So we can read targets.txt inside Kali.
    cmd = "curl -I $(cat targets.txt)"
    run_step("Run curl", "kali.run", {"command": cmd})
    
    # 6. Kali: Save Output to File (inside Kali, appearing on Host)
    cmd = "curl -I example.com > scan_results.txt"
    run_step("Save Results", "kali.run", {"command": cmd})
    
    # 7. File System: Verify Results on Host
    res = registry.execute("file.read", {"path": "scan_results.txt"})
    if "HTTP" in res:
        print("✅ Verification: File created by Kali is readable on Host!")
    else:
        print("❌ Verification Failed: Result file empty or missing.")
        
    # 8. Stop Session
    run_step("Stop Session", "kali.stop_session", {})

except Exception as e:
    print(f"❌ CRITICAL ERROR: {e}")
    registry.execute("kali.stop_session", {})
