#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
注册界面
保持与 Vue 版本一致的视觉风格
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor

from utils.styles import AppStyles
from utils.api_client import api_post


class RegisterView(QWidget):
    """注册视图"""

    # 信号定义
    register_success = pyqtSignal()  # 注册成功
    goto_login = pyqtSignal()        # 跳转到登录

    def __init__(self):
        super().__init__()
        self.countdown = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_countdown)
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

        # 注册卡片
        self.card = QFrame()
        self.card.setFixedWidth(420)
        self.card.setStyleSheet(AppStyles.get_login_card_style())

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(20)

        # 标题
        title_label = QLabel('注册')
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont('Microsoft YaHei', 28, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("""
            color: #667eea;
            font-weight: 600;
        """)
        card_layout.addWidget(title_label)

        # 表单区域
        form_layout = QVBoxLayout()
        form_layout.setSpacing(16)

        # 邮箱
        email_layout = QVBoxLayout()
        email_layout.setSpacing(8)
        email_label = QLabel('邮箱')
        email_label.setStyleSheet('color: #2c3e50; font-weight: 500;')
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText('请输入邮箱')
        self.email_input.setStyleSheet(AppStyles.get_input_style())
        self.email_input.setMinimumHeight(44)
        email_layout.addWidget(email_label)
        email_layout.addWidget(self.email_input)
        form_layout.addLayout(email_layout)

        # 验证码
        captcha_layout = QVBoxLayout()
        captcha_layout.setSpacing(8)
        captcha_label = QLabel('验证码')
        captcha_label.setStyleSheet('color: #2c3e50; font-weight: 500;')

        captcha_input_layout = QHBoxLayout()
        captcha_input_layout.setSpacing(10)

        self.captcha_input = QLineEdit()
        self.captcha_input.setPlaceholderText('请输入验证码')
        self.captcha_input.setStyleSheet(AppStyles.get_input_style())
        self.captcha_input.setMinimumHeight(44)

        self.send_code_btn = QPushButton('发送验证码')
        self.send_code_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #409eff, stop:1 #67c23a);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 16px;
                font-weight: 600;
                font-size: 13px;
                min-width: 100px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #3a8ee6, stop:1 #5daf34);
            }
            QPushButton:disabled {
                background: #cccccc;
            }
        """)
        self.send_code_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.send_code_btn.clicked.connect(self.send_code)

        captcha_input_layout.addWidget(self.captcha_input, 2)
        captcha_input_layout.addWidget(self.send_code_btn, 1)

        captcha_layout.addWidget(captcha_label)
        captcha_layout.addLayout(captcha_input_layout)
        form_layout.addLayout(captcha_layout)

        # 密码
        password_layout = QVBoxLayout()
        password_layout.setSpacing(8)
        password_label = QLabel('密码')
        password_label.setStyleSheet('color: #2c3e50; font-weight: 500;')
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('请输入密码')
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet(AppStyles.get_input_style())
        self.password_input.setMinimumHeight(44)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        form_layout.addLayout(password_layout)

        # 确认密码
        confirm_layout = QVBoxLayout()
        confirm_layout.setSpacing(8)
        confirm_label = QLabel('确认密码')
        confirm_label.setStyleSheet('color: #2c3e50; font-weight: 500;')
        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText('请再次输入密码')
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_input.setStyleSheet(AppStyles.get_input_style())
        self.confirm_input.setMinimumHeight(44)
        confirm_layout.addWidget(confirm_label)
        confirm_layout.addWidget(self.confirm_input)
        form_layout.addLayout(confirm_layout)

        card_layout.addLayout(form_layout)

        # 注册按钮
        self.register_btn = QPushButton('注册')
        self.register_btn.setStyleSheet(AppStyles.get_primary_button_style())
        self.register_btn.setMinimumHeight(48)
        self.register_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.register_btn.clicked.connect(self.handle_register)
        card_layout.addWidget(self.register_btn)

        # 登录链接
        self.login_btn = QPushButton('已有账号？去登录')
        self.login_btn.setStyleSheet(AppStyles.get_secondary_button_style())
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.clicked.connect(self.goto_login.emit)
        card_layout.addWidget(self.login_btn)

        # 添加弹性空间
        card_layout.addStretch()

        # 将卡片添加到主布局
        main_layout.addWidget(self.card, alignment=Qt.AlignmentFlag.AlignCenter)

    def send_code(self):
        """发送验证码"""
        email = self.email_input.text().strip()

        if not email:
            QMessageBox.warning(self, '提示', '请先输入邮箱')
            self.email_input.setFocus()
            return

        # 简单验证邮箱格式
        if '@' not in email or '.' not in email:
            QMessageBox.warning(self, '提示', '请输入正确的邮箱格式')
            self.email_input.setFocus()
            return

        # 禁用按钮
        self.send_code_btn.setEnabled(False)
        self.send_code_btn.setText('发送中...')

        try:
            response = api_post('/user/captcha', {'email': email})

            if response.is_success:
                QMessageBox.information(self, '成功', '验证码发送成功')
                self.countdown = 60
                self.update_countdown()
                self.timer.start(1000)
            else:
                QMessageBox.warning(self, '失败', response.message or '验证码发送失败')
                self.send_code_btn.setEnabled(True)
                self.send_code_btn.setText('发送验证码')

        except Exception as e:
            QMessageBox.critical(self, '错误', f'发送失败：{str(e)}')
            self.send_code_btn.setEnabled(True)
            self.send_code_btn.setText('发送验证码')

    def update_countdown(self):
        """更新倒计时"""
        if self.countdown > 0:
            self.send_code_btn.setText(f'{self.countdown}s')
            self.countdown -= 1
        else:
            self.timer.stop()
            self.send_code_btn.setEnabled(True)
            self.send_code_btn.setText('发送验证码')

    def handle_register(self):
        """处理注册"""
        email = self.email_input.text().strip()
        captcha = self.captcha_input.text().strip()
        password = self.password_input.text().strip()
        confirm_password = self.confirm_input.text().strip()

        # 验证输入
        if not email:
            QMessageBox.warning(self, '提示', '请输入邮箱')
            self.email_input.setFocus()
            return

        if not captcha:
            QMessageBox.warning(self, '提示', '请输入验证码')
            self.captcha_input.setFocus()
            return

        if not password:
            QMessageBox.warning(self, '提示', '请输入密码')
            self.password_input.setFocus()
            return

        if len(password) < 6:
            QMessageBox.warning(self, '提示', '密码长度不能少于6位')
            self.password_input.setFocus()
            return

        if password != confirm_password:
            QMessageBox.warning(self, '提示', '两次输入密码不一致')
            self.confirm_input.setFocus()
            return

        # 禁用按钮，显示加载状态
        self.register_btn.setEnabled(False)
        self.register_btn.setText('注册中...')

        try:
            response = api_post('/user/register', {
                'email': email,
                'captcha': captcha,
                'password': password
            })

            if response.is_success:
                QMessageBox.information(self, '成功', '注册成功，请登录')
                self.register_success.emit()
            else:
                QMessageBox.warning(self, '注册失败', response.message or '注册失败')

        except Exception as e:
            QMessageBox.critical(self, '错误', f'注册失败：{str(e)}')

        finally:
            # 恢复按钮状态
            self.register_btn.setEnabled(True)
            self.register_btn.setText('注册')

    def clear_fields(self):
        """清空输入框"""
        self.email_input.clear()
        self.captcha_input.clear()
        self.password_input.clear()
        self.confirm_input.clear()
        self.register_btn.setEnabled(True)
        self.register_btn.setText('注册')
        self.send_code_btn.setEnabled(True)
        self.send_code_btn.setText('发送验证码')
        self.timer.stop()
        self.countdown = 0
