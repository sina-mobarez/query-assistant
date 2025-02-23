import requests
import sqlparse
from typing import Optional
from config import Config

class NLPToSQL:
    def __init__(self):
        self.ollama_url = Config.OLLAMA_URL
        
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
            schema_text += "Columns: " + ", ".join(table['columns']) + "\n"
        
        return schema_text

    def call_ollama(self, prompt: str) -> Optional[str]:
        """Make API call to Ollama"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": "gemma:2b",
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "top_p": 0.9
                    }
                }
            )
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            print(f"Error calling Ollama API: {str(e)}")
            return None

    def generate_sql(self, natural_query: str, db) -> Optional[str]:
        """Convert natural language to SQL using Ollama"""
        schema = self.get_table_schema(db)
        
        prompt = f"""You are a SQL expert. Your task is to convert natural language queries to valid PostgreSQL SQL queries.
Given this database schema:

{schema}

Convert this natural language query to SQL:
"{natural_query}"

Requirements:
- Return only the PostgreSQL SQL query without any explanation or additional text
- Use proper table joins and WHERE clauses
- Ensure efficient query performance
- Use appropriate date functions for time-based queries

SQL Query:"""

        try:
            response = self.call_ollama(prompt)
            if not response:
                return None


            sql = response.strip()

            sql = sql.replace("```sql", "").replace("```", "").strip()
            

            formatted_sql = sqlparse.format(
                sql,
                reindent=True,
                keyword_case='upper',
                indent_width=4
            )
            return formatted_sql
            
        except Exception as e:
            print(f"Error generating SQL: {str(e)}")
            return None