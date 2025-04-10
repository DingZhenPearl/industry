import subprocess
import json
import sys

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

def test_get_users():
    """测试获取用户列表"""
    result = run_command(["python", "pyScripts/user_data_operations.py", "get-users"])
    if result and result.get('success'):
        print("获取用户列表成功")
        print(f"用户数量: {len(result['data'])}")
    else:
        print("获取用户列表失败")
    print("-" * 50)

def test_get_lines():
    """测试获取产线列表"""
    result = run_command(["python", "pyScripts/user_data_operations.py", "get-lines", "1"])
    if result and result.get('success'):
        print("获取产线列表成功")
        print(f"产线数量: {len(result['data'])}")
        print(f"产线列表: {result['data']}")
    else:
        print("获取产线列表失败")
    print("-" * 50)

def test_verify_user():
    """测试验证用户登录"""
    # 测试正确的用户名和密码
    result = run_command(["python", "pyScripts/user_data_operations.py", "verify-user", "admin", "admin123", "supervisor"])
    if result and result.get('authenticated'):
        print("用户验证成功")
    else:
        print("用户验证失败")

    # 测试错误的密码
    result = run_command(["python", "pyScripts/user_data_operations.py", "verify-user", "admin", "wrongpassword", "supervisor"])
    if not result or not result.get('authenticated'):
        print("密码错误测试通过")
    else:
        print("密码错误测试失败")
    print("-" * 50)

def main():
    print("开始测试用户数据操作工具...")

    # 运行测试
    test_get_users()
    test_get_lines()
    test_verify_user()

    print("测试完成")

if __name__ == "__main__":
    main()
