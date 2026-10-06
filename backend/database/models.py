# MySQL schema — incidents table
SCHEMA = """
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