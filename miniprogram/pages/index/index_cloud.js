// 使用微信云开发版本
Page({
  data: {
    prompt: '',
    durationOptions: ['8秒', '12秒', '16秒'],
    durationIndex: 0,
    loading: false,
    videoUrl: '',
    errorMessage: ''
  },

  onLoad() {
    // 初始化云开发
    if (!wx.cloud) {
      console.error('请使用 2.2.3 或以上的基础库以使用云能力')
      return
    }
    wx.cloud.init({
      env: 'your_env_id', // 替换为你的云环境ID
      traceUser: true
    })
  },

  onPromptInput(e) {
    this.setData({
      prompt: e.detail.value
    })
  },

  onDurationChange(e) {
    this.setData({
      durationIndex: parseInt(e.detail.value)
    })
  },

  async generateVideo() {
    const { prompt, durationIndex, durationOptions } = this.data

    if (!prompt.trim()) {
      this.setData({
        errorMessage: '请输入视频描述'
      })
      return
    }

    this.setData({
      loading: true,
      errorMessage: '',
      videoUrl: ''
    })

    try {
      // 调用云函数生成视频
      const duration = durationOptions[durationIndex].replace('秒', '')
      const res = await wx.cloud.callFunction({
        name: 'generateVideo',
        data: {
          prompt: prompt,
          seconds: duration
        }
      })

      if (res.result.success) {
        this.setData({
          videoUrl: res.result.videoUrl
        })
      } else {
        this.setData({
          errorMessage: res.result.error || '生成失败，请重试'
        })
      }
    } catch (error) {
      console.error('生成视频失败:', error)
      this.setData({
        errorMessage: '生成失败，请检查网络连接'
      })
    } finally {
      this.setData({
        loading: false
      })
    }
  }
})
