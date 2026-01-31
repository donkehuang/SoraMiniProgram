App({
  onLaunch() {
    console.log('Sora视频生成小程序启动')

    // 初始化云开发
    if (wx.cloud) {
      // 云环境ID（请在微信云开发控制台查看正确的环境ID）
      // 环境ID格式示例：cloud1-2gd0041e12763b47 或 18823db6-a1b6-4a84-b472-8cf1a5e2bc8a
      const envId = 'cloud1-2gd0041e12763b47'  // ← 替换为你的实际环境ID

      wx.cloud.init({
        env: envId,
        traceUser: true
      })
      console.log('[云开发] 初始化成功，环境ID:', envId)
    } else {
      console.error('[云开发] 当前环境不支持云开发')
    }
  }
})
