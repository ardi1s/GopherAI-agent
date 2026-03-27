#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GopherAI PyQt Client 一键启动脚本 (跨平台)
支持 Windows、macOS、Linux
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


class Colors:
    """终端颜色"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'

    @classmethod
    def disable(cls):
        """禁用颜色（Windows CMD）"""
        cls.RED = ''
        cls.GREEN = ''
        cls.YELLOW = ''
        cls.BLUE = ''
        cls.NC = ''


def print_banner():
    """打印启动横幅"""
    print(f"{Colors.BLUE}{'=' * 40}{Colors.NC}")
    print(f"{Colors.BLUE}  GopherAI PyQt Client 启动器{Colors.NC}")
    print(f"{Colors.BLUE}{'=' * 40}{Colors.NC}")
    print()


def find_python():
    """查找可用的 Python 解释器"""
    # 首先检查当前运行的 Python
    current_version = sys.version_info
    if current_version.major == 3 and current_version.minor >= 8:
        return sys.executable
    
    # 尝试常见的 Python 命令
    commands = ['python3', 'python3.11', 'python3.10', 'python3.9', 'python3.8', 'python']
    
    for cmd in commands:
        try:
            result = subprocess.run(
                [cmd, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # 检查版本
                version_str = result.stdout.strip() or result.stderr.strip()
                # 解析版本号
                import re
                match = re.search(r'(\d+)\.(\d+)', version_str)
                if match:
                    major, minor = int(match.group(1)), int(match.group(2))
                    if major == 3 and minor >= 8:
                        return cmd
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue
    
    return None


def check_python():
    """检查 Python 版本"""
    python_cmd = find_python()
    
    if python_cmd is None:
        print(f"{Colors.RED}错误: 未找到 Python 3.8+，请先安装 Python{Colors.NC}")
        print(f"{Colors.YELLOW}提示: macOS 可以使用 'brew install python3'{Colors.NC}")
        return None
    
    # 获取版本信息
    try:
        result = subprocess.run(
            [python_cmd, '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        version_str = result.stdout.strip() or result.stderr.strip()
        print(f"{Colors.GREEN}✓ {version_str}{Colors.NC}")
        print(f"{Colors.GREEN}✓ 使用解释器: {python_cmd}{Colors.NC}")
        return python_cmd
    except Exception as e:
        print(f"{Colors.RED}错误: 无法获取 Python 版本: {e}{Colors.NC}")
        return None


def get_venv_python():
    """获取虚拟环境中的 Python 路径"""
    script_dir = Path(__file__).parent
    venv_path = script_dir / "venv"
    
    if platform.system() == "Windows":
        python_exe = venv_path / "Scripts" / "python.exe"
    else:
        python_exe = venv_path / "bin" / "python"
    
    return python_exe


def create_venv(python_cmd):
    """创建虚拟环境"""
    venv_path = Path(__file__).parent / "venv"
    venv_python = get_venv_python()
    
    if venv_python.exists():
        print(f"{Colors.GREEN}✓ 虚拟环境已存在{Colors.NC}")
        return str(venv_python)
    
    print(f"{Colors.YELLOW}⚠ 正在创建虚拟环境...{Colors.NC}")
    try:
        subprocess.run([python_cmd, "-m", "venv", str(venv_path)], check=True)
        print(f"{Colors.GREEN}✓ 虚拟环境创建完成{Colors.NC}")
        return str(venv_python)
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}错误: 创建虚拟环境失败: {e}{Colors.NC}")
        return None


def install_dependencies(python_exe):
    """安装依赖"""
    print()
    print(f"{Colors.BLUE}检查依赖...{Colors.NC}")
    
    # 检查 PyQt6 是否已安装
    try:
        subprocess.run(
            [python_exe, "-c", "import PyQt6"],
            check=True,
            capture_output=True
        )
        print(f"{Colors.GREEN}✓ 依赖已安装{Colors.NC}")
        return True
    except subprocess.CalledProcessError:
        pass
    
    print(f"{Colors.YELLOW}⚠ 正在安装依赖...{Colors.NC}")
    
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    try:
        # 升级 pip
        subprocess.run(
            [python_exe, "-m", "pip", "install", "--upgrade", "pip"],
            check=True,
            capture_output=True
        )
        
        # 安装依赖
        subprocess.run(
            [python_exe, "-m", "pip", "install", "-r", str(requirements_file)],
            check=True
        )
        
        print(f"{Colors.GREEN}✓ 依赖安装完成{Colors.NC}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}错误: 安装依赖失败: {e}{Colors.NC}")
        return False


def check_backend():
    """检查后端服务"""
    print()
    print(f"{Colors.BLUE}检查后端服务...{Colors.NC}")
    
    api_client_file = Path(__file__).parent / "utils" / "api_client.py"
    
    if not api_client_file.exists():
        print(f"{Colors.YELLOW}⚠ 未找到配置文件{Colors.NC}")
        return
    
    # 读取后端地址
    try:
        with open(api_client_file, 'r', encoding='utf-8') as f:
            for line in f:
                if 'BASE_URL' in line and '=' in line:
                    url = line.split('=')[1].strip().strip('"').strip("'")
                    print(f"{Colors.YELLOW}  配置的后端地址: {url}{Colors.NC}")
                    break
    except Exception:
        pass


def launch_app(python_exe):
    """启动应用"""
    print()
    print(f"{Colors.BLUE}{'=' * 40}{Colors.NC}")
    print(f"{Colors.GREEN}  正在启动 GopherAI PyQt Client...{Colors.NC}")
    print(f"{Colors.BLUE}{'=' * 40}{Colors.NC}")
    print()
    
    start_script = Path(__file__).parent / "start.py"
    
    try:
        subprocess.run([python_exe, str(start_script)])
    except KeyboardInterrupt:
        print()
        print(f"{Colors.YELLOW}用户取消启动{Colors.NC}")
    except Exception as e:
        print(f"{Colors.RED}错误: 启动失败: {e}{Colors.NC}")


def main():
    """主函数"""
    # Windows CMD 不支持 ANSI 颜色，禁用颜色
    if platform.system() == "Windows" and "TERM" not in os.environ:
        Colors.disable()
    
    print_banner()
    
    # 检查 Python
    python_cmd = check_python()
    if python_cmd is None:
        input("\n按回车键退出...")
        return 1
    
    # 创建虚拟环境
    venv_python = create_venv(python_cmd)
    if venv_python is None:
        input("\n按回车键退出...")
        return 1
    
    # 安装依赖
    if not install_dependencies(venv_python):
        input("\n按回车键退出...")
        return 1
    
    # 检查后端
    check_backend()
    
    # 启动应用
    launch_app(venv_python)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
