#!/bin/bash
# Health Coach 前端一键启动脚本

echo "========================================"
echo "  基因健康教练 - 前端启动脚本"
echo "========================================"
echo ""

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python3"
    echo "请先安装 Python 3.8 或更高版本"
    exit 1
fi

echo "✓ Python 版本: $(python3 --version)"
echo ""

# 检查是否在虚拟环境中
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  警告: 未检测到虚拟环境"
    echo "建议在虚拟环境中运行此脚本"
    echo ""
    read -p "是否继续? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✓ 虚拟环境: $VIRTUAL_ENV"
    echo ""
fi

# 检查streamlit是否已安装
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "⚠️  Streamlit 未安装"
    echo "正在安装 Streamlit..."
    echo ""
    pip install streamlit
    echo ""
    if [ $? -eq 0 ]; then
        echo "✓ Streamlit 安装成功"
    else
        echo "❌ Streamlit 安装失败"
        exit 1
    fi
else
    echo "✓ Streamlit 已安装"
    echo ""
fi

# 检查frontend.py是否存在
if [ ! -f "frontend.py" ]; then
    echo "❌ 错误: 未找到 frontend.py 文件"
    echo "请确保在 health_coach 项目目录中运行此脚本"
    exit 1
fi

echo "========================================"
echo "  启动前端服务器..."
echo "========================================"
echo ""
echo "🌐 前端地址: http://localhost:8502"
echo "📱 局域网访问: http://$(hostname -I | awk '{print $1}'):8502"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""
echo "========================================"
echo ""

# 启动streamlit
python3 -m streamlit run frontend.py --server.port=8502
