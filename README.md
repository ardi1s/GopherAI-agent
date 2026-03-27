# GopherAI

一个基于 Go + Vue.js 的智能对话系统，支持 RAG（检索增强生成）、MCP（模型调用协议）、多模型切换等功能。

## 功能特性

- 🤖 多模型支持：支持通义千问、Ollama 等多种大语言模型
- 📚 RAG 检索：基于 Redis Stack 的向量检索，支持文档问答
- 🔧 MCP 集成：支持调用外部工具（天气查询、时间查询等）
- 🎯 智能路由：自动识别用户意图，选择最优模型
- 💬 流式输出：支持 SSE 实时流式响应
- 🔐 JWT 认证：安全的用户认证机制
- 📱 响应式 UI：基于 Vue 3 的现代化前端
- 🐳 云原生支持：完整的 Docker 和 Kubernetes 部署方案

## 项目结构

```
GopherAI/
├── common/                   # 公共组件
│   ├── aihelper/            # AI 模型封装
│   ├── rag/                 # RAG 检索
│   ├── redis/               # Redis 客户端
│   ├── rabbitmq/            # RabbitMQ 客户端
│   ├── mysql/               # MySQL 客户端
│   ├── mcp/                 # MCP 客户端/服务器
│   └── ...
├── controller/               # 控制器层
├── service/                  # 服务层
│   ├── intent/              # 意图识别
│   └── session/             # 会话管理
├── dao/                      # 数据访问层
├── model/                    # 数据模型
├── router/                   # 路由配置
├── middleware/               # 中间件
├── config/                   # 配置文件
│   ├── config.toml.example  # 配置模板
│   └── config.docker.toml   # Docker 专用配置
├── vue-frontend/             # 前端代码
├── deploy/                   # 部署配置
│   ├── docker/              # Docker 配置
│   │   ├── Dockerfile       # 后端 Dockerfile
│   │   ├── Dockerfile.frontend # 前端 Dockerfile
│   │   ├── docker-compose.yml   # 生产环境
│   │   ├── docker-compose.dev.yml # 开发环境
│   │   └── .dockerignore
│   ├── k8s/                 # Kubernetes 配置
│   │   ├── namespace.yaml
│   │   ├── secret.yaml
│   │   ├── configmap.yaml
│   │   ├── mysql.yaml
│   │   ├── redis.yaml
│   │   ├── rabbitmq.yaml
│   │   ├── backend.yaml
│   │   ├── frontend.yaml
│   │   ├── ingress.yaml
│   │   └── kustomization.yaml
│   └── Makefile            # 部署脚本
└── main.go                   # 入口文件
```

## 快速开始（Docker 部署）

### 环境要求

- Docker Desktop 4.0+
- Docker Compose 2.0+

### 1. 配置 Docker 镜像源（国内用户）

编辑 Docker 配置文件：

```bash
# 编辑 daemon.json
nano ~/.docker/daemon.json
```

添加以下内容：

```json
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io"
  ]
}
```

重启 Docker Desktop 使配置生效。

### 2. 克隆项目

```bash
git clone <your-repo-url>
cd GopherAI-v2
```

### 3. 启动服务

```bash
# 进入部署目录
cd deploy/docker

# 启动所有服务（后台运行）
docker-compose up -d
```

### 4. 访问服务

- **前端页面**: http://localhost
- **后端 API**: http://localhost:9091
- **RabbitMQ 管理界面**: http://localhost:15672 (账号: admin / 密码: admin123)

### 5. 停止服务

```bash
# 停止所有服务（保留数据）
cd deploy/docker
docker-compose down

# 启动已停止的服务
docker-compose up -d

# 停止并删除容器+数据（慎用）
docker-compose down -v
```

## Redis 高可用架构

项目采用 **RDB + AOF 混合持久化 + Sentinel 主从架构**：

```
┌─────────────┐     主从复制      ┌─────────────┐
│ Redis Master │ ─────────────► │ Redis Slave  │
│   (主节点)   │                 │   (从节点)   │
└──────┬──────┘                 └─────────────┘
       │
       │ 监控
       ▼
┌─────────────┐
│Redis Sentinel│  自动故障转移
│   (哨兵)    │
└─────────────┘
```

**特性**：
- **RDB 快照持久化**：后台定时保存，数据快速恢复
- **AOF 日志持久化**：每秒同步，最大限度防止数据丢失
- **主从自动同步**：从节点实时同步主节点数据
- **Sentinel 自动故障转移**：主节点宕机时自动提升从节点为新主节点

## 本地开发环境

### 环境要求

- Go 1.24+
- Node.js 18+
- Redis Stack 7.2+
- MySQL 8.0+
- RabbitMQ 3.12+

### 1. 启动基础设施

```bash
# 使用 Docker Compose 启动基础设施（MySQL、Redis、RabbitMQ）
make dev-up

# 或者手动启动
redis-stack-server
mysql -u root -p
rabbitmq-server
```

### 2. 安装依赖

```bash
# 安装 Go 依赖
go mod download

# 安装前端依赖
cd vue-frontend
npm install
```

### 3. 配置项目

```bash
# 复制配置文件模板
cp config/config.toml.example config/config.toml

# 编辑配置文件，填入你的 API Key 和数据库配置
vim config/config.toml
```

**重要配置项：**

- `apiKey`: 阿里百炼 API Key（从 https://dashscope.console.aliyun.com/ 获取）
- `email`: 用于发送验证码的邮箱
- `authcode`: QQ 邮箱授权码
- `mysqlConfig`: MySQL 数据库配置
- `redisConfig`: Redis 配置

### 4. 启动服务

```bash
# 方式一：使用启动脚本
./start-local.sh

# 方式二：手动启动
# 1. 启动后端
go run main.go

# 2. 启动前端（新终端）
cd vue-frontend
npm run serve
```

访问 http://localhost:8080 即可使用。

## Kubernetes 部署

### 1. 修改配置

```bash
# 编辑 deploy/k8s/secret.yaml，填入真实的密钥和 API Key
vim deploy/k8s/secret.yaml
```

### 2. 部署到 Kubernetes

```bash
# 部署到 Kubernetes
make deploy-k8s

# 查看部署状态
make k8s-status

# 查看日志
make k8s-logs-backend
make k8s-logs-frontend

# 本地端口转发测试
make k8s-port-forward-frontend  # 访问 http://localhost:8080
make k8s-port-forward-backend   # 访问 http://localhost:9090
```

### 3. Kubernetes 架构

```
Namespace: gopherai
├── ConfigMap
│   ├── gopherai-config       # 应用配置
│   └── gopherai-nginx-config # Nginx 配置
├── Secret
│   └── gopherai-secrets      # 敏感信息
├── Deployment
│   ├── gopherai-mysql        # MySQL 数据库
│   ├── gopherai-redis        # Redis 缓存
│   ├── gopherai-rabbitmq     # RabbitMQ 消息队列
│   ├── gopherai-backend      # 后端服务 (2+ 副本)
│   └── gopherai-frontend     # 前端服务 (2+ 副本)
├── Service
│   ├── gopherai-mysql
│   ├── gopherai-redis
│   ├── gopherai-rabbitmq
│   ├── gopherai-backend
│   └── gopherai-frontend
├── PersistentVolumeClaim
│   ├── mysql-pvc
│   ├── redis-pvc
│   └── rabbitmq-pvc
├── HorizontalPodAutoscaler
│   ├── gopherai-backend-hpa  # 自动扩缩容 2-10 副本
│   └── gopherai-frontend-hpa # 自动扩缩容 2-5 副本
└── Ingress
    ├── gopherai-ingress      # 生产环境（HTTPS）
    └── gopherai-ingress-local # 本地测试
```

## 常用命令

```bash
cd deploy

# Docker Compose
make docker-compose-up      # 启动完整环境
make docker-compose-down     # 停止环境
make docker-compose-logs    # 查看日志
make docker-compose-build   # 重新构建并启动

# 开发环境
make dev-up                # 启动基础设施
make dev-down             # 停止基础设施

# Kubernetes
make deploy-k8s            # 部署到 K8s
make delete-k8s            # 从 K8s 删除
make k8s-status            # 查看状态
make k8s-logs-backend     # 查看后端日志
make k8s-logs-frontend    # 查看前端日志

# 构建
make build                 # 构建所有镜像
make build-backend         # 仅构建后端
make build-frontend        # 仅构建前端
make push                  # 推送镜像

# 清理
make clean                # 清理 Docker 资源
```

## 核心功能说明

### 1. 意图识别路由

系统会自动识别用户意图，选择最优模型：

- **普通聊天**：直接调用大模型
- **RAG 检索**：用户询问文档内容时，自动检索相关文档
- **MCP 工具**：用户查询天气、时间时，自动调用工具
- **联动模式**：同时需要文档和工具时，执行 RAG+MCP 联动

示例：
```
用户：帮我查一下文档里的代码架构，然后告诉我明天天气怎么样
→ 自动触发 RAG+MCP 联动工作流
```

### 2. RAG 检索增强

- 使用 Redis Stack 的向量检索功能
- 支持多种文档格式（PDF、Word、Markdown 等）
- 自动切片、向量化、索引

### 3. MCP 工具调用

- 支持 Function Calling
- 可扩展自定义工具
- 内置天气查询、时间查询等工具

## 常见问题

### Q: Docker 镜像拉取失败？

A: 配置国内镜像源：

```bash
# 编辑 ~/.docker/daemon.json
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io"
  ]
}
```

重启 Docker Desktop 后重试。

### Q: 端口被占用？

A: 修改 `deploy/docker/docker-compose.yml` 中的端口映射：

```yaml
ports:
  - "9091:9090"  # 将主机端口从 9090 改为 9091
```

### Q: 如何获取 API Key？

A: 访问 [阿里百炼控制台](https://dashscope.console.aliyun.com/) 注册并获取。

### Q: Redis Stack 如何安装？

A:
```bash
# macOS
brew install redis-stack

# Docker
docker run -d -p 6379:6379 redis/redis-stack-server:latest
```

### Q: 前端无法连接后端？

A: 检查：
1. 后端是否在 9090 端口运行
2. 前端 API 配置是否正确
3. CORS 是否配置

### Q: Kubernetes 部署失败？

A: 检查：
1. 是否正确修改了 `deploy/k8s/secret.yaml` 中的密钥
2. 是否有足够的存储类（StorageClass）
3. Ingress Controller 是否已安装（如 Nginx Ingress）

```bash
# 检查 Ingress Controller
kubectl get pods -n ingress-nginx

# 如果没有，安装 Nginx Ingress
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml
```

## License

MIT License

## 联系方式

如有问题，请提交 Issue 或联系开发者。
