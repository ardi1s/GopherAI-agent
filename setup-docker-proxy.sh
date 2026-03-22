#!/bin/bash

# Docker 代理配置脚本
# 代理地址：http://127.0.0.1:7890

PROXY_URL="http://127.0.0.1:7890"

echo "配置 Docker 代理..."

# 创建 Docker 配置目录
mkdir -p ~/.docker

# 配置 Docker 客户端代理
cat > ~/.docker/config.json << EOF
{
  "proxies": {
    "default": {
      "httpProxy": "${PROXY_URL}",
      "httpsProxy": "${PROXY_URL}",
      "noProxy": "localhost,127.0.0.1,.local"
    }
  }
}
EOF

echo "Docker 客户端代理配置完成！"
echo "配置文件位置：~/.docker/config.json"
echo ""
echo "请重启 Docker Desktop 使配置生效："
echo "1. 点击屏幕顶部 Docker 图标"
echo "2. 选择 Quit Docker Desktop"
echo "3. 重新打开 Docker Desktop"
