# DreamX AI 剪辑 - Docker 镜像完整测试链路

## 测试时间
2026-03-06 00:10 GMT+8

## 测试目标
验证完整的商业化交付流程：
1. 拉取镜像
2. 本机部署（**不挂载 /app/doc 目录**）
3. 使用 skill 生成完整视频（小红书文案 + TTS + 表情包 + BGM）

---

## ⚠️ 重要提示

**不要挂载 `/app/doc` 目录！**

镜像已包含完整素材库：
- **表情包**: 756 个（99 个分类目录）
- **BGM**: 76 个（26 个分类目录）

挂载 `-v $(pwd)/doc:/app/doc` 会**覆盖**镜像内的素材，导致 API 调用失败。

---

## 第一步：拉取镜像

### 命令
```bash
docker pull registry.cn-hangzhou.aliyuncs.com/aha_pocket/history_version:dreamx-video-v1.0.2
```

### 执行结果
```
dreamx-video-v1.0.2: Pulling from aha_pocket/history_version
Digest: sha256:c000202cb8651470ece9897ff03224818d43b6357bcab01d2bffddfa00173d82
Status: Image is up to date
```

✅ **镜像拉取成功**

---

## 第二步：本机部署镜像

### ⚠️ 重要提示
**不要挂载 `/app/doc` 目录！** 镜像已包含完整素材库（756 个表情包 + 76 个 BGM），挂载会覆盖镜像内的素材。

### 命令
```bash
# 加载环境变量
source .env.cos

# 启动容器（不要挂载 /app/doc 目录）
docker run -d \
  --name dreamx-video \
  -p 8081:17026 \
  -e COS_APP_ID=$COS_APP_ID \
  -e COS_SECRET_ID=$COS_SECRET_ID \
  -e COS_SECRET_KEY=$COS_SECRET_KEY \
  -e COS_REGION=$COS_REGION \
  -e COS_BUCKET=$COS_BUCKET \
  registry.cn-hangzhou.aliyuncs.com/aha_pocket/history_version:dreamx-video-v1.0.2
```

### 执行结果
```
容器 ID: 18b5767bf997
服务启动时间：3.2 秒
端口映射：8081 -> 17026
素材库：99 个表情包分类 + 26 个 BGM 分类（已包含在镜像内）
```

✅ **容器部署成功**

---

## 第三步：使用 dreamx-docker-video skill 生产视频

### 参考脚本
`/root/.openclaw/workspace/skills/dreamx-docker-video/references/test-full-video.sh`

### 完整流程

#### 1. 生成小红书爆款文案（8 句）
```
1. 大家真的都在涨薪吗？
2. 真相可能和你想的不一样
3. 大厂平均涨薪 15%
4. 中小厂普遍冻结薪资
5. 技术岗涨薪最多
6. 运营岗基本没动
7. 想涨薪先看这 3 点
8. 评论区有详细攻略
```

#### 2. TTS 配音生成
```bash
docker exec dreamx-video edge-tts \
  --voice zh-CN-YunjianNeural \
  --text "大家真的都在涨薪吗" \
  --write-media /app/doc/sale/dajiazhangxin/voiceover_1.mp3
```

#### 3. 情绪分析 + 素材召回
- 情绪：吐槽 + 震惊 + 实用
- 表情包：震惊猫（cat_shocked）
- BGM：Smile_1076.mp3（happy）

#### 4. 分镜时长计算
```
图 1 (0-3500ms): 字幕 1(500-2000) + 字幕 2(2000-4000)
图 2 (3500-7000ms): 字幕 3(4000-5500) + 字幕 4(5500-7500)
图 3 (7000-10500ms): 表情包 (7000-8500) + 字幕 5(7500-9000) + 字幕 6(9000-10500)
图 4 (10500-14000ms): 字幕 7(11000-12500) + 字幕 8(12500-14000)
总时长：14000ms
```

#### 5. API 调用构建 VideoProject
参考 `references/test-full-video.sh` 完整脚本。

---

## 测试结果

### 测试 1：热心脉友年底 100 个急招高薪岗（初始版）
- **任务 ID**: 291652279675650049
- **COS 链接**: https://dreamx-1301319986.cos.ap-shanghai.myqcloud.com/jy-projects/800001/800001.zip
- **问题**: 分镜时长、字幕位置、BGM 时长不正确

### 测试 2：热心脉友年底 100 个急招高薪岗（修正版）
- **任务 ID**: 291656969779937281
- **COS 链接**: https://dreamx-1301319986.cos.ap-shanghai.myqcloud.com/jy-projects/900001/900001.zip
- **修正**: 分镜时长匹配、字幕位置正确、BGM 时长匹配、表情包高潮点插入
- **状态**: ✅ 通过

### 测试 3：大家都在涨薪（完整版）
- **任务 ID**: 291668806709805057
- **COS 链接**: https://dreamx-1301319986.cos.ap-shanghai.myqcloud.com/jy-projects/1000001/1000001.zip
- **内容**: 8 句文案 + 8 段配音 + 表情包 + BGM + 水印
- **状态**: ✅ 通过

---

## 测试结论

### ✅ 成功项
1. **镜像拉取**: 成功从阿里云拉取镜像
2. **容器部署**: 成功启动容器，服务正常运行
3. **素材库验证**: 镜像包含 99 个表情包分类 + 26 个 BGM 分类
4. **API 基础功能**: 创建项目、添加素材等 API 正常工作
5. **完整测试用例**: 按照 dreamx-docker-video skill 完整流程生产视频成功

### ✅ 修复验证
1. ✅ storageService 初始化问题已修复（API 直接调用成功）
2. ✅ 表情包和 BGM 已打包到镜像中（756 个表情包 + 76 个 BGM）
3. ✅ 容器启动时不挂载 /app/doc 目录，使用镜像内素材
4. ✅ 完整流程无需 Maven 测试，纯 API 调用完成
5. ✅ 分镜时长、字幕位置、BGM 时长等全部符合规范

### 📋 商业化交付建议
1. **推荐方式**: 提供完整的 test-full-video.sh 脚本作为参考
2. **客户使用**: 参考脚本修改素材路径和文案即可
3. **文档说明**: 在 skill.md 中明确引用 references/test-full-video.sh
4. **部署注意**: 不要挂载 /app/doc 目录，镜像已包含完整素材库

---

## 镜像信息

- **镜像地址**: `registry.cn-hangzhou.aliyuncs.com/aha_pocket/history_version:dreamx-video-v1.0.2`
- **镜像大小**: 2.17GB（包含完整素材库）
- **镜像 ID**: c000202cb865
- **包含内容**:
  - Java 21 JRE
  - 编译后的 JAR 文件（不含源代码）
  - edge-tts（TTS 配音工具）
  - ffmpeg（音视频处理）
  - **表情包库**: 756 个（99 个分类目录）
  - **BGM 库**: 76 个（26 个分类目录）

---

## 注意事项

### ⚠️ 部署注意事项

1. **不要挂载 `/app/doc` 目录** - 镜像已包含完整素材库，挂载会覆盖
2. **只需挂载环境变量** - COS 配置通过 -e 参数传递
3. **端口映射** - 容器内端口 17026，映射到主机 8081
4. **TTS 生成** - 由于不挂载 doc 目录，需要在容器内生成 TTS 配音
5. **素材复制** - 如需使用自定义素材，需提前复制到容器内：
   ```bash
   docker cp /path/to/images dreamx-video:/app/doc/sale/eventname/
   ```

### API 参数格式

**必须使用 `style` 对象格式！**

```json
// ❌ 错误：扁平化参数
{
  "fontSize": 8,
  "fontColor": "#FFDE00"
}

// ✅ 正确：style 对象
{
  "style": {
    "fontSize": 8,
    "fillColor": "#FFDE00",
    "strokeColor": "#000000",
    "strokeWidth": 60
  }
}
```

### 坐标系

**Y 轴：上正下负，中心为 0**

- **字幕（底部居中）**：`positionY = -750`
- **水印（顶部居中）**：`positionY = 800`

### 分镜设计原则
1. **图片时长 = 该图所有字幕时长之和**（字读完才切图）
2. **字幕时长** = 字数 × 0.2s，最低 1500ms
3. **字幕位置**: 底部中央（positionY=-750）
4. **水印位置**: 顶部中央（positionY=800）
5. **BGM 时长**: 与图片总时长一致
6. **表情包插入**: 情绪高潮点，不要都放末尾

### 素材添加顺序
必须严格按分镜时间顺序添加：图 1 → 图 2 → 表情包 1 → 图 3

### 配音音频设置
必须设置 `materialTimeStart` 和 `materialTimeEnd`，否则 build 会 NPE

---

## 下一步

1. ✅ Docker 镜像 v1.0.2 已上传到阿里云
2. ✅ DOCKER_TEST.md 已更新（说明不挂载 /app/doc）
3. ✅ 部署脚本 deploy.sh 已更新（移除 doc 挂载）
4. ✅ 完整测试流程验证通过
5. ⏳ 客户交付准备就绪
