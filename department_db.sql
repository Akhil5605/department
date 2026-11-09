-- department_db.sql
-- Complete MySQL database setup for Department Webpage

-- Drop database if exists (be careful with this in production)
-- DROP DATABASE IF EXISTS department_db;

-- Create database
CREATE DATABASE IF NOT EXISTS department_db;
USE department_db;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fullname VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create departments table (for future expansion)
CREATE TABLE IF NOT EXISTS departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample department data
INSERT INTO departments (name, description) VALUES 
('Engineering', 'Software and hardware engineering department'),
('Research', 'Research and development division'),
('Administration', 'Department administration and management');

-- Insert sample user (password: 'password123')
-- The hash is SHA-256 of 'password123'
INSERT INTO users (fullname, email, password_hash) 
VALUES ('Admin User', 'admin@dept.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f');

-- Show table structure
DESCRIBE users;

-- Show all users
SELECT * FROM users;

-- Show all departments
SELECT * FROM departments;

-- Query to check user login (example)
-- SELECT * FROM users WHERE email = 'admin@dept.com' AND password_hash = SHA2('password123', 256);