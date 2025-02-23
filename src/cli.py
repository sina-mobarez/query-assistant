import typer
from typing import Dict, List, Optional
from rich.console import Console
from rich.table import Table
from database import Database

console = Console()
app = typer.Typer()


def display_result(results: Optional[List[Dict]]):
    """Display query results in a formatted table."""
    if not results:
        console.print("[red]No results or error occurred[/red]")
        return

    if isinstance(results, list) and len(results) > 0:
        table = Table(show_header=True, header_style="bold blue")

        for key in results[0].keys():
            table.add_column(str(key))

        for row in results:
            table.add_row(*[str(value) for value in row.values()])

        console.print(table)


@app.command()
def query(
    sql: str = typer.Option(..., "--sql", "-s", help="SQL query to execute"),
    save: bool = typer.Option(False, "--save", "-S", help="Save query results to file"),
):
    """Execute SQL query and display results."""
    db = Database()

    try:
        results = db.execute_query(sql)
        display_result(results)

        if save and results:
            import json
            from datetime import datetime

            filename = f"query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, "w") as f:
                json.dump(results, f, indent=2, default=str)
            console.print(f"[green]Results saved to {filename}[/green]")

    finally:
        db.disconnect()
