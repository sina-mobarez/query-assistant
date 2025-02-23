from openai import OpenAI
from typing import Optional
import sqlparse
from config import Config


class NLPToSQL:
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)

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

    def generate_sql(self, natural_query: str, db) -> Optional[str]:
        """Convert natural language to SQL using OpenAI"""
        schema = self.get_table_schema(db)

        prompt = f"""Given the following database schema:

{schema}

Convert this natural language query to SQL:
"{natural_query}"

Requirements:
- Use valid PostgreSQL syntax
- Return only the SQL query without any explanation
- Ensure the query is efficient and properly formatted
- Include appropriate JOINs and WHERE clauses
- Use proper date functions for time-based queries

SQL Query:"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a SQL expert. Generate only SQL queries without any explanation or additional text.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=500,
            )

            sql = response.choices[0].message.content.strip()
            formatted_sql = sqlparse.format(
                sql, reindent=True, keyword_case="upper", indent_width=4
            )
            return formatted_sql

        except Exception as e:
            print(f"Error generating SQL: {str(e)}")
            return None
