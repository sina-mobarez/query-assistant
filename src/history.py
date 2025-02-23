import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict


class QueryHistory:
    def __init__(self):
        self.history_file = Path.home() / ".pgcli_history.json"
        self.load_history()

    def load_history(self):
        """Load query history from file."""
        if self.history_file.exists():
            try:
                with open(self.history_file) as f:
                    self.history = json.load(f)
            except json.JSONDecodeError:
                self.history = []
        else:
            self.history = []

    def save_history(self):
        """Save query history to file."""
        with self.history_file.open("w") as f:
            json.dump(self.history, f, indent=2)

    def add_query(self, query: str, success: bool):
        """Add a query to the history."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "success": success,
        }
        self.history.append(entry)
        self.save_history()

    def get_recent_queries(self, limit: int = 10) -> List[Dict]:
        """Get the most recent queries."""
        return self.history[-limit:]
