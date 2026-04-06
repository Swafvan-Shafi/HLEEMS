-- HLEEMS Database Schema (Updated v4)
-- Strict 3NF, Security, referential integrity with explicit PKs

DROP DATABASE IF EXISTS hleems_db;
CREATE DATABASE hleems_db;
USE hleems_db;

-- Base Users table (Authenticates everyone securely)
CREATE TABLE users (
    id VARCHAR(50) PRIMARY KEY,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('student', 'warden', 'admin') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Hostel Block (Hierarchy expanded)
CREATE TABLE hostel_block (
    block_id VARCHAR(50) PRIMARY KEY,
    block_name VARCHAR(100) NOT NULL,
    capacity INT DEFAULT 0
) ENGINE=InnoDB;

-- Warden table 
CREATE TABLE warden (
    warden_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    phone VARCHAR(20),
    block_id VARCHAR(50),
    FOREIGN KEY (warden_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (block_id) REFERENCES hostel_block(block_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- Student table
CREATE TABLE student (
    student_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    room_number VARCHAR(20) NOT NULL,
    phone VARCHAR(20),
    block_id VARCHAR(50) NOT NULL,
    late_warning_sent BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (block_id) REFERENCES hostel_block(block_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- Permission Request for Entry/Exit (V3: Split temporal fields)
CREATE TABLE permission_request (
    request_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL,
    request_type ENUM('late_entry', 'exit') NOT NULL,
    entry_date DATE DEFAULT NULL,
    entry_time TIME DEFAULT NULL,
    exit_time TIME DEFAULT NULL, 
    reentry_time TIME DEFAULT NULL,
    reason TEXT NOT NULL,
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    warden_id VARCHAR(50) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE,
    FOREIGN KEY (warden_id) REFERENCES warden(warden_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- Entry Records
CREATE TABLE entry_record (
    record_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL,
    entry_time DATETIME NOT NULL,
    is_late BOOLEAN DEFAULT FALSE,
    recorded_by VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE,
    FOREIGN KEY (recorded_by) REFERENCES warden(warden_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- Exit Records
CREATE TABLE exit_record (
    record_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL,
    exit_time DATETIME NOT NULL,
    recorded_by VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE,
    FOREIGN KEY (recorded_by) REFERENCES warden(warden_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- Indexes for performance
CREATE INDEX idx_student_id ON permission_request(student_id);
CREATE INDEX idx_warden_id ON permission_request(warden_id);
CREATE INDEX idx_entry_student ON entry_record(student_id);
CREATE INDEX idx_exit_student ON exit_record(student_id);
