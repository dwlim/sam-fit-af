"""Database operations for activities table."""

import psycopg2
from psycopg2.extras import execute_values
from typing import List, Dict, Any
from datetime import datetime
from .config import DB_PARAMS

class ActivityDB:
    def __init__(self, db_params: Dict[str, Any] = DB_PARAMS):
        self.db_params = db_params
    
    def _get_connection(self):
        return psycopg2.connect(**self.db_params)

    def create_activities_table(self):
        """Create activities table and indexes if they don't exist."""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS activities (
            -- Basic Identification
            activity_id BIGINT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            device_id VARCHAR(50),
            data_source VARCHAR(50),

            -- Activity Metadata
            start_time TIMESTAMP NOT NULL,
            activity_type VARCHAR(50),
            has_splits BOOLEAN,

            -- Duration Metrics
            duration FLOAT,
            moving_time FLOAT,
            elapsed_time FLOAT,

            -- Distance and Speed
            distance FLOAT,
            average_speed FLOAT,
            max_speed FLOAT,
            average_grade_adjusted_speed FLOAT,

            -- Heart Rate Data
            average_heart_rate FLOAT,
            max_heart_rate FLOAT,
            hr_time_z1_seconds FLOAT,
            hr_time_z2_seconds FLOAT,
            hr_time_z3_seconds FLOAT,
            hr_time_z4_seconds FLOAT,
            hr_time_z5_seconds FLOAT,

            -- Power Data
            average_power FLOAT,
            max_power FLOAT,
            power_time_z1_seconds FLOAT,
            power_time_z2_seconds FLOAT,
            power_time_z3_seconds FLOAT,
            power_time_z4_seconds FLOAT,
            power_time_z5_seconds FLOAT,

            -- Cadence
            average_cadence FLOAT,
            max_cadence FLOAT,

            -- Elevation Data
            elevation_gain FLOAT,
            elevation_loss FLOAT,
            min_elevation FLOAT,
            max_elevation FLOAT,

            -- Temperature
            average_temperature FLOAT,
            max_temperature FLOAT,

            -- Split Times
            fastest_split_1_mile FLOAT,
            fastest_split_1k FLOAT,
            fastest_split_5k FLOAT,
            fastest_split_10k FLOAT,
            split_summaries JSONB,

            -- Training Effect and Load
            training_effect_label VARCHAR(50),
            aerobic_training_effect FLOAT,
            anaerobic_training_effect FLOAT,
            aerobic_training_effect_message TEXT,
            anaerobic_training_effect_message TEXT,
            activity_training_load FLOAT,
            vo2_max FLOAT,

            -- Intensity Minutes
            moderate_intensity_minutes FLOAT,
            vigorous_intensity_minutes FLOAT,

            -- Energy
            calories FLOAT,

            -- Metadata
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fit_file_path VARCHAR(255),
            fit_file_downloaded_at TIMESTAMP
        );

        -- Create indexes for common queries
        CREATE INDEX IF NOT EXISTS idx_activities_user_time 
        ON activities (user_id, start_time DESC);

        CREATE INDEX IF NOT EXISTS idx_activities_type 
        ON activities (activity_type);

        CREATE INDEX IF NOT EXISTS idx_activities_date 
        ON activities (start_time);

        -- Create index for power activities
        CREATE INDEX IF NOT EXISTS idx_activities_power 
        ON activities (user_id, average_power) 
        WHERE average_power IS NOT NULL;

        -- Create index for heart rate data
        CREATE INDEX IF NOT EXISTS idx_activities_hr 
        ON activities (user_id, average_heart_rate) 
        WHERE average_heart_rate IS NOT NULL;
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(create_table_sql)
            conn.commit()

    def upsert_activities(self, activities: List[Dict[str, Any]]) -> None:
        """Insert or update multiple activities in the database."""
        if not activities:
            return

        columns = activities[0].keys()
        values = [[activity[column] for column in columns] for activity in activities]
        
        upsert_sql = f"""
        INSERT INTO activities ({', '.join(columns)})
        VALUES %s
        ON CONFLICT (activity_id) DO UPDATE SET
        {', '.join(f"{col} = EXCLUDED.{col}" for col in columns if col != 'activity_id')};
        """
        
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    execute_values(cur, upsert_sql, values)
                conn.commit()
        except Exception as e:
            print(f"Error upserting activities: {e}")
            raise 

    def add_column(self, column_name: str, column_type: str, default_value: Any = None) -> None:
        """Add a new column to the activities table if it doesn't exist.
        
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
                    WHERE table_name = 'activities' 
                    AND column_name = %s;
                """, (column_name,))
                
                if not cur.fetchone():
                    # Column doesn't exist, so add it
                    sql = f"ALTER TABLE activities ADD COLUMN {column_name} {column_type}"
                    if default_value is not None:
                        sql += f" DEFAULT {default_value}"
                    cur.execute(sql)
                    print(f"Added column {column_name} to activities table")
                else:
                    print(f"Column {column_name} already exists in activities table")
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
                sql = f"UPDATE activities SET {column_name} = %s"
                if where_clause:
                    sql += f" WHERE {where_clause}"
                
                cur.execute(sql, (value,))
                rows_updated = cur.rowcount
                print(f"Updated {rows_updated} rows in column {column_name}")
            conn.commit()
