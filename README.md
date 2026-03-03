# DreamX AI 剪辑项目 - 交付版本

## 项目简介

DreamX 是一个 AI 驱动的营销视频自动化生成系统，支持：
- 自动生成小红书爆款文案
- TTS 配音
- 表情包和 BGM 智能召回
- 生成剪映工程文件
- 上传腾讯云 COS

## 技术栈

- Java 21
- Spring Boot 3.5.8
- Maven 3.9.9
- edge-tts（TTS 配音）
- 腾讯云 COS

## 环境要求

### 必需
- Docker（用于运行服务）
- OpenClaw（AI Agent 框架）
- Claude API Key
- 腾讯云 COS 账号（需要以下信息）：
  - COS_APP_ID
  - COS_SECRET_ID
  - COS_SECRET_KEY
  - COS_REGION
  - COS_BUCKET

### 可选
- Mac Mini（推荐用于测试）

## 快速开始

### 1. 配置环境变量

创建 `.env.cos` 文件：

```bash
export COS_APP_ID=your_app_id
export COS_SECRET_ID=your_secret_id
export COS_SECRET_KEY=your_secret_key
export COS_REGION=ap-shanghai
export COS_BUCKET=your_bucket_name
```

### 2. 构建 Docker 镜像

```bash
docker build -t dreamx-video:latest .
```

### 3. 运行服务

```bash
# 加载环境变量
source .env.cos

# 运行容器
docker run -d \
  --name dreamx-video \
  -p 8080:8080 \
  -e COS_APP_ID=$COS_APP_ID \
  -e COS_SECRET_ID=$COS_SECRET_ID \
  -e COS_SECRET_KEY=$COS_SECRET_KEY \
  -e COS_REGION=$COS_REGION \
  -e COS_BUCKET=$COS_BUCKET \
  -v $(pwd)/doc:/app/doc \
  dreamx-video:latest
```

### 4. 测试视频生成

```bash
# 运行测试（千问奶茶示例）
source .env.cos
mvn test -Dtest=QianwenNaichaTest -pl duo-video-api
```

## 项目结构

```
dreamX/
├── duo-server-base/      # 基础服务模块
├── duo-video-base/       # 视频处理基础模块
├── duo-video-jy/         # 剪映工程构建模块
├── duo-video-api/        # REST API 模块
├── doc/                  # 素材库
│   ├── sale/            # 营销素材
│   ├── memes/           # 表情包库
│   ├── bgm/             # BGM 库
│   └── crawler/         # 素材爬取脚本
├── Dockerfile           # Docker 镜像配置
├── .env.cos             # COS 配置（需自行创建）
└── README.md            # 本文件
```

## API 接口

### 创建项目
```
POST /api/project
{
  "projectId": 200001,
  "projectName": "示例视频",
  "width": 1080,
  "height": 1920
}
```

### 添加图片
```
POST /api/project/image
{
  "projectId": 200001,
  "imageId": 200101,
  "imageUrl": "file:///app/doc/sale/example/1.png",
  "startTime": 0,
  "duration": 3000,
  "zoomX": 10000,
  "zoomY": 10000,
  "positionX": 0,
  "positionY": 0
}
```

### 添加音频
```
POST /api/project/audio
{
  "projectId": 200001,
  "audioId": 200201,
  "audioUrl": "file:///app/doc/bgm/example.mp3",
  "startTime": 0,
  "duration": 10000,
  "volume": -30
}
```

### 添加字幕
```
POST /api/project/text
{
  "projectId": 200001,
  "text": "示例字幕",
  "startTime": 0,
  "duration": 2000,
  "positionX": 0,
  "positionY": 750,
  "asSubtitle": true,
  "style": {
    "fontSize": 8,
    "bold": true,
    "textAlign": 1,
    "fontName": "抖音美好体",
    "fillColor": "#FFDE00",
    "strokeColor": "#000000",
    "strokeWidth": 60
  }
}
```

### 构建视频
```
POST /api/project/build
{
  "projectId": 200001
}
```

返回：
```json
{
  "code": 0,
  "data": 290956748376768513,
  "message": "success"
}
```

## OpenClaw Skill 集成

项目包含两个 skill：

### 1. dreamx-smart-editing（完整流程）
位置：`/root/.openclaw/workspace/skills/dreamx-smart-editing/`

功能：
- 接收素材（图片+音频+事件描述）
- 生成小红书爆款文案
- TTS 配音
- 表情包和 BGM 召回
- 构建剪映工程
- 上传 COS

### 2. dreamx-docker-video（Docker 镜像版）
位置：待创建

功能：
- 使用 Docker 镜像生成视频
- 简化部署流程
- 适合客户环境

## 素材库

### 表情包库
- 位置：`doc/memes/`
- 分类：shocked, funny, stonks, sad, angry 等
- 总数：756 个

### BGM 库
- 位置：`doc/bgm/`
- 分类：funny, action, chill, corporate 等
- 总数：76 个

### 元数据库
- 位置：`doc/crawler/media_library.db`
- 类型：SQLite
- 内容：表情包和 BGM 的标签、情绪、角色等元数据

## 测试示例

项目包含完整的测试用例：

1. **千问奶茶事件**（`QianwenNaichaTest.java`）
   - 4 张图片 + 2 个表情包
   - 8 句小红书文案
   - BGM：Just Kidding
   - 总时长：16.3 秒

2. **拼多多春节加班**（`PddSpringV2Test.java`）
   - 一图多句 + 表情包穿插
   - 素材库召回 BGM

## 常见问题

### Q: Docker 镜像构建失败？
A: 确保 Docker 有足够的内存（建议 4GB+），Maven 依赖下载可能需要时间。

### Q: COS 上传失败？
A: 检查 `.env.cos` 配置是否正确，确保 COS Bucket 有公有读权限。

### Q: TTS 配音失败？
A: 确保容器内安装了 `edge-tts`，可以手动测试：
```bash
docker exec -it dreamx-video edge-tts --list-voices
```

### Q: 视频时长计算不准确？
A: 每句字幕时长 = 字数 × 0.2s，最低 1.5s，最高 4s。

## 技术支持

- 项目仓库：https://github.com/Mv-Victor/dreamX
- 分支：`delivery/minimal-v1`
- 联系方式：通过 OpenClaw 联系

## 许可证

MIT License
