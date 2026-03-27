#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GopherAI PyQt Client
基于 PyQt6 的桌面客户端，替代原有的 Vue 前端
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QFont, QFontDatabase

from views.login_view import LoginView
from views.register_view import RegisterView
from views.menu_view import MenuView
from views.ai_chat_view import AIChatView
from views.image_recognition_view import ImageRecognitionView
from utils.styles import AppStyles


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings('GopherAI', 'PyQtClient')
        self.token = self.settings.value('token', '')
        
        self.setWindowTitle('GopherAI - AI 应用平台')
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # 设置全局样式
        self.setStyleSheet(AppStyles.get_global_style())
        
        # 创建堆叠窗口管理器
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        # 初始化各个视图
        self.login_view = LoginView()
        self.register_view = RegisterView()
        self.menu_view = MenuView()
        self.ai_chat_view = AIChatView()
        self.image_recognition_view = ImageRecognitionView()
        
        # 添加视图到堆叠窗口
        self.stack.addWidget(self.login_view)      # 0
        self.stack.addWidget(self.register_view)   # 1
        self.stack.addWidget(self.menu_view)       # 2
        self.stack.addWidget(self.ai_chat_view)    # 3
        self.stack.addWidget(self.image_recognition_view)  # 4
        
        # 连接信号
        self._connect_signals()
        
        # 检查登录状态
        if self.token:
            self.show_menu()
        else:
            self.show_login()
    
    def _connect_signals(self):
        # 登录视图信号
        self.login_view.login_success.connect(self.on_login_success)
        self.login_view.goto_register.connect(self.show_register)
        
        # 注册视图信号
        self.register_view.register_success.connect(self.show_login)
        self.register_view.goto_login.connect(self.show_login)
        
        # 菜单视图信号
        self.menu_view.goto_ai_chat.connect(self.show_ai_chat)
        self.menu_view.goto_image_recognition.connect(self.show_image_recognition)
        self.menu_view.logout.connect(self.on_logout)
        
        # AI 聊天视图信号
        self.ai_chat_view.goto_menu.connect(self.show_menu)
        
        # 图像识别视图信号
        self.image_recognition_view.goto_menu.connect(self.show_menu)
    
    def show_login(self):
        self.stack.setCurrentIndex(0)
        self.login_view.clear_fields()
    
    def show_register(self):
        self.stack.setCurrentIndex(1)
        self.register_view.clear_fields()
    
    def show_menu(self):
        self.stack.setCurrentIndex(2)
    
    def show_ai_chat(self):
        self.ai_chat_view.load_sessions()
        self.stack.setCurrentIndex(3)
    
    def show_image_recognition(self):
        self.stack.setCurrentIndex(4)
    
    def on_login_success(self, token):
        self.token = token
        self.settings.setValue('token', token)
        self.show_menu()
    
    def on_logout(self):
        self.token = ''
        self.settings.remove('token')
        self.show_login()
    
    def closeEvent(self, event):
        # 清理资源
        self.ai_chat_view.cleanup()
        self.image_recognition_view.cleanup()
        event.accept()


def main():
    # 启用高 DPI 支持
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    
    # 设置应用字体
    font = QFont('Microsoft YaHei', 10)
    app.setFont(font)
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
