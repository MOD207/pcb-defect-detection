CREATE DATABASE pcb_inspection;
USE pcb_inspection;

CREATE TABLE inspections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    original_filename VARCHAR(255),
    result_filename VARCHAR(255),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE detections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspection_id INT,
    defect_class VARCHAR(50),
    confidence FLOAT,
    FOREIGN KEY (inspection_id) REFERENCES inspections(id)
);