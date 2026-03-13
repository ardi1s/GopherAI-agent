#!/bin/bash

# GopherAI 本地开发环境一键启动脚本

echo "🚀 GopherAI 本地开发环境启动脚本"
echo "=================================="

# 检查并启动 MySQL
echo "📦 检查 MySQL 状态..."
if ! brew services list | grep mysql | grep "started" > /dev/null; then
    echo "  启动 MySQL..."
    brew services start mysql
    sleep 3
else
    echo "  MySQL 已运行 ✓"
fi

# 检查并启动 Redis
echo "📦 检查 Redis 状态..."
if ! brew services list | grep redis | grep "started" > /dev/null; then
    echo "  启动 Redis..."
    brew services start redis
    sleep 2
else
    echo "  Redis 已运行 ✓"
fi

# 检查并启动 RabbitMQ
echo "📦 检查 RabbitMQ 状态..."
if ! brew services list | grep rabbitmq | grep "started" > /dev/null; then
    echo "  启动 RabbitMQ..."
    brew services start rabbitmq
    sleep 3
else
    echo "  RabbitMQ 已运行 ✓"
fi

# 检查数据库是否存在
echo "🗄️  检查数据库..."
if ! mysql -u root -e "USE GopherAI" 2>/dev/null; then
    echo "  创建数据库 GopherAI..."
    mysql -u root -e "CREATE DATABASE IF NOT EXISTS GopherAI CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    echo "  数据库创建成功 ✓"
else
    echo "  数据库已存在 ✓"
fi

# 修改配置文件（将 rabbitmq host 从 "rabbitmq" 改为 "127.0.0.1"）
echo "⚙️  检查配置文件..."
if grep -q 'host= "rabbitmq"' config/config.toml; then
    echo "  修改 RabbitMQ 配置..."
    sed -i '' 's/host= "rabbitmq"/host= "127.0.0.1"/' config/config.toml
    echo "  配置修改完成 ✓"
else
    echo "  配置已正确设置 ✓"
fi

echo ""
echo "✅ 环境准备完成！"
echo ""
echo "📝 服务状态:"
echo "  - MySQL:    localhost:3306"
echo "  - Redis:    localhost:6379"
echo "  - RabbitMQ: localhost:5672"
echo ""
echo "🚀 启动 GopherAI 服务..."
echo "=================================="
go run main.go
