import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Optional
from config import Config


class Database:
    def __init__(self):
        self.conn = None

    def connect(self):
        """Establish a database connection"""
        try:
            self.conn = psycopg2.connect(
                Config.get_connection_string(), cursor_factory=RealDictCursor
            )
            return True
        except psycopg2.Error as e:
            print(f"Error connecting to the database: {e}")
            return False

    def disconnect(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()

    def execute_query(self, query: str) -> Optional[List[Dict]]:
        """Execute SQL query and return the results"""
        if not self.conn:
            if not self.connect():
                return None

        try:
            with self.conn.cursor() as cur:
                cur.execute(query)
                if cur.description:
                    results = cur.fetchall()
                    return [dict(row) for row in results]
                else:
                    self.conn.commit()
                    return [
                        {
                            "message": f"Query executed successfully. Rows affected: {cur.rowcount}"
                        }
                    ]

        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"Error executing query: {e}")
            return None
