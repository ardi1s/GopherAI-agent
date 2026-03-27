#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用样式定义
保持与 Vue 前端一致的视觉风格
"""

from PyQt6.QtGui import QColor, QLinearGradient, QBrush, QFont
from PyQt6.QtCore import Qt


class AppStyles:
    """应用样式类"""
    
    # 颜色定义 - 与 Vue 版本一致
    PRIMARY_COLOR = "#667eea"
    SECONDARY_COLOR = "#764ba2"
    SUCCESS_COLOR = "#67c23a"
    WARNING_COLOR = "#e6a23c"
    DANGER_COLOR = "#f56c6c"
    INFO_COLOR = "#409eff"
    
    # 渐变色
    PRIMARY_GRADIENT = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #667eea, stop:1 #764ba2)"
    SUCCESS_GRADIENT = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #67c23a, stop:1 #409eff)"
    PINK_GRADIENT = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f093fb, stop:1 #f5576c)"
    
    # 背景色
    BG_GRADIENT = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #667eea, stop:1 #764ba2)"
    CARD_BG = "rgba(255, 255, 255, 0.95)"
    INPUT_BG = "rgba(255, 255, 255, 0.96)"
    
    # 文字颜色
    TEXT_PRIMARY = "#2c3e50"
    TEXT_SECONDARY = "#7f8c8d"
    TEXT_WHITE = "#ffffff"
    
    # 边框颜色
    BORDER_LIGHT = "rgba(0, 0, 0, 0.06)"
    BORDER_WHITE = "rgba(255, 255, 255, 0.2)"
    
    @staticmethod
    def get_global_style():
        """获取全局样式"""
        return """
        /* 全局样式 */
        QWidget {
            font-family: "Microsoft YaHei", "PingFang SC", "Helvetica Neue", Arial, sans-serif;
            outline: none;
        }
        
        /* 滚动条样式 */
        QScrollBar:vertical {
            background: transparent;
            width: 8px;
            border-radius: 4px;
        }
        
        QScrollBar::handle:vertical {
            background: rgba(102, 126, 234, 0.3);
            border-radius: 4px;
            min-height: 30px;
        }
        
        QScrollBar::handle:vertical:hover {
            background: rgba(102, 126, 234, 0.5);
        }
        
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            height: 0px;
        }
        
        QScrollBar:horizontal {
            background: transparent;
            height: 8px;
            border-radius: 4px;
        }
        
        QScrollBar::handle:horizontal {
            background: rgba(102, 126, 234, 0.3);
            border-radius: 4px;
            min-width: 30px;
        }
        
        /* 消息框样式 */
        QMessageBox {
            background: white;
        }
        
        QMessageBox QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #667eea, stop:1 #764ba2);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 8px 20px;
            font-weight: 600;
            min-width: 80px;
        }
        
        QMessageBox QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #5a6fd6, stop:1 #6a4190);
        }
        """
    
    @staticmethod
    def get_login_card_style():
        """登录/注册卡片样式"""
        return """
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        """
    
    @staticmethod
    def get_primary_button_style():
        """主按钮样式 - 渐变背景"""
        return """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px 24px;
                font-weight: 600;
                font-size: 15px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #5a6fd6, stop:1 #6a4190);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4e63c2, stop:1 #5e3780);
            }
            QPushButton:disabled {
                background: #cccccc;
            }
        """
    
    @staticmethod
    def get_secondary_button_style():
        """次要按钮样式"""
        return """
            QPushButton {
                background: transparent;
                color: #409eff;
                border: none;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                color: #66b1ff;
                text-decoration: underline;
            }
        """
    
    @staticmethod
    def get_input_style():
        """输入框样式"""
        return """
            QLineEdit, QTextEdit {
                background: rgba(255, 255, 255, 0.96);
                border: 2px solid rgba(0, 0, 0, 0.06);
                border-radius: 12px;
                padding: 12px 16px;
                font-size: 15px;
                color: #2c3e50;
            }
            QLineEdit:focus, QTextEdit:focus {
                border-color: #409eff;
            }
            QLineEdit:disabled, QTextEdit:disabled {
                background: #f5f7fa;
                color: #c0c4cc;
            }
        """
    
    @staticmethod
    def get_session_list_style():
        """会话列表样式"""
        return """
            QListWidget {
                background: rgba(255, 255, 255, 0.95);
                border: none;
                outline: none;
                padding: 0;
            }
            QListWidget::item {
                background: transparent;
                color: #2c3e50;
                padding: 15px 20px;
                border-bottom: 1px solid rgba(0, 0, 0, 0.03);
            }
            QListWidget::item:hover {
                background: rgba(102, 126, 234, 0.06);
            }
            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #667eea, stop:1 #764ba2);
                color: white;
                font-weight: 600;
            }
        """
    
    @staticmethod
    def get_menu_card_style():
        """菜单卡片样式"""
        return """
            QFrame#menuCard {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            QFrame#menuCard:hover {
                background: rgba(255, 255, 255, 1);
            }
        """
    
    @staticmethod
    def get_chat_message_user_style():
        """用户消息气泡样式"""
        return """
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #667eea, stop:1 #764ba2);
            color: white;
            border-radius: 18px;
            padding: 14px 18px;
            font-size: 15px;
            line-height: 1.6;
        """
    
    @staticmethod
    def get_chat_message_ai_style():
        """AI 消息气泡样式"""
        return """
            background: rgba(255, 255, 255, 0.95);
            color: #2c3e50;
            border-radius: 18px;
            padding: 14px 18px;
            font-size: 15px;
            line-height: 1.6;
            border: 1px solid rgba(255, 255, 255, 0.3);
        """


class GradientBackground:
    """渐变背景工具类"""
    
    @staticmethod
    def get_primary_gradient():
        """获取主渐变"""
        gradient = QLinearGradient(0, 0, 1, 1)
        gradient.setCoordinateMode(QLinearGradient.CoordinateMode.ObjectBoundingMode)
        gradient.setColorAt(0, QColor("#667eea"))
        gradient.setColorAt(1, QColor("#764ba2"))
        return QBrush(gradient)
    
    @staticmethod
    def get_success_gradient():
        """获取成功渐变"""
        gradient = QLinearGradient(0, 0, 1, 1)
        gradient.setCoordinateMode(QLinearGradient.CoordinateMode.ObjectBoundingMode)
        gradient.setColorAt(0, QColor("#67c23a"))
        gradient.setColorAt(1, QColor("#409eff"))
        return QBrush(gradient)
