Page({
  /**
   * 页面的初始数据
   */
  data: {
    // 视频相关
    videoUrl: '',
    videoDuration: '8秒',
    orientation: 'vertical', // vertical 或 horizontal
    resolution: '720p',
    size: '720x1280',
    prompt: '',
    style: '',

    // 播放状态
    isPlaying: false,
    isLoading: true,
    currentTime: 0,
    duration: 0
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {
    console.log('[结果页] 页面加载，参数:', options)

    // 从选项中获取视频信息
    if (options.videoUrl) {
      this.setData({
        videoUrl: decodeURIComponent(options.videoUrl)
      })
    }

    if (options.duration) {
      this.setData({
        videoDuration: options.duration + '秒'
      })
    }

    if (options.orientation) {
      this.setData({
        orientation: options.orientation
      })
    }

    if (options.size) {
      this.setData({
        size: options.size
      })
    }

    if (options.prompt) {
      this.setData({
        prompt: decodeURIComponent(options.prompt)
      })
    }

    if (options.style) {
      this.setData({
        style: options.style
      })
    }
  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady() {
    console.log('[结果页] 页面渲染完成')
  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow() {
    console.log('[结果页] 页面显示')
  },

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide() {
    console.log('[结果页] 页面隐藏')
    // 页面隐藏时暂停视频
    this.pauseVideo()
  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload() {
    console.log('[结果页] 页面卸载')
  },

  /**
   * 视频播放事件
   */
  onVideoPlay(e) {
    console.log('[结果页] 视频开始播放')
    this.setData({
      isPlaying: true,
      isLoading: false
    })
  },

  /**
   * 视频暂停事件
   */
  onVideoPause(e) {
    console.log('[结果页] 视频暂停')
    this.setData({
      isPlaying: false
    })
  },

  /**
   * 视频加载完成事件
   */
  onVideoLoad(e) {
    console.log('[结果页] 视频加载完成')
    this.setData({
      isLoading: false
    })
  },

  /**
   * 视频播放时间更新
   */
  onVideoTimeUpdate(e) {
    this.setData({
      currentTime: e.detail.currentTime,
      duration: e.detail.duration
    })
  },

  /**
   * 视频播放错误
   */
  onVideoError(e) {
    console.error('[结果页] 视频播放错误:', e)
    wx.showToast({
      title: '视频加载失败',
      icon: 'none',
      duration: 2000
    })
    this.setData({
      isLoading: false
    })
  },

  /**
   * 重播视频
   */
  replayVideo() {
    console.log('[结果页] 重播视频')
    const videoContext = wx.createVideoContext('resultVideo')
    if (videoContext) {
      videoContext.seek(0)
      videoContext.play()
    }
  },

  /**
   * 播放视频
   */
  playVideo() {
    console.log('[结果页] 播放视频')
    const videoContext = wx.createVideoContext('resultVideo')
    if (videoContext) {
      videoContext.play()
    }
  },

  /**
   * 暂停视频
   */
  pauseVideo() {
    console.log('[结果页] 暂停视频')
    const videoContext = wx.createVideoContext('resultVideo')
    if (videoContext) {
      videoContext.pause()
    }
  },

  /**
   * 保存视频到相册
   */
  saveVideoToGallery() {
    console.log('[结果页] 保存视频到相册')

    // 检查权限
    wx.getSetting({
      success: (res) => {
        if (!res.authSetting['scope.writePhotosAlbum']) {
          wx.authorize({
            scope: 'scope.writePhotosAlbum',
            success: () => {
              this.downloadAndSaveVideo()
            },
            fail: () => {
              wx.showModal({
                title: '需要授权',
                content: '需要您授权保存到相册',
                confirmText: '去授权',
                cancelText: '取消',
                success: (res) => {
                  if (res.confirm) {
                    wx.openSetting()
                  }
                }
              })
            }
          })
        } else {
          this.downloadAndSaveVideo()
        }
      }
    })
  },

  /**
   * 下载并保存视频
   */
  downloadAndSaveVideo() {
    wx.showLoading({
      title: '保存中...'
    })

    wx.downloadFile({
      url: this.data.videoUrl,
      success: (res) => {
        if (res.statusCode === 200) {
          wx.saveVideoToPhotosAlbum({
            filePath: res.tempFilePath,
            success: () => {
              wx.hideLoading()
              wx.showToast({
                title: '保存成功',
                icon: 'success'
              })
            },
            fail: (err) => {
              wx.hideLoading()
              console.error('[结果页] 保存失败:', err)
              wx.showToast({
                title: '保存失败',
                icon: 'none'
              })
            }
          })
        }
      },
      fail: (err) => {
        wx.hideLoading()
        console.error('[结果页] 下载失败:', err)
        wx.showToast({
          title: '下载失败',
          icon: 'none'
        })
      }
    })
  },

  /**
   * 下载视频到本地
   */
  downloadVideo() {
    console.log('[结果页] 下载视频')

    wx.showLoading({
      title: '下载中...'
    })

    wx.downloadFile({
      url: this.data.videoUrl,
      success: (res) => {
        wx.hideLoading()
        if (res.statusCode === 200) {
          wx.showToast({
            title: '下载成功',
            icon: 'success'
          })
          console.log('[结果页] 视频已保存到:', res.tempFilePath)
        }
      },
      fail: (err) => {
        wx.hideLoading()
        console.error('[结果页] 下载失败:', err)
        wx.showToast({
          title: '下载失败',
          icon: 'none'
        })
      }
    })
  },

  /**
   * 重新生成
   */
  regenerate() {
    console.log('[结果页] 重新生成')
    wx.showModal({
      title: '提示',
      content: '确定要重新生成吗？',
      success: (res) => {
        if (res.confirm) {
          // 返回主页并保留提示词
          wx.navigateBack({
            delta: 1,
            success: () => {
              // 通过全局事件通知主页重新生成
              const pages = getCurrentPages()
              const prevPage = pages[pages.length - 1]
              if (prevPage && prevPage.regenerateVideo) {
                prevPage.regenerateVideo(this.data.prompt)
              }
            }
          })
        }
      }
    })
  },

  /**
   * 返回上一页
   */
  goBack() {
    console.log('[结果页] 返回')
    wx.navigateBack({
      delta: 1
    })
  },

  /**
   * 返回首页
   */
  goHome() {
    console.log('[结果页] 返回首页')
    wx.reLaunch({
      url: '/pages/index/index'
    })
  },

  /**
   * 新建视频
   */
  generateNew() {
    console.log('[结果页] 新建视频')
    wx.reLaunch({
      url: '/pages/index/index'
    })
  },

  /**
   * 页面相关事件处理函数
   */
  onPullDownRefresh() {

  },

  onReachBottom() {

  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage() {
    return {
      title: '我用AI生成了这个视频',
      path: '/pages/index/index',
      imageUrl: this.data.videoUrl
    }
  },

  /**
   * 用户点击右上角分享到朋友圈
   */
  onShareTimeline() {
    return {
      title: 'AI视频创作',
      query: '',
      imageUrl: this.data.videoUrl
    }
  }
})
