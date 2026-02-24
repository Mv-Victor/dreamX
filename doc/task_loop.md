# DreamX Task Loop (Ralph-Wiggum Style)

## How It Works
- Each iteration: read this file → pick highest priority incomplete task → execute → update status → loop
- Memory preserved via this file + git commits + daily memory notes
- Driven by cron (every 20 min) + sessions_spawn for isolated execution

## Current Iteration
- **Last run:** 2026-02-24 11:15 GMT+8
- **Last task:** 素材爬取 (DONE)
- **Next task:** 重做 PDD 视频

## Task Queue (priority order)

### P0 - Blocking
- [x] 素材爬取方案落地 (agent-browser + Giphy + Mixkit)
- [x] 首轮爬取完成 (103 memes + 24 BGMs)

### P1 - Core
- [ ] 重做 PDD 视频 (projectId: 200003)
  - 写完整 6-10 句爆款脚本
  - 分配到 4 张图片（每图多句字幕）
  - 用情绪召回匹配表情包 + BGM
  - 生成剪映工程文件
  - 上传 COS 返回下载链接
- [ ] 更新 dreamx-smart-editing SKILL.md（新分镜逻辑）

### P2 - Enhancement
- [ ] 实现 ralph-wiggum 自驱动 cron 循环
- [ ] 素材库二轮扩充（shy 分类为空，补充中文梗图）
- [ ] BGM 去重（有重复的 Comical / Upbeat Jazz / Games Worldbeat）

### P3 - Nice to Have
- [ ] 素材质量审核（部分 GIF 可能不适合营销视频）
- [ ] 添加中文表情包源（微信表情、斗图啦等）

## Learnings
- Giphy/Tenor API 从国内直连全部被墙
- agent-browser 走独立浏览器环境，可以绕过网络限制
- Mixkit preview MP3 加 Referer 头即可直接下载
- dbbqb.com SSL 证书过期，返回 base64 内联图（反爬）
- python3.12 有完整依赖，python3.11 缺 aiohttp/aiosqlite
- base64 中转 GIF 限制在 3MB 以内比较稳定

## Blockers
- GitHub 从本机访问不了（无法直接看 ralph 源码）
- 中文表情包平台大多有反爬或已关站
