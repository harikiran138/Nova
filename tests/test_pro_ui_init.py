import sys
import os
from pathlib import Path

# Add project root to path (so 'src' is importable)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_ui_instantiation():
    print("🎨 Testing Pro UI Instantiation...")
    
    try:
        from ui.nova_tui import NovaApp
        from ui.widgets.dashboard_widgets import VisionPanel, SystemMonitor
        from ui.theme_manager import ThemeManager
        from agent_core.config import Config
        
        # Test 1: Check Imports
        print("[PASS] Imports successful.")
        
        # Test 2: Check Widget Composition
        config = Config.from_env()
        app = NovaApp(config)
        
        # We can't easily run app.compose() without a full Textual app context,
        # but we can check if the methods exist.
        if hasattr(app, "handle_agent_event"):
             print("[PASS] handle_agent_event method exists.")
             
        # Test 3: Theme Manager CSS
        tm = ThemeManager(Path("/tmp"))
        css = tm.get_css()
        if ".vision-panel" in css and "#main_container" in css:
             print("[PASS] CSS generation includes new dashboard classes.")
        else:
             print("[FAIL] CSS generation missing dashboard classes.")
             
        # Test 4: Dashboard Widgets
        vp = VisionPanel()
        sm = SystemMonitor()
        print("[PASS] Dashboard widgets instantiated.")
        
    except ImportError as e:
        print(f"[FAIL] Import Error: {e}")
    except Exception as e:
        print(f"[FAIL] Error: {e}")

if __name__ == "__main__":
    test_ui_instantiation()
