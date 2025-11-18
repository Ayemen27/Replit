"""
Database Tools
Execute SQL queries safely
"""

import sqlite3
import os
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class DatabaseTools:
    """
    Database operations toolkit
    
    Tools:
    - execute_sql: Execute SQL queries safely
    """
    
    def __init__(self):
        pass
    
    def execute_sql(
        self,
        query: str,
        database: str = "sqlite",
        params: Optional[tuple] = None,
        fetch: bool = True
    ) -> Dict:
        """
        Execute SQL query safely
        
        Args:
            query: SQL query to execute
            database: Database type (sqlite, postgresql)
            params: Query parameters (for prepared statements)
            fetch: Whether to fetch results (SELECT queries)
        
        Returns:
            Dict with 'success', 'rows', 'affected', and optional 'error'
        """
        try:
            database = database.lower()
            
            if database == "sqlite":
                return self._execute_sqlite(query, params, fetch)
            elif database in ["postgresql", "postgres", "pg"]:
                return self._execute_postgresql(query, params, fetch)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported database type: {database}"
                }
        
        except Exception as e:
            logger.error(f"Error executing SQL: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query[:100]
            }
    
    def _execute_sqlite(
        self,
        query: str,
        params: Optional[tuple],
        fetch: bool
    ) -> Dict:
        """Execute SQLite query"""
        # Use state database from cache manager
        from pathlib import Path
        db_path = Path("data/state.db")
        
        # Ensure data directory exists
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with sqlite3.connect(str(db_path)) as conn:
                cursor = conn.cursor()
                
                # Execute query
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                # Fetch results if SELECT
                if fetch and query.strip().upper().startswith("SELECT"):
                    rows = cursor.fetchall()
                    columns = [desc[0] for desc in cursor.description] if cursor.description else []
                    
                    # Convert to list of dicts
                    result_rows = [
                        dict(zip(columns, row))
                        for row in rows
                    ]
                    
                    return {
                        "success": True,
                        "database": "sqlite",
                        "rows": result_rows,
                        "count": len(result_rows),
                        "columns": columns
                    }
                else:
                    # For INSERT, UPDATE, DELETE
                    affected = cursor.rowcount
                    conn.commit()
                    
                    return {
                        "success": True,
                        "database": "sqlite",
                        "affected": affected,
                        "message": f"Query executed, {affected} rows affected"
                    }
        
        except sqlite3.Error as e:
            logger.error(f"SQLite error: {e}")
            return {
                "success": False,
                "error": f"SQLite error: {str(e)}",
                "database": "sqlite"
            }
    
    def _execute_postgresql(
        self,
        query: str,
        params: Optional[tuple],
        fetch: bool
    ) -> Dict:
        """Execute PostgreSQL query"""
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            
            # Get connection details from environment
            connection_params = {
                "host": os.getenv("PGHOST", "localhost"),
                "port": int(os.getenv("PGPORT", "5432")),
                "database": os.getenv("PGDATABASE", "postgres"),
                "user": os.getenv("PGUSER", "postgres"),
                "password": os.getenv("PGPASSWORD", "")
            }
            
            with psycopg2.connect(**connection_params, cursor_factory=RealDictCursor) as conn:
                with conn.cursor() as cursor:
                    # Execute query
                    if params:
                        cursor.execute(query, params)
                    else:
                        cursor.execute(query)
                    
                    # Fetch results if SELECT
                    if fetch and query.strip().upper().startswith("SELECT"):
                        rows = cursor.fetchall()
                        
                        # Convert RealDictRow to regular dicts
                        result_rows = [dict(row) for row in rows]
                        columns = list(result_rows[0].keys()) if result_rows else []
                        
                        return {
                            "success": True,
                            "database": "postgresql",
                            "rows": result_rows,
                            "count": len(result_rows),
                            "columns": columns
                        }
                    else:
                        # For INSERT, UPDATE, DELETE
                        affected = cursor.rowcount
                        conn.commit()
                        
                        return {
                            "success": True,
                            "database": "postgresql",
                            "affected": affected,
                            "message": f"Query executed, {affected} rows affected"
                        }
        
        except ImportError:
            return {
                "success": False,
                "error": "psycopg2 not installed. Install with: pip install psycopg2-binary"
            }
        
        except Exception as e:
            logger.error(f"PostgreSQL error: {e}")
            return {
                "success": False,
                "error": f"PostgreSQL error: {str(e)}",
                "database": "postgresql"
            }


# Convenience function
_db_tools = DatabaseTools()

def execute_sql(
    query: str,
    database: str = "sqlite",
    params: Optional[tuple] = None,
    fetch: bool = True
) -> Dict:
    """Execute SQL query"""
    return _db_tools.execute_sql(query, database, params, fetch)
