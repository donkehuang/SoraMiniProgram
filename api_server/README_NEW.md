# Sora视频生成API服务 - 异步版本

## 🎯 新架构说明

### 核心改进

采用**异步处理 + 轮询查询**架构，完美解决视频生成时间过长的问题：

1. **立即响应** - API立即返回任务ID，不等待视频生成完成
2. **后台处理** - 服务器异步处理视频生成和下载
3. **进度轮询** - 小程序定期查询视频生成状态
4. **本地存储** - 视频下载到服务器本地，提供稳定的播放URL

---

## 📋 API接口说明

### 1. 创建视频生成任务

**接口：** `POST /api/generate-video`

**请求参数：**
```json
{
  "prompt": "一只可爱的小猫在草地上奔跑",
  "seconds": "12"
}
```

**响应（立即返回）：**
```json
{
  "success": true,
  "videoId": "video_xxxxxxxxxxxx",
  "status": "queued",
  "message": "视频生成任务已创建"
}
```

**状态说明：**
- `queued` - 任务已创建，排队中
- `in_progress` - 视频生成中
- `completed` - 视频生成完成
- `failed` - 生成失败

---

### 2. 查询视频状态

**接口：** `GET /api/video-status/{videoId}`

**响应：**
```json
{
  "success": true,
  "videoId": "video_xxxxxxxxxxxx",
  "status": "in_progress",
  "progress": 45
}
```

**状态说明：**
- `status` - 当前状态 (queued/in_progress/completed/failed)
- `progress` - 进度百分比 (0-100)
- `videoUrl` - 如果状态为completed，返回本地播放地址

**完成时响应：**
```json
{
  "success": true,
  "videoId": "video_xxxxxxxxxxxx",
  "status": "completed",
  "progress": 100,
  "videoUrl": "/videos/video_xxxxxxxxxxxx.mp4"
}
```

**失败时响应：**
```json
{
  "success": true,
  "videoId": "video_xxxxxxxxxxxx",
  "status": "failed",
  "progress": 0,
  "error": "错误信息"
}
```

---

### 3. 播放视频

**接口：** `GET /videos/{filename}`

**说明：** 直接返回视频文件供小程序播放

**使用：**
```
http://localhost:5000/videos/video_xxxxxxxxxxxx.mp4
```

---

### 4. 健康检查

**接口：** `GET /api/health`

**响应：**
```json
{
  "status": "ok",
  "active_tasks": 3
}
```

---

### 5. 查看所有任务（调试用）

**接口：** `GET /api/tasks`

**响应：**
```json
{
  "success": true,
  "tasks": {
    "video_xxx1": {
      "status": "completed",
      "progress": 100
    },
    "video_xxx2": {
      "status": "in_progress",
      "progress": 45
    }
  }
}
```

---

## 🔄 完整工作流程

### 步骤1：创建任务

```
小程序 → API: POST /api/generate-video
API → Sora: 创建视频任务
API → 小程序: 立即返回 {videoId: "xxx", status: "queued"}  ✅
```

### 步骤2：后台处理

```
服务器后台线程：
1. 轮询查询Sora API状态
2. 显示进度：0% → 100%
3. 下载视频到本地：generated_videos/video_xxx.mp4
4. 更新状态为completed
```

### 步骤3：轮询查询

```
小程序（每3秒）：
→ GET /api/video-status/xxx
← {"status": "in_progress", "progress": 45}  继续等待
→ GET /api/video-status/xxx
← {"status": "completed", "videoUrl": "/videos/xxx.mp4"}  ✅ 完成
```

### 步骤4：播放视频

```
小程序 video组件:
src="http://localhost:5000/videos/xxx.mp4"
```

---

## 🎨 小程序界面展示

### 生成中状态：
```
┌─────────────────────────┐
│   📹 视频生成中...       │
│   排队中 (0%)           │
│                         │
│   ░░░░░░░░░░░░░░░░░░░░  │
│   0%                    │
│                         │
│   ⏱️ 预计需要5分钟       │
│   请耐心等待             │
│                         │
│   [取消生成]             │
└─────────────────────────┘
```

### 生成中（处理中）：
```
┌─────────────────────────┐
│   📹 视频生成中...       │
│   生成中 (45%)           │
│                         │
│   █████████░░░░░░░░░░░  │
│   45%                   │
│                         │
│   ⏱️ 预计需要5分钟       │
│   请耐心等待             │
│                         │
│   [取消生成]             │
└─────────────────────────┘
```

### 生成完成：
```
┌─────────────────────────┐
│   ✅ 生成成功！          │
│                         │
│   [▶ 播放视频]           │
└─────────────────────────┘
```

---

## 🚀 快速开始

### 1. 启动API服务器

```bash
cd api_server
python sora_api.py
```

应该看到：
```
* Running on http://0.0.0.0:5000
```

服务器会自动创建 `generated_videos` 目录存放生成的视频。

### 2. 启动小程序

在微信开发者工具中打开 `miniprogram` 目录，编译运行。

### 3. 测试流程

1. 在小程序中输入视频描述
2. 点击"生成视频"
3. 看到进度条显示"排队中"
4. 几秒后变为"生成中"，进度条开始增长
5. 等待约5分钟，进度达到100%
6. 自动显示视频播放器

---

## 📊 API服务器日志示例

```
2026-01-28 00:30:00 - INFO - [请求] 收到视频生成请求
2026-01-28 00:30:00 - INFO - [参数] prompt: 一只可爱的小猫..., seconds: 12
2026-01-28 00:30:01 - INFO - [创建] 视频任务创建成功，视频ID: video_xxx
2026-01-28 00:30:01 - INFO - [异步处理] 开始处理视频: video_xxx
2026-01-28 00:30:05 - INFO - [进度] 排队中: [---] 0.0%
2026-01-28 00:30:08 - INFO - [进度] 处理中: [====] 10.5%
2026-01-28 00:30:35 - INFO - [进度] 处理中: [=========] 50.2%
2026-01-28 00:31:05 - INFO - [完成] 视频生成完成，开始下载...
2026-01-28 00:31:10 - INFO - [下载] 视频已保存到: generated_videos/video_xxx.mp4
```

---

## 🛠️ 配置说明

### 视频存储目录

默认存储在 `generated_videos/` 目录，可以在 `sora_api.py` 中修改：

```python
VIDEOS_DIR = "generated_videos"  # 修改这里
```

### 轮询间隔

小程序每3秒查询一次状态，可在 `index.js` 中修改：

```javascript
const pollInterval = 3000  // 修改这里，单位：毫秒
```

### API服务器端口

默认端口5000，可在 `sora_api.py` 中修改：

```python
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # 修改这里
    app.run(host='0.0.0.0', port=port, debug=True)
```

---

## ✅ 优势总结

### 相比之前版本的改进：

| 功能 | 之前版本 | 新版本 |
|------|---------|--------|
| **响应时间** | 5分钟超时 | 立即返回 |
| **用户体验** | 长时间等待无反馈 | 实时进度显示 |
| **视频URL** | 占位符URL（不可用） | 本地文件URL（稳定） |
| **状态追踪** | 无 | 精确进度 0-100% |
| **错误处理** | 超时后才知道 | 实时错误提示 |
| **并发能力** | 单线程阻塞 | 多线程异步 |

---

## 🧪 测试API

### 测试创建任务：

```bash
curl -X POST http://localhost:5000/api/generate-video \
  -H "Content-Type: application/json" \
  -d '{"prompt": "测试视频", "seconds": "8"}'
```

### 测试查询状态：

```bash
curl http://localhost:5000/api/video-status/video_xxx
```

### 测试查看所有任务：

```bash
curl http://localhost:5000/api/tasks
```

---

## 📝 注意事项

1. **视频存储** - 生成的视频会保存在服务器本地，注意磁盘空间
2. **并发限制** - 建议控制同时生成的视频数量，避免服务器过载
3. **超时处理** - Sora API可能超时，已添加重试机制（最多3次）
4. **任务清理** - 建议定期清理旧的视频文件，避免占用过多空间

---

## 🎉 完成！

现在你的小程序已经支持：
- ✅ 立即响应（不等待5分钟）
- ✅ 实时进度显示
- ✅ 稳定的视频播放
- ✅ 友好的用户体验

开始使用吧！🚀
