from textual.color import Color

class NovaPalette:
    """Nova Design System Colors."""
    
    # Colors
    PRIMARY = "#00aeff"      # Nova Blue (Electric)
    SECONDARY = "#0077cc"    # Darker Blue
    ACCENT = "#00ff9d"       # Cyber Green (Success)
    WARNING = "#ffb700"      # Amber
    ERROR = "#ff0055"        # Neon Red
    BACKGROUND = "#0a0a12"   # Deep Space Black
    SURFACE = "#151520"      # Panel Background
    BORDER = "#2a2a35"       # Subtle Border
    TEXT = "#e0e0e0"         # Off-white
    TEXT_DIM = "#808090"     # Dimmed text

    CSS = f"""
    Screen {{
        background: {BACKGROUND};
        color: {TEXT};
    }}

    Header {{
        background: {SURFACE};
        color: {PRIMARY};
        dock: top;
        height: 1;
        border-bottom: solid {BORDER};
    }}

    Footer {{
        background: {SURFACE};
        color: {TEXT_DIM};
        dock: bottom;
        height: 1;
        border-top: solid {BORDER};
    }}

    .glow {{
        color: {PRIMARY};
        text-style: bold;
    }}
    
    #main_container {{
        layout: grid;
        grid-size: 2;
        grid-columns: 2fr 1fr;
    }}
    
    /* Panels */
    .panel {{
        background: {SURFACE};
        border: solid {BORDER};
        padding: 1;
        margin: 1;
    }}
    
    .panel:focus {{
        border: solid {PRIMARY};
    }}
    
    /* Input */
    Input {{
        background: {SURFACE};
        border: solid {BORDER};
        color: {TEXT};
    }}
    
    Input:focus {{
        border: solid {PRIMARY};
    }}
    """
