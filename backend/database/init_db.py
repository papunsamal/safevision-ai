import mysql.connector
from mysql.connector import Error
from ..config import settings
from ..utils.logger import get_logger

logger = get_logger("db_init")

def create_tables_if_not_exists():
    """
    Connects to MySQL and creates 'incidents' and 'daily_stats' tables 
    if they don't already exist. This makes the project 'Plug-and-Play'.
    """
    try:
        # 1. Connect to Server (not specific DB yet)
        conn = mysql.connector.connect(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD
        )
        
        if conn.is_connected():
            cursor = conn.cursor()
            
            # 2. Create Database if not exists
            db_name = settings.MYSQL_DB
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            logger.info(f"✅ Database '{db_name}' ensured.")
            
            # Switch to the database
            cursor.execute(f"USE {db_name}")
            
            # 3. Create 'incidents' Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS incidents (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    type VARCHAR(50) NOT NULL, -- PPE, FIRE, SMOKE
                    severity VARCHAR(20) NOT NULL, -- HIGH, CRITICAL, MEDIUM
                    message TEXT NOT NULL,
                    camera VARCHAR(50),
                    zone VARCHAR(100),
                    worker_id INT,
                    frame_url VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_type_created (type, created_at)
                ) ENGINE=InnoDB;
            """)
            logger.info("✅ Table 'incidents' ensured.")

            # 4. Create 'daily_stats' Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_stats (
                    stat_date DATE PRIMARY KEY,
                    total_workers INT DEFAULT 0,
                    compliant_workers INT DEFAULT 0,
                    ppe_violations INT DEFAULT 0,
                    fire_incidents INT DEFAULT 0,
                    smoke_incidents INT DEFAULT 0
                ) ENGINE=InnoDB;
            """)
            logger.info("✅ Table 'daily_stats' ensured.")
            
            # 5. Create 'alert_cooldowns' Table (For Dedup Logic)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alert_cooldowns (
                    cooldown_key VARCHAR(255) PRIMARY KEY, -- e.g., CAM-01_NO_HELMET_Worker5
                    last_triggered TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP
                ) ENGINE=InnoDB;
            """)
            logger.info("✅ Table 'alert_cooldowns' ensured.")

            conn.commit()
            print("\n🎉 DATABASE SETUP COMPLETE! All tables are ready.\n")
            
    except Error as e:
        print(f"\n❌ DATABASE ERROR: {e}\n")
        logger.error(f"DB Init Failed: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    create_tables_if_not_exists()