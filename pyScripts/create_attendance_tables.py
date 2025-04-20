#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import mysql.connector
from mysql.connector import Error
import sys
import io

# 设置输出编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def get_db_connection():
    """获取数据库连接"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='mwYgR7#*X2',  # 请根据实际情况修改密码
            database='industry_db',
            charset='utf8mb4',
            use_unicode=True
        )
        return connection
    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'数据库连接失败: {str(e)}'
        }, ensure_ascii=False))
        exit(1)

def create_attendance_tables(drop_existing=False):
    """创建打卡记录表和请假记录表"""
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # 如果需要，删除现有表
        if drop_existing:
            cursor.execute("DROP TABLE IF EXISTS attendance_records")
            cursor.execute("DROP TABLE IF EXISTS leave_requests")

        # 创建打卡记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance_records (
                id INT AUTO_INCREMENT PRIMARY KEY,
                employee_id VARCHAR(20) NOT NULL COMMENT '员工工号',
                check_in_time DATETIME COMMENT '上班打卡时间',
                check_out_time DATETIME COMMENT '下班打卡时间',
                date DATE NOT NULL COMMENT '日期',
                status ENUM('正常', '迟到', '早退', '缺勤') DEFAULT '正常' COMMENT '考勤状态',
                notes TEXT COMMENT '备注',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_employee_id (employee_id),
                INDEX idx_date (date)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='打卡记录表'
        """)

        # 创建请假记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leave_requests (
                id INT AUTO_INCREMENT PRIMARY KEY,
                employee_id VARCHAR(20) NOT NULL COMMENT '员工工号',
                leave_type ENUM('事假', '病假', '年假', '其他') NOT NULL COMMENT '请假类型',
                start_date DATE NOT NULL COMMENT '开始日期',
                end_date DATE NOT NULL COMMENT '结束日期',
                reason TEXT COMMENT '请假原因',
                status ENUM('待审批', '已批准', '已拒绝', '已取消') DEFAULT '待审批' COMMENT '请假状态',
                approver_id VARCHAR(20) COMMENT '审批人工号',
                approval_time DATETIME COMMENT '审批时间',
                approval_notes TEXT COMMENT '审批备注',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_employee_id (employee_id),
                INDEX idx_status (status)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='请假记录表'
        """)

        # 修改用户表，添加状态字段（如果不存在）
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.columns
            WHERE table_schema = 'industry_db'
            AND table_name = 'users'
            AND column_name = 'status'
        """)

        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                ALTER TABLE users
                ADD COLUMN status VARCHAR(20) DEFAULT 'active' COMMENT '员工状态'
            """)

        connection.commit()
        print(json.dumps({
            'success': True,
            'message': '打卡记录表和请假记录表创建成功'
        }, ensure_ascii=False))

    except Error as e:
        print(json.dumps({
            'success': False,
            'error': f'创建表时出错: {str(e)}'
        }, ensure_ascii=False))
        if connection:
            connection.rollback()
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    # 检查是否有命令行参数
    drop_existing = False
    if len(sys.argv) > 1 and sys.argv[1] == '--drop':
        drop_existing = True

    create_attendance_tables(drop_existing)
