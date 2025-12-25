import time
import sys
from rich.console import Console

console = Console()

def simulate_typing(text: str, speed: float = 0.005):
    """Simulate typing effect for text output.
    
    Args:
        text: Text to print
        speed: Delay between characters in seconds (default: 0.005 for fast typing)
    """
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        if speed > 0:
            time.sleep(speed)
    sys.stdout.write("\n")
