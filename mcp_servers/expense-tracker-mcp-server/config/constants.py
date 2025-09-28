import os
from fastmcp import FastMCP


mcp = FastMCP("Expense_Tracker_2025")

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DB_PATH = os.path.join(BASE_DIR, "db", "expenses.db")
CATEGORIES_PATH = os.path.join(BASE_DIR, "config", "categories.json")