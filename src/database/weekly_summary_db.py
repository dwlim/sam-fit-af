"""Database operations for weekly_summary table."""

import psycopg2
from psycopg2.extras import execute_values
from typing import Dict, Any
from .config import DB_PARAMS
from dataclasses import asdict
import json


class WeeklySummaryDB:
    def __init__(self, db_params: Dict[str, Any] = DB_PARAMS):
        self.db_params = db_params
    
    def _get_connection(self):
        return psycopg2.connect(**self.db_params)

    def create_weekly_summary_table(self):
        """Create weekly_summary table and indexes if they don't exist."""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS weekly_summary (
            -- Identification
            summary_id VARCHAR(100),
            athlete_id INTEGER NOT NULL,
            start_date TIMESTAMP NOT NULL,
            end_date TIMESTAMP NOT NULL,
            
            -- Basic Metrics
            total_duration_seconds FLOAT,
            total_duration_formatted VARCHAR(20),
            total_distance_meters FLOAT,
            total_distance_formatted VARCHAR(20),
            num_sessions INTEGER,

            -- Sport-specific duration metrics
            num_sessions_cycling INTEGER,
            num_sessions_running INTEGER,
            num_sessions_swimming INTEGER,
            total_duration_cycling_seconds FLOAT,
            total_duration_running_seconds FLOAT,
            total_duration_swimming_seconds FLOAT,
            total_duration_cycling_formatted VARCHAR(20),
            total_duration_running_formatted VARCHAR(20),
            total_duration_swimming_formatted VARCHAR(20),
            
            -- Training Load
            total_training_load FLOAT,
            time_in_hr_zones JSONB,  -- Store zone times as JSON object
            time_in_hr_zones_formatted JSONB,  -- Store zone times as JSON object
            time_in_power_zones JSONB,  -- Store zone times as JSON object
            time_in_power_zones_formatted JSONB,  -- Store zone times as JSON object

            -- Sport specific training load metrics
            total_training_load_cycling FLOAT,
            total_training_load_running FLOAT,
            total_training_load_swimming FLOAT,

            time_in_hr_zones_cycling JSONB,
            time_in_hr_zones_running JSONB,
            time_in_hr_zones_swimming JSONB,
            time_in_hr_zones_cycling_formatted JSONB,
            time_in_hr_zones_running_formatted JSONB,
            time_in_hr_zones_swimming_formatted JSONB,
            
            time_in_power_zones_cycling JSONB,
            time_in_power_zones_running JSONB,
            time_in_power_zones_cycling_formatted JSONB,
            time_in_power_zones_running_formatted JSONB,
            
            -- Performance Metrics
            best_5k_time FLOAT,
            best_5k_formatted VARCHAR(20),
            best_10k_time FLOAT,
            best_10k_formatted VARCHAR(20),
            
            -- VO2max Tracking
            vo2max_start FLOAT,
            vo2max_end FLOAT,
            vo2max_change FLOAT,
            vo2max_min FLOAT,
            vo2max_max FLOAT,
            
            -- Training Phase
            training_phase VARCHAR(50),
            
            -- Metadata
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            -- Ensure we only have one summary per athlete per week
            UNIQUE(athlete_id, start_date)
        );

        -- Create indexes for common queries
        CREATE INDEX IF NOT EXISTS idx_weekly_summary_athlete 
        ON weekly_summary (athlete_id, start_date DESC);

        CREATE INDEX IF NOT EXISTS idx_weekly_summary_date 
        ON weekly_summary (start_date);
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(create_table_sql)
            conn.commit()

    def upsert_weekly_summary(self, summary: Dict[str, Any]) -> None:
        """Insert or update a weekly summary in the database.
        
        Args:
            summary: Dictionary containing the weekly summary data to upsert
        """
        # Convert dictionary fields to JSON strings for JSONB columns
        summary_dict = asdict(summary).copy()  # Make a copy to avoid modifying the original
        jsonb_columns = [
            'time_in_hr_zones',
            'time_in_power_zones',
            'time_in_hr_zones_formatted',
            'time_in_power_zones_formatted',
            'time_in_hr_zones_cycling',
            'time_in_hr_zones_running',
            'time_in_hr_zones_swimming',
            'time_in_hr_zones_cycling_formatted',
            'time_in_hr_zones_running_formatted',
            'time_in_hr_zones_swimming_formatted',
            'time_in_power_zones_cycling',
            'time_in_power_zones_running',
            'time_in_power_zones_cycling_formatted',
            'time_in_power_zones_running_formatted'
        ]
        for column in jsonb_columns:
            if column in summary_dict:
                summary_dict[column] = json.dumps(summary_dict[column])

        columns = summary_dict.keys()
        values = [summary_dict[column] for column in columns]
        
        upsert_sql = f"""
        INSERT INTO weekly_summary ({', '.join(columns)})
        VALUES %s
        ON CONFLICT (athlete_id, start_date) DO UPDATE SET
        {', '.join(f"{col} = EXCLUDED.{col}" for col in columns 
                  if col not in ['athlete_id', 'start_date'])};
        """
        
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    execute_values(cur, upsert_sql, [values])
            conn.commit()
        except Exception as e:
            print(f"Error upserting weekly summary: {e}")
            raise

    def add_column(self, column_name: str, column_type: str, default_value: Any = None) -> None:
        """Add a new column to the weekly_summary table if it doesn't exist.
        
        Args:
            column_name: Name of the new column
            column_type: SQL type of the new column (e.g., 'FLOAT', 'VARCHAR(50)', 'JSONB')
            default_value: Optional default value for the column
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                # Check if column exists
                cur.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'weekly_summary' 
                    AND column_name = %s;
                """, (column_name,))
                
                if not cur.fetchone():
                    # Column doesn't exist, so add it
                    sql = f"ALTER TABLE weekly_summary ADD COLUMN {column_name} {column_type}"
                    if default_value is not None:
                        sql += f" DEFAULT {default_value}"
                    cur.execute(sql)
                    print(f"Added column {column_name} to weekly_summary table")
                else:
                    print(f"Column {column_name} already exists in weekly_summary table")
            conn.commit() 

    def update_column_values(self, column_name: str, value: Any, where_clause: str = None) -> None:
        """Update values in a specific column for existing rows.
        
        Args:
            column_name: Name of the column to update
            value: Value to set
            where_clause: Optional WHERE clause to filter which rows to update
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                sql = f"UPDATE weekly_summary SET {column_name} = %s"
                if where_clause:
                    sql += f" WHERE {where_clause}"
                
                cur.execute(sql, (value,))
                rows_updated = cur.rowcount
                print(f"Updated {rows_updated} rows in column {column_name}")
            conn.commit() 