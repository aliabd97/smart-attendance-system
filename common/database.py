"""
Database helper utilities for SQLite operations
Provides common database functionality for all services
"""

import sqlite3
from typing import List, Dict, Optional, Any
from datetime import datetime


class Database:
    """
    SQLite database helper with common operations
    """

    def __init__(self, db_path: str):
        """
        Initialize database connection

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.connection = None
        self._connect()

    def _connect(self):
        """Establish database connection"""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row  # Return rows as dictionaries
            print(f"✅ Connected to database: {self.db_path}")
        except Exception as e:
            print(f"❌ Failed to connect to database: {e}")
            raise

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """
        Execute a SQL query

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Cursor object
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            return cursor
        except Exception as e:
            print(f"❌ Database error: {e}")
            self.connection.rollback()
            raise

    def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict]:
        """
        Fetch a single row

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Dictionary of row data or None
        """
        cursor = self.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None

    def fetch_all(self, query: str, params: tuple = ()) -> List[Dict]:
        """
        Fetch all rows

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            List of dictionaries
        """
        cursor = self.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def insert(self, table: str, data: Dict) -> int:
        """
        Insert a row into a table

        Args:
            table: Table name
            data: Dictionary of column:value pairs

        Returns:
            Last inserted row ID
        """
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        cursor = self.execute(query, tuple(data.values()))
        return cursor.lastrowid

    def update(self, table: str, data: Dict, where: str, where_params: tuple = ()) -> int:
        """
        Update rows in a table

        Args:
            table: Table name
            data: Dictionary of column:value pairs to update
            where: WHERE clause (without the WHERE keyword)
            where_params: Parameters for WHERE clause

        Returns:
            Number of affected rows
        """
        set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {where}"
        params = tuple(data.values()) + where_params
        cursor = self.execute(query, params)
        return cursor.rowcount

    def delete(self, table: str, where: str, where_params: tuple = ()) -> int:
        """
        Delete rows from a table

        Args:
            table: Table name
            where: WHERE clause (without the WHERE keyword)
            where_params: Parameters for WHERE clause

        Returns:
            Number of deleted rows
        """
        query = f"DELETE FROM {table} WHERE {where}"
        cursor = self.execute(query, where_params)
        return cursor.rowcount

    def create_table(self, schema: str):
        """
        Create a table from SQL schema

        Args:
            schema: CREATE TABLE SQL statement
        """
        self.execute(schema)
        print(f"✅ Table created successfully")

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("✅ Database connection closed")
