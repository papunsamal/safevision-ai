# MySQL schema — 2 tables

INCIDENTS_TABLE = """
CREATE TABLE IF NOT EXISTS incidents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    message VARCHAR(255) NOT NULL,
    camera VARCHAR(50),
    zone VARCHAR(100),
    worker_id INT,
    frame_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_type (type),
    INDEX idx_created (created_at)
) ENGINE=InnoDB
"""

DAILY_STATS_TABLE = """
CREATE TABLE IF NOT EXISTS daily_stats (
    stat_date DATE PRIMARY KEY,
    total_workers INT DEFAULT 0,
    compliant_workers INT DEFAULT 0,
    ppe_violations INT DEFAULT 0,
    fire_incidents INT DEFAULT 0,
    smoke_incidents INT DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB
"""