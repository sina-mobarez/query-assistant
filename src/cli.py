from datetime import datetime
import json
from pathlib import Path
import threading
import time
import typer
from typing import Dict, List, Optional
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax
from rich.prompt import Confirm
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.styles import Style
from database import Database
from history import QueryHistory
from nlp import NLPToSQL

console = Console()
app = typer.Typer()
query_history = QueryHistory()


class CLI:
    def __init__(self):
        self.db = Database()
        self.nlp = NLPToSQL()
        self._stop_animation = False

        examples_path = Path("../examples.gist")
        if examples_path.exists():
            if self.nlp.load_examples(examples_path):
                console.print("[green]Loaded query examples successfully[/green]")
            else:
                console.print("[yellow]No valid query examples found[/yellow]")

    def process_natural_query(self, query: str) -> Optional[str]:
        """Process natural language query and return SQL"""
        self._stop_animation = False
        animation_thread = threading.Thread(target=self._show_thinking_animation)
        animation_thread.daemon = True
        animation_thread.start()
        try:
            sql = self.nlp.generate_sql(query, self.db)
            
            self._stop_animation = True
            animation_thread.join()
            if sql:
                console.print("\n[bold blue]Generated SQL:[/bold blue]")
                console.print(Syntax(sql, "sql", theme="monokai"))

                if Confirm.ask("Execute this SQL query?"):
                    return sql
            return None
        except Exception as e:
            self._stop_animation = True
            animation_thread.join()
            console.print(f"[red]Error: {str(e)}[/red]")
            return None
        
    def _show_thinking_animation(self):
            """Display a thinking animation while waiting for the model response"""
            with console.status("[bold blue]Thinking...[/bold blue]", spinner="dots") as status:
                while not self._stop_animation:
                    time.sleep(0.1)
                    

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

    cli = CLI()
    if not cli.db.connect():
        console.print("[red]Failed to connect to database[/red]")
        return

    session = PromptSession(
        history=InMemoryHistory(),
        style=Style.from_dict(
            {
                "prompt": "ansicyan bold",
            }
        ),
    )

    console.print(
        "[bold green]Welcome to PostgreSQL Interactive CLI with NLP![/bold green]"
    )
    console.print("Enter SQL queries, natural language queries, or special commands:")
    console.print("  [blue]\\q[/blue] - Quit")
    console.print("  [blue]\\h[/blue] - Show query history")
    console.print("  [blue]\\c[/blue] - Clear screen")
    console.print("\nTip: Start your query with '?' to use natural language processing")

    try:
        while True:
            try:
                user_input = session.prompt(" > ")

                if user_input.lower() in ("\\q", "quit", "exit"):
                    break
                elif user_input.lower() in ("\\h", "history"):
                    display_query_history()
                    continue
                elif user_input.lower() in ("\\c", "clear"):
                    console.clear()
                    continue
                elif not user_input.strip():
                    continue

                if user_input.startswith("?"):
                    natural_query = user_input[1:].strip()
                    sql = cli.process_natural_query(natural_query)
                    if not sql:
                        continue
                else:
                    sql = user_input

                results = cli.db.execute_query(sql)
                success = results is not None
                query_history.add_query(sql, success)

                if success:
                    display_result(results)
                    console.print("[dim]Query executed successfully[/dim]")

            except KeyboardInterrupt:
                continue
            except EOFError:
                break
            except Exception as e:
                console.print(f"[red]Error: {str(e)}[/red]")
                query_history.add_query(user_input, False)

    finally:
        cli.db.disconnect()
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
