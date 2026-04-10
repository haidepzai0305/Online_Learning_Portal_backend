create database course_db;
use course_db;

CREATE TABLE courses (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    description TEXT,
    syllabus TEXT,
    professor_id BIGINT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_professor (professor_id),
    FULLTEXT INDEX ft_title_desc (title, description)
);

CREATE TABLE course_materials (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    course_id BIGINT,
    title VARCHAR(255),
    file_url VARCHAR(500),
    file_type VARCHAR(50),
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_course (course_id)
);

CREATE TABLE announcements (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    course_id BIGINT,
    title VARCHAR(255),
    content TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_course (course_id)
);