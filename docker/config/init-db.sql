-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS industry_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE industry_db;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(64) NOT NULL,
    role VARCHAR(20) NOT NULL,
    phone VARCHAR(20),
    status ENUM('在岗', '请假', '离岗') DEFAULT '在岗',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    group_id INT NULL COMMENT '所属分组ID',
    employee_id VARCHAR(20) NULL COMMENT '工号'
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 设备表
CREATE TABLE IF NOT EXISTS equipment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    equipment_name VARCHAR(100) NOT NULL COMMENT '设备名称',
    equipment_code VARCHAR(50) NOT NULL UNIQUE COMMENT '设备编码',
    line_id VARCHAR(50) NOT NULL COMMENT '所属产线ID',
    equipment_type VARCHAR(50) COMMENT '设备类型',
    status VARCHAR(20) DEFAULT '正常' COMMENT '运行状态',
    worker_id VARCHAR(20) NULL COMMENT '负责工人的工号',
    description TEXT COMMENT '设备描述',
    location VARCHAR(100) COMMENT '设备位置',
    sensor_projects JSON COMMENT '传感器项目列表',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_line_id (line_id),
    INDEX idx_status (status),
    INDEX idx_worker_id (worker_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='设备静态信息表';

-- 设备状态表
CREATE TABLE IF NOT EXISTS equipment_status (
    id INT AUTO_INCREMENT PRIMARY KEY,
    equipment_id INT NOT NULL COMMENT '设备ID',
    runtime_hours FLOAT DEFAULT 0 COMMENT '运行时长(小时)',
    collection_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '数据采集时间',
    sensor_data JSON COMMENT '传感器实时数据',
    fault_probability FLOAT DEFAULT 0 COMMENT '估计故障概率',
    FOREIGN KEY (equipment_id) REFERENCES equipment(id) ON DELETE CASCADE,
    INDEX idx_equipment_id (equipment_id),
    INDEX idx_collection_time (collection_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='设备实时状态表';

-- 产线表
CREATE TABLE IF NOT EXISTS production_line (
    id INT AUTO_INCREMENT PRIMARY KEY,
    line_name VARCHAR(100) NOT NULL UNIQUE COMMENT '产线名称',
    equipment_list JSON COMMENT '包括的设备',
    theoretical_capacity FLOAT COMMENT '理论产能',
    status VARCHAR(20) DEFAULT '正常' COMMENT '运行状态',
    foreman_id VARCHAR(20) NULL COMMENT '负责工长工号',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_line_name (line_name),
    INDEX idx_status (status),
    INDEX idx_foreman_id (foreman_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='产线静态信息表';

-- 产线状态表
CREATE TABLE IF NOT EXISTS production_line_status (
    id INT AUTO_INCREMENT PRIMARY KEY,
    line_id INT NOT NULL COMMENT '产线ID',
    runtime_hours FLOAT DEFAULT 0 COMMENT '运行时长(小时)',
    collection_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '数据采集时间',
    current_capacity FLOAT DEFAULT 0 COMMENT '当前产能',
    efficiency FLOAT DEFAULT 0 COMMENT '效率(%)',
    environment_data JSON COMMENT '环境数据',
    FOREIGN KEY (line_id) REFERENCES production_line(id) ON DELETE CASCADE,
    INDEX idx_line_id (line_id),
    INDEX idx_collection_time (collection_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='产线实时状态表';

-- 工单表
CREATE TABLE IF NOT EXISTS workorders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_number VARCHAR(50) NOT NULL UNIQUE COMMENT '工单编号',
    title VARCHAR(100) NOT NULL COMMENT '工单标题',
    description TEXT COMMENT '工单描述',
    status ENUM('待分配', '进行中', '已完成', '已取消') DEFAULT '待分配' COMMENT '工单状态',
    priority ENUM('低', '中', '高', '紧急') DEFAULT '中' COMMENT '优先级',
    created_by VARCHAR(20) NOT NULL COMMENT '创建人工号',
    assigned_to VARCHAR(20) NULL COMMENT '分配给谁',
    group_id INT NULL COMMENT '分配给哪个班组',
    start_date DATE NULL COMMENT '开始日期',
    due_date DATE NULL COMMENT '截止日期',
    completed_date DATE NULL COMMENT '完成日期',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_status (status),
    INDEX idx_assigned_to (assigned_to),
    INDEX idx_group_id (group_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='工单表';

-- 考勤记录表
CREATE TABLE IF NOT EXISTS attendance_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id VARCHAR(20) NOT NULL COMMENT '员工工号',
    date DATE NOT NULL COMMENT '日期',
    check_in_time TIME NULL COMMENT '上班时间',
    check_out_time TIME NULL COMMENT '下班时间',
    status ENUM('正常', '迟到', '早退', '缺勤') DEFAULT '正常' COMMENT '考勤状态',
    notes TEXT COMMENT '备注',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY idx_employee_date (employee_id, date),
    INDEX idx_employee_id (employee_id),
    INDEX idx_date (date),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='考勤记录表';

-- 插入测试用户数据
INSERT IGNORE INTO users (username, password, role, phone, group_id, employee_id) VALUES 
('SP0001', '6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b', 'supervisor', '13800000001', 1, 'SP0001'),
('FM0002', '5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9', 'foreman', '13800000002', 2, 'FM0002'),
('WK0008', '5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9', 'member', '13800000008', 2, 'WK0008'),
('SF0009', '5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9', 'safety_officer', '13800000009', 3, 'SF0009');

-- 插入测试产线数据
INSERT IGNORE INTO production_line (line_name, theoretical_capacity, status, foreman_id) VALUES
('产线A', 100.0, '正常', 'FM0002'),
('产线B', 120.0, '正常', 'FM0002'),
('产线C', 90.0, '维护中', NULL);

-- 插入测试设备数据
INSERT IGNORE INTO equipment (equipment_name, equipment_code, line_id, equipment_type, status, worker_id, location) VALUES
('车床1号', 'EQ001', '1', '车床', '正常', 'WK0008', '车间A区'),
('铣床2号', 'EQ002', '1', '铣床', '正常', 'WK0008', '车间A区'),
('钻床3号', 'EQ003', '2', '钻床', '维修中', NULL, '车间B区'),
('磨床4号', 'EQ004', '2', '磨床', '正常', NULL, '车间B区'),
('车床5号', 'EQ005', '3', '车床', '停用', NULL, '车间C区');

-- 插入测试工单数据
INSERT IGNORE INTO workorders (order_number, title, description, status, priority, created_by, assigned_to, group_id, start_date, due_date) VALUES
('WO20250401001', '设备维修工单', '车床1号需要例行维护', '进行中', '中', 'SP0001', 'WK0008', 2, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 7 DAY)),
('WO20250401002', '产线调整工单', '产线B需要调整布局', '待分配', '高', 'SP0001', 'FM0002', 2, NULL, DATE_ADD(CURDATE(), INTERVAL 14 DAY)),
('WO20250401003', '安全检查工单', '车间A区安全隐患排查', '待分配', '紧急', 'SP0001', 'SF0009', 3, NULL, DATE_ADD(CURDATE(), INTERVAL 3 DAY));
