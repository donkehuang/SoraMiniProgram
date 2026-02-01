// 使用本地API服务版本（集成微信云存储）
import cloudStorage from '../../utils/cloudStorage.js'

Page({
  data: {
    prompt: '',
    durationOptions: ['4秒', '8秒', '12秒'],
    durationIndex: 0,
    loading: false,
    videoUrl: '',
    errorMessage: '',
    apiBaseUrl: 'http://192.168.31.110:5000', // API服务器地址（使用本机IP）

    // 视频生成状态
    isGenerating: false,
    currentVideoId: null,
    generationProgress: 0,
    generationStatus: '',
    statusText: '',

    // 云存储上传状态
    isUploading: false,
    uploadProgress: 0,

    // 背景视频 - 使用云存储（请将下面的 URL 替换为你的云存储 URL）
    backgroundVideoUrl: 'https://636c-cloud1-2gd0041e12763b47-1401157928.tcb.qcloud.la/background/background.mp4?sign=9bf5ba795ce36ce41900bf2f984fcff8&t=1769920825',
    showBackgroundVideo: true,
    backgroundVideoLoading: true
  },

  onLoad() {
    console.log('[页面加载] 首页加载完成')
    console.log('[背景视频] 路径:', this.data.backgroundVideoUrl)
    
    // 设置背景视频加载超时
    setTimeout(() => {
      this.setData({
        backgroundVideoLoading: false
      })
    }, 3000)
  },

  // 背景视频播放成功
  onBackgroundVideoPlay(e) {
    console.log('[背景视频] 播放成功')
    this.setData({
      showBackgroundVideo: true,
      backgroundVideoLoading: false
    })
  },

  // 背景视频加载错误
  onBackgroundVideoError(e) {
    console.error('[背景视频] 加载失败:', e.detail)
    wx.showToast({
      title: '背景视频加载失败',
      icon: 'none',
      duration: 2000
    })
    this.setData({
      showBackgroundVideo: false,
      backgroundVideoLoading: false
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
    const { prompt, durationIndex, durationOptions, apiBaseUrl } = this.data

    if (!prompt.trim()) {
      this.setData({
        errorMessage: '请输入视频描述'
      })
      return
    }

    // 清除之前的错误信息
    this.setData({
      errorMessage: '',
      videoUrl: ''
    })

    try {
      const duration = durationOptions[durationIndex].replace('秒', '')

      console.log('[开始] 创建视频生成任务...')

      // 封装 wx.request 为 Promise
      const requestPromise = new Promise((resolve, reject) => {
        wx.request({
          url: `${apiBaseUrl}/api/generate-video`,
          method: 'POST',
          data: {
            prompt: prompt,
            seconds: duration
          },
          header: {
            'content-type': 'application/json'
          },
          success: resolve,
          fail: reject
        })
      })

      const res = await requestPromise
      console.log('[响应] 创建任务响应:', res.data)

      // 检查响应数据
      if (!res.data || !res.data.success) {
        throw new Error(res.data?.error || '创建任务失败')
      }

      const videoId = res.data.videoId
      console.log('[成功] 任务创建成功，视频ID:', videoId)

      // 开始轮询查询状态
      this.setData({
        currentVideoId: videoId,
        isGenerating: true,
        generationProgress: 0,
        generationStatus: 'queued',
        statusText: '排队中...'
      })

      // 启动轮询
      this.pollVideoStatus(videoId, apiBaseUrl)

    } catch (error) {
      console.error('[错误] 生成视频失败:', error)
      this.setData({
        errorMessage: error.message || '生成失败，请检查API服务器是否正常运行'
      })
    }
  },

  // 轮询查询视频状态
  pollVideoStatus(videoId, apiBaseUrl) {
    const pollInterval = 3000 // 每3秒查询一次

    const poll = async () => {
      try {
        const res = await new Promise((resolve, reject) => {
          wx.request({
            url: `${apiBaseUrl}/api/video-status/${videoId}`,
            method: 'GET',
            header: {
              'content-type': 'application/json'
            },
            success: resolve,
            fail: reject
          })
        })

        console.log('[状态查询] 响应:', res.data)

        if (!res.data || !res.data.success) {
          throw new Error('查询状态失败')
        }

        const status = res.data.status
        const progress = res.data.progress

        // 更新状态显示
        const statusMap = {
          'queued': '排队中',
          'in_progress': '生成中',
          'completed': '已完成',
          'failed': '失败'
        }

        this.setData({
          generationStatus: status,
          generationProgress: progress,
          statusText: `${statusMap[status] || status} (${progress}%)`
        })

        console.log(`[进度] ${statusMap[status]}: ${progress}%`)

        // 检查状态
        if (status === 'completed') {
          // 视频生成完成
          console.log('[完成] 视频生成完成')

          // 显示上传状态
          this.setData({
            statusText: '等待视频就绪...'
          })

          // 等待2秒，确保服务器端已经完成视频下载
          console.log('[等待] 等待服务器端完成视频下载...')
          await new Promise(resolve => setTimeout(resolve, 2000))

          // 显示上传状态
          this.setData({
            statusText: '正在下载视频...'
          })

          try {
            // 1. 下载视频到本地临时路径（带重试）
            console.log('[步骤1] 开始下载视频到本地...')
            const localPath = await this.downloadVideoWithRetry(videoId, apiBaseUrl, 3)
            console.log('[步骤1] 下载完成:', localPath)

            // 2. 上传到微信云存储
            console.log('[步骤2] 开始上传到云存储...')
            this.setData({
              isUploading: true
            })

            const timestamp = Date.now()
            const cloudPath = `videos/${timestamp}_${videoId}.mp4`
            const uploadResult = await cloudStorage.uploadFile(localPath, cloudPath)

            console.log('[步骤2] 上传成功!')
            console.log('[步骤2] fileID:', uploadResult.fileID)
            console.log('[步骤2] URL:', uploadResult.tempFileURL)

            // 3. 保存视频信息到云数据库
            console.log('[步骤3] 保存视频信息到云数据库...')
            await this.saveVideoToDatabase(videoId, uploadResult, timestamp)

            // 4. 使用云存储URL
            this.setData({
              isGenerating: false,
              isUploading: false,
              videoUrl: uploadResult.tempFileURL,
              generationProgress: 100,
              statusText: '生成完成！'
            })

            // 5. 清理本地临时文件
            wx.removeSavedFile({
              filePath: localPath,
              success: () => {
                console.log('[清理] 本地临时文件已删除')
              },
              fail: (err) => {
                console.warn('[清理] 删除临时文件失败:', err)
              }
            })

          } catch (error) {
            console.error('[错误] 上传失败:', error)
            this.setData({
              isGenerating: false,
              isUploading: false,
              errorMessage: `上传失败: ${error.message || '未知错误'}`
            })
          }

          return // 停止轮询

        } else if (status === 'failed') {
          // 视频生成失败
          console.error('[失败] 视频生成失败:', res.data.error)

          this.setData({
            isGenerating: false,
            errorMessage: res.data.error || '视频生成失败'
          })

          return // 停止轮询

        } else {
          // 继续轮询
          setTimeout(() => {
            if (this.data.currentVideoId === videoId) {
              poll()
            }
          }, pollInterval)
        }

      } catch (error) {
        console.error('[错误] 状态查询失败:', error)

        // 如果不是正在生成，停止轮询
        if (this.data.currentVideoId !== videoId) {
          return
        }

        // 继续轮询（网络错误不中断）
        setTimeout(() => {
          if (this.data.currentVideoId === videoId) {
            poll()
          }
        }, pollInterval)
      }
    }

    // 开始轮询
    poll()
  },

  // 取消生成
  cancelGeneration() {
    console.log('[取消] 取消视频生成')
    this.setData({
      currentVideoId: null,
      isGenerating: false,
      generationProgress: 0,
      statusText: ''
    })
  },

  // 保存视频信息到云数据库
  async saveVideoToDatabase(videoId, uploadResult, timestamp) {
    try {
      const db = wx.cloud.database()

      // 获取当前用户信息（如果已登录）
      const userInfo = wx.getStorageSync('userInfo') || {}

      // 格式化日期
      const date = new Date(timestamp)
      const dateStr = `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`

      const videoData = {
        videoId: videoId,
        prompt: this.data.prompt,
        duration: this.data.durationOptions[this.data.durationIndex],
        fileID: uploadResult.fileID,
        httpURL: uploadResult.tempFileURL || uploadResult.fileID,
        createTime: db.serverDate(),
        date: dateStr,
        timestamp: timestamp,
        userInfo: userInfo.nickName ? {
          nickName: userInfo.nickName,
          avatarUrl: userInfo.avatarUrl
        } : null
      }

      console.log('[数据库] 保存视频信息:', videoData)

      // 保存到云数据库
      const res = await db.collection('videos').add({
        data: videoData
      })

      console.log('[数据库] 保存成功:', res._id)
      console.log('[数据库] 视频信息已保存到云数据库')

    } catch (error) {
      console.error('[数据库] 保存失败:', error)
      // 保存失败不影响视频生成流程，只是无法在作品页显示
      wx.showToast({
        title: '作品保存失败',
        icon: 'none'
      })
    }
  },

  // 智能等待视频文件就绪
  async waitForVideoReady(videoId, apiBaseUrl) {
    console.log('[等待] 开始智能等待视频文件就绪...')

    const filename = `${videoId}.mp4`
    const maxAttempts = 10  // 最多尝试10次
    const checkInterval = 3000  // 每3秒检查一次

    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      console.log(`[等待] 第 ${attempt} 次检查文件...`)

      try {
        // 尝试请求文件
        const fileExists = await this.checkVideoExists(videoId, apiBaseUrl)

        if (fileExists) {
          console.log(`[等待] ✅ 文件就绪，第 ${attempt} 次检查成功`)
          return true  // 文件存在，可以继续
        }

        // 文件不存在，等待后重试
        console.log(`[等待] ⏸️ 文件未就绪，等待 ${checkInterval/1000} 秒后重试...`)
        await new Promise(resolve => setTimeout(resolve, checkInterval))

      } catch (error) {
        console.error(`[等待] 第 ${attempt} 次检查出错:`, error)
        
        // 最后一次尝试失败，直接返回，让下载重试机制处理
        if (attempt === maxAttempts) {
          console.warn('[等待] 已达到最大尝试次数，继续下载流程')
          return false
        }
        
        // 等待后继续尝试
        await new Promise(resolve => setTimeout(resolve, checkInterval))
      }
    }

    console.log('[等待] 等待结束，继续下载')
    return false
  },

  // 检查视频文件是否存在
  async checkVideoExists(videoId, apiBaseUrl) {
    const filename = `${videoId}.mp4`
    const url = `${apiBaseUrl}/videos/${filename}`

    return new Promise((resolve, reject) => {
      wx.request({
        url: url,
        method: 'HEAD',
        timeout: 5000,
        success: (res) => {
          // HEAD请求成功，检查状态码
          resolve(res.statusCode === 200)
        },
        fail: (err) => {
          // 请求失败
          resolve(false)
        }
      })
    })
  },

  // 跳转到测试页面
  goToTest() {
    wx.navigateTo({
      url: '/pages/test/test'
    })
  },

  // 视频播放事件
  onVideoPlay(e) {
    console.log('[视频] 开始播放:', e)
  },

  // 视频加载完成事件
  onVideoLoad(e) {
    console.log('[视频] 加载完成:', e)
    console.log('[视频] 视频时长:', e.detail.duration)
  },

  // 视频错误事件
  onVideoError(e) {
    console.error('[视频] 播放错误:', e)
    console.error('[视频] 错误详情:', e.detail)
    this.setData({
      errorMessage: `视频播放错误: ${e.detail.errMsg || '未知错误'}`
    })
  },

  // 下载视频到本地临时目录（带重试）
  async downloadVideoWithRetry(videoId, apiBaseUrl, maxRetries = 3) {
    console.log(`[重试下载] 开始下载视频，最大重试次数: ${maxRetries}`)

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        console.log(`[重试下载] 第 ${attempt} 次尝试...`)

        const localPath = await this.downloadVideoToLocal(videoId, apiBaseUrl)
        console.log(`[重试下载] ✅ 第 ${attempt} 次下载成功`)
        return localPath

      } catch (error) {
        console.error(`[重试下载] ❌ 第 ${attempt} 次失败:`, error.message)

        // 如果是最后一次尝试，抛出错误
        if (attempt === maxRetries) {
          console.error(`[重试下载] 已达到最大重试次数，放弃`)
          throw error
        }

        // 等待2秒后重试
        const waitTime = 2000
        console.log(`[重试下载] 等待 ${waitTime}ms 后重试...`)
        await new Promise(resolve => setTimeout(resolve, waitTime))
      }
    }
  },

  // 下载视频到本地临时目录
  async downloadVideoToLocal(videoId, apiBaseUrl) {
    console.log('[下载] 开始下载视频到本地')

    const filename = `${videoId}.mp4`
    const url = `${apiBaseUrl}/videos/${filename}`

    return new Promise((resolve, reject) => {
      wx.downloadFile({
        url: url,
        success: (res) => {
          if (res.statusCode === 200) {
            console.log('[下载] 下载成功:', res.tempFilePath)
            console.log('[下载] 文件大小:', res.tempFileSize)
            resolve(res.tempFilePath)
          } else {
            console.error('[下载] HTTP错误:', res.statusCode)
            reject(new Error(`下载失败: HTTP ${res.statusCode}`))
          }
        },
        fail: (err) => {
          console.error('[下载] 下载失败:', err)
          reject(new Error(err.errMsg || '下载失败'))
        }
      })
    })
  }
})
