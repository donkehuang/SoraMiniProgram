// pages/smile-result/smile-result.js
Page({
  /**
   * 页面的初始数据
   */
  data: {
    imageUrl: '',
    prompt: '',
    orientation: 'vertical',
    resolution: '高清',
    generatedAt: '',
    imageLoading: true,
    backgroundVideoFileID: 'cloud://cloud1-2gd0041e12763b47.636c-cloud1-2gd0041e12763b47-1401157928/background/background.mp4',
    backgroundVideoUrl: '',
    showBackgroundVideo: false,
    backgroundVideoLoading: false
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {
    // 获取系统状态栏高度
    const systemInfo = wx.getSystemInfoSync()
    const statusBarHeight = systemInfo.statusBarHeight || 0
    const navigationBarHeight = statusBarHeight + 88 // 88rpx = 44px 是导航栏内容高度
    console.log('[开口笑结果页] 状态栏高度:', statusBarHeight, '导航栏高度:', navigationBarHeight)

    this.setData({
      statusBarHeight: statusBarHeight,
      navigationBarHeight: navigationBarHeight
    })

    this.loadBackgroundVideo()
    console.log('[开口笑结果页] 加载参数:', options)

    // 解析参数
    let imageUrl = options.imageUrl ? decodeURIComponent(options.imageUrl) : ''
    const prompt = options.prompt ? decodeURIComponent(options.prompt) : ''
    const orientation = options.orientation || 'vertical'
    const resolution = options.resolution || '高清'

    console.log('[开口笑结果页] 原始图片URL:', imageUrl)

    // 检查是否已经是临时URL（避免重复转换）
    const isTempUrl = imageUrl.includes('http://tmp') || imageUrl.includes('https://tmp')

    // 如果是云存储路径且不是临时URL，需要获取临时URL
    if (!isTempUrl && (imageUrl.includes('cloud://') || imageUrl.includes('tcb.qcloud.la'))) {
      console.log('[开口笑结果页] 检测到云存储URL，尝试获取临时URL')

      if (wx.cloud) {
        wx.cloud.getTempFileURL({
          fileList: [imageUrl],
          success: (res) => {
            if (res.fileList && res.fileList.length > 0) {
              const tempUrl = res.fileList[0].tempFileURL
              console.log('[开口笑结果页] 临时URL获取成功:', tempUrl)
              this.setData({
                imageUrl: tempUrl,
                prompt,
                orientation,
                resolution,
                generatedAt: this.formatTime(new Date()),
                imageLoading: false  // 关键：获取到URL后，设置imageLoading为false，等待图片的bindload事件
              })
              console.log('[开口笑结果页] setData后数据检查 - imageUrl:', tempUrl, 'imageLoading: false')
            } else {
              console.error('[开口笑结果页] 临时URL获取失败：返回数据为空')
              this.setData({
                imageUrl,
                prompt,
                orientation,
                resolution,
                generatedAt: this.formatTime(new Date()),
                imageLoading: false  // 即使失败也设为false，避免一直显示加载
              })
            }
          },
          fail: (err) => {
            console.error('[开口笑结果页] 临时URL获取失败:', err)
            // 失败时使用原始URL
            this.setData({
              imageUrl,
              prompt,
              orientation,
              resolution,
              generatedAt: this.formatTime(new Date()),
              imageLoading: false
            })
          }
        })
      } else {
        console.warn('[开口笑结果页] 云开发未初始化，使用原始URL')
        this.setData({
          imageUrl,
          prompt,
          orientation,
          resolution,
          generatedAt: this.formatTime(new Date()),
          imageLoading: false
        })
      }
    } else {
      // 普通URL或临时URL直接使用
      console.log('[开口笑结果页] 使用URL:', imageUrl, '(临时URL:', isTempUrl ? '是' : '否', ')')
      this.setData({
        imageUrl,
        prompt,
        orientation,
        resolution,
        generatedAt: this.formatTime(new Date()),
        imageLoading: false
      })
    }

    console.log('[开口笑结果页] 页面数据:', this.data)
  },

  /**
   * 加载背景视频
   */
  async loadBackgroundVideo() {
    console.log('[开口笑结果页] 开始加载背景视频')

    this.setData({
      backgroundVideoLoading: true,
      showBackgroundVideo: false
    })

    if (wx.cloud) {
      try {
        // 尝试从云存储获取背景视频
        const result = await wx.cloud.getTempFileURL({
          fileList: [this.data.backgroundVideoFileID]
        })

        console.log('[开口笑结果页] 背景视频获取结果:', result)

        if (result.fileList && result.fileList.length > 0 && result.fileList[0].status === 0) {
          const tempURL = result.fileList[0].tempFileURL
          console.log('[开口笑结果页] 背景视频临时URL:', tempURL)
          this.setData({
            backgroundVideoUrl: tempURL,
            showBackgroundVideo: true,
            backgroundVideoLoading: false
          })
        } else {
          console.error('[开口笑结果页] 背景视频获取失败')
          this.setData({
            backgroundVideoLoading: false,
            showBackgroundVideo: false
          })
        }
      } catch (err) {
        console.error('[开口笑结果页] 背景视频加载异常:', err)
        this.setData({
          backgroundVideoLoading: false,
          showBackgroundVideo: false
        })
      }
    } else {
      console.warn('[开口笑结果页] 云开发未初始化，不显示背景视频')
      this.setData({
        backgroundVideoLoading: false,
        showBackgroundVideo: false
      })
    }
  },

  /**
   * 背景视频播放成功
   */
  onBackgroundVideoPlay(e) {
    console.log('[开口笑结果页] 背景视频播放成功:', e)
    this.setData({
      showBackgroundVideo: true,
      backgroundVideoLoading: false
    })
  },

  /**
   * 背景视频加载失败
   */
  onBackgroundVideoError(e) {
    console.error('[开口笑结果页] 背景视频加载失败:', e)
    this.setData({
      showBackgroundVideo: false,
      backgroundVideoLoading: false
    })
  },

  /**
   * 图片加载完成
   */
  onImageLoad(e) {
    console.log('[开口笑结果页] 图片加载成功:', e.detail)
    this.setData({
      imageLoading: false
    })
  },

  /**
   * 图片加载失败
   */
  onImageError(e) {
    console.error('[开口笑结果页] 图片加载失败:', e.detail)
    console.error('[开口笑结果页] 图片URL:', this.data.imageUrl)
    console.error('[开口笑结果页] 错误类型:', e.detail.errMsg)
    console.error('[开口笑结果页] 当前状态:', this.data)

    // 停止加载动画
    this.setData({
      imageLoading: false
    })

    // 显示错误提示
    wx.showModal({
      title: '图片加载失败',
      content: '无法加载生成的图片。\n\n可能原因：\n1. 图片URL已过期（云存储临时URL有效期为2小时）\n2. 网络连接问题\n3. 云存储权限问题',
      confirmText: '重新生成',
      cancelText: '返回',
      success: (res) => {
        if (res.confirm) {
          // 返回重新生成
          console.log('[开口笑结果页] 用户选择重新生成')
          wx.navigateBack()
        } else {
          // 返回上一页
          console.log('[开口笑结果页] 用户选择返回')
          wx.navigateBack()
        }
      }
    })
  },

  /**
   * 保存到相册
   */
  saveToAlbum() {
    const { imageUrl } = this.data

    if (!imageUrl) {
      wx.showToast({
        title: '图片URL无效',
        icon: 'none'
      })
      return
    }

    console.log('[开口笑结果页] 保存到相册:', imageUrl)

    wx.downloadFile({
      url: imageUrl,
      success: (res) => {
        if (res.statusCode === 200) {
          const tempFilePath = res.tempFilePath

          wx.saveImageToPhotosAlbum({
            filePath: tempFilePath,
            success: () => {
              wx.showToast({
                title: '已保存到相册',
                icon: 'success'
              })
            },
            fail: (err) => {
              console.error('[开口笑结果页] 保存失败:', err)

              if (err.errMsg.includes('auth')) {
                wx.showModal({
                  title: '授权提示',
                  content: '需要您的相册权限才能保存图片',
                  confirmText: '去授权',
                  success: (modalRes) => {
                    if (modalRes.confirm) {
                      wx.openSetting()
                    }
                  }
                })
              } else {
                wx.showToast({
                  title: '保存失败',
                  icon: 'none'
                })
              }
            }
          })
        } else {
          wx.showToast({
            title: '下载失败',
            icon: 'none'
          })
        }
      },
      fail: (err) => {
        console.error('[开口笑结果页] 下载失败:', err)
        wx.showToast({
          title: '下载失败',
          icon: 'none'
        })
      }
    })
  },

  /**
   * 下载图片
   */
  downloadImage() {
    const { imageUrl } = this.data

    if (!imageUrl) {
      wx.showToast({
        title: '图片URL无效',
        icon: 'none'
      })
      return
    }

    console.log('[开口笑结果页] 下载图片:', imageUrl)

    wx.downloadFile({
      url: imageUrl,
      success: (res) => {
        if (res.statusCode === 200) {
          wx.showToast({
            title: '下载成功',
            icon: 'success'
          })
        } else {
          wx.showToast({
            title: '下载失败',
            icon: 'none'
          })
        }
      },
      fail: (err) => {
        console.error('[开口笑结果页] 下载失败:', err)
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
    console.log('[开口笑结果页] 重新生成')
    wx.navigateBack({
      delta: 1
    })
  },

  /**
   * 返回上一页
   */
  goBack() {
    console.log('[开口笑结果页] 返回上一页 - 触发')
    
    // 获取当前页面栈
    const pages = getCurrentPages()
    console.log('[开口笑结果页] 当前页面栈长度:', pages.length)
    
    if (pages.length > 1) {
      wx.showToast({
        title: '返回中...',
        icon: 'none',
        duration: 500
      })
      setTimeout(() => {
        wx.navigateBack({
          delta: 1,
          fail: (err) => {
            console.error('[开口笑结果页] 返回失败:', err)
            // 如果navigateBack失败,尝试回到首页
            wx.switchTab({
              url: '/pages/index/index'
            })
          }
        })
      }, 300)
    } else {
      console.log('[开口笑结果页] 没有上一页,返回首页')
      wx.showToast({
        title: '返回首页...',
        icon: 'none',
        duration: 500
      })
      setTimeout(() => {
        wx.switchTab({
          url: '/pages/index/index'
        })
      }, 300)
    }
  },

  /**
   * 返回首页
   */
  goHome() {
    console.log('[开口笑结果页] 返回首页')
    wx.switchTab({
      url: '/pages/index/index'
    })
  },

  /**
   * 新建图片
   */
  createNew() {
    console.log('[开口笑结果页] 新建图片')
    wx.reLaunch({
      url: '/pages/index/index?function=smile'
    })
  },

  /**
   * 分享
   */
  onShareAppMessage() {
    const { prompt } = this.data
    return {
      title: `我用开口笑生成了${prompt || '超有趣的图片'}`,
      path: '/pages/index/index',
      imageUrl: this.data.imageUrl || ''
    }
  },

  /**
   * 格式化时间
   */
  formatTime(date) {
    const year = date.getFullYear()
    const month = date.getMonth() + 1
    const day = date.getDate()
    const hour = date.getHours()
    const minute = date.getMinutes()

    return `${year}-${month}-${day} ${hour}:${minute}`
  }
})
