.PHONY: build build-backend build-frontend push push-backend push-frontend deploy deploy-k8s clean docker-compose-up docker-compose-down help

# 基础路径
ROOT_DIR := $(shell cd ../ && pwd)
DC_DIR := $(ROOT_DIR)/deploy/docker

# 镜像配置
REGISTRY ?= docker.io
BACKEND_IMAGE ?= gopherai/backend
FRONTEND_IMAGE ?= gopherai/frontend
TAG ?= latest

# 构建所有镜像
build: build-backend build-frontend

# 构建后端镜像
build-backend:
	cd $(ROOT_DIR) && docker build -t $(BACKEND_IMAGE):$(TAG) -f $(DC_DIR)/Dockerfile .

# 构建前端镜像
build-frontend:
	cd $(ROOT_DIR) && docker build -t $(FRONTEND_IMAGE):$(TAG) -f $(DC_DIR)/Dockerfile.frontend $(ROOT_DIR)/vue-frontend

# 推送所有镜像
push: push-backend push-frontend

# 推送后端镜像
push-backend:
	docker push $(BACKEND_IMAGE):$(TAG)

# 推送前端镜像
push-frontend:
	docker push $(FRONTEND_IMAGE):$(TAG)

# 标记镜像为最新版本
tag-latest:
	docker tag $(BACKEND_IMAGE):$(TAG) $(BACKEND_IMAGE):latest
	docker tag $(FRONTEND_IMAGE):$(TAG) $(FRONTEND_IMAGE):latest

# Docker Compose 命令
docker-compose-up:
	cd $(DC_DIR) && docker-compose up -d

docker-compose-down:
	cd $(DC_DIR) && docker-compose down

docker-compose-logs:
	cd $(DC_DIR) && docker-compose logs -f

docker-compose-build:
	cd $(DC_DIR) && docker-compose up -d --build

# 开发环境（仅基础设施）
dev-up:
	cd $(DC_DIR) && docker-compose -f docker-compose.dev.yml up -d

dev-down:
	cd $(DC_DIR) && docker-compose -f docker-compose.dev.yml down

# Kubernetes 部署
deploy-k8s:
	cd $(ROOT_DIR)/deploy/k8s && kubectl apply -k .

# 删除 K8s 部署
delete-k8s:
	cd $(ROOT_DIR)/deploy/k8s && kubectl delete -k .

# 查看 K8s 状态
k8s-status:
	kubectl get all -n gopherai

# 查看 K8s 日志
k8s-logs-backend:
	kubectl logs -l app=gopherai-backend -n gopherai --tail=100 -f

k8s-logs-frontend:
	kubectl logs -l app=gopherai-frontend -n gopherai --tail=100 -f

# 端口转发（本地测试）
k8s-port-forward-backend:
	kubectl port-forward svc/gopherai-backend 9090:9090 -n gopherai

k8s-port-forward-frontend:
	kubectl port-forward svc/gopherai-frontend 8080:80 -n gopherai

# 清理
clean:
	docker system prune -f
	docker volume prune -f

# 帮助
help:
	@echo "Available targets:"
	@echo "  build              - Build all Docker images"
	@echo "  build-backend      - Build backend Docker image"
	@echo "  build-frontend     - Build frontend Docker image"
	@echo "  push               - Push all Docker images"
	@echo "  docker-compose-up  - Start with Docker Compose"
	@echo "  docker-compose-down- Stop Docker Compose"
	@echo "  dev-up             - Start dev environment (infra only)"
	@echo "  deploy-k8s         - Deploy to Kubernetes"
	@echo "  delete-k8s         - Delete from Kubernetes"
	@echo "  k8s-status         - Check Kubernetes status"
	@echo "  clean              - Clean up Docker resources"
