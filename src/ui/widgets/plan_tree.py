from textual.widgets import Static
from rich.tree import Tree
from rich.text import Text

class PlanTree(Static):
    """Visualizes the agent's plan and decision tree."""
    
    DEFAULT_CSS = """
    PlanTree {
        background: $background;
        color: $text;
        padding: 1;
        border: solid $border;
    }
    """

    def on_mount(self):
        self.update_tree([])

    def update_task(self, task):
        """Update based on a Task object."""
        tree = Tree(Text(f"MISSION: {task.goal.upper()}", style="bold cyan"))
        
        for step in task.steps:
            status_icon = "✓" if step.status == "completed" else "▶" if step.status == "in_progress" else "○"
            color = "green" if step.status == "completed" else "yellow" if step.status == "in_progress" else "white"
            
            node = tree.add(Text(f"{status_icon} {step.description}", style=color))
            if step.tool:
                node.add(Text(f"🔧 {step.tool}", style="cyan dim"))
            if step.result:
                # Truncate result for tree view
                res_text = str(step.result)[:50] + "..." if len(str(step.result)) > 50 else str(step.result)
                node.add(Text(f"⮑ {res_text}", style="dim italic"))
            if step.error:
                node.add(Text(f"✗ ERROR: {step.error}", style="red bold"))
        
        self.update(tree)

    def update_tree(self, steps=None):
        """Update the visual tree of the plan (legacy compat)."""
        tree = Tree(Text("MISSION PLAN", style="bold cyan"))
        tree.add("[dim]Awaiting next task...[/dim]")
        self.update(tree)