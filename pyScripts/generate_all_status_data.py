#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import sys
import io

# 设置输出编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def main():
    print("开始生成模拟数据...")
    
    # 生成产线状态数据
    print("\n=== 生成产线状态数据 ===")
    result = subprocess.run(
        ["python", "pyScripts/generate_production_line_status.py"],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    print(result.stdout)
    if result.stderr:
        print("错误:", result.stderr)
    
    # 生成设备状态数据
    print("\n=== 生成设备状态数据 ===")
    result = subprocess.run(
        ["python", "pyScripts/generate_equipment_status.py"],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    print(result.stdout)
    if result.stderr:
        print("错误:", result.stderr)
    
    print("\n所有模拟数据生成完成！")

if __name__ == "__main__":
    main()
