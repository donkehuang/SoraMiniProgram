// pages/works/works.js
Page({
  data: {
    videos: [],
    loading: false
  },

  onLoad() {
    console.log('[作品] 页面加载')
    this.loadVideos()
  },

  onShow() {
    console.log('[作品] 页面显示')
    // 每次显示都刷新列表
    this.loadVideos()
  },

  async loadVideos() {
    console.log('[作品] 加载视频列表')
    this.setData({ loading: true })

    try {
      // 这里需要实现云数据库查询
      // 暂时模拟数据
      await new Promise(resolve => setTimeout(resolve, 1000))

      // TODO: 从云数据库查询视频列表
      // const res = await wx.cloud.database().collection('videos').get()
      
      const mockVideos = []

      this.setData({
        videos: mockVideos,
        loading: false
      })

      console.log('[作品] 加载完成，视频数量:', mockVideos.length)

    } catch (error) {
      console.error('[作品] 加载失败:', error)
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      })
      this.setData({ loading: false })
    }
  },

  playVideo(e) {
    const video = e.currentTarget.dataset.video
    console.log('[作品] 播放视频:', video)

    // 跳转到视频播放页面或使用弹窗播放
    // 暂时使用系统播放器
    wx.navigateTo({
      url: `/pages/player/player?url=${encodeURIComponent(video.httpURL)}&title=${video.name || '视频作品'}`
    })
  },

  downloadVideo(e) {
    const video = e.currentTarget.dataset.video
    console.log('[作品] 下载视频:', video)

    wx.downloadFile({
      url: video.httpURL,
      success: (res) => {
        console.log('[作品] 下载成功:', res.tempFilePath)
        wx.saveVideoToPhotosAlbum({
          filePath: res.tempFilePath,
          success: () => {
            wx.showToast({
              title: '已保存到相册',
              icon: 'success'
            })
          },
          fail: (err) => {
            console.error('[作品] 保存失败:', err)
            wx.showToast({
              title: '保存失败',
              icon: 'none'
            })
          }
        })
      },
      fail: (err) => {
        console.error('[作品] 下载失败:', err)
        wx.showToast({
          title: '下载失败',
          icon: 'none'
        })
      }
    })
  },

  goToIndex() {
    wx.switchTab({
      url: '/pages/index/index'
    })
  }
})
