"""Database initialization script.

Usage:
    python -m src.database.init_db
"""

import logging
from .activities_db import ActivityDB
from .weekly_summary_db import WeeklySummaryDB
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize database tables."""
    try:
        db = ActivityDB()
        logger.info("Creating activities table...")
        db.create_activities_table()
        logger.info("Activities table created successfully")

        db = WeeklySummaryDB()
        logger.info("Creating weekly_summary table...")
        db.create_weekly_summary_table()
        logger.info("Weekly summary table created successfully")

        # TODO: Create performance_benchmarks table
        # TODO: Create training_metadata table
        
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

if __name__ == "__main__":
    init_database() 