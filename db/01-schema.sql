USE attendance;
CREATE TABLE sessions(session_id VARCHAR(128) COLLATE utf8mb4_bin PRIMARY KEY, expires INT UNSIGNED NOT NULL, data MEDIUMTEXT COLLATE utf8mb4_bin);
CREATE TABLE users (
 id INT PRIMARY KEY AUTO_INCREMENT, code VARCHAR(30) NOT NULL UNIQUE,
 name VARCHAR(100) NOT NULL, email VARCHAR(120) NOT NULL UNIQUE,
 password_hash VARCHAR(100) NOT NULL, role ENUM('admin','employee') NOT NULL DEFAULT 'employee',
 active BOOLEAN NOT NULL DEFAULT TRUE, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE shifts (
 id INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(80) NOT NULL UNIQUE,
 start_time TIME NOT NULL, end_time TIME NOT NULL,
 CHECK(end_time > start_time)
);
CREATE TABLE attendance (
 id INT PRIMARY KEY AUTO_INCREMENT, user_id INT NOT NULL, shift_id INT NOT NULL,
 work_date DATE NOT NULL, check_in DATETIME NOT NULL, check_out DATETIME NULL,
 UNIQUE KEY one_shift_per_day(user_id,shift_id,work_date),
 FOREIGN KEY(user_id) REFERENCES users(id), FOREIGN KEY(shift_id) REFERENCES shifts(id),
 CHECK(check_out IS NULL OR check_out >= check_in), INDEX(work_date)
);
