import time
from pathlib import Path
from src.agent_core.tools.registry import ToolRegistry

# Setup
workspace = Path("mission_workspace")
workspace.mkdir(exist_ok=True)
registry = ToolRegistry(workspace)

def log(msg):
    print(f"[MISSION] {msg}")

try:
    log("🚀 Starting Autonomous Mission")
    
    # 1. System Health
    log("Checking System Health...")
    usage = registry.execute("sys.usage", {})["result"]
    disk = registry.execute("sys.disk", {"path": "/"})["result"]
    log(f"CPU: {usage['cpu']}%, RAM: {usage['ram']}%")
    log(f"Disk Free: {disk['free'] // (1024**3)} GB")
    
    # 2. Network Check
    log("Checking Network...")
    net_status = registry.execute("net.check", {})["result"]
    log(f"Network: {net_status}")
    
    if net_status != "Online":
        log("❌ Network offline. Aborting.")
        exit(1)
        
    # 3. Download Data
    log("Downloading Data...")
    target_url = "https://www.example.com"
    dest_file = "example.html"
    res = registry.execute("net.download", {"url": target_url, "dest": dest_file})
    log(res["result"])
    
    # 4. Analyze (Shell Command)
    log("Analyzing Data (Word Count)...")
    # wc is not in DANGEROUS_COMMANDS, so this should run without confirmation
    wc_res = registry.execute("shell.run", {"command": f"wc -w {dest_file}"})
    if wc_res["success"]:
        count = wc_res["result"].strip().split()[0]
        log(f"Word Count: {count}")
    else:
        log(f"Analysis Failed: {wc_res['error']}")
        count = "Unknown"
        
    # 5. Generate Report
    log("Generating Report...")
    report_content = f"""
# Mission Report
Date: {time.ctime()}

## System Status
- CPU: {usage['cpu']}%
- RAM: {usage['ram']}%
- Disk Free: {disk['free'] // (1024**3)} GB

## Data Analysis
- Source: {target_url}
- Status: Downloaded
- Word Count: {count}
"""
    registry.execute("file.write", {"path": "report.md", "content": report_content})
    log("Report saved to 'report.md'")
    
    # Verify Report
    verify = registry.execute("file.read", {"path": "report.md"})
    if "Mission Report" in verify["result"]:
        log("✅ Mission Complete & Verified")
    else:
        log("❌ Verification Failed")

except Exception as e:
    log(f"❌ CRITICAL ERROR: {e}")
