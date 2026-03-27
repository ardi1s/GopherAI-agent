#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
登录界面
保持与 Vue 版本一致的视觉风格
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QFrame, QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSettings
from PyQt6.QtGui import QFont, QPalette, QColor

from utils.styles import AppStyles
from utils.api_client import api_post, APIClient


class LoginView(QWidget):
    """登录视图"""
    
    # 信号定义
    login_success = pyqtSignal(str)  # 登录成功，传递 token
    goto_register = pyqtSignal()      # 跳转到注册
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        # 设置渐变背景
        self.setAutoFillBackground(True)
        palette = self.palette()
        gradient_color = QColor("#667eea")
        palette.setColor(QPalette.ColorRole.Window, gradient_color)
        self.setPalette(palette)
        
        # 主布局 - 居中
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 登录卡片
        self.card = QFrame()
        self.card.setFixedWidth(420)
        self.card.setStyleSheet(AppStyles.get_login_card_style())
        
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(24)
        
        # 标题
        title_label = QLabel('登录')
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont('Microsoft YaHei', 28, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("""
            color: transparent;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #667eea, stop:1 #764ba2);
            -webkit-background-clip: text;
            background-clip: text;
        """)
        # 使用渐变文字效果
        title_label.setStyleSheet("""
            color: #667eea;
            font-weight: 600;
        """)
        card_layout.addWidget(title_label)
        
        # 表单区域
        form_layout = QVBoxLayout()
        form_layout.setSpacing(20)
        
        # 用户名
        username_layout = QVBoxLayout()
        username_layout.setSpacing(8)
        username_label = QLabel('用户名')
        username_label.setStyleSheet('color: #2c3e50; font-weight: 500;')
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('请输入用户名')
        self.username_input.setStyleSheet(AppStyles.get_input_style())
        self.username_input.setMinimumHeight(48)
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        form_layout.addLayout(username_layout)
        
        # 密码
        password_layout = QVBoxLayout()
        password_layout.setSpacing(8)
        password_label = QLabel('密码')
        password_label.setStyleSheet('color: #2c3e50; font-weight: 500;')
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('请输入密码')
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet(AppStyles.get_input_style())
        self.password_input.setMinimumHeight(48)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        form_layout.addLayout(password_layout)
        
        card_layout.addLayout(form_layout)
        
        # 登录按钮
        self.login_btn = QPushButton('登录')
        self.login_btn.setStyleSheet(AppStyles.get_primary_button_style())
        self.login_btn.setMinimumHeight(48)
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.clicked.connect(self.handle_login)
        card_layout.addWidget(self.login_btn)
        
        # 注册链接
        self.register_btn = QPushButton('还没有账号？去注册')
        self.register_btn.setStyleSheet(AppStyles.get_secondary_button_style())
        self.register_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.register_btn.clicked.connect(self.goto_register.emit)
        card_layout.addWidget(self.register_btn)
        
        # 添加弹性空间
        card_layout.addStretch()
        
        # 将卡片添加到主布局
        main_layout.addWidget(self.card, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 连接回车键
        self.username_input.returnPressed.connect(self.password_input.setFocus)
        self.password_input.returnPressed.connect(self.handle_login)
    
    def handle_login(self):
        """处理登录"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        # 验证输入
        if not username:
            QMessageBox.warning(self, '提示', '请输入用户名')
            self.username_input.setFocus()
            return
        
        if not password:
            QMessageBox.warning(self, '提示', '请输入密码')
            self.password_input.setFocus()
            return
        
        if len(password) < 6:
            QMessageBox.warning(self, '提示', '密码长度不能少于6位')
            self.password_input.setFocus()
            return
        
        # 禁用按钮，显示加载状态
        self.login_btn.setEnabled(False)
        self.login_btn.setText('登录中...')
        
        try:
            # 发送登录请求
            response = api_post('/user/login', {
                'username': username,
                'password': password
            })
            
            if response.is_success:
                token = response.data.get('token', '')
                APIClient.set_token(token)
                QMessageBox.information(self, '成功', '登录成功')
                self.login_success.emit(token)
            else:
                QMessageBox.warning(self, '登录失败', response.message or '登录失败')
        
        except Exception as e:
            QMessageBox.critical(self, '错误', f'登录失败：{str(e)}')
        
        finally:
            # 恢复按钮状态
            self.login_btn.setEnabled(True)
            self.login_btn.setText('登录')
    
    def clear_fields(self):
        """清空输入框"""
        self.username_input.clear()
        self.password_input.clear()
        self.login_btn.setEnabled(True)
        self.login_btn.setText('登录')
