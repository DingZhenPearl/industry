#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import subprocess
import sys

def test_update_equipment():
    """测试更新设备信息，包括传感器项目"""
    # 准备测试数据
    equipment_id = "6"  # 假设ID为6的设备存在
    equipment_data = {
        "equipment_name": "测试设备",
        "equipment_code": "TEST-001",
        "equipment_type": "测试类型",
        "line_id": "1",
        "sensor_projects": {
            "temperature": "温度",
            "pressure": "压力"
        }
    }
    
    # 将数据转换为JSON字符串
    data_json = json.dumps(equipment_data, ensure_ascii=False)
    
    # 构建命令
    cmd = [
        "python", 
        "pyScripts/update_equipment.py", 
        "--equipment-id", equipment_id, 
        "--data", data_json
    ]
    
    # 执行命令
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        print(result.stdout)
        if result.stderr:
            print("错误输出:", result.stderr)
    except Exception as e:
        print(f"执行命令时出错: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    test_update_equipment()
