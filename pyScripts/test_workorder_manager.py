import subprocess
import json
import datetime

def run_command(command):
    """运行命令并返回结果"""
    print(f"执行命令: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
    
    if result.returncode != 0:
        print(f"命令执行失败，返回码: {result.returncode}")
        print(f"错误输出: {result.stderr}")
        return None
    
    try:
        # 尝试解析JSON输出
        output = result.stdout.strip()
        json_result = json.loads(output)
        return json_result
    except json.JSONDecodeError:
        # 如果不是JSON格式，返回原始输出
        return result.stdout.strip()

def test_create_table():
    """测试创建工单表"""
    result = run_command(["python", "pyScripts/workorder_manager.py", "create-table"])
    print(f"创建工单表结果: {result}")
    print("-" * 50)

def test_add_workorder():
    """测试添加工单"""
    # 创建一个设备维护工单
    maintenance_data = {
        "task_type": "设备维护",
        "task_details": "数控车床XX-001出现异常噪音，需要检修",
        "start_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "deadline": (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
        "creator": "admin",
        "foreman": "foreman1",
        "team": "1",
        "production_line": "1",
        "extension_fields": {
            "发现时间": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "设备": "数控车床XX-001"
        }
    }
    
    result = run_command([
        "python", "pyScripts/workorder_manager.py", "add", 
        "--data", json.dumps(maintenance_data, ensure_ascii=False)
    ])
    
    if result and result.get('success'):
        print(f"添加设备维护工单成功，工单编号: {result.get('workorder_number')}")
        maintenance_workorder = result.get('workorder_number')
    else:
        print("添加设备维护工单失败")
        maintenance_workorder = None
    
    # 创建一个产线巡检工单
    inspection_data = {
        "task_type": "产线巡检",
        "task_details": "对1号产线进行例行巡检",
        "start_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "deadline": (datetime.datetime.now() + datetime.timedelta(hours=4)).strftime("%Y-%m-%d %H:%M:%S"),
        "creator": "foreman1",
        "foreman": "foreman1",
        "team": "1",
        "production_line": "1",
        "extension_fields": {}
    }
    
    result = run_command([
        "python", "pyScripts/workorder_manager.py", "add", 
        "--data", json.dumps(inspection_data, ensure_ascii=False)
    ])
    
    if result and result.get('success'):
        print(f"添加产线巡检工单成功，工单编号: {result.get('workorder_number')}")
        inspection_workorder = result.get('workorder_number')
    else:
        print("添加产线巡检工单失败")
        inspection_workorder = None
    
    # 创建一个排班任务工单
    scheduling_data = {
        "task_type": "排班任务",
        "task_details": "安排工人操作数控车床XX-001进行零件加工",
        "start_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "deadline": (datetime.datetime.now() + datetime.timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
        "creator": "foreman1",
        "foreman": "foreman1",
        "team": "1",
        "production_line": "1",
        "extension_fields": {
            "设备": "数控车床XX-001"
        }
    }
    
    result = run_command([
        "python", "pyScripts/workorder_manager.py", "add", 
        "--data", json.dumps(scheduling_data, ensure_ascii=False)
    ])
    
    if result and result.get('success'):
        print(f"添加排班任务工单成功，工单编号: {result.get('workorder_number')}")
        scheduling_workorder = result.get('workorder_number')
    else:
        print("添加排班任务工单失败")
        scheduling_workorder = None
    
    print("-" * 50)
    return maintenance_workorder, inspection_workorder, scheduling_workorder

def test_update_workorder(workorder_number):
    """测试更新工单"""
    if not workorder_number:
        print("没有可用的工单编号，跳过更新测试")
        return
    
    update_data = {
        "status": "进行中",
        "team_members": "worker1,worker2",
        "actual_end_time": None
    }
    
    result = run_command([
        "python", "pyScripts/workorder_manager.py", "update", 
        "--number", workorder_number,
        "--data", json.dumps(update_data, ensure_ascii=False)
    ])
    
    if result and result.get('success'):
        print(f"更新工单成功，工单编号: {result.get('workorder_number')}")
    else:
        print("更新工单失败")
    
    print("-" * 50)

def test_get_workorder(workorder_number):
    """测试获取单个工单"""
    if not workorder_number:
        print("没有可用的工单编号，跳过获取测试")
        return
    
    result = run_command([
        "python", "pyScripts/workorder_manager.py", "get", 
        "--number", workorder_number
    ])
    
    if result and result.get('success'):
        print(f"获取工单成功:")
        workorder = result.get('data')
        print(f"工单编号: {workorder.get('workorder_number')}")
        print(f"任务类型: {workorder.get('task_type')}")
        print(f"任务详情: {workorder.get('task_details')}")
        print(f"状态: {workorder.get('status')}")
        print(f"扩展字段: {workorder.get('extension_fields')}")
    else:
        print("获取工单失败")
    
    print("-" * 50)

def test_list_workorders():
    """测试获取工单列表"""
    # 获取所有工单
    result = run_command([
        "python", "pyScripts/workorder_manager.py", "list"
    ])
    
    if result and result.get('success'):
        workorders = result.get('data')
        print(f"获取工单列表成功，共 {len(workorders)} 条工单")
    else:
        print("获取工单列表失败")
    
    # 按类型筛选
    result = run_command([
        "python", "pyScripts/workorder_manager.py", "list",
        "--type", "设备维护"
    ])
    
    if result and result.get('success'):
        workorders = result.get('data')
        print(f"获取设备维护工单成功，共 {len(workorders)} 条工单")
    else:
        print("获取设备维护工单失败")
    
    print("-" * 50)

def test_stats():
    """测试获取工单统计信息"""
    result = run_command([
        "python", "pyScripts/workorder_manager.py", "stats"
    ])
    
    if result and result.get('success'):
        stats = result.get('data')
        print(f"获取工单统计信息成功:")
        print(f"总工单数: {stats.get('total')}")
        print(f"今日新增: {stats.get('today_count')}")
        print(f"本周工单: {stats.get('week_count')}")
        
        print("按状态统计:")
        for item in stats.get('status_stats', []):
            print(f"  {item.get('status')}: {item.get('count')}")
        
        print("按类型统计:")
        for item in stats.get('type_stats', []):
            print(f"  {item.get('task_type')}: {item.get('count')}")
    else:
        print("获取工单统计信息失败")
    
    print("-" * 50)

def test_delete_workorder(workorder_number):
    """测试删除工单"""
    if not workorder_number:
        print("没有可用的工单编号，跳过删除测试")
        return
    
    result = run_command([
        "python", "pyScripts/workorder_manager.py", "delete", 
        "--number", workorder_number
    ])
    
    if result and result.get('success'):
        print(f"删除工单成功，工单编号: {result.get('workorder_number')}")
    else:
        print("删除工单失败")
    
    print("-" * 50)

def main():
    print("开始测试工单管理工具...")
    
    # 创建工单表
    test_create_table()
    
    # 添加工单
    maintenance_workorder, inspection_workorder, scheduling_workorder = test_add_workorder()
    
    # 更新工单
    if maintenance_workorder:
        test_update_workorder(maintenance_workorder)
    
    # 获取单个工单
    if maintenance_workorder:
        test_get_workorder(maintenance_workorder)
    
    # 获取工单列表
    test_list_workorders()
    
    # 获取工单统计信息
    test_stats()
    
    # 删除工单（可选，取消注释以测试删除功能）
    # if scheduling_workorder:
    #     test_delete_workorder(scheduling_workorder)
    
    print("测试完成")

if __name__ == "__main__":
    main()
