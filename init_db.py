from db_utils import db_manager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Initialize the database and create necessary directories."""
    try:
        # Database manager will automatically initialize the database
        logger.info("Database initialization complete")
        logger.info(f"Database location: {db_manager.db_path}")
        logger.info(f"CSV export location: {db_manager.CSV_PATH}")
        logger.info(f"Backup directory: {db_manager.BACKUP_DIR}")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

if __name__ == "__main__":
    main() 