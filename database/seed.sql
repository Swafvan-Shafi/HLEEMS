-- Seed Data for HLEEMS (v3)

USE hleems_db;

-- Insert Extensive Hostel Blocks
INSERT INTO hostel_block (block_id, block_name, capacity) VALUES 
('MLH', 'MLH', 200),
('LH_1', 'LH Block 1', 100),
('LH_2', 'LH Block 2', 100),
('LH_3', 'LH Block 3', 100),
('LH_4', 'LH Block 4', 100),
('MBH1', 'MBH1', 250),
('MBH2_A', 'MBH2 - A', 100),
('MBH2_B', 'MBH2 - B', 100),
('MBH2_C', 'MBH2 - C', 100),
('MBH2_D', 'MBH2 - D', 100),
('MBH2_E', 'MBH2 - E', 100),
('MBH2_F', 'MBH2 - F', 100),
('MBH2_G', 'MBH2 - G', 100),
('HOSTEL_A', 'A Hostel', 300),
('HOSTEL_B', 'B Hostel', 300),
('HOSTEL_C', 'C Hostel', 300);

-- Insert Dummy Users
INSERT INTO users (id, password_hash, role) VALUES 
('admin1', 'DUMMYHASH_OVERWRITTEN', 'admin'),
('war_001', 'DUMMYHASH_OVERWRITTEN', 'warden'),
('stu_001', 'DUMMYHASH_OVERWRITTEN', 'student'),
('stu_002', 'DUMMYHASH_OVERWRITTEN', 'student');

-- Insert Warden
INSERT INTO warden (warden_id, name, email, phone, block_id) VALUES 
('war_001', 'Alice Warden', 'alice@hleems.com', '555-1234', 'MLH');

-- Insert Student
INSERT INTO student (student_id, name, email, room_number, phone, block_id) VALUES 
('stu_001', 'Bob Student', 'bob@hleems.com', '101', '555-9876', 'MLH'),
('stu_002', 'Charlie Requestor', 'charlie@hleems.com', '102', '555-3333', 'MLH');

-- Add Dummy request so Warden sees immediately
INSERT INTO permission_request (student_id, request_type, entry_date, entry_time, reason, status)
VALUES ('stu_002', 'late_entry', '2026-05-01', '21:30:00', 'Train delayed', 'pending');
