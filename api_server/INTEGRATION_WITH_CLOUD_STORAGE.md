# 微信云存储集成方案

## 🎯 推荐方案：小程序端上传

这是**最简单、最可靠**的方案，不需要复杂的服务器配置。

---

## 📋 完整工作流程

### 当前流程（只用本地存储）
```
1. 小程序 → API: 生成视频
2. API → Sora: 创建视频任务
3. API → 下载视频到本地: generated_videos/video_xxx.mp4
4. API → 小程序: 返回 http://localhost:5000/videos/video_xxx.mp4
5. 小程序: 显示视频播放器 ❌ 只能在本地访问
```

### 新流程（使用云存储）
```
1. 小程序 → API: 生成视频
2. API → Sora: 创建视频任务
3. API → 下载视频到本地: generated_videos/video_xxx.mp4
4. API → 小程序: 返回 http://localhost:5000/videos/video_xxx.mp4
5. 小程序: 下载视频到本地临时路径 ✅
6. 小程序: 上传到微信云存储 ✅
7. 小程序: 获得永久访问URL ✅
8. 小程序: 显示视频播放器 ✅
```

---

## 🚀 实现步骤

### 第1步：开通微信云存储

#### 1.1 打开云开发控制台

1. 打开微信开发者工具
2. 点击 **"云开发"** 按钮
3. 进入控制台

#### 1.2 开通云存储

1. 左侧菜单 → **"存储"**
2. 点击 **"开通"**
3. 记录云环境ID（类似 `cloud1-xxx`）

#### 1.3 获取环境ID

在云开发控制台顶部可以看到：
```
云开发环境: cloud1-3gxxxxx
```

复制这个ID，配置到小程序。

---

### 第2步：配置小程序

#### 2.1 修改 app.js

打开 `miniprogram/app.js`：

```javascript
App({
  onLaunch() {
    console.log('Sora视频生成小程序启动')

    // 初始化云开发
    if (wx.cloud) {
      wx.cloud.init({
        env: 'cloud1-3gxxxxx'  // 替换为你的云环境ID
        traceUser: true
      })
      console.log('[云开发] 初始化成功')
    } else {
      console.error('[云开发] 当前环境不支持云开发')
    }
  }
})
```

#### 2.2 修改 project.config.json

打开 `miniprogram/project.config.json`，添加云函数根目录：

```json
{
  "cloudfunctionRoot": "cloudfunctions/",
  "cloudbaseRoot": "cloudbase/",
  ...
}
```

---

### 第3步：修改小程序上传逻辑

打开 `miniprogram/pages/index/index.js`，修改视频完成处理：

```javascript
// 引入云存储工具
import cloudStorage from '../../utils/cloudStorage.js'

// 在 pollVideoStatus 函数中，找到视频完成的部分
if (status === 'completed') {
  console.log('[完成] 视频生成完成')

  // 1. 先从API下载视频到本地临时目录
  const localTempPath = await this.downloadToLocal(videoId, apiBaseUrl)

  // 2. 上传到微信云存储
  const uploadResult = await cloudStorage.uploadFile(
    localTempPath,
    `videos/${new Date().getTime()}_${videoId}.mp4`
  )

  console.log('[完成] 上传到云存储成功')
  console.log('[完成] fileID:', uploadResult.fileID)
  console.log('[完成] URL:', uploadResult.tempFileURL)

  // 3. 使用云存储URL
  this.setData({
    isGenerating: false,
    videoUrl: uploadResult.tempFileURL,
    generationProgress: 100,
    statusText: '生成完成！'
  })

  // 4. 清理本地临时文件
  wx.removeSavedFile({
    filePath: localTempPath
  })

  return
}

// 新增：下载视频到本地
async downloadToLocal(videoId, apiBaseUrl) {
  console.log('[下载] 开始下载视频到本地')

  const filename = `${videoId}.mp4`
  const url = `${apiBaseUrl}/videos/${filename}`

  return new Promise((resolve, reject) => {
    wx.downloadFile({
      url: url,
      success: (res) => {
        console.log('[下载] 下载成功:', res.tempFilePath)
        resolve(res.tempFilePath)
      },
      fail: (err) => {
        console.error('[下载] 下载失败:', err)
        reject(new Error(err.errMsg || '下载失败'))
      }
    })
  })
}
```

---

### 第4步：上传云函数

在微信开发者工具中：

1. 右键 `cloudfunctions/uploadVideo` 文件夹
2. 选择 **"上传并部署：云端安装依赖"**
3. 等待部署完成

---

## 🎨 界面更新

修改 `miniprogram/pages/index/index.wxml`，在上传时显示进度：

```xml
<!-- 在进度区域添加上传状态 -->
<view class="progress-section" wx:if="{{isGenerating}}">
  <view class="progress-header">
    <text class="progress-title">📹 视频生成中...</text>
    <text class="progress-status">{{statusText}}</text>
  </view>

  <view class="progress-bar-container">
    <view class="progress-bar-fill" style="width: {{generationProgress}}%"></view>
  </view>

  <!-- 上传中状态 -->
  <view class="upload-status" wx:if="{{isUploading}}">
    <text>☁️ 正在上传到云存储...</text>
  </view>

  <text class="progress-info">⏱️ 预计需要5分钟，请耐心等待</text>
</view>
```

---

## ✅ 优势

### 对比本地存储：

| 特性 | 本地存储 | 微信云存储 |
|------|----------|------------|
| **访问范围** | 仅本地 | 全网可访问 |
| **速度** | 慢（受限于服务器带宽）| 快（CDN加速）|
| **稳定性** | 依赖服务器运行 | 高可用 |
| **分享性** | 无法分享 | 可分享 |
| **成本** | 免费 | 免费额度+付费 |
| **配置** | 无需配置 | 需要开通云存储 |

---

## 📊 费用说明

### 免费额度（新用户）：
- 存储空间：5GB
- 月下载流量：5GB
- CDN流量：5GB/月

### 超出免费额度后（参考）：
- 存储：约 0.118元/GB/月
- CDN流量：约 0.18元/GB
- 下载流量：约 0.5元/GB

**估算：**
- 假设每个视频50MB
- 可存储约100个视频（5GB）
- 每月可播放约100次（5GB）

---

## 🔧 配置文件清单

需要修改的文件：

1. ✅ `miniprogram/app.js` - 初始化云开发
2. ✅ `miniprogram/project.config.json` - 添加云配置
3. ✅ `miniprogram/pages/index/index.js` - 添加上传逻辑
4. ✅ `miniprogram/utils/cloudStorage.js` - 已创建
5. ✅ `cloudfunctions/uploadVideo/` - 已创建

---

## 🎯 快速开始

### 1. 开通云存储（5分钟）

```
微信开发者工具 → 云开发 → 存储 → 开通
```

### 2. 获取环境ID（1分钟）

在云开发控制台查看环境ID，例如：`cloud1-3gxxxxx`

### 3. 修改小程序代码（10分钟）

按照上述步骤修改 `app.js` 和 `index.js`

### 4. 上传云函数（2分钟）

右键 `cloudfunctions/uploadVideo` → 上传并部署

### 5. 测试（5分钟）

运行小程序，生成视频，观察上传过程

---

## 📝 注意事项

### 1. fileID vs tempFileURL

- **fileID**: `cloud://xxx.mp4` - 永久标识，可长期使用
- **tempFileURL**: `https://xxx.mp4` - 临时URL，有时效（通常是2小时）

**正确做法：**
- 使用 fileID 作为主键
- 需要播放时，调用 `getTempFileURL(fileID)` 获取URL
- 或者使用云存储的HTTP CDN链接（如果配置了）

### 2. 文件路径规范

```
videos/20240128_1234567890.mp4
└─── ├───┬────────┘
    │    └── 时间戳
    └─── 固定目录
```

### 3. 大小限制

- 单文件：最大100MB
- 总存储：免费5GB

如果视频超过100MB，需要压缩或分片。

---

## 🚀 测试验证

### 测试步骤：

1. ✅ 云存储已开通
2. ✅ 小程序云开发已初始化
3. ✅ 云函数已部署
4. ✅ 生成视频
5. ✅ 下载到本地临时目录
6. ✅ 上传到云存储
7. ✅ 获得云存储URL
8. ✅ 视频可以播放

### 查看云存储文件：

在云开发控制台 → 存储，可以看到上传的视频文件。

---

## 💡 进阶优化

### 1. 使用永久CDN链接

如果需要永久可分享的链接，可以：

```javascript
// 获取永久链接（需要配置域名）
wx.cloud.getURL({
  fileList: [fileID],
  success: (res) => {
    console.log('[云存储] 永久URL:', res.fileList[0].tempFileURL)
  }
})
```

### 2. 批量删除旧视频

定期清理云存储，避免占用空间：

```javascript
// 删除超过7天的视频
cloudStorage.deleteFile('cloud://videos/old_video.mp4')
```

### 3. 使用云数据库记录

在云数据库中记录视频信息：

```javascript
// 上传成功后，记录到数据库
wx.cloud.database().collection('videos').add({
  data: {
    fileID: uploadResult.fileID,
    prompt: this.data.prompt,
    createTime: new Date(),
    userId: 'user_123'
  }
})
```

---

## 📞 需要帮助？

如果遇到问题，检查：

1. **云存储是否开通？**
   - 云开发控制台 → 存储

2. **环境ID是否正确？**
   - 控制台顶部查看

3. **云函数是否部署？**
   - 右键上传并部署

4. **小程序权限？**
   - 详情 → 本地设置 → 不校验合法域名

---

现在按照这个方案，视频就可以永久存储到微信云存储，全网可访问了！🎉
