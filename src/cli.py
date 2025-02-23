from datetime import datetime
import json
import typer
from typing import Dict, List, Optional
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax
from rich.prompt import Confirm
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import Style
from pygments.lexers.sql import SqlLexer
from database import Database
from history import QueryHistory

console = Console()
app = typer.Typer()
query_history = QueryHistory()


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


def display_query_history():
    """Display recent query history"""
    recent_queries = query_history.get_recent_queries()

    if not recent_queries:
        console.print("[yellow]No query history found[/yellow]")
        return

    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Timestamp")
    table.add_column("Query")
    table.add_column("Status")

    for entry in recent_queries:
        status = "[green]Success[/green]" if entry["success"] else "[red]Failed[/red]"
        table.add_row(entry["timestamp"], entry["query"], status)

    console.print("\n[bold]Recent Query History:[/bold]")
    console.print(table)


def interactive_mode():
    """Interactive REPL mode"""

    db = Database()
    if not db.connect():
        console.print("[red]Unable to connect to database[/red]")
        return

    session = PromptSession(
        history=InMemoryHistory(),
        lexer=PygmentsLexer(SqlLexer),
        style=Style.from_dict(
            {
                "propmt": "ansicyan bold",
            }
        ),
    )

    console.print("[bold green]Welcome to Query Assistant ![/bold green]")
    console.print("Just ask me your question or special commands:")
    console.print("  [blue]\\q[/blue] - Quit")
    console.print("  [blue]\\h[/blue] - Show query history")
    console.print("  [blue]\\c[/blue] - Clear screen")

    try:
        while True:
            try:
                query = session.prompt("> ")

                if query.lower() in ("\\q", "quit", "exit"):
                    break
                elif query.lower() in ("\\h", "history"):
                    display_query_history()
                    continue
                elif query.lower() in ("\\c", "clear"):
                    console.clear()
                    continue
                elif not query.strip():
                    continue

                results = db.execute_query(query)
                success = results is not None
                query_history.add_query(query, success)

                if success:
                    display_result(results)

                    console.print("[dim]Query executed successfully[/dim]")

            except KeyboardInterrupt:
                continue
            except EOFError:
                break
            except Exception as e:
                console.print(f"[red]Error: {str(e)}[/red]")
                query_history.add_query(query, False)

    finally:
        db.disconnect()
        console.print("\nGoodbye!")


@app.command()
def run(
    sql: str = typer.Option(None, "--sql", "-s", help="SQL query to execute"),
    save: bool = typer.Option(False, "--save", help="Save query results to file"),
    interactive: bool = typer.Option(
        True, "--interactive", "-i", help="Run in interactive mode"
    ),
):
    """PostgreSQL CLI with interactive mode and query history"""
    if sql:
        db = Database()
        try:
            results = db.execute_query(sql)
            success = results is not None
            query_history.add_query(sql, success)
            display_result(results)

            if save and results:
                filename = (
                    f"query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                )
                with open(filename, "w") as f:
                    json.dump(results, f, indent=2)
                console.print(f"[green]Results saved to {filename}[/green]")

        finally:
            db.disconnect()
    elif interactive:
        interactive_mode()
    else:
        console.print("Please provide a SQL query or use interactive mode")
