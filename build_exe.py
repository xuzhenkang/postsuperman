#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包脚本 - 将postsuperman打包为exe文件
"""

import os
import sys
import subprocess


def install_pyinstaller():
    """安装PyInstaller"""
    print("正在安装PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller安装成功！")
        return True
    except subprocess.CalledProcessError:
        print("PyInstaller安装失败！")
        return False


def build_exe():
    """构建exe文件"""
    print("开始构建exe文件...")

    # PyInstaller命令参数
    cmd = [
        "pyinstaller",
        "--onefile",  # 打包成单个exe文件
        "--windowed",  # 不显示控制台窗口
        "--name=postsuperman_v1.0.0",  # 设置exe文件名
        "--icon=ui/app.ico",  # 设置图标（如果有的话）
        "--add-data=requirements.txt;.",  # 包含requirements.txt
        "--clean",  # 清理临时文件
        "main.py"  # 主程序文件
    ]

    try:
        subprocess.check_call(cmd)
        print("exe文件构建成功！")
        
        # 手动复制必要的文件到dist目录
        import shutil
        dist_dir = "dist"
        if not os.path.exists(dist_dir):
            os.makedirs(dist_dir)
            
        # 复制图标文件
        if os.path.exists("ui/app.ico"):
            shutil.copy2("ui/app.ico", os.path.join(dist_dir, "app.ico"))
            print("图标文件复制成功！")
            
        return True
    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e}")
        return False


def create_icon():
    """创建简单的图标文件（如果不存在）"""
    if not os.path.exists("ui/app.ico"):
        print("创建默认图标...")
        # 这里可以添加创建图标的代码
        # 暂时跳过图标创建
        pass


def main():
    """主函数"""
    print("=== 长文本二维码生成器 - 打包工具 ===")

    # 检查Python版本
    if sys.version_info < (3, 6):
        print("错误：需要Python 3.6或更高版本！")
        return

    # 检查主程序文件
    if not os.path.exists("main.py"):
        print("错误：找不到main.py文件！")
        return

    # 安装PyInstaller
    if not install_pyinstaller():
        return

    # 创建图标
    create_icon()

    # 构建exe
    if build_exe():
        print("\n=== 构建完成 ===")
        print("exe文件位置: dist/postsuperman_v1.0.0.exe")
        print("你可以将exe文件复制到任何地方运行！")
    else:
        print("\n=== 构建失败 ===")


if __name__ == "__main__":
    main()
