#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
菜单界面
保持与 Vue 版本一致的视觉风格
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor, QPixmap, QPainter, QPainterPath

from utils.styles import AppStyles


class MenuCard(QFrame):
    """菜单卡片组件"""

    clicked = pyqtSignal()

    def __init__(self, icon_text, title, description, parent=None):
        super().__init__(parent)
        self.setObjectName('menuCard')
        self.setFixedSize(320, 280)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # 设置样式
        self.setStyleSheet("""
            QFrame#menuCard {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            QFrame#menuCard:hover {
                background: rgba(255, 255, 255, 1);
            }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 40, 30, 40)

        # 图标
        icon_label = QLabel(icon_text)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_font = QFont('Microsoft YaHei', 48)
        icon_label.setFont(icon_font)
        layout.addWidget(icon_label)

        # 标题
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont('Microsoft YaHei', 24, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet('color: #2c3e50;')
        layout.addWidget(title_label)

        # 描述
        desc_label = QLabel(description)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_font = QFont('Microsoft YaHei', 14)
        desc_label.setFont(desc_font)
        desc_label.setStyleSheet('color: #7f8c8d;')
        layout.addWidget(desc_label)

    def mousePressEvent(self, event):
        self.clicked.emit()


class MenuView(QWidget):
    """菜单视图"""

    # 信号定义
    goto_ai_chat = pyqtSignal()
    goto_image_recognition = pyqtSignal()
    logout = pyqtSignal()

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

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 顶部导航栏
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet("""
            background: rgba(255, 255, 255, 0.1);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        """)

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(30, 0, 30, 0)

        # 标题
        title_label = QLabel('AI应用平台')
        title_font = QFont('Microsoft YaHei', 24, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet('color: white;')
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # 退出按钮
        logout_btn = QPushButton('退出登录')
        logout_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                color: white;
                border-radius: 10px;
                padding: 10px 20px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.3);
            }
        """)
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.clicked.connect(self.handle_logout)
        header_layout.addWidget(logout_btn)

        main_layout.addWidget(header)

        # 内容区域
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 卡片网格
        grid_layout = QHBoxLayout()
        grid_layout.setSpacing(40)
        grid_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # AI 聊天卡片
        self.chat_card = MenuCard('💬', 'AI聊天', '与AI进行智能对话')
        self.chat_card.clicked.connect(self.goto_ai_chat.emit)
        grid_layout.addWidget(self.chat_card)

        # 图像识别卡片
        self.image_card = MenuCard('📷', '图像识别', '上传图片进行AI识别')
        self.image_card.clicked.connect(self.goto_image_recognition.emit)
        grid_layout.addWidget(self.image_card)

        content_layout.addLayout(grid_layout)
        main_layout.addWidget(content, stretch=1)

    def handle_logout(self):
        """处理退出登录"""
        reply = QMessageBox.question(
            self,
            '提示',
            '确定要退出登录吗？',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.logout.emit()
