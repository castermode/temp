#!/bin/bash

# Mem0 HTTP 服务器启动脚本

echo "============================================================"
echo "🚀 启动 Mem0 HTTP 服务器"
echo "============================================================"

# 检查环境变量
if [ -z "$GPT_41_NANO_KEY" ]; then
    echo "⚠️  警告: 环境变量 GPT_41_NANO_KEY 未设置"
    echo "请运行: export GPT_41_NANO_KEY='your-api-key'"
fi

if [ -z "$TEXT_EMBEDDING_3_SMALL" ]; then
    echo "⚠️  警告: 环境变量 TEXT_EMBEDDING_3_SMALL 未设置"
    echo "请运行: export TEXT_EMBEDDING_3_SMALL='your-api-key'"
fi

# 初始化目录结构
echo ""
echo "初始化数据库目录..."
mkdir -p memorydb/history
mkdir -p memorydb/vector
mkdir -p memorydb/graph
echo "✅ 目录结构已准备就绪"

# 检查依赖
echo ""
echo "检查依赖..."
python -c "import fastapi" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ FastAPI 未安装"
    echo "正在安装依赖..."
    pip install -r requirements_server.txt
fi

# 启动服务器
echo ""
echo "============================================================"
echo "✅ 启动服务器..."
echo "============================================================"
echo ""
echo "📖 API 文档: http://localhost:8000/docs"
echo "🔍 健康检查: http://localhost:8000/health"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "============================================================"
echo ""

# 运行服务器
python mem0_server.py

