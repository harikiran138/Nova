import time
from pathlib import Path
from src.agent_core.tools.registry import ToolRegistry

registry = ToolRegistry(Path("."))

def log(msg):
    print(f"[TEST] {msg}")

try:
    # 1. Start Session
    log("Starting Kali Session...")
    res = registry.execute("kali.start_session", {})
    log(res)
    
    # 2. Check initial state (nmap should be missing)
    log("Checking for nmap (expect missing)...")
    res = registry.execute("kali.nmap", {"target": "localhost", "args": "-V"})
    log(res)
    
    # 3. Install nmap
    log("Installing nmap (this may take a while)...")
    # We use a small package 'iputils-ping' or 'nmap' if network is fast.
    # nmap is about 20MB. Should be fine.
    res = registry.execute("kali.install", {"packages": "nmap"})
    log(f"Install Output: {res[-100:]}") # Last 100 chars
    
    # 4. Run nmap again
    log("Running nmap (expect success)...")
    res = registry.execute("kali.nmap", {"target": "127.0.0.1", "args": "-p 80"})
    log(res)
    
    # 5. Stop Session
    log("Stopping Session...")
    res = registry.execute("kali.stop_session", {})
    log(res)

except Exception as e:
    log(f"ERROR: {e}")
    # Cleanup
    registry.execute("kali.stop_session", {})
