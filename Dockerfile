# DreamX AI 剪辑服务 - Docker 镜像
FROM maven:3.9.9-eclipse-temurin-21-alpine AS builder

WORKDIR /build

# 复制 pom 文件
COPY pom.xml .
COPY duo-server-base/pom.xml duo-server-base/
COPY duo-video-base/pom.xml duo-video-base/
COPY duo-video-jy/pom.xml duo-video-jy/
COPY duo-video-api/pom.xml duo-video-api/

# 下载依赖
RUN mvn dependency:go-offline -B

# 复制源代码
COPY duo-server-base/src duo-server-base/src
COPY duo-video-base/src duo-video-base/src
COPY duo-video-jy/src duo-video-jy/src
COPY duo-video-api/src duo-video-api/src

# 编译
RUN mvn clean package -DskipTests -B

# 运行时镜像
FROM eclipse-temurin:21-jre-alpine

WORKDIR /app

# 安装 edge-tts（TTS 配音工具）
RUN apk add --no-cache python3 py3-pip ffmpeg && \
    pip3 install --no-cache-dir --break-system-packages edge-tts

# 复制编译产物
COPY --from=builder /build/duo-video-api/target/duo-video-api-*.jar app.jar

# 复制素材文件（表情包、BGM、营销素材）
COPY doc/ /app/doc/

# 创建临时目录
RUN mkdir -p /app/tmp/jy-drafts

# 暴露端口
EXPOSE 8080

# 启动命令
ENTRYPOINT ["java", "-jar", "app.jar"]
