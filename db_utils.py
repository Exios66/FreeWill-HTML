from pathlib import Path
import sqlite3
import pandas as pd
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DB_DIR = Path("data")
DB_PATH = DB_DIR / "survey_responses.db"
CSV_PATH = DB_DIR / "survey_responses.csv"
BACKUP_DIR = DB_DIR / "backups"

# Ensure directories exist
DB_DIR.mkdir(exist_ok=True)
BACKUP_DIR.mkdir(exist_ok=True)

class DatabaseManager:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Create and return a database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        """Initialize database with enhanced schema."""
        try:
            with self.get_connection() as conn:
                conn.executescript('''
                    CREATE TABLE IF NOT EXISTS responses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        responses TEXT NOT NULL,
                        scores TEXT NOT NULL,
                        metadata TEXT NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        version INTEGER DEFAULT 1
                    );

                    CREATE INDEX IF NOT EXISTS idx_timestamp ON responses(timestamp);
                    CREATE INDEX IF NOT EXISTS idx_created_at ON responses(created_at);
                    
                    CREATE TRIGGER IF NOT EXISTS update_responses_timestamp 
                    AFTER UPDATE ON responses
                    BEGIN
                        UPDATE responses SET updated_at = DATETIME('now') 
                        WHERE id = NEW.id;
                    END;
                ''')
                logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise

    def insert_response(self, data: Dict[str, Any]) -> int:
        """Insert a new survey response and return its ID."""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('''
                    INSERT INTO responses (timestamp, responses, scores, metadata)
                    VALUES (?, ?, ?, ?)
                ''', (
                    datetime.now().isoformat(),
                    json.dumps(data['responses']),
                    json.dumps(data['scores']),
                    json.dumps(data['metadata'])
                ))
                self.update_csv()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Failed to insert response: {e}")
            raise

    def get_response(self, response_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a specific response by ID."""
        try:
            with self.get_connection() as conn:
                result = conn.execute(
                    'SELECT * FROM responses WHERE id = ?', 
                    (response_id,)
                ).fetchone()
                if result:
                    return self._parse_response(dict(result))
                return None
        except Exception as e:
            logger.error(f"Failed to retrieve response {response_id}: {e}")
            raise

    def get_all_responses(self) -> List[Dict[str, Any]]:
        """Retrieve all responses with parsed JSON."""
        try:
            with self.get_connection() as conn:
                results = conn.execute('SELECT * FROM responses').fetchall()
                return [self._parse_response(dict(row)) for row in results]
        except Exception as e:
            logger.error(f"Failed to retrieve responses: {e}")
            raise

    def update_csv(self) -> None:
        """Update CSV export with enhanced error handling and backup."""
        try:
            # Create backup of existing CSV
            if CSV_PATH.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = BACKUP_DIR / f"survey_responses_{timestamp}.csv"
                CSV_PATH.rename(backup_path)

            # Generate new CSV
            responses = self.get_all_responses()
            if not responses:
                logger.info("No responses to export")
                return

            df = pd.DataFrame(responses)
            
            # Normalize nested JSON columns
            for col in ['responses', 'scores', 'metadata']:
                if col in df.columns:
                    normalized = pd.json_normalize(df[col].tolist())
                    normalized.columns = [f"{col}_{c}" for c in normalized.columns]
                    df = df.drop(columns=[col]).join(normalized)

            df.to_csv(CSV_PATH, index=False)
            logger.info(f"CSV export updated successfully: {CSV_PATH}")
        except Exception as e:
            logger.error(f"Failed to update CSV: {e}")
            raise

    def get_statistics(self) -> Dict[str, Any]:
        """Get enhanced statistics about survey responses."""
        try:
            with self.get_connection() as conn:
                stats = {
                    "total_responses": conn.execute(
                        "SELECT COUNT(*) FROM responses"
                    ).fetchone()[0],
                    "latest_response": conn.execute(
                        "SELECT MAX(timestamp) FROM responses"
                    ).fetchone()[0],
                    "responses_by_date": dict(conn.execute("""
                        SELECT date(timestamp) as date, COUNT(*) as count 
                        FROM responses 
                        GROUP BY date(timestamp)
                        ORDER BY date DESC
                    """).fetchall()),
                }

                if stats["total_responses"] > 0:
                    df = pd.read_sql_query(
                        "SELECT scores FROM responses", 
                        conn
                    )
                    scores = df['scores'].apply(json.loads)
                    stats["average_scores"] = {
                        category: scores.apply(
                            lambda x: x.get(category, 0)
                        ).mean()
                        for category in scores.iloc[0].keys()
                    }
                else:
                    stats["average_scores"] = {}

                return stats
        except Exception as e:
            logger.error(f"Failed to retrieve statistics: {e}")
            raise

    @staticmethod
    def _parse_response(row: Dict[str, Any]) -> Dict[str, Any]:
        """Parse JSON fields in a response row."""
        for field in ['responses', 'scores', 'metadata']:
            if field in row and isinstance(row[field], str):
                row[field] = json.loads(row[field])
        return row

    def backup_database(self) -> Path:
        """Create a timestamped backup of the database."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = BACKUP_DIR / f"survey_responses_{timestamp}.db"
            
            with self.get_connection() as conn:
                backup = sqlite3.connect(backup_path)
                conn.backup(backup)
                backup.close()
            
            logger.info(f"Database backup created: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Failed to create database backup: {e}")
            raise

# Create global instance
db_manager = DatabaseManager() 