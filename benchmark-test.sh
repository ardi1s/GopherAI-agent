#!/bin/bash

# GopherAI 性能测试一键脚本（仅需Redis）

echo "🚀 GopherAI 性能测试脚本"
echo "=================================="

# 检查并启动 Redis
echo "📦 检查 Redis 状态..."
if ! brew services list | grep redis | grep "started" > /dev/null; then
    echo "  启动 Redis..."
    brew services start redis
    sleep 2
else
    echo "  Redis 已运行 ✓"
fi

echo ""
echo "✅ Redis 准备完成！"
echo ""
echo "🧪 开始运行性能测试..."
echo "=================================="

cd "$(dirname "$0")"
go test -bench=. -benchmem ./benchmark/ -v

echo ""
echo "✅ 性能测试完成！"
echo "📊 查看详细报告: benchmark/performance_report.md"
