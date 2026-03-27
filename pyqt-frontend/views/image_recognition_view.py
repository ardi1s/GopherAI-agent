#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图像识别界面
保持与 Vue 版本一致的视觉风格
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QFileDialog, QMessageBox, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor, QPixmap

from utils.styles import AppStyles
from utils.api_client import APIClient


class ImageMessageBubble(QFrame):
    """图像消息气泡组件"""

    def __init__(self, role, content, image_path=None, parent=None):
        super().__init__(parent)
        self.role = role
        self.content = content
        self.image_path = image_path
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # 头部
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        sender_label = QLabel('你' if self.role == 'user' else 'AI')
        sender_font = QFont('Microsoft YaHei', 13, QFont.Weight.Bold)
        sender_label.setFont(sender_font)
        header_layout.addWidget(sender_label)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # 内容
        content_label = QLabel(self.content)
        content_label.setWordWrap(True)
        content_font = QFont('Microsoft YaHei', 14)
        content_label.setFont(content_font)

        # 设置样式
        if self.role == 'user':
            content_label.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #667eea, stop:1 #764ba2);
                    color: white;
                    border-radius: 18px;
                    padding: 14px 18px;
                    line-height: 1.6;
                }
            """)
        else:
            content_label.setStyleSheet("""
                QLabel {
                    background: rgba(255, 255, 255, 0.95);
                    color: #2c3e50;
                    border-radius: 18px;
                    padding: 14px 18px;
                    line-height: 1.6;
                    border: 1px solid rgba(255, 255, 255, 0.3);
                }
            """)

        layout.addWidget(content_label)

        # 如果有图片，显示图片
        if self.image_path:
            image_label = QLabel()
            pixmap = QPixmap(self.image_path)
            # 缩放图片
            scaled_pixmap = pixmap.scaledToWidth(250, Qt.TransformationMode.SmoothTransformation)
            image_label.setPixmap(scaled_pixmap)
            image_label.setStyleSheet("""
                QLabel {
                    border-radius: 12px;
                    margin-top: 12px;
                }
            """)
            layout.addWidget(image_label)

        # 设置最大宽度
        self.setMaximumWidth(700)


class ImageRecognitionView(QWidget):
    """图像识别视图"""

    goto_menu = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.selected_file = None
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
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 左侧会话列表
        session_panel = QFrame()
        session_panel.setFixedWidth(280)
        session_panel.setStyleSheet("""
            background: rgba(255, 255, 255, 0.95);
            border-right: 1px solid rgba(0, 0, 0, 0.08);
        """)

        session_layout = QVBoxLayout(session_panel)
        session_layout.setContentsMargins(0, 0, 0, 0)
        session_layout.setSpacing(0)

        # 会话列表头部
        session_header = QFrame()
        session_header.setFixedHeight(80)
        session_header.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(102,126,234,0.06), stop:1 rgba(103,194,58,0.06));
            border-bottom: 1px solid rgba(0, 0, 0, 0.06);
        """)

        header_layout = QVBoxLayout(session_header)
        header_layout.setContentsMargins(20, 20, 20, 20)

        header_label = QLabel('图像识别')
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_font = QFont('Microsoft YaHei', 16, QFont.Weight.Bold)
        header_label.setFont(header_font)
        header_label.setStyleSheet('color: #2c3e50;')
        header_layout.addWidget(header_label)

        session_layout.addWidget(session_header)

        # 当前会话项
        session_item = QLabel('图像识别助手')
        session_item.setAlignment(Qt.AlignmentFlag.AlignCenter)
        session_item.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #667eea, stop:1 #764ba2);
                color: white;
                font-weight: 600;
                padding: 15px 20px;
                border-bottom: 1px solid rgba(0, 0, 0, 0.03);
            }
        """)
        session_layout.addWidget(session_item)
        session_layout.addStretch()

        main_layout.addWidget(session_panel)

        # 右侧聊天区域
        chat_area = QFrame()
        chat_area.setStyleSheet('background: transparent;')

        chat_layout = QVBoxLayout(chat_area)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(0)

        # 顶部工具栏
        toolbar = QFrame()
        toolbar.setFixedHeight(70)
        toolbar.setStyleSheet("""
            background: rgba(255, 255, 255, 0.95);
            border-bottom: 1px solid rgba(0, 0, 0, 0.06);
        """)

        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(20, 10, 20, 10)
        toolbar_layout.setSpacing(15)

        # 返回按钮
        back_btn = QPushButton('← 返回')
        back_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.22);
                border: 1px solid rgba(0, 0, 0, 0.06);
                color: #2c3e50;
                border-radius: 10px;
                padding: 8px 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.32);
            }
        """)
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(self.goto_menu.emit)
        toolbar_layout.addWidget(back_btn)

        # 标题
        title_label = QLabel('AI 图像识别助手')
        title_font = QFont('Microsoft YaHei', 20, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet('color: #2c3e50;')
        toolbar_layout.addWidget(title_label)

        toolbar_layout.addStretch()

        chat_layout.addWidget(toolbar)

        # 消息区域
        self.messages_scroll = QScrollArea()
        self.messages_scroll.setWidgetResizable(True)
        self.messages_scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
        """)
        self.messages_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.messages_container = QWidget()
        self.messages_container.setStyleSheet('background: transparent;')
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.messages_layout.setSpacing(18)
        self.messages_layout.setContentsMargins(30, 30, 30, 30)
        self.messages_layout.addStretch()

        self.messages_scroll.setWidget(self.messages_container)
        chat_layout.addWidget(self.messages_scroll, stretch=1)

        # 输入区域
        input_panel = QFrame()
        input_panel.setFixedHeight(100)
        input_panel.setStyleSheet("""
            background: rgba(255, 255, 255, 0.96);
            border-top: 1px solid rgba(0, 0, 0, 0.06);
        """)

        input_layout = QHBoxLayout(input_panel)
        input_layout.setContentsMargins(24, 20, 24, 20)
        input_layout.setSpacing(20)

        # 文件选择按钮
        self.file_btn = QPushButton('选择图片')
        self.file_btn.setStyleSheet("""
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
        """)
        self.file_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.file_btn.clicked.connect(self.select_file)
        input_layout.addWidget(self.file_btn)

        # 文件名显示
        self.file_label = QLabel('未选择文件')
        self.file_label.setStyleSheet('color: #666; font-size: 14px;')
        input_layout.addWidget(self.file_label, stretch=1)

        # 发送按钮
        self.send_btn = QPushButton('发送图片')
        self.send_btn.setFixedSize(120, 50)
        self.send_btn.setStyleSheet(AppStyles.get_primary_button_style())
        self.send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.send_btn.clicked.connect(self.send_image)
        self.send_btn.setEnabled(False)
        input_layout.addWidget(self.send_btn)

        chat_layout.addWidget(input_panel)

        main_layout.addWidget(chat_area, stretch=1)

    def select_file(self):
        """选择图片文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            '选择图片',
            '',
            '图片文件 (*.png *.jpg *.jpeg *.gif *.bmp);;所有文件 (*)'
        )

        if file_path:
            self.selected_file = file_path
            file_name = file_path.split('/')[-1]
            self.file_label.setText(file_name)
            self.send_btn.setEnabled(True)

    def send_image(self):
        """发送图片进行识别"""
        if not self.selected_file:
            QMessageBox.warning(self, '提示', '请先选择图片')
            return

        # 添加用户消息
        file_name = self.selected_file.split('/')[-1]
        user_bubble = ImageMessageBubble(
            'user',
            f'已上传图片: {file_name}',
            self.selected_file
        )
        self.add_message_bubble_widget(user_bubble)

        # 禁用发送按钮
        self.send_btn.setEnabled(False)
        self.send_btn.setText('识别中...')

        try:
            # 读取文件并创建 multipart 请求
            boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'

            with open(self.selected_file, 'rb') as f:
                file_data = f.read()

            # 构建 multipart body
            body = (
                f'------WebKitFormBoundary7MA4YWxkTrZu0gW\r\n'
                f'Content-Disposition: form-data; name="image"; filename="{file_name}"\r\n'
                f'Content-Type: image/jpeg\r\n\r\n'
            ).encode('utf-8') + file_data + b'\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--\r\n'

            content_type = f'multipart/form-data; boundary={boundary}'

            response = APIClient().post_form('/image/recognize', body, content_type)

            if response.is_success:
                class_name = response.data.get('class_name', '')
                if class_name:
                    ai_text = f'识别结果: {class_name}'
                else:
                    ai_text = f'[错误] {response.message or "识别失败"}'

                ai_bubble = ImageMessageBubble('assistant', ai_text)
                self.add_message_bubble_widget(ai_bubble)
            else:
                error_text = f'[错误] {response.message or "识别失败"}'
                ai_bubble = ImageMessageBubble('assistant', error_text)
                self.add_message_bubble_widget(ai_bubble)

        except Exception as e:
            error_text = f'[错误] 无法连接到服务器或上传失败: {str(e)}'
            ai_bubble = ImageMessageBubble('assistant', error_text)
            self.add_message_bubble_widget(ai_bubble)

        finally:
            # 恢复按钮状态
            self.send_btn.setEnabled(True)
            self.send_btn.setText('发送图片')

            # 清空选择
            self.selected_file = None
            self.file_label.setText('未选择文件')
            self.send_btn.setEnabled(False)

    def add_message_bubble_widget(self, bubble):
        """添加消息气泡组件"""
        # 创建容器来对齐消息
        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)

        if bubble.role == 'user':
            container_layout.addStretch()
            container_layout.addWidget(bubble)
        else:
            container_layout.addWidget(bubble)
            container_layout.addStretch()

        # 插入到 stretch 之前
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, container)

        # 滚动到底部
        from PyQt6.QtWidgets import QApplication
        QApplication.processEvents()
        self.messages_scroll.verticalScrollBar().setValue(
            self.messages_scroll.verticalScrollBar().maximum()
        )

    def cleanup(self):
        """清理资源"""
        pass
