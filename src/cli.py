from typing import Dict, List, Optional
from rich.console import Console
from rich.table import Table

console = Console()


def display_result(results: Optional[List[Dict]]):
    """Display query results in a formatted table."""
    if not results:
        console.print("[red]No results or error occurred[/red].")
        return
    
    if isinstance(results, list) and len(results) > 0:
        table = Table(show_header=True, header_style="bold blue")
        
        for key in results[0].keys():
            table.add_column(str(key))

        for row in results:
            table.add_row(*[str(value) for value in row.values()])

        console.print(table)

