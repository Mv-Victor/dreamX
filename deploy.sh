#!/bin/bash
# DreamX AI 剪辑项目 - 快速部署脚本

set -e

echo "=== DreamX AI 剪辑项目部署 ==="
echo ""

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

echo "✅ Docker 已安装"

# 检查环境变量
if [ ! -f ".env.cos" ]; then
    echo "❌ 未找到 .env.cos 文件"
    echo "请创建 .env.cos 文件并配置以下环境变量："
    echo "  export COS_APP_ID=your_app_id"
    echo "  export COS_SECRET_ID=your_secret_id"
    echo "  export COS_SECRET_KEY=your_secret_key"
    echo "  export COS_REGION=ap-shanghai"
    echo "  export COS_BUCKET=your_bucket_name"
    exit 1
fi

echo "✅ 找到 .env.cos 配置文件"

# 加载环境变量
source .env.cos

# 检查必需的环境变量
if [ -z "$COS_APP_ID" ] || [ -z "$COS_SECRET_ID" ] || [ -z "$COS_SECRET_KEY" ]; then
    echo "❌ COS 环境变量未配置完整"
    exit 1
fi

echo "✅ COS 环境变量已配置"

# 构建 Docker 镜像
echo ""
echo "开始构建 Docker 镜像..."
docker build -t dreamx-video:latest .

if [ $? -eq 0 ]; then
    echo "✅ Docker 镜像构建成功"
else
    echo "❌ Docker 镜像构建失败"
    exit 1
fi

# 停止并删除旧容器
if docker ps -a | grep -q dreamx-video; then
    echo ""
    echo "停止并删除旧容器..."
    docker stop dreamx-video 2>/dev/null || true
    docker rm dreamx-video 2>/dev/null || true
fi

# 启动新容器（不挂载 doc 目录，使用镜像内的素材库）
echo ""
echo "启动 Docker 容器..."
docker run -d \
  --name dreamx-video \
  -p 8081:17026 \
  -e COS_APP_ID=$COS_APP_ID \
  -e COS_SECRET_ID=$COS_SECRET_ID \
  -e COS_SECRET_KEY=$COS_SECRET_KEY \
  -e COS_REGION=$COS_REGION \
  -e COS_BUCKET=$COS_BUCKET \
  dreamx-video:latest

if [ $? -eq 0 ]; then
    echo "✅ Docker 容器启动成功"
    echo "📦 镜像已包含完整素材库（756 个表情包 + 76 个 BGM）"
    echo "⚠️  不要挂载 /app/doc 目录，否则会覆盖镜像内的素材"
else
    echo "❌ Docker 容器启动失败"
    exit 1
fi

# 等待服务启动
echo ""
echo "等待服务启动..."
sleep 5

# 检查服务健康状态
if curl -s http://localhost:8080/actuator/health > /dev/null; then
    echo "✅ 服务健康检查通过"
else
    echo "⚠️  服务可能还在启动中，请稍后检查"
fi

echo ""
echo "=== 部署完成 ==="
echo ""
echo "服务地址: http://localhost:8080"
echo "查看日志: docker logs -f dreamx-video"
echo "停止服务: docker stop dreamx-video"
echo ""
