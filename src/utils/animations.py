
import time
import random
from rich.console import Console
from rich.live import Live
from rich.text import Text
from rich.spinner import Spinner
from rich.layout import Layout
from rich.panel import Panel

console = Console()

def run_matrix_rain(duration: int = 5):
    """
    Simulates a Matrix-style digital rain effect.
    """
    width = console.size.width
    height = console.size.height
    
    # Characters to use
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*"
    
    # Initialize columns
    columns = [random.randint(0, height) for _ in range(width)]
    
    start_time = time.time()
    
    with Live(console=console, refresh_per_second=20, screen=True) as live:
        while time.time() - start_time < duration:
            # Build the frame
            text = Text()
            
            # Create a grid of characters
            grid = [[" " for _ in range(width)] for _ in range(height)]
            
            for x in range(width):
                # Update column position
                if random.random() < 0.1:  # Chance to reset or move faster
                    columns[x] = 0 if columns[x] > height else columns[x] + 1
                else:
                    columns[x] = (columns[x] + 1) % (height + 5) # Allow to go off screen slightly
                
                # Draw the trail
                head = columns[x]
                for y in range(height):
                    if 0 <= head - y < 15: # Trail length
                        char = random.choice(chars)
                        if head - y == 0:
                            color = "white" # Head is white
                        elif head - y < 4:
                            color = "bright_green"
                        else:
                            color = "green"
                        
                        # We can't easily build a 2D grid with single Text object efficiently in this loop 
                        # without being slow in Python.
                        # Simplified approach: Just generate lines.
                        pass

            # Optimized approach for Python performance:
            # Generate random lines with green characters
            output_lines = []
            for _ in range(height):
                line = ""
                for _ in range(width):
                    if random.random() < 0.05:
                        line += f"[bright_green]{random.choice(chars)}[/bright_green]"
                    elif random.random() < 0.1:
                        line += f"[green]{random.choice(chars)}[/green]"
                    else:
                        line += " "
                output_lines.append(line)
            
            live.update(Text.from_markup("\n".join(output_lines)))
            time.sleep(0.05)

def run_matrix_rain_optimized(duration: int = 5):
    """
    Optimized Matrix rain using vertical columns logic.
    """
    import shutil
    cols, rows = shutil.get_terminal_size()
    
    # State for each column: (current_row, speed, chars)
    columns = []
    for _ in range(cols):
        columns.append({
            "y": random.randint(-rows, 0),
            "speed": random.uniform(0.5, 1.5),
            "chars": [random.choice("01") for _ in range(rows + 10)]
        })

    start_time = time.time()
    
    with Live(console=console, refresh_per_second=15, screen=True) as live:
        while time.time() - start_time < duration:
            text = Text()
            
            # We will construct the screen buffer
            buffer = [[" " for _ in range(cols)] for _ in range(rows)]
            
            for x, col in enumerate(columns):
                col["y"] += col["speed"]
                head_y = int(col["y"])
                
                if head_y > rows + 10:
                    col["y"] = random.randint(-10, -1)
                    col["speed"] = random.uniform(0.5, 1.5)
                    head_y = int(col["y"])
                
                # Draw trail
                for i in range(15): # Trail length
                    y_pos = head_y - i
                    if 0 <= y_pos < rows:
                        char = col["chars"][y_pos % len(col["chars"])]
                        if i == 0:
                            buffer[y_pos][x] = f"[white]{char}[/white]"
                        elif i < 3:
                            buffer[y_pos][x] = f"[bright_green]{char}[/bright_green]"
                        else:
                            buffer[y_pos][x] = f"[green]{char}[/green]"
            
            # Flatten buffer to string
            screen_content = ""
            for row in buffer:
                screen_content += "".join(row) + "\n"
                
            live.update(Text.from_markup(screen_content))
            time.sleep(0.05)

def run_spinner(text: str = "Processing...", duration: int = 5, style: str = "dots"):
    """
    Runs a high-quality spinner.
    """
    with Live(Spinner(style, text=f"[bold cyan]{text}[/bold cyan]"), refresh_per_second=20, transient=True):
        time.sleep(duration)

def run_pulse(text: str = "NOVA", duration: int = 5):
    """
    Displays pulsing text.
    """
    start_time = time.time()
    
    with Live(console=console, refresh_per_second=10, transient=True) as live:
        while time.time() - start_time < duration:
            for i in range(0, 101, 5): # Fade in
                color = f"rgb({int(2.55*i)},{int(2.55*i)},255)"
                live.update(Panel(f"[{color}]{text}[/{color}]", border_style=color))
                time.sleep(0.05)
            
            for i in range(100, -1, -5): # Fade out
                color = f"rgb({int(2.55*i)},{int(2.55*i)},255)"
                live.update(Panel(f"[{color}]{text}[/{color}]", border_style=color))
                time.sleep(0.05)

def run_system_scan(duration: int = 5):
    """
    Simulates a system scan with progress bars.
    """
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        transient=True
    ) as progress:
        task1 = progress.add_task("[cyan]Scanning Memory...", total=100)
        task2 = progress.add_task("[green]Verifying Integrity...", total=100, start=False)
        task3 = progress.add_task("[magenta]Optimizing Neural Pathways...", total=100, start=False)
        
        while not progress.finished:
            progress.update(task1, advance=random.uniform(0.5, 2))
            if progress.tasks[0].completed > 50:
                progress.start_task(task2)
                progress.update(task2, advance=random.uniform(0.5, 2.5))
            if progress.tasks[1].completed > 50:
                progress.start_task(task3)
                progress.update(task3, advance=random.uniform(0.5, 3))
            
            time.sleep(0.05)

if __name__ == "__main__":
    # Demo mode
    console.print("[bold]1. Matrix Rain[/bold]")
    run_matrix_rain_optimized(duration=3)
    
    console.print("[bold]2. Spinner[/bold]")
    run_spinner(duration=2)
    
    console.print("[bold]3. Pulse[/bold]")
    run_pulse(duration=3)
    
    console.print("[bold]4. System Scan[/bold]")
    run_system_scan(duration=3)
