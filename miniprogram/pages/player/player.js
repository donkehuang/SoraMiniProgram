// pages/player/player.js
Page({
  data: {
    videoUrl: '',
    videoPrompt: '',
    promptPreview: '',
    promptExpanded: false,
    showExpandBtn: false,
    videoDuration: '',
    videoDate: '',
    isPlaying: true,
    // 进度相关
    currentTime: 0,
    duration: 0,
    progressPercent: 0,
    currentTimeStr: '00:00',
    durationStr: '00:00'
  },

  onLoad(options) {
    console.log('[播放器] 页面加载', options)

    const { url, prompt, duration, date } = options
    const fullPrompt = decodeURIComponent(prompt || '')
    
    // 生成预览文本（前50个字符）
    const preview = fullPrompt.length > 50 ? fullPrompt.substring(0, 50) + '...' : fullPrompt
    const needExpand = fullPrompt.length > 50

    this.setData({
      videoUrl: decodeURIComponent(url || ''),
      videoPrompt: fullPrompt,
      promptPreview: preview,
      showExpandBtn: needExpand,
      promptExpanded: false,
      videoDuration: decodeURIComponent(duration || '12秒'),
      videoDate: decodeURIComponent(date || new Date().toLocaleDateString())
    })
  },

  onReady() {
    this.videoContext = wx.createVideoContext('myVideo', this)
  },

  // 点击视频区域，切换播放/暂停
  togglePlay() {
    if (this.data.isPlaying) {
      this.videoContext.pause()
    } else {
      this.videoContext.play()
    }
  },

  // 切换prompt展开/收起
  togglePrompt() {
    if (this.data.showExpandBtn) {
      this.setData({
        promptExpanded: !this.data.promptExpanded
      })
    }
  },

  // 格式化时间（秒转为 mm:ss）
  formatTime(seconds) {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  },

  onPlay() {
    console.log('[播放器] 开始播放')
    this.setData({ isPlaying: true })
  },

  onPause() {
    console.log('[播放器] 暂停播放')
    this.setData({ isPlaying: false })
  },

  onTimeUpdate(e) {
    const { currentTime, duration } = e.detail
    const percent = duration > 0 ? (currentTime / duration) * 100 : 0
    
    this.setData({
      currentTime: currentTime,
      duration: duration,
      progressPercent: percent,
      currentTimeStr: this.formatTime(currentTime),
      durationStr: this.formatTime(duration)
    })
  },

  onEnded() {
    console.log('[播放器] 播放结束')
    this.setData({ 
      isPlaying: false,
      progressPercent: 100
    })
  },

  onError(e) {
    console.error('[播放器] 播放错误:', e)
    wx.showToast({
      title: '播放失败',
      icon: 'none'
    })
  },

  onFullscreenChange(e) {
    console.log('[播放器] 全屏状态变化:', e.detail.fullScreen)
  },

  goBack() {
    wx.navigateBack()
  },

  onShareAppMessage() {
    return {
      title: this.data.videoPrompt || 'AI生成的精彩视频',
      path: '/pages/player/player?url=' + encodeURIComponent(this.data.videoUrl) + '&prompt=' + encodeURIComponent(this.data.videoPrompt),
      imageUrl: ''
    }
  }
})
