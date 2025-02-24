import requests
import sqlparse
import re
from typing import Optional, List
from config import Config


class QueryExample:
    def __init__(self, natural_query: str, sql_query: str):
        self.natural_query = natural_query.strip()
        self.sql_query = sqlparse.format(
            sql_query.strip(), reindent=True, keyword_case="upper", indent_width=4
        )

    @classmethod
    def from_gist(cls, content: str) -> List["QueryExample"]:
        """Parse gist file content into query examples"""
        examples = []

        blocks = re.split(r"\n\s*\n", content)

        for block in blocks:
            if not block.strip():
                continue

            parts = block.split("\n", 1)
            if len(parts) != 2:
                continue

            natural_query = parts[0].strip("- ").strip()
            sql_query = parts[1].strip()

            if not natural_query or not sql_query:
                continue

            examples.append(cls(natural_query, sql_query))

        return examples


class NLPToSQL:
    def __init__(self):
        self.ollama_url = Config.OLLAMA_URL
        self.examples: List[QueryExample] = []

    def load_examples(self, file_path: str) -> bool:
        """Load query examples from a gist file"""
        try:
            with open(file_path, "r") as f:
                content = f.read()
            self.examples = QueryExample.from_gist(content)
            return len(self.examples) > 0
        except Exception as e:
            print(f"Error loading examples: {str(e)}")
            return False

    def get_table_schema(self, db) -> str:
        """Get database schema for context"""
        schema_query = """
        SELECT 
            table_name,
            array_agg(column_name || ' ' || data_type) as columns
        FROM information_schema.columns
        WHERE table_schema = 'public'
        GROUP BY table_name;
        """
        results = db.execute_query(schema_query)
        if not results:
            return ""

        schema_text = "Database Schema:\n"
        for table in results:
            schema_text += f"\nTable: {table['table_name']}\n"
            schema_text += "Columns: " + ", ".join(table["columns"]) + "\n"

        return schema_text

    def calculate_similarity(self, query: str, example: QueryExample) -> float:
        """Calculate similarity score between query and example"""
        query_words = set(query.lower().split())
        example_words = set(example.natural_query.lower().split())

        if not query_words or not example_words:
            return 0.0
        intersection = len(query_words & example_words)
        union = len(query_words | example_words)
        return intersection / union if union > 0 else 0.0

    def get_relevant_examples(
        self, query: str, max_examples: int = 3
    ) -> List[QueryExample]:
        """Get most relevant examples for the given query"""

        scored_examples = [
            (self.calculate_similarity(query, example), example)
            for example in self.examples
        ]

        scored_examples.sort(key=lambda x: x[0], reverse=True)
        return [
            example for score, example in scored_examples[:max_examples] if score > 0
        ]

    def call_ollama(self, prompt: str) -> Optional[str]:
        """Make API call to Ollama"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": "gemma:2b",
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.1, "top_p": 0.9},
                },
            )
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            print(f"Error calling Ollama API: {str(e)}")
            return None

    def generate_sql(self, natural_query: str, db) -> Optional[str]:
        """Convert natural language to SQL using Ollama with examples"""
        schema = self.get_table_schema(db)
        relevant_examples = self.get_relevant_examples(natural_query)

        examples_text = ""
        if relevant_examples:
            examples_text = "\nHere are some example queries:\n\n"
            for ex in relevant_examples:
                examples_text += f"Natural Query: {ex.natural_query}\n"
                examples_text += f"SQL Query: {ex.sql_query}\n\n"

        prompt = f"""You are a SQL expert. Convert natural language queries to valid PostgreSQL SQL queries.
Given this database schema:

{schema}
{examples_text}
Convert this natural language query to SQL:
"{natural_query}"

Requirements:
- Return only the PostgreSQL SQL query without any explanation or additional text
- Use proper table joins and WHERE clauses
- Ensure efficient query performance
- Use appropriate date functions for time-based queries
- Follow the style of the example queries when applicable

SQL Query:"""

        try:
            response = self.call_ollama(prompt)
            if not response:
                return None

            sql = response.strip()
            sql = sql.replace("```sql", "").replace("```", "").strip()

            formatted_sql = sqlparse.format(
                sql, reindent=True, keyword_case="upper", indent_width=4
            )
            return formatted_sql

        except Exception as e:
            print(f"Error generating SQL: {str(e)}")
            return None
