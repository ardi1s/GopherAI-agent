#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GopherAI PyQt Client 启动脚本
"""

import sys
import os

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import main

if __name__ == '__main__':
    main()
