@echo off
chcp 65001 >nul
REM GopherAI PyQt Client 一键启动脚本 (Windows)

title GopherAI PyQt Client 启动器

echo ========================================
echo   GopherAI PyQt Client 启动器
echo ========================================
echo.

REM 获取脚本所在目录
cd /d "%~dp0"

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

for /f "tokens=2" %%a in ('python --version 2^>^&1') do (
    echo [√] Python 版本: %%a
)

REM 检查虚拟环境
if exist "venv\Scripts\activate.bat" (
    echo [√] 发现虚拟环境，正在激活...
    call venv\Scripts\activate.bat
) else (
    echo [!] 未找到虚拟环境，正在创建...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo [√] 虚拟环境创建完成
)

REM 检查依赖是否安装
echo.
echo 检查依赖...

python -c "import PyQt6" >nul 2>&1
if errorlevel 1 (
    echo [!] PyQt6 未安装，正在安装依赖...
    pip install --upgrade pip
    pip install -r requirements.txt
    echo [√] 依赖安装完成
) else (
    echo [√] 依赖已安装
)

REM 检查后端服务（可选）
echo.
echo 检查后端服务...

if exist "utils\api_client.py" (
    for /f "tokens=3 delims== " %%a in ('findstr /C:"BASE_URL" utils\api_client.py') do (
        set "BACKEND_URL=%%a"
        set "BACKEND_URL=!BACKEND_URL:"=!"
        echo   配置的后端地址: !BACKEND_URL!
    )
) else (
    echo [!] 未找到配置文件
)

echo.
echo ========================================
echo   正在启动 GopherAI PyQt Client...
echo ========================================
echo.

REM 启动应用
python start.py

REM 退出虚拟环境
call venv\Scripts\deactivate.bat

pause
