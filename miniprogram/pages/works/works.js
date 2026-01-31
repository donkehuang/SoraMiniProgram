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
      const db = wx.cloud.database()

      // 从云数据库查询视频列表，按时间倒序
      const res = await db.collection('videos')
        .orderBy('createTime', 'desc')
        .limit(20)
        .get()

      console.log('[作品] 查询结果:', res.data.length, '条')

      // 格式化视频数据
      const videos = res.data.map(item => ({
        _id: item._id,
        videoId: item.videoId,
        fileID: item.fileID,
        httpURL: item.httpURL,
        name: item.prompt ? item.prompt.substring(0, 50) + (item.prompt.length > 50 ? '...' : '') : '视频作品',
        date: item.date || new Date(item.timestamp).toLocaleDateString(),
        duration: item.duration || '未知',
        createTime: item.createTime
      }))

      this.setData({
        videos: videos,
        loading: false
      })

      console.log('[作品] 加载完成，视频数量:', videos.length)

    } catch (error) {
      console.error('[作品] 加载失败:', error)

      // 如果是云数据库未配置，提示用户
      if (error.errCode === -501001 || error.errMsg.includes('数据库')) {
        wx.showToast({
          title: '云数据库未配置',
          icon: 'none',
          duration: 2000
        })
      } else {
        wx.showToast({
          title: '加载失败',
          icon: 'none'
        })
      }

      this.setData({ loading: false })
    }
  },

  playVideo(e) {
    const video = e.currentTarget.dataset.video
    console.log('[作品] 播放视频:', video)

    // 跳转到视频播放页面
    wx.navigateTo({
      url: `/pages/player/player?url=${encodeURIComponent(video.httpURL)}&title=${encodeURIComponent(video.name || '视频作品')}&duration=${encodeURIComponent(video.duration || '12秒')}&date=${encodeURIComponent(video.date)}`
    })
  },

  downloadVideo(e) {
    const video = e.currentTarget.dataset.video
    console.log('[作品] 下载视频:', video)
    console.log('[作品] 视频URL:', video.httpURL)

    wx.showLoading({
      title: '下载中...'
    })

    wx.downloadFile({
      url: video.httpURL,
      success: (res) => {
        console.log('[作品] 下载成功:', res.tempFilePath)
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
            console.error('[作品] 保存失败:', err)
            wx.hideLoading()
            wx.showToast({
              title: '保存失败，请检查相册权限',
              icon: 'none'
            })
          }
        })
      },
      fail: (err) => {
        console.error('[作品] 下载失败:', err)
        wx.hideLoading()
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
