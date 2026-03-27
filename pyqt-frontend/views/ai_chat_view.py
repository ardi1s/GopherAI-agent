#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 聊天界面
保持与 Vue 版本一致的视觉风格
"""

import re
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QListWidget, QListWidgetItem, QTextEdit, QComboBox,
    QCheckBox, QFileDialog, QMessageBox, QScrollArea, QSizePolicy,
    QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, pyqtSlot, QUrl
from PyQt6.QtGui import QFont, QPalette, QColor, QDesktopServices

from utils.styles import AppStyles
from utils.api_client import (
    api_get, api_post, StreamingAPIWorker, TTSQueryWorker
)


class MessageBubble(QFrame):
    """消息气泡组件"""

    def __init__(self, role, content, parent=None):
        super().__init__(parent)
        self.role = role
        self.content = content
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

        # AI 消息添加 TTS 按钮
        if self.role == 'assistant':
            self.tts_btn = QPushButton('🔊')
            self.tts_btn.setFixedSize(32, 32)
            self.tts_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #67c23a, stop:1 #409eff);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #5daf34, stop:1 #3a8ee6);
                }
            """)
            self.tts_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.tts_btn.clicked.connect(self.play_tts)
            header_layout.addWidget(self.tts_btn)
            header_layout.addStretch()
        else:
            header_layout.addStretch()

        layout.addLayout(header_layout)

        # 内容
        self.content_label = QLabel()
        self.content_label.setWordWrap(True)
        self.content_label.setTextFormat(Qt.TextFormat.RichText)
        self.content_label.setOpenExternalLinks(True)
        self.content_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextBrowserInteraction
        )

        content_font = QFont('Microsoft YaHei', 14)
        self.content_label.setFont(content_font)

        # 设置样式
        if self.role == 'user':
            self.content_label.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #667eea, stop:1 #764ba2);
                    color: white;
                    border-radius: 18px;
                    padding: 14px 18px;
                    line-height: 1.6;
                }
            """)
            self.setStyleSheet("""
                MessageBubble {
                    background: transparent;
                }
            """)
        else:
            self.content_label.setStyleSheet("""
                QLabel {
                    background: rgba(255, 255, 255, 0.95);
                    color: #2c3e50;
                    border-radius: 18px;
                    padding: 14px 18px;
                    line-height: 1.6;
                    border: 1px solid rgba(255, 255, 255, 0.3);
                }
            """)

        self.update_content(self.content)
        layout.addWidget(self.content_label)

        # 设置最大宽度
        self.setMaximumWidth(700)

    def update_content(self, content):
        """更新内容（支持 Markdown 简单渲染）"""
        self.content = content
        # 简单的 Markdown 渲染
        html = content
        html = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', html)  # 粗体
        html = re.sub(r'\*(.+?)\*', r'<i>\1</i>', html)     # 斜体
        html = re.sub(r'`(.+?)`', r'<code style="background:rgba(0,0,0,0.1);padding:2px 4px;border-radius:4px;">\1</code>', html)  # 代码
        html = html.replace('\n', '<br>')  # 换行
        self.content_label.setText(html)

    def play_tts(self):
        """播放语音"""
        if not self.content:
            return

        self.tts_btn.setEnabled(False)
        self.tts_btn.setText('⏳')

        try:
            response = api_post('/AI/chat/tts', {'text': self.content})

            if response.is_success:
                task_id = response.data.get('task_id')
                if task_id:
                    self.tts_worker = TTSQueryWorker(task_id)
                    self.tts_worker.result_ready.connect(self.on_tts_ready)
                    self.tts_worker.error_signal.connect(self.on_tts_error)
                    self.tts_worker.start()
                else:
                    QMessageBox.warning(self, '错误', '无法创建语音合成任务')
                    self.tts_btn.setEnabled(True)
                    self.tts_btn.setText('🔊')
            else:
                QMessageBox.warning(self, '错误', response.message or '请求语音接口失败')
                self.tts_btn.setEnabled(True)
                self.tts_btn.setText('🔊')

        except Exception as e:
            QMessageBox.critical(self, '错误', f'TTS 请求失败：{str(e)}')
            self.tts_btn.setEnabled(True)
            self.tts_btn.setText('🔊')

    def on_tts_ready(self, audio_url):
        """TTS 结果就绪"""
        self.tts_btn.setEnabled(True)
        self.tts_btn.setText('🔊')

        # 打开音频链接
        if audio_url:
            QDesktopServices.openUrl(QUrl(audio_url))

    def on_tts_error(self, error_msg):
        """TTS 错误"""
        self.tts_btn.setEnabled(True)
        self.tts_btn.setText('🔊')
        QMessageBox.warning(self, '错误', error_msg)


class AIChatView(QWidget):
    """AI 聊天视图"""

    goto_menu = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.sessions = {}
        self.current_session_id = None
        self.temp_session = False
        self.messages = []
        self.streaming_worker = None
        self.current_ai_bubble = None
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
        session_header.setFixedHeight(100)
        session_header.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(102,126,234,0.06), stop:1 rgba(103,194,58,0.06));
            border-bottom: 1px solid rgba(0, 0, 0, 0.06);
        """)

        header_layout = QVBoxLayout(session_header)
        header_layout.setContentsMargins(20, 20, 20, 20)
        header_layout.setSpacing(12)

        header_label = QLabel('会话列表')
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_font = QFont('Microsoft YaHei', 14, QFont.Weight.Bold)
        header_label.setFont(header_font)
        header_label.setStyleSheet('color: #2c3e50;')
        header_layout.addWidget(header_label)

        # 新聊天按钮
        new_chat_btn = QPushButton('＋ 新聊天')
        new_chat_btn.setStyleSheet(AppStyles.get_primary_button_style())
        new_chat_btn.setMinimumHeight(40)
        new_chat_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        new_chat_btn.clicked.connect(self.create_new_session)
        header_layout.addWidget(new_chat_btn)

        session_layout.addWidget(session_header)

        # 会话列表
        self.session_list = QListWidget()
        self.session_list.setStyleSheet(AppStyles.get_session_list_style())
        self.session_list.itemClicked.connect(self.on_session_selected)
        session_layout.addWidget(self.session_list)

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

        # 同步历史按钮
        self.sync_btn = QPushButton('同步历史数据')
        self.sync_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #67c23a, stop:1 #409eff);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 8px 14px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #5daf34, stop:1 #3a8ee6);
            }
            QPushButton:disabled {
                background: #cccccc;
            }
        """)
        self.sync_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.sync_btn.clicked.connect(self.sync_history)
        toolbar_layout.addWidget(self.sync_btn)

        toolbar_layout.addStretch()

        # 模型选择
        model_label = QLabel('选择模型：')
        model_label.setStyleSheet('color: #2c3e50; font-weight: 500;')
        toolbar_layout.addWidget(model_label)

        self.model_combo = QComboBox()
        self.model_combo.addItems(['🤖 自动识别', '阿里百炼', '阿里百炼 RAG', '阿里百炼 MCP'])
        self.model_combo.setCurrentIndex(1)  # 默认选择阿里百炼
        self.model_combo.setStyleSheet("""
            QComboBox {
                background: white;
                border: 1px solid rgba(0, 0, 0, 0.06);
                border-radius: 8px;
                padding: 6px 10px;
                color: #2c3e50;
                font-weight: 600;
                min-width: 120px;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox QAbstractItemView {
                background: white;
                border: 1px solid rgba(0, 0, 0, 0.06);
                selection-background-color: #667eea;
            }
        """)
        toolbar_layout.addWidget(self.model_combo)

        # 流式响应复选框
        self.streaming_check = QCheckBox('流式响应')
        self.streaming_check.setStyleSheet('color: #2c3e50;')
        toolbar_layout.addWidget(self.streaming_check)

        # 上传按钮
        self.upload_btn = QPushButton('📎 上传文档(.md/.txt)')
        self.upload_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f093fb, stop:1 #f5576c);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 8px 14px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #e083eb, stop:1 #e5475c);
            }
        """)
        self.upload_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.upload_btn.clicked.connect(self.upload_file)
        toolbar_layout.addWidget(self.upload_btn)

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
        input_panel.setFixedHeight(120)
        input_panel.setStyleSheet("""
            background: rgba(255, 255, 255, 0.96);
            border-top: 1px solid rgba(0, 0, 0, 0.06);
        """)

        input_layout = QHBoxLayout(input_panel)
        input_layout.setContentsMargins(24, 20, 24, 20)
        input_layout.setSpacing(15)

        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText('请输入你的问题...')
        self.message_input.setStyleSheet("""
            QTextEdit {
                background: rgba(255, 255, 255, 0.96);
                border: 2px solid rgba(0, 0, 0, 0.06);
                border-radius: 12px;
                padding: 12px 16px;
                font-size: 15px;
                color: #2c3e50;
            }
            QTextEdit:focus {
                border-color: #409eff;
            }
        """)
        self.message_input.setMaximumHeight(80)
        input_layout.addWidget(self.message_input, stretch=1)

        self.send_btn = QPushButton('发送')
        self.send_btn.setFixedSize(100, 50)
        self.send_btn.setStyleSheet(AppStyles.get_primary_button_style())
        self.send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_btn)

        chat_layout.addWidget(input_panel)

        main_layout.addWidget(chat_area, stretch=1)

        # 连接回车键发送
        self.message_input.installEventFilter(self)

    def eventFilter(self, obj, event):
        """事件过滤器，处理回车键发送"""
        if obj == self.message_input and event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_Return and not event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                self.send_message()
                return True
        return super().eventFilter(obj, event)

    def load_sessions(self):
        """加载会话列表"""
        try:
            response = api_get('/AI/chat/sessions')

            if response.is_success:
                sessions_data = response.data.get('sessions', [])
                self.sessions = {}
                self.session_list.clear()

                for session in sessions_data:
                    sid = str(session.get('sessionId', ''))
                    name = session.get('name', f'会话 {sid[:8]}...')
                    self.sessions[sid] = {
                        'id': sid,
                        'name': name,
                        'messages': []
                    }

                    item = QListWidgetItem(name)
                    item.setData(Qt.ItemDataRole.UserRole, sid)
                    self.session_list.addItem(item)

        except Exception as e:
            QMessageBox.warning(self, '错误', f'加载会话列表失败：{str(e)}')

    def create_new_session(self):
        """创建新会话"""
        self.current_session_id = 'temp'
        self.temp_session = True
        self.messages = []
        self.clear_messages()
        self.message_input.setFocus()

    def on_session_selected(self, item):
        """选择会话"""
        session_id = item.data(Qt.ItemDataRole.UserRole)
        if not session_id:
            return

        self.current_session_id = session_id
        self.temp_session = False

        # 加载历史消息
        self.switch_session(session_id)

    def switch_session(self, session_id):
        """切换会话"""
        try:
            response = api_post('/AI/chat/history', {'sessionId': session_id})

            if response.is_success:
                history = response.data.get('history', [])
                self.messages = []
                self.clear_messages()

                for item in history:
                    role = 'user' if item.get('is_user') else 'assistant'
                    content = item.get('content', '')
                    self.messages.append({'role': role, 'content': content})
                    self.add_message_bubble(role, content)

                # 更新会话存储
                if session_id in self.sessions:
                    self.sessions[session_id]['messages'] = self.messages.copy()

        except Exception as e:
            QMessageBox.warning(self, '错误', f'加载历史消息失败：{str(e)}')

    def sync_history(self):
        """同步历史数据"""
        if not self.current_session_id or self.temp_session:
            QMessageBox.warning(self, '提示', '请选择已有会话进行同步')
            return

        self.switch_session(self.current_session_id)

    def clear_messages(self):
        """清空消息显示"""
        # 移除所有消息气泡
        while self.messages_layout.count() > 1:  # 保留 stretch
            item = self.messages_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def add_message_bubble(self, role, content):
        """添加消息气泡"""
        bubble = MessageBubble(role, content)

        # 创建容器来对齐消息
        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)

        if role == 'user':
            container_layout.addStretch()
            container_layout.addWidget(bubble)
        else:
            container_layout.addWidget(bubble)
            container_layout.addStretch()

        # 插入到 stretch 之前
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, container)

        # 滚动到底部
        QApplication.processEvents()
        self.messages_scroll.verticalScrollBar().setValue(
            self.messages_scroll.verticalScrollBar().maximum()
        )

        return bubble

    def send_message(self):
        """发送消息"""
        content = self.message_input.toPlainText().strip()

        if not content:
            QMessageBox.warning(self, '提示', '请输入消息内容')
            return

        # 添加用户消息
        self.messages.append({'role': 'user', 'content': content})
        self.add_message_bubble('user', content)

        # 清空输入框
        self.message_input.clear()

        # 更新会话存储
        if not self.temp_session and self.current_session_id:
            if self.current_session_id in self.sessions:
                if not self.sessions[self.current_session_id].get('messages'):
                    self.sessions[self.current_session_id]['messages'] = []
                self.sessions[self.current_session_id]['messages'].append(
                    {'role': 'user', 'content': content}
                )

        # 禁用发送按钮
        self.send_btn.setEnabled(False)
        self.send_btn.setText('发送中...')

        # 检查是否流式响应
        if self.streaming_check.isChecked():
            self.handle_streaming_send(content)
        else:
            self.handle_normal_send(content)

    def handle_normal_send(self, question):
        """处理普通发送"""
        model_type = self.get_model_type()

        try:
            if self.temp_session:
                # 新会话
                response = api_post('/AI/chat/send-new-session', {
                    'question': question,
                    'modelType': model_type
                })

                if response.is_success:
                    session_id = str(response.data.get('sessionId', ''))
                    ai_content = response.data.get('Information', '')

                    # 更新会话
                    self.sessions[session_id] = {
                        'id': session_id,
                        'name': '新会话',
                        'messages': [
                            {'role': 'user', 'content': question},
                            {'role': 'assistant', 'content': ai_content}
                        ]
                    }

                    self.current_session_id = session_id
                    self.temp_session = False

                    # 添加到列表
                    item = QListWidgetItem('新会话')
                    item.setData(Qt.ItemDataRole.UserRole, session_id)
                    self.session_list.addItem(item)

                    # 显示 AI 回复
                    self.messages.append({'role': 'assistant', 'content': ai_content})
                    self.add_message_bubble('assistant', ai_content)

                    # 显示智能选择提示
                    used_model = response.data.get('usedModelType')
                    if used_model and model_type == 'auto':
                        model_names = {'1': '阿里百炼', '2': '阿里百炼 RAG', '3': '阿里百炼 MCP'}
                        QMessageBox.information(
                            self, '提示',
                            f"已智能选择模型：{model_names.get(used_model, used_model)}"
                        )
                else:
                    QMessageBox.warning(self, '错误', response.message or '发送失败')
                    self.messages.pop()
            else:
                # 已有会话
                response = api_post('/AI/chat/send', {
                    'question': question,
                    'modelType': model_type,
                    'sessionId': self.current_session_id
                })

                if response.is_success:
                    ai_content = response.data.get('Information', '')

                    # 更新会话存储
                    if self.current_session_id in self.sessions:
                        self.sessions[self.current_session_id]['messages'].append(
                            {'role': 'assistant', 'content': ai_content}
                        )

                    # 显示 AI 回复
                    self.messages.append({'role': 'assistant', 'content': ai_content})
                    self.add_message_bubble('assistant', ai_content)

                    # 显示智能选择提示
                    used_model = response.data.get('usedModelType')
                    if used_model and model_type == 'auto':
                        model_names = {'1': '阿里百炼', '2': '阿里百炼 RAG', '3': '阿里百炼 MCP'}
                        QMessageBox.information(
                            self, '提示',
                            f"已智能选择模型：{model_names.get(used_model, used_model)}"
                        )
                else:
                    QMessageBox.warning(self, '错误', response.message or '发送失败')
                    # 回滚
                    if self.current_session_id in self.sessions:
                        self.sessions[self.current_session_id]['messages'].pop()
                    self.messages.pop()

        except Exception as e:
            QMessageBox.critical(self, '错误', f'发送失败：{str(e)}')
            # 回滚
            if not self.temp_session and self.current_session_id in self.sessions:
                if self.sessions[self.current_session_id].get('messages'):
                    self.sessions[self.current_session_id]['messages'].pop()
            if self.messages:
                self.messages.pop()

        finally:
            self.send_btn.setEnabled(True)
            self.send_btn.setText('发送')

    def handle_streaming_send(self, question):
        """处理流式发送"""
        model_type = self.get_model_type()

        # 添加空的 AI 消息气泡
        self.current_ai_bubble = self.add_message_bubble('assistant', '')
        self.messages.append({'role': 'assistant', 'content': ''})

        if not self.temp_session and self.current_session_id:
            if self.current_session_id in self.sessions:
                if not self.sessions[self.current_session_id].get('messages'):
                    self.sessions[self.current_session_id]['messages'] = []
                self.sessions[self.current_session_id]['messages'].append(
                    {'role': 'assistant', 'content': ''}
                )

        # 确定端点
        if self.temp_session:
            endpoint = '/AI/chat/send-stream-new-session'
            data = {'question': question, 'modelType': model_type}
        else:
            endpoint = '/AI/chat/send-stream'
            data = {
                'question': question,
                'modelType': model_type,
                'sessionId': self.current_session_id
            }

        # 创建流式工作线程
        self.streaming_worker = StreamingAPIWorker(endpoint, data)
        self.streaming_worker.data_received.connect(self.on_stream_data)
        self.streaming_worker.json_received.connect(self.on_stream_json)
        self.streaming_worker.finished_signal.connect(self.on_stream_finished)
        self.streaming_worker.error_signal.connect(self.on_stream_error)
        self.streaming_worker.start()

    def on_stream_data(self, data):
        """接收流式数据"""
        if self.current_ai_bubble:
            current_content = self.current_ai_bubble.content
            new_content = current_content + data
            self.current_ai_bubble.update_content(new_content)

            # 更新消息列表
            if self.messages:
                self.messages[-1]['content'] = new_content

            # 滚动到底部
            self.messages_scroll.verticalScrollBar().setValue(
                self.messages_scroll.verticalScrollBar().maximum()
            )

    def on_stream_json(self, json_data):
        """接收 JSON 数据"""
        # 处理 sessionId
        if 'sessionId' in json_data:
            new_sid = str(json_data['sessionId'])
            if self.temp_session:
                self.sessions[new_sid] = {
                    'id': new_sid,
                    'name': '新会话',
                    'messages': self.messages.copy()
                }
                self.current_session_id = new_sid
                self.temp_session = False

                # 添加到列表
                item = QListWidgetItem('新会话')
                item.setData(Qt.ItemDataRole.UserRole, new_sid)
                self.session_list.addItem(item)

        # 处理 usedModelType
        if 'usedModelType' in json_data:
            used_model = json_data['usedModelType']
            if self.get_model_type() == 'auto':
                model_names = {'1': '阿里百炼', '2': '阿里百炼 RAG', '3': '阿里百炼 MCP'}
                QMessageBox.information(
                    self, '提示',
                    f"已智能选择模型：{model_names.get(used_model, used_model)}"
                )

    def on_stream_finished(self):
        """流式传输完成"""
        self.send_btn.setEnabled(True)
        self.send_btn.setText('发送')
        self.current_ai_bubble = None

        # 同步到会话存储
        if not self.temp_session and self.current_session_id:
            if self.current_session_id in self.sessions:
                if self.messages:
                    self.sessions[self.current_session_id]['messages'][-1]['content'] = \
                        self.messages[-1]['content']

    def on_stream_error(self, error_msg):
        """流式传输错误"""
        self.send_btn.setEnabled(True)
        self.send_btn.setText('发送')
        QMessageBox.warning(self, '错误', f'流式传输出错：{error_msg}')

        # 回滚
        if not self.temp_session and self.current_session_id in self.sessions:
            if self.sessions[self.current_session_id].get('messages'):
                self.sessions[self.current_session_id]['messages'].pop()
        if self.messages:
            self.messages.pop()

        # 移除 AI 气泡
        if self.current_ai_bubble:
            # 找到并移除包含该气泡的容器
            for i in range(self.messages_layout.count() - 1):
                widget = self.messages_layout.itemAt(i).widget()
                if widget and self.current_ai_bubble in widget.findChildren(MessageBubble):
                    widget.deleteLater()
                    break

        self.current_ai_bubble = None

    def get_model_type(self):
        """获取选择的模型类型"""
        index = self.model_combo.currentIndex()
        model_types = ['auto', '1', '2', '3']
        return model_types[index]

    def upload_file(self):
        """上传文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            '选择文件',
            '',
            '文本文件 (*.md *.txt);;所有文件 (*)'
        )

        if not file_path:
            return

        # 检查文件类型
        if not (file_path.endswith('.md') or file_path.endswith('.txt')):
            QMessageBox.warning(self, '错误', '只允许上传 .md 或 .txt 文件')
            return

        try:
            from utils.api_client import APIClient

            # 读取文件并创建 multipart 请求
            import urllib.request
            import mimetypes

            boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'

            with open(file_path, 'rb') as f:
                file_data = f.read()

            file_name = file_path.split('/')[-1]

            # 构建 multipart body
            body = (
                f'------WebKitFormBoundary7MA4YWxkTrZu0gW\r\n'
                f'Content-Disposition: form-data; name="file"; filename="{file_name}"\r\n'
                f'Content-Type: text/plain\r\n\r\n'
            ).encode('utf-8') + file_data + b'\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--\r\n'

            content_type = f'multipart/form-data; boundary={boundary}'

            response = APIClient().post_form('/file/upload', body, content_type)

            if response.is_success:
                QMessageBox.information(self, '成功', '文件上传成功')
            else:
                QMessageBox.warning(self, '错误', response.message or '上传失败')

        except Exception as e:
            QMessageBox.critical(self, '错误', f'文件上传失败：{str(e)}')

    def cleanup(self):
        """清理资源"""
        if self.streaming_worker and self.streaming_worker.isRunning():
            self.streaming_worker.stop()
