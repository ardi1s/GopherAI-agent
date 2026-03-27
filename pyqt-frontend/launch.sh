#!/bin/bash
# -*- coding: utf-8 -*-
# GopherAI PyQt Client 一键启动脚本 (Linux/macOS)

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  GopherAI PyQt Client 启动器${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检测可用的 Python 命令
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}错误: 未找到 Python，请先安装 Python 3.8+${NC}"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓ Python 版本: $PYTHON_VERSION${NC}"
echo -e "${GREEN}✓ 使用命令: $PYTHON_CMD${NC}"

# 检查虚拟环境
VENV_PYTHON="$SCRIPT_DIR/venv/bin/python"
if [ -d "venv" ] && [ -f "$VENV_PYTHON" ]; then
    echo -e "${GREEN}✓ 发现虚拟环境${NC}"
    PYTHON_CMD="$VENV_PYTHON"
else
    echo -e "${YELLOW}⚠ 未找到虚拟环境，正在创建...${NC}"
    $PYTHON_CMD -m venv venv
    echo -e "${GREEN}✓ 虚拟环境创建完成${NC}"
    PYTHON_CMD="$VENV_PYTHON"
fi

# 检查依赖是否安装
echo ""
echo -e "${BLUE}检查依赖...${NC}"

if ! "$PYTHON_CMD" -c "import PyQt6" 2>/dev/null; then
    echo -e "${YELLOW}⚠ PyQt6 未安装，正在安装依赖...${NC}"
    "$PYTHON_CMD" -m pip install --upgrade pip
    "$PYTHON_CMD" -m pip install -r requirements.txt
    echo -e "${GREEN}✓ 依赖安装完成${NC}"
else
    echo -e "${GREEN}✓ 依赖已安装${NC}"
fi

# 检查后端服务是否可访问（可选）
echo ""
echo -e "${BLUE}检查后端服务...${NC}"

# 从 api_client.py 读取配置
if [ -f "utils/api_client.py" ]; then
    BACKEND_URL=$(grep "BASE_URL" utils/api_client.py | head -1 | sed 's/.*= "\(.*\)".*/\1/')
    echo -e "${YELLOW}  配置的后端地址: $BACKEND_URL${NC}"
    
    # 尝试连接后端（静默）
    if curl -s --max-time 2 "$BACKEND_URL" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ 后端服务可访问${NC}"
    else
        echo -e "${YELLOW}⚠ 后端服务暂时无法访问，请确保后端已启动${NC}"
    fi
else
    echo -e "${YELLOW}⚠ 未找到配置文件${NC}"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}  正在启动 GopherAI PyQt Client...${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 启动应用
"$PYTHON_CMD" start.py
