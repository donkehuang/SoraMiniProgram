// pages/works/works.js
Page({
  data: {
    videos: [],
    images: [],
    loading: false
  },

  onLoad() {
    console.log('[作品] 页面加载')
    this.loadWorks()
  },

  onShow() {
    console.log('[作品] 页面显示')
    // 每次显示都刷新列表
    this.loadWorks()
  },

  async loadWorks() {
    console.log('[作品] 加载作品列表')
    this.setData({ loading: true })

    try {
      // 并行加载视频和图片
      await Promise.all([
        this.loadVideos(),
        this.loadImages()
      ])

      this.setData({ loading: false })
      console.log('[作品] 加载完成')

    } catch (error) {
      console.error('[作品] 加载失败:', error)
      wx.showToast({
        title: '加载失败: ' + (error.message || error.errMsg),
        icon: 'none',
        duration: 3000
      })
      this.setData({ loading: false })
    }
  },

  async loadVideos() {
    console.log('[作品] 加载视频列表')

    try {
      // 使用云函数获取视频
      const res = await wx.cloud.callFunction({
        name: 'getVideos'
      })

      if (!res.result.success) {
        throw new Error(res.result.error || '获取视频列表失败')
      }

      console.log('[作品] 云函数返回视频:', res.result.data.length, '条')

      // 格式化视频数据
      const videos = res.result.data.map(item => ({
        _id: item._id,
        videoId: item.videoId,
        fileID: item.fileID,
        httpURL: item.tempFileURL || item.httpURL,
        name: item.prompt ? item.prompt.substring(0, 50) + (item.prompt.length > 50 ? '...' : '') : '视频作品',
        prompt: item.prompt || '',
        date: item.date || new Date(item.timestamp).toLocaleDateString(),
        duration: item.duration || '未知',
        createTime: item.createTime
      }))

      this.setData({ videos: videos })
      console.log('[作品] 视频加载完成，数量:', videos.length)

    } catch (error) {
      console.error('[作品] 视频加载失败:', error)
      if (error.errMsg && error.errMsg.includes('FunctionName')) {
        await this.loadVideosDirectly()
      }
    }
  },

  async loadImages() {
    console.log('[作品] 加载图片列表')

    try {
      const db = wx.cloud.database()

      // 查询所有图片类型的作品
      const res = await db.collection('images')
        .orderBy('createTime', 'desc')
        .limit(20)
        .get()

      console.log('[作品] 数据库查询图片结果:', res.data.length, '条')

      // 获取所有 fileID
      const fileIDs = res.data.map(item => item.fileID).filter(id => id)

      if (fileIDs.length === 0) {
        this.setData({ images: [] })
        return
      }

      // 批量获取新的临时链接
      console.log('[作品] 刷新图片临时链接...')
      const urlRes = await wx.cloud.getTempFileURL({
        fileList: fileIDs
      })

      // 创建 fileID -> tempURL 的映射
      const urlMap = {}
      urlRes.fileList.forEach(file => {
        urlMap[file.fileID] = file.tempFileURL
      })

      // 格式化图片数据
      const images = res.data.map(item => ({
        _id: item._id,
        fileID: item.fileID,
        httpURL: urlMap[item.fileID] || item.httpURL,
        name: item.text ? item.text.substring(0, 50) + (item.text.length > 50 ? '...' : '') : '图片作品',
        text: item.text || '',
        style: item.style || '',
        date: item.date || new Date(item.timestamp).toLocaleDateString(),
        createTime: item.createTime
      }))

      this.setData({ images: images })
      console.log('[作品] 图片加载完成，数量:', images.length)

    } catch (error) {
      console.error('[作品] 图片加载失败:', error)
      this.setData({ images: [] })
    }
  },

  // 备用方案：直接查询数据库并刷新临时链接
  async loadVideosDirectly() {
    try {
      const db = wx.cloud.database()

      // 从云数据库查询视频列表
      const res = await db.collection('videos')
        .orderBy('createTime', 'desc')
        .limit(20)
        .get()

      console.log('[作品] 数据库查询结果:', res.data.length, '条')

      // 获取所有 fileID
      const fileIDs = res.data.map(item => item.fileID).filter(id => id)

      if (fileIDs.length === 0) {
        this.setData({
          videos: [],
          loading: false
        })
        return
      }

      // 批量获取新的临时链接
      console.log('[作品] 刷新临时链接...')
      const urlRes = await wx.cloud.getTempFileURL({
        fileList: fileIDs
      })

      // 创建 fileID -> tempURL 的映射
      const urlMap = {}
      urlRes.fileList.forEach(file => {
        urlMap[file.fileID] = file.tempFileURL
      })

      // 格式化视频数据，使用新的临时链接
      const videos = res.data.map(item => ({
        _id: item._id,
        videoId: item.videoId,
        fileID: item.fileID,
        httpURL: urlMap[item.fileID] || item.httpURL, // 使用新的临时链接
        name: item.prompt ? item.prompt.substring(0, 50) + (item.prompt.length > 50 ? '...' : '') : '视频作品',
        prompt: item.prompt || '', // 完整prompt
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
      console.error('[作品] 备用方案也失败:', error)
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

    // 跳转到视频播放页面，传递prompt
    wx.navigateTo({
      url: `/pages/player/player?url=${encodeURIComponent(video.httpURL)}&duration=${encodeURIComponent(video.duration || '12秒')}&date=${encodeURIComponent(video.date)}&prompt=${encodeURIComponent(video.prompt || video.name || '')}`
    })
  },

  previewImage(e) {
    const image = e.currentTarget.dataset.image
    console.log('[作品] 预览图片:', image)

    wx.previewImage({
      urls: [image.httpURL],
      current: image.httpURL
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
