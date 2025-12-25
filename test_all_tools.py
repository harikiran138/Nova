import os
import shutil
import json
from pathlib import Path
from src.agent_core.tools.registry import ToolRegistry

# Setup
TEST_DIR = Path("test_workspace")
if TEST_DIR.exists():
    shutil.rmtree(TEST_DIR)
TEST_DIR.mkdir()

registry = ToolRegistry(TEST_DIR)
report = []

def log(tool_name, status, output):
    print(f"[{status}] {tool_name}")
    report.append(f"| {tool_name} | {status} | `{str(output)[:100]}...` |")

print("Starting Tool Verification...")
report.append("# Nova v2.0 Tool Verification Report")
report.append("| Tool | Status | Output Preview |")
report.append("|---|---|---|")

# --- File Tools ---
try:
    registry.execute("file.write", {"path": "hello.txt", "content": "Hello Nova!"})
    log("file.write", "PASS", "File written")
    
    content = registry.execute("file.read", {"path": "hello.txt"})
    if content == "Hello Nova!":
        log("file.read", "PASS", content)
    else:
        log("file.read", "FAIL", f"Content mismatch: {content}")
        
    files = registry.execute("file.list", {"path": "."})
    log("file.list", "PASS", files)
    
    registry.execute("file.mkdir", {"path": "subdir"})
    log("file.mkdir", "PASS", "Dir created")
    
    registry.execute("file.copy", {"src": "hello.txt", "dst": "subdir/hello_copy.txt"})
    log("file.copy", "PASS", "File copied")
    
except Exception as e:
    log("File Tools", "FAIL", str(e))

# --- Git Tools ---
try:
    # Initialize dummy repo
    os.system(f"cd {TEST_DIR} && git init")
    os.system(f"cd {TEST_DIR} && git config user.email 'test@nova.ai' && git config user.name 'Nova Test'")
    
    status = registry.execute("git.status", {})
    log("git.status", "PASS", status)
    
    registry.execute("git.add", {"files": ["."]})
    log("git.add", "PASS", "Files added")
    
    registry.execute("git.commit", {"message": "Initial commit"})
    log("git.commit", "PASS", "Committed")
    
    log_out = registry.execute("git.log", {})
    log("git.log", "PASS", log_out)
    
except Exception as e:
    log("Git Tools", "FAIL", str(e))

# --- System Tools ---
try:
    usage = registry.execute("sys.usage", {})
    log("sys.usage", "PASS", usage)
    
    info = registry.execute("sys.osinfo", {})
    log("sys.osinfo", "PASS", info)
except Exception as e:
    log("System Tools", "FAIL", str(e))

# --- Web Tools ---
try:
    # Mock search
    res = registry.execute("web.search", {"query": "Nova AI"})
    log("web.search", "PASS", res)
    
    # Real request (might fail if no internet, but we'll try)
    # Using a reliable small site
    # res = registry.execute("web.get", {"url": "http://example.com"})
    # log("web.get", "PASS", res)
except Exception as e:
    log("Web Tools", "FAIL", str(e))

# --- Kali Tools ---
try:
    # Check if docker is available
    if registry.kali.client:
        # Simple run
        res = registry.execute("kali.run", {"command": "echo 'Kali is alive'"})
        if "Kali is alive" in res:
            log("kali.run", "PASS", res)
        else:
            log("kali.run", "FAIL", res)
            
        # Nmap (localhost) - might fail if network restricted, but tool execution should pass
        # We'll just check version to be safe and fast
        res = registry.execute("kali.nmap", {"target": "127.0.0.1", "args": "-V"})
        log("kali.nmap", "PASS", res)
        
    else:
        log("Kali Tools", "SKIP", "Docker not available")
except Exception as e:
    log("Kali Tools", "FAIL", str(e))


# Save Report
Path("tool_report.md").write_text("\n".join(report))
print("Report saved to tool_report.md")
