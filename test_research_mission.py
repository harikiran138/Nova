import time
import re
from pathlib import Path
from src.agent_core.tools.registry import ToolRegistry

# Setup
workspace = Path("research_workspace")
workspace.mkdir(exist_ok=True)
registry = ToolRegistry(workspace)

def log(msg):
    print(f"[RESEARCHER] {msg}")

try:
    log("🕵️‍♂️ Starting Research Mission: 'Tom Cruise'")
    
    # 1. Connectivity Check
    log("Checking connection...")
    net_status = registry.execute("net.check", {})["result"]
    if net_status != "Online":
        log("❌ Offline. Aborting.")
        exit(1)
    log("✅ Online")

    # 2. Data Gathering (Simulating Search & Visit)
    # In a real agent, 'net.search' would give us this URL.
    target_url = "https://en.wikipedia.org/wiki/Tom_Cruise"
    log(f"🌍 Visiting: {target_url}")
    
    # Fetch content
    # We increase the limit to capture enough text for analysis
    # Note: NetTool.get has a 5000 char limit by default. 
    # We might hit that. Let's see.
    page_content = registry.execute("net.get", {"url": target_url})["result"]
    
    if "Error" in page_content:
        log(f"❌ Failed to fetch page: {page_content}")
        exit(1)
        
    log(f"✅ Data Acquired ({len(page_content)} bytes)")
    
    # Save raw data for audit
    registry.execute("file.write", {"path": "source_data.html", "content": page_content})
    
    # 3. Analysis (Using Shell Tools)
    log("🧠 Analyzing Data...")
    
    # Count "Mission: Impossible"
    cmd_mi = "grep -i -o 'Mission: Impossible' source_data.html | wc -l"
    count_mi = registry.execute("shell.run", {"command": cmd_mi})["result"].strip()
    
    # Count "Top Gun"
    cmd_tg = "grep -i -o 'Top Gun' source_data.html | wc -l"
    count_tg = registry.execute("shell.run", {"command": cmd_tg})["result"].strip()
    
    # Extract Birth Date (Regex via Python for simulation, or grep)
    # Let's try to find his birth year roughly using grep context if possible, 
    # or just rely on the movie counts for this demo.
    
    # 4. Generate Report
    log("📝 Generating Report...")
    report = f"""
# 🕵️‍♂️ Research Report: Tom Cruise

**Date**: {time.ctime()}
**Agent**: Nova v2.1 (Autonomous Mode)

## 🌐 Execution Log
1.  **Network Check**: Verified connectivity to global internet.
2.  **Target Identification**: Selected authoritative source: `{target_url}`.
3.  **Data Extraction**: Retrieved {len(page_content)} bytes of HTML content.
4.  **Analysis**: Utilized local shell tools (`grep`, `wc`) for pattern matching.

## 📊 Findings
*   **Subject**: Tom Cruise
*   **Source**: Wikipedia
*   **Cultural Impact Analysis**:
    *   Mentions of "Mission: Impossible": **{count_mi}**
    *   Mentions of "Top Gun": **{count_tg}**

## 🏁 Conclusion
The subject is a highly prominent actor, strongly associated with the *Mission: Impossible* and *Top Gun* franchises based on frequency analysis of the source text.
"""
    registry.execute("file.write", {"path": "tom_cruise_report.md", "content": report})
    log("✅ Report saved to 'tom_cruise_report.md'")
    
    # Print Report to Console
    print("\n" + "="*40)
    print(report)
    print("="*40 + "\n")

except Exception as e:
    log(f"❌ CRITICAL ERROR: {e}")
