// pages/player/player.js
Page({
  data: {
    videoUrl: '',
    videoTitle: '',
    videoDuration: '',
    videoDate: ''
  },

  onLoad(options) {
    console.log('[播放器] 页面加载', options)

    const { url, title, duration, date } = options

    this.setData({
      videoUrl: decodeURIComponent(url || ''),
      videoTitle: decodeURIComponent(title || '视频'),
      videoDuration: decodeURIComponent(duration || '12秒'),
      videoDate: decodeURIComponent(date || new Date().toLocaleDateString())
    })
  },

  onReady() {
    this.videoContext = wx.createVideoContext('myVideo', this)
  },

  onPlay() {
    console.log('[播放器] 开始播放')
  },

  onPause() {
    console.log('[播放器] 暂停播放')
  },

  onTimeUpdate(e) {
    // 可以在这里更新进度条
  },

  onEnded() {
    console.log('[播放器] 播放结束')
    wx.showToast({
      title: '播放结束',
      icon: 'none'
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

  downloadVideo() {
    console.log('[播放器] 下载视频:', this.data.videoUrl)

    wx.showLoading({
      title: '下载中...'
    })

    wx.downloadFile({
      url: this.data.videoUrl,
      success: (res) => {
        console.log('[播放器] 下载成功:', res.tempFilePath)
        wx.saveVideoToPhotosAlbum({
          filePath: res.tempFilePath,
          success: () => {
            wx.hideLoading()
            wx.showToast({
              title: '已保存到相册',
              icon: 'success'
            })
          },
          fail: (err) => {
            console.error('[播放器] 保存失败:', err)
            wx.hideLoading()
            wx.showToast({
              title: '保存失败，请检查相册权限',
              icon: 'none'
            })
          }
        })
      },
      fail: (err) => {
        console.error('[播放器] 下载失败:', err)
        wx.hideLoading()
        wx.showToast({
          title: '下载失败',
          icon: 'none'
        })
      }
    })
  },

  goBack() {
    wx.navigateBack()
  },

  onShareAppMessage() {
    return {
      title: this.data.videoTitle,
      path: '/pages/player/player?url=' + encodeURIComponent(this.data.videoUrl) + '&title=' + encodeURIComponent(this.data.videoTitle),
      imageUrl: ''
    }
  }
})
