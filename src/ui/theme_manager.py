import json
from pathlib import Path
from typing import Dict, Any

class ThemeManager:
    """Manages UI themes."""
    
    def __init__(self, themes_dir: Path):
        self.themes_dir = themes_dir
        self.themes: Dict[str, Dict] = {}
        self.current_theme = "nova_blue"
        self.load_themes()
        
    def load_themes(self):
        """Load all JSON themes from the themes directory."""
        if not self.themes_dir.exists():
            return
            
        for file in self.themes_dir.glob("*.json"):
            try:
                data = json.loads(file.read_text())
                self.themes[file.stem] = data
            except Exception as e:
                print(f"Failed to load theme {file}: {e}")
                
    def get_theme(self, name: str) -> Dict:
        """Get raw theme data."""
        return self.themes.get(name, self.themes.get("nova_blue"))

    def get_css(self) -> str:
        """Generate CSS variables for the current theme."""
        theme = self.get_theme(self.current_theme)
        if not theme: return ""
        
        c = theme["colors"]
        
        return f"""
    /* CSS Variables */
    $primary: {c['primary']};
    $secondary: {c['secondary']};
    $accent: {c['accent']};
    $warning: {c['warning']};
    $error: {c['error']};
    $background: {c['background']};
    $surface: {c['surface']};
    $border: {c['border']};
    $text: {c['text']};
    $text-dim: {c['text_dim']};
    
    Screen {{
        background: $background;
        color: $text;
    }}

    Horizontal {{
        height: 100%;
    }}
    
    #main_container {{
        height: 100%;
    }}

    #chat_area {{
        width: 50%;
    }}

    #plan_panel {{
        width: 25%;
    }}

    #tool_panel {{
        width: 25%;
    }}
    
    /* Common Styles using Variables */
    .panel {{
        background: $surface;
        border: solid $border;
        padding: 1;
    }}
    
    .panel:focus {{
        border: solid $primary;
    }}
    
    Input {{
        background: $surface;
        border: solid $border;
        color: $text;
    }}
    
    Input:focus {{
        border: solid $primary;
    }}
    
    .header {{
        color: $primary;
        text-style: bold;
        border-bottom: solid $border;
    }}

    /* StatusBar Styles */
    StatusBar {{
        dock: bottom;
        height: 1;
        background: $surface;
        color: $text-dim;
        layout: horizontal;
    }}
    
    .status-item {{
        padding: 0 1;
        min-width: 10;
    }}
    
    .sandbox-safe {{
        color: $accent;
        text-style: bold;
    }}
    
    .sandbox-unsafe {{
        color: $error;
        text-style: bold;
    }}
    
    /* Dashboard Layout */
    #main_container {{
        layout: grid;
        grid-size: 2;
        grid-columns: 2fr 1fr;
    }}
    
    /* Right Column Panels */
    .monitor-panel, .vision-panel, .memory-panel {{
        background: $surface;
        border: solid $border;
        margin-bottom: 1;
        height: auto;
    }}
    
    .header-small {{
        background: $border;
        color: $accent;
        text-style: bold;
        padding: 0 1;
        width: 100%;
    }}
    
    /* Monitor */
    .monitor-row {{
        height: 3;
        align-vertical: middle;
        padding: 0 1;
    }}
    .label {{ width: 10; color: $text-dim; }}
    Digits {{ color: $primary; }}
    
    /* Vision */
    .vision-content {{
        padding: 1;
        color: $secondary;
    }}
    
    /* Memory */
    .memory-log {{
        height: 1fr;
        border-top: solid $border;
        background: $background;
        color: $text-dim;
    }}
    """
    
    def cycle_theme(self) -> str:
        """Switch to the next available theme."""
        names = list(self.themes.keys())
        if not names: return self.current_theme
        
        try:
            idx = names.index(self.current_theme)
            next_idx = (idx + 1) % len(names)
            self.current_theme = names[next_idx]
        except ValueError:
            self.current_theme = names[0]
            
        return self.current_theme