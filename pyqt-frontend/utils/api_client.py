#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 客户端
处理与后端的所有 HTTP 通信
"""

import json
import urllib.request
import urllib.error
import urllib.parse
from typing import Optional, Dict, Any, Callable
from PyQt6.QtCore import QObject, pyqtSignal, QThread


class APIConfig:
    """API 配置"""
    BASE_URL = "http://localhost:8080"  # 根据实际后端地址修改
    API_PREFIX = "/api"
    TIMEOUT = 30  # 秒


class APIResponse:
    """API 响应包装类"""
    def __init__(self, data: dict, status_code: int = 200):
        self.data = data
        self.status_code = status_code
    
    @property
    def is_success(self) -> bool:
        return self.data.get('status_code') == 1000
    
    @property
    def message(self) -> str:
        return self.data.get('status_msg', '')


class APIClient(QObject):
    """API 客户端"""
    
    # 信号
    request_finished = pyqtSignal(object)  # APIResponse
    request_error = pyqtSignal(str)
    
    _instance = None
    _token = ""
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        super().__init__()
    
    @classmethod
    def set_token(cls, token: str):
        cls._token = token
    
    @classmethod
    def get_token(cls) -> str:
        return cls._token
    
    @classmethod
    def clear_token(cls):
        cls._token = ""
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        is_json: bool = True
    ) -> APIResponse:
        """发送 HTTP 请求"""
        url = f"{APIConfig.BASE_URL}{APIConfig.API_PREFIX}{endpoint}"
        
        # 准备 headers
        req_headers = {
            'Accept': 'application/json',
        }
        
        if is_json:
            req_headers['Content-Type'] = 'application/json'
        
        # 添加认证 token
        if self._token:
            req_headers['Authorization'] = f'Bearer {self._token}'
        
        # 合并自定义 headers
        if headers:
            req_headers.update(headers)
        
        # 准备请求数据
        req_data = None
        if data:
            if is_json:
                req_data = json.dumps(data).encode('utf-8')
            else:
                req_data = data
        
        # 创建请求
        request = urllib.request.Request(
            url,
            data=req_data,
            headers=req_headers,
            method=method
        )
        
        try:
            response = urllib.request.urlopen(request, timeout=APIConfig.TIMEOUT)
            response_data = json.loads(response.read().decode('utf-8'))
            return APIResponse(response_data, response.getcode())
        except urllib.error.HTTPError as e:
            if e.code == 401:
                self.clear_token()
            error_data = json.loads(e.read().decode('utf-8')) if e.read() else {}
            return APIResponse(error_data, e.code)
        except Exception as e:
            raise e
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> APIResponse:
        """GET 请求"""
        if params:
            query_string = urllib.parse.urlencode(params)
            endpoint = f"{endpoint}?{query_string}"
        return self._make_request('GET', endpoint)
    
    def post(self, endpoint: str, data: Optional[Dict] = None) -> APIResponse:
        """POST 请求"""
        return self._make_request('POST', endpoint, data)
    
    def post_form(self, endpoint: str, data: bytes, content_type: str) -> APIResponse:
        """POST 表单数据"""
        headers = {'Content-Type': content_type}
        return self._make_request('POST', endpoint, data, headers, is_json=False)


# 便捷函数
def api_get(endpoint: str, params: Optional[Dict] = None) -> APIResponse:
    return APIClient().get(endpoint, params)

def api_post(endpoint: str, data: Optional[Dict] = None) -> APIResponse:
    return APIClient().post(endpoint, data)


def api_post_form(endpoint: str, data: bytes, content_type: str) -> APIResponse:
    return APIClient().post_form(endpoint, data, content_type)


class StreamingAPIWorker(QThread):
    """流式 API 请求工作线程"""
    
    data_received = pyqtSignal(str)  # 接收到的数据
    json_received = pyqtSignal(dict)  # 接收到的 JSON 数据
    finished_signal = pyqtSignal()  # 完成信号
    error_signal = pyqtSignal(str)  # 错误信号
    
    def __init__(self, endpoint: str, data: dict):
        super().__init__()
        self.endpoint = endpoint
        self.data = data
        self._is_running = True
    
    def run(self):
        """执行流式请求"""
        url = f"{APIConfig.BASE_URL}{APIConfig.API_PREFIX}{self.endpoint}"
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream',
        }
        
        if APIClient._token:
            headers['Authorization'] = f'Bearer {APIClient._token}'
        
        request = urllib.request.Request(
            url,
            data=json.dumps(self.data).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        try:
            response = urllib.request.urlopen(request, timeout=APIConfig.TIMEOUT)
            
            buffer = ""
            while self._is_running:
                chunk = response.read(1024).decode('utf-8')
                if not chunk:
                    break
                
                buffer += chunk
                lines = buffer.split('\n')
                buffer = lines.pop() if lines else ""
                
                for line in lines:
                    line = line.strip()
                    if line.startswith('data:'):
                        data = line[5:].strip()
                        
                        if data == '[DONE]':
                            self.finished_signal.emit()
                            return
                        
                        # 尝试解析 JSON
                        if data.startswith('{'):
                            try:
                                json_data = json.loads(data)
                                self.json_received.emit(json_data)
                            except:
                                self.data_received.emit(data)
                        else:
                            self.data_received.emit(data)
            
            self.finished_signal.emit()
            
        except Exception as e:
            self.error_signal.emit(str(e))
    
    def stop(self):
        """停止请求"""
        self._is_running = False
        self.wait(1000)


class TTSQueryWorker(QThread):
    """TTS 查询工作线程"""
    
    result_ready = pyqtSignal(str)  # 音频 URL
    error_signal = pyqtSignal(str)
    
    def __init__(self, task_id: str):
        super().__init__()
        self.task_id = task_id
        self.max_attempts = 30
        self.poll_interval = 2  # 秒
    
    def run(self):
        """轮询查询 TTS 结果"""
        import time
        
        # 先等待 5 秒
        time.sleep(5)
        
        for attempt in range(self.max_attempts):
            try:
                response = api_get('/AI/chat/tts/query', {'task_id': self.task_id})
                
                if response.is_success:
                    task_status = response.data.get('task_status')
                    
                    if task_status == 'Success':
                        task_result = response.data.get('task_result', '')
                        self.result_ready.emit(task_result)
                        return
                    elif task_status in ['Running', 'Created']:
                        time.sleep(self.poll_interval)
                        continue
                    else:
                        self.error_signal.emit('语音合成失败')
                        return
                else:
                    time.sleep(self.poll_interval)
                    
            except Exception as e:
                time.sleep(self.poll_interval)
        
        self.error_signal.emit('语音合成超时')
