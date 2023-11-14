# _*_coding:utf-8_*_
import os
import subprocess
import sys
import platform


def check_python_version():
    if platform.python_version_tuple()[0] == '3':  # 检查系统Python解释器的主版本号是否为3
        return 'python3'
    else:
        return 'error'


def run_script(script_path):
    python_cmd = check_python_version()
    if python_cmd == "python3":
        subprocess.run([python_cmd, script_path], check=True)
    else:
        print("解释器错误！")


# 获取当前目录下的所有文件
file_list = os.listdir()

# 筛选出.py文件
python_scripts = [file for file in file_list if file.endswith(".py")]

# 排除当前脚本
current_script = os.path.basename(__file__)
python_scripts = [script for script in python_scripts if script != current_script]

# 打印所有的.py文件
print("请选择要运行的脚本：")
for i, script in enumerate(python_scripts):
    print(f"{i + 1}. {script}")

# 获取用户选择的脚本
selection = input("输入相应的序号以选择要运行的脚本：")

# 执行用户选择的脚本
if selection.isdigit() and int(selection) in range(1, len(python_scripts) + 1):
    script_to_run = python_scripts[int(selection) - 1]
    run_script(script_to_run)
else:
    print("选择无效。")
