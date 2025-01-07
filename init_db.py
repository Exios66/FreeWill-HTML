import sqlite3
import os
from pathlib import Path

# Create data directory if it doesn't exist
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

# Database paths
DB_PATH = data_dir / "survey_responses.db"

def init_db():
    """Initialize the database with proper schema"""
    print(f"Initializing database at {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create responses table with proper schema
    c.execute('''
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            responses TEXT NOT NULL,
            scores TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create indices for better query performance
    c.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON responses(timestamp)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON responses(created_at)')
    
    # Create views for easy analysis
    c.execute('''
        CREATE VIEW IF NOT EXISTS response_stats AS
        SELECT 
            COUNT(*) as total_responses,
            MIN(timestamp) as first_response,
            MAX(timestamp) as last_response,
            COUNT(*) * 1.0 / (
                JULIANDAY(MAX(timestamp)) - JULIANDAY(MIN(timestamp)) + 1
            ) as responses_per_day
        FROM responses
    ''')
    
    conn.commit()
    print("Database initialized successfully!")
    
    # Create empty CSV file if it doesn't exist
    csv_path = data_dir / "survey_responses.csv"
    if not csv_path.exists():
        csv_path.touch()
        print(f"Created empty CSV file at {csv_path}")
    
    conn.close()

if __name__ == "__main__":
    init_db() 