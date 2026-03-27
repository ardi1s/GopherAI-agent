# GopherAI PyQt Client

基于 PyQt6 开发的 GopherAI 桌面客户端，完整替代 Vue 前端，保持一致的界面风格和全部功能特性。

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.4+-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

## ✨ 功能特性

### 用户认证
- ✅ 用户登录（支持 Token 持久化）
- ✅ 邮箱验证码注册（60秒倒计时）
- ✅ 自动登录状态保持

### AI 聊天
- ✅ 会话管理（创建、切换、删除、同步历史）
- ✅ 多模型支持（自动识别、阿里百炼、RAG、MCP）
- ✅ 流式响应模式（SSE 实时推送）
- ✅ 普通响应模式
- ✅ TTS 语音播放（支持轮询查询结果）
- ✅ 文档上传（.md / .txt）

### 图像识别
- ✅ 图片上传识别
- ✅ 支持多种图片格式（PNG、JPG、JPEG、GIF、BMP）

## 📋 环境要求

- **Python**: 3.8 或更高版本
- **操作系统**: Windows 10+ / macOS 10.14+ / Linux
- **后端服务**: 需要启动 GopherAI 后端服务

## 🚀 快速开始

### 一键启动（推荐）

#### macOS / Linux
```bash
cd pyqt-frontend
./launch.sh
```

#### Windows
```cmd
cd pyqt-frontend
launch.bat
```

#### 跨平台（Python）
```bash
cd pyqt-frontend
python3 launch.py
```

### 手动安装

如果你希望手动配置环境：

```bash
# 1. 进入项目目录
cd pyqt-frontend

# 2. 创建虚拟环境（推荐）
python3 -m venv venv

# 3. 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 启动应用
python start.py
```

## 📁 项目结构

```
pyqt-frontend/
├── main.py                      # 主入口，QStackedWidget 管理多视图
├── start.py                     # 启动脚本
├── launch.py                    # 一键启动器（跨平台 Python）
├── launch.sh                    # 一键启动脚本（Linux/macOS）
├── launch.bat                   # 一键启动脚本（Windows）
├── requirements.txt             # 依赖列表
├── README.md                    # 项目说明
├── utils/                       # 工具模块
│   ├── __init__.py
│   ├── api_client.py           # HTTP API 客户端
│   │                           # - 支持 GET/POST 请求
│   │                           # - 支持文件上传（multipart/form-data）
│   │                           # - 支持流式响应（SSE）
│   │                           # - TTS 轮询查询
│   └── styles.py               # 全局样式定义
│                               # - 渐变背景
│                               # - 按钮样式
│                               # - 输入框样式
│                               # - 滚动条样式
└── views/                       # 视图模块
    ├── __init__.py
    ├── login_view.py           # 登录界面
    ├── register_view.py        # 注册界面（含验证码倒计时）
    ├── menu_view.py            # 菜单导航界面
    ├── ai_chat_view.py         # AI 聊天界面
    │                           # - 会话列表管理
    │                           # - 消息气泡显示
    │                           # - 流式响应处理
    │                           # - TTS 播放
    └── image_recognition_view.py  # 图像识别界面
```

## ⚙️ 配置说明

### 修改后端 API 地址

编辑 `utils/api_client.py`：

```python
class APIConfig:
    BASE_URL = "http://localhost:8080"    # 修改为你的后端地址
    API_PREFIX = "/api"                    # API 前缀
    TIMEOUT = 30                           # 请求超时时间（秒）
```

### API 端点列表

| 端点 | 方法 | 说明 |
|------|------|------|
| `/user/login` | POST | 用户登录 |
| `/user/register` | POST | 用户注册 |
| `/user/captcha` | POST | 发送验证码 |
| `/AI/chat/sessions` | GET | 获取会话列表 |
| `/AI/chat/history` | POST | 获取会话历史 |
| `/AI/chat/send` | POST | 发送消息（已有会话） |
| `/AI/chat/send-new-session` | POST | 发送消息（新会话） |
| `/AI/chat/send-stream` | POST | 流式发送（已有会话） |
| `/AI/chat/send-stream-new-session` | POST | 流式发送（新会话） |
| `/AI/chat/tts` | POST | 创建 TTS 任务 |
| `/AI/chat/tts/query` | GET | 查询 TTS 结果 |
| `/file/upload` | POST | 上传文档 |
| `/image/recognize` | POST | 图像识别 |

## 🔧 核心实现

### 流式响应处理

使用 `StreamingAPIWorker`（QThread 子类）处理 SSE 流：

```python
class StreamingAPIWorker(QThread):
    data_received = pyqtSignal(str)      # 文本数据
    json_received = pyqtSignal(dict)     # JSON 数据
    finished_signal = pyqtSignal()       # 完成信号
    error_signal = pyqtSignal(str)       # 错误信号
```

### TTS 轮询查询

```python
class TTSQueryWorker(QThread):
    result_ready = pyqtSignal(str)       # 音频 URL
    error_signal = pyqtSignal(str)
    
    # 轮询策略：先等待 5 秒，然后每 2 秒查询一次，最多 30 次
```
## 🐛 常见问题

### Q: 提示 "command not found: python"

**A:** macOS/Linux 系统通常使用 `python3` 而不是 `python`，请使用：

```bash
python3 launch.py
```

或创建软链接：

```bash
ln -s $(which python3) /usr/local/bin/python
```

### Q: PyQt6 安装失败

**A:** 确保你的 Python 版本 >= 3.8，并尝试：

```bash
pip install --upgrade pip
pip install PyQt6
```

macOS 可能需要先安装 Qt 依赖：

```bash
brew install qt
```

### Q: 无法连接到后端

**A:** 
1. 检查后端服务是否已启动
2. 检查 `utils/api_client.py` 中的 `BASE_URL` 配置是否正确
3. 检查网络连接和防火墙设置

### Q: 流式响应不显示

**A:** 
1. 确保后端支持 SSE 流式输出
2. 检查浏览器/网络代理是否干扰
3. 查看控制台日志获取详细错误信息

## 🔮 未来扩展

- [ ] 系统托盘图标
- [ ] 全局快捷键（快速唤醒）
- [ ] 消息通知（系统通知中心）
- [ ] 主题切换（暗黑模式）
- [ ] 字体大小调整
- [ ] 聊天记录导出
- [ ] 多语言支持

## 🤝 贡献指南

欢迎提交 Issue 和 PR！

## 📄 许可证

MIT License

## 🙏 致谢

- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GUI 框架
- [GopherAI](https://github.com/your-org/gopherai) - 后端服务

---

**注意**: 首次运行时会自动创建虚拟环境并安装依赖，可能需要几分钟时间，请耐心等待。
