// 使用本地API服务版本（集成微信云存储）
import cloudStorage from '../../utils/cloudStorage.js'

Page({
  data: {
    prompt: '',
    durationOptions: ['4秒', '8秒', '12秒'],
    durationIndex: 0,
    orientationOptions: ['横屏 16:9', '竖屏 9:16'],
    orientationIndex: 1,  // 默认竖屏
    loading: false,
    videoUrl: '',
    errorMessage: '',
    apiBaseUrl: 'https://www.enfuri51.xyz', // API服务器地址（HTTPS域名）

    // 界面状态
    showCreateView: false, // 是否显示创作界面

    // 预设prompt风格
    styleOptions: [],
    styleIndex: 0,
    
    // 风格模板数据（从prompt.md解析）
    promptTemplates: {
      '4秒': [
        { name: '卡点/潮流热点', template: 'Upbeat viral [trend sound], 3-4 ultra-fast scene cuts, hard beat sync with flash effects, dynamic zoom/pan, no text (duet-friendly frame), 4s high-energy clip, bright saturated color grading, TikTok\'s classic fast-cut style. The video script output is in English. All languages, subtitles, and voiceovers are in Chinese.' },
        { name: '美食制作', template: 'Viral food ASMR [trend sound], fast close-up of [core step], sizzle/crunch ASMR, golden food texture, 1s finished food close-up, no text, 4s appetizing clip, warm tone, TikTok fast food ASMR style. The video script output is in English. All languages, subtitles, and voiceovers are in Chinese.' },
        { name: '生活小技巧', template: 'Upbeat casual [trend sound], 1s problem close-up, 2s quick fix with [tool/skill], 1s result close-up, bold neon text [1-word tip] (pop-up), 4s TikTok quick hack, bright indoor light, fast pace. The video script output is in English. All languages, subtitles, and voiceovers are in Chinese.' },
        { name: '萌宠日常', template: 'Viral cute [trend sound], fast close-up of [pet] doing [fun action], silly face focus, no text, 4s TikTok pet clip, warm tone, flash effect on cute frame, 4:5 aspect. The video script output is in English. All languages, subtitles, and voiceovers are in Chinese.' },
        { name: '美妆教程', template: 'Viral beauty [trend sound], fast close-up of [core beauty step], smooth hand movement, 1s finished effect close-up, no text, 4s TikTok beauty clip, soft ring light, flash effect on end frame. The video script output is in English. All languages, subtitles, and voiceovers are in Chinese.' },
        { name: '搞笑小剧场', template: 'Viral funny [trend sound], 2-person quick interaction, [funny twist], laugh sound effect (loud) at end, neon text [funny emoji/1 word joke] (pop-up), 4s TikTok funny skit, bright scene light, 4:5 aspect. The video script output is in English. All languages, subtitles, and voiceovers are in Chinese.' }
      ],
      '8秒': [
        { name: '卡点/潮流热点', template: 'Viral [trend sound] (chorus drop), slow-in fast-out lens, 5-6 beat-synced cuts, body/object sync to rhythm, flash/strobe effects on hard beats, bold neon text pop-up (1 word) on beat, 8s seamless clip, TikTok trend-ready, high energy. The video script output is in English. All languages, subtitles, and voiceovers are in Chinese.' },
        { name: '美食制作', template: 'Trend food ASMR sound, 2 key [simple food] steps (ultra-close up), loud crisp ASMR, pan to finished food at 6s, 1s bite shot with crunch sound, neon text [food name] (bottom), 8s TikTok food bite clip, warm fast tone, 4:5 aspect. The video script output is in English. All languages, subtitles, and voiceovers are in Chinese.' },
        { name: '生活小技巧', template: 'Light trend sound, 2s problem scene (fast), 3-5s 2 hack steps (ultra-close up), 6-8s result (flash effect), bold text [problem + solution] (bottom), 8s TikTok hack clip, casual home scene, no clutter. The video script output is in English. All languages, subtitles, and voiceovers are in Chinese.' },
        { name: '萌宠日常', template: 'Playful viral [trend sound], 2 pet cute moments (fast cut), slow mo on funny expression, pan camera follow pet, neon text [pet name + cute phrase] (corner), 8s TikTok pet daily, cozy home scene, laugh sound effect at end. The video script output is in English. All languages, subtitles, and voiceovers are in Chinese.' },
        { name: '美妆教程', template: 'Light beauty trend sound, 2 [makeup/skincare] steps (fast close up), smooth operation, 6s half-face effect (flash), neon text [product/step name] (bottom), 8s TikTok beauty tutorial, soft ring light, 4:5 aspect. The video script output is in English. All languages, subtitles, and voiceovers are in Chinese.' },
        { name: '搞笑小剧场', template: 'Funny viral trend sound, 1-scene skit, 2s setup (fast), 3-6s funny development, 7-8s punchline + funny reaction (flash), neon text [plot hint] (bottom), comedy sound effects (giggle/surprise), 8s TikTok skit, casual home/cafe scene. The video script output is in English. All languages, subtitles, and voiceovers are in Chinese.' }
      ],
      '12秒': [
        { name: '卡点/潮流热点', template: 'Full short viral [trend sound], 2s slow-mo opening, 7-8 non-stop beat-synced cuts, every beat matched with action/transition, dynamic camera (spin/zoom), colorful flash text overlay on beats, cool freeze frame end, 4:5 aspect, TikTok duet/stitch-friendly. The video script output is in English. All languages, subtitles, and voiceovers are in Chinese.' },
        { name: '美食制作', template: 'Casual food trend sound, 3-4 [easy food] steps (fast close up), non-stop crisp ASMR, seasoning close-up at 5s (flash effect), flip/fry at 8s, plating at 10s, neon text [food name + quick tip] (bottom), 12s TikTok food make clip, warm kitchen scene. The video script output is in English. All languages, subtitles, and voiceovers are in Chinese.' },
        { name: '生活小技巧', template: 'Casual upbeat sound, 2s messy problem scene (fast), 3-9s 3 hack steps (fast close up, flash on steps), 10-12s result + "save it" neon text pop-up, 12s TikTok hack clip, casual home scene, 4:5 aspect. The video script output is in English. All languages, subtitles, and voiceovers are in Chinese.' },
        { name: '萌宠日常', template: 'Cute viral trend sound, 3 pet sweet moments (fast cut), slow mo on key cute frames, owner hand touch pet (flash effect) at 8s, neon text [short cute sentence] (bottom), pet wink/lick end frame, 12s TikTok pet daily, soft home light. The video script output is in English. All languages, subtitles, and voiceovers are in Chinese.' },
        { name: '美妆教程', template: 'Casual beauty trend sound, 3 [daily makeup/skincare] steps (fast close up), smooth hand movement, 9s full-face effect (flash), neon numbered text [Step1/2/3] (bottom), head turn pose end, 12s TikTok beauty tutorial, soft ring light. The video script output is in English. All languages, subtitles, and voiceovers are in Chinese.' },
        { name: '搞笑小剧场', template: 'Upbeat comedy trend sound, 1-scene 2-3 character skit, 2s fast setup, 3-8s development (fast cut + small twists), 9-12s punchline + over-the-top funny reaction, non-stop comedy sound effects, neon text [dialogue/caption] (bottom), funny freeze frame end, 12s TikTok skit, bright daily scene. The video script output is in English. All languages, subtitles, and voiceovers are in Chinese.' }
      ]
    },

    // 视频生成状态
    isGenerating: false,
    currentVideoId: null,
    generationProgress: 0,
    generationStatus: '',
    statusText: '',

    // 云存储上传状态
    isUploading: false,
    uploadProgress: 0,

    // 背景视频 - 使用云存储FileID（自动获取临时URL）
    backgroundVideoFileID: 'cloud://cloud1-2gd0041e12763b47.636c-cloud1-2gd0041e12763b47-1401157928/background/background.mp4',
    backgroundVideoUrl: '',
    showBackgroundVideo: false,
    backgroundVideoLoading: true
  },

  onLoad() {
    console.log('[页面加载] 首页加载完成')
    
    // 初始化风格选项（根据默认时长）
    this.updateStyleOptions()

    // 动态获取背景视频URL
    this.loadBackgroundVideo()
  },

  // 动态加载背景视频URL
  async loadBackgroundVideo() {
    try {
      console.log('[背景视频] 开始获取临时URL...')
      
      if (!wx.cloud) {
        console.error('[背景视频] 云开发未初始化')
        this.setData({
          backgroundVideoLoading: false,
          showBackgroundVideo: false
        })
        return
      }

      const result = await wx.cloud.getTempFileURL({
        fileList: [this.data.backgroundVideoFileID]
      })

      if (result.fileList && result.fileList.length > 0) {
        const tempURL = result.fileList[0].tempFileURL
        console.log('[背景视频] 获取临时URL成功:', tempURL)
        
        this.setData({
          backgroundVideoUrl: tempURL,
          showBackgroundVideo: true,
          backgroundVideoLoading: false
        })
      } else {
        throw new Error('未获取到临时URL')
      }
    } catch (error) {
      console.error('[背景视频] 获取临时URL失败:', error)
      this.setData({
        backgroundVideoLoading: false,
        showBackgroundVideo: false
      })
      
      // 不显示错误提示，静默失败
    }
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
    const newIndex = parseInt(e.detail.value)
    this.setData({
      durationIndex: newIndex,
      styleIndex: 0  // 重置风格选择
    })
    // 更新风格选项
    this.updateStyleOptions()
  },

  onStyleChange(e) {
    this.setData({
      styleIndex: parseInt(e.detail.value)
    })
  },

  // 根据当前时长更新风格选项
  updateStyleOptions() {
    const duration = this.data.durationOptions[this.data.durationIndex]
    const templates = this.data.promptTemplates[duration] || []
    const styleNames = templates.map(t => t.name)
    
    this.setData({
      styleOptions: styleNames
    })
    
    console.log('[风格更新] 时长:', duration, '风格选项:', styleNames)
  },

  onOrientationChange(e) {
    this.setData({
      orientationIndex: parseInt(e.detail.value)
    })
  },

  // 卡片点击事件
  enterCreate() {
    console.log('[卡片] 进入创作界面')
    this.setData({
      showCreateView: true
    })
  },

  enterImageGen() {
    wx.showToast({
      title: '生图功能即将上线',
      icon: 'none',
      duration: 2000
    })
  },

  enterPromptEdit() {
    wx.showToast({
      title: '提示词优化即将上线',
      icon: 'none',
      duration: 2000
    })
  },

  backToMain() {
    console.log('[返回] 回到主界面')
    this.setData({
      showCreateView: false
    })
  },

  async generateVideo() {
    const { prompt, durationIndex, durationOptions, orientationIndex, styleIndex, apiBaseUrl } = this.data

    if (!prompt.trim()) {
      this.setData({
        errorMessage: '请输入视频描述'
      })
      return
    }

    // 检查登录状态
    const userInfo = wx.getStorageSync('userInfo')
    if (!userInfo || !userInfo.nickName) {
      wx.showModal({
        title: '需要登录',
        content: '请先登录后再生成视频，以便保存您的作品',
        confirmText: '去登录',
        cancelText: '取消',
        success: (res) => {
          if (res.confirm) {
            // 跳转到"我的"页面登录
            wx.switchTab({
              url: '/pages/profile/profile'
            })
          }
        }
      })
      return
    }

    // 清除之前的错误信息
    this.setData({
      errorMessage: '',
      videoUrl: ''
    })

    // 显示调试信息：API地址
    console.log('===========================================')
    console.log('[调试] API地址:', apiBaseUrl)
    const networkType = await this.getNetworkType()
    console.log('[调试] 网络类型:', networkType)
    console.log('===========================================')

    // 保存调试信息到data，用于界面显示
    this.setData({
      debugNetworkType: networkType
    })

    try {
      const duration = durationOptions[durationIndex].replace('秒', '')

      // 根据方向设置分辨率
      const size = orientationIndex === 0 ? '1280x720' : '720x1280' // 0=横屏, 1=竖屏

      console.log('[开始] 创建视频生成任务...', { duration, size })

      // 第一步：使用GPT优化提示词
      this.setData({
        isGenerating: true,
        generationProgress: 5,
        statusText: '正在优化提示词...'
      })

      // 获取选中的风格模板
      const durationKey = durationOptions[durationIndex]
      const templates = this.data.promptTemplates[durationKey] || []
      const selectedTemplate = templates[styleIndex]
      
      if (!selectedTemplate) {
        throw new Error('未找到对应的风格模板')
      }

      console.log('[优化] 调用GPT优化提示词...', {
        userDescription: prompt,
        styleTemplate: selectedTemplate.template,
        duration: durationKey
      })

      // 调用GPT优化API
      const optimizeResult = await new Promise((resolve, reject) => {
        console.log('[优化] 请求URL:', `${apiBaseUrl}/api/optimize-prompt`)
        wx.request({
          url: `${apiBaseUrl}/api/optimize-prompt`,
          method: 'POST',
          data: {
            userDescription: prompt,
            styleTemplate: selectedTemplate.template,
            duration: durationKey
          },
          header: {
            'content-type': 'application/json'
          },
          success: (res) => {
            console.log('[优化] API响应状态码:', res.statusCode)
            console.log('[优化] API响应数据:', res.data)
            this.setData({ statusText: `GPT优化中... (${res.statusCode})` })
            resolve(res)
          },
          fail: (err) => {
            console.error('[优化] 请求失败:', err)
            console.error('[优化] 错误详情:', JSON.stringify(err))
            reject(new Error(`GPT优化请求失败: ${err.errMsg}`))
          }
        })
      })

      if (optimizeResult.statusCode !== 200 || !optimizeResult.data.success) {
        throw new Error(optimizeResult.data.error || 'GPT优化失败')
      }

      const optimizedPrompt = optimizeResult.data.optimizedPrompt
      console.log('[优化] GPT优化完成:', optimizedPrompt)

      // 第二步：使用优化后的提示词生成视频
      this.setData({
        generationProgress: 15,
        statusText: '正在创建视频任务...'
      })

      // 封装 wx.request 为 Promise
      const requestPromise = new Promise((resolve, reject) => {
        console.log('[生成] 请求URL:', `${apiBaseUrl}/api/generate-video`)
        console.log('[生成] 请求参数:', { prompt: optimizedPrompt.substring(0, 50) + '...', seconds: duration, size })
        wx.request({
          url: `${apiBaseUrl}/api/generate-video`,
          method: 'POST',
          data: {
            prompt: optimizedPrompt,  // 使用优化后的提示词
            seconds: duration,
            size: size
          },
          header: {
            'content-type': 'application/json'
          },
          success: (res) => {
            console.log('[生成] API响应状态码:', res.statusCode)
            console.log('[生成] API响应数据:', res.data)
            this.setData({ statusText: `创建任务中... (${res.statusCode})` })
            resolve(res)
          },
          fail: (err) => {
            console.error('[生成] 请求失败:', err)
            console.error('[生成] 错误详情:', JSON.stringify(err))
            reject(new Error(`生成视频请求失败: ${err.errMsg}`))
          }
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
        generationProgress: 20,  // 从20%开始，前面15%是优化阶段
        generationStatus: 'queued',
        statusText: '排队中...'
      })

      // 启动轮询
      this.pollVideoStatus(videoId, apiBaseUrl)

    } catch (error) {
      console.error('[错误] 生成视频失败:', error)
      console.error('[错误] 错误堆栈:', error.stack)

      // 显示详细错误信息
      const errorMsg = error.message || '生成失败，请检查API服务器是否正常运行'
      console.error('[错误] 错误信息:', errorMsg)

      this.setData({
        errorMessage: errorMsg,
        isGenerating: false,
        generationProgress: 0
      })

      // 如果是网络错误，提示检查网络连接
      if (errorMsg.includes('request:fail') || errorMsg.includes('网络') || errorMsg.includes('timeout')) {
        wx.showModal({
          title: '网络错误',
          content: '请检查网络连接或稍后重试',
          showCancel: false
        })
      }
    }
  },

  // 轮询查询视频状态
  pollVideoStatus(videoId, apiBaseUrl) {
    const pollInterval = 3000 // 每3秒查询一次

    const poll = async () => {
      try {
        const res = await new Promise((resolve, reject) => {
          console.log('[状态查询] 请求URL:', `${apiBaseUrl}/api/video-status/${videoId}`)
          wx.request({
            url: `${apiBaseUrl}/api/video-status/${videoId}`,
            method: 'GET',
            header: {
              'content-type': 'application/json'
            },
            success: (res) => {
              console.log('[状态查询] API响应状态码:', res.statusCode)
              console.log('[状态查询] API响应数据:', res.data)
              resolve(res)
            },
            fail: (err) => {
              console.error('[状态查询] 请求失败:', err)
              console.error('[状态查询] 错误详情:', JSON.stringify(err))
              reject(new Error(`状态查询失败: ${err.errMsg}`))
            }
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

        // 更新状态显示（保留GPT优化阶段的进度）
        const actualProgress = Math.max(20, progress * 0.8 + 20)  // 20%-100%区间
        
        this.setData({
          generationStatus: status,
          generationProgress: actualProgress,
          statusText: `${statusMap[status] || status} (${Math.round(actualProgress)}%)`
        })

        console.log(`[进度] ${statusMap[status]}: ${Math.round(actualProgress)}%`)

        // 检查状态
        if (status === 'completed') {
          // 视频生成完成
          console.log('[完成] 视频生成完成')

          // 显示上传状态
          this.setData({
            statusText: '等待视频就绪...'
          })

          // 等待更多时间，确保服务器端已经完成视频下载
          console.log('[等待] 等待服务器端完成视频下载...')
          await new Promise(resolve => setTimeout(resolve, 5000))

          // 显示上传状态
          this.setData({
            statusText: '正在下载视频...'
          })

          try {
            // 智能等待：持续检查文件是否就绪
            console.log('[等待] 开始智能等待视频文件就绪...')
            const fileReady = await this.waitForVideoReady(videoId, apiBaseUrl)

            if (!fileReady) {
              throw new Error('视频文件未就绪，服务器可能还在处理')
            }
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

            // 4. 标记完成（不显示视频）
            this.setData({
              isGenerating: false,
              isUploading: false,
              videoUrl: '',  // 不显示视频
              generationProgress: 100,
              statusText: '生成完成！视频已保存到作品'
            })

            // 5. 显示成功提示并返回主界面
            wx.showToast({
              title: '已保存到作品',
              icon: 'success',
              duration: 2000
            })

            // 延迟1秒后返回主界面
            setTimeout(() => {
              this.setData({
                showCreateView: false,
                prompt: '',
                isGenerating: false,
                generationProgress: 0,
                statusText: ''
              })
            }, 2000)

            // 6. 清理本地临时文件
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

        // 如果是404错误（任务不存在），说明服务器重启了，标记为失败
        if (error.message && error.message.includes('视频任务不存在')) {
          console.error('[错误] 服务器重启，任务丢失')
          this.setData({
            isGenerating: false,
            errorMessage: '服务器重启，请重新生成视频'
          })
          return
        }

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

      // 获取当前用户信息
      const userInfo = wx.getStorageSync('userInfo')
      
      // 再次检查登录状态（双重保险）
      if (!userInfo || !userInfo.nickName) {
        throw new Error('用户未登录，无法保存作品')
      }

      // 格式化日期
      const date = new Date(timestamp)
      const dateStr = `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`

      // 获取视频方向和分辨率
      const orientation = this.data.orientationIndex === 0 ? 'horizontal' : 'vertical'
      const size = this.data.orientationIndex === 0 ? '1280x720' : '720x1280'

      const videoData = {
        videoId: videoId,                           // Sora视频ID
        prompt: this.data.prompt,                   // 提示词
        duration: this.data.durationOptions[this.data.durationIndex],  // 时长
        size: size,                                 // 分辨率
        orientation: orientation,                   // 方向
        fileID: uploadResult.fileID,               // 云存储文件ID
        httpURL: uploadResult.tempFileURL || uploadResult.fileID,  // 临时URL
        status: 'completed',                        // 状态
        createTime: db.serverDate(),               // 服务器时间
        date: dateStr,                             // 日期字符串
        timestamp: timestamp,                       // 时间戳
        userInfo: {
          nickName: userInfo.nickName,
          avatarUrl: userInfo.avatarUrl
        },
        viewCount: 0,                              // 查看次数
        likeCount: 0                               // 点赞次数
      }

      console.log('[数据库] 保存视频信息:', videoData)

      // 保存到云数据库（自动添加 _openid）
      const res = await db.collection('videos').add({
        data: videoData
      })

      console.log('[数据库] 保存成功:', res._id)
      console.log('[数据库] 视频信息已保存到云数据库')

    } catch (error) {
      console.error('[数据库] 保存失败:', error)
      
      // 如果是权限错误，提示用户登录
      if (error.errCode === -502003 || error.message.includes('permission denied')) {
        wx.showModal({
          title: '保存失败',
          content: '数据库权限不足，请退出重新登录',
          confirmText: '去登录',
          success: (res) => {
            if (res.confirm) {
              // 清除登录信息
              wx.removeStorageSync('userInfo')
              // 跳转到登录页
              wx.switchTab({
                url: '/pages/profile/profile'
              })
            }
          }
        })
      } else {
        // 其他错误
        wx.showToast({
          title: '作品保存失败',
          icon: 'none'
        })
      }
      
      throw error  // 重新抛出错误，让上层处理
    }
  },

  // 智能等待视频文件就绪
  async waitForVideoReady(videoId, apiBaseUrl) {
    console.log('[等待] 开始智能等待视频文件就绪...')

    const filename = `${videoId}.mp4`
    const maxAttempts = 20  // 最多尝试20次（60秒）
    const checkInterval = 3000  // 每3秒检查一次

    // 首次等待5秒，给服务器更多时间完成文件写入
    console.log('[等待] 首次等待5秒，等待服务器完成文件写入...')
    await new Promise(resolve => setTimeout(resolve, 5000))

    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      console.log(`[等待] 第 ${attempt} 次检查文件...`)

      try {
        // 尝试请求文件
        const fileExists = await this.checkVideoExists(videoId, apiBaseUrl)

        if (fileExists) {
          console.log(`[等待] ✅ 文件就绪，第 ${attempt} 次检查成功`)
          return true  // 文件存在，可以继续
        }

        // 文件不存在，更新状态
        const progress = 95 + (attempt / maxAttempts) * 5  // 95%-100%
        this.setData({
          generationProgress: Math.min(progress, 100),
          statusText: `等待文件就绪... (${attempt}/${maxAttempts})`
        })

        // 等待后重试
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

  // 检查视频文件是否存在（使用GET请求的range方式）
  async checkVideoExists(videoId, apiBaseUrl) {
    const filename = `${videoId}.mp4`
    const url = `${apiBaseUrl}/videos/${filename}`

    return new Promise((resolve, reject) => {
      // 使用GET请求，只请求第一个字节来检查文件是否存在和大小
      wx.request({
        url: url,
        method: 'GET',
        header: {
          'Range': 'bytes=0-0'  // 只请求第一个字节
        },
        timeout: 5000,
        success: (res) => {
          // GET请求成功，检查状态码和响应大小
          const contentLength = res.header['Content-Length'] || res.header['content-length'] || 0
          const contentType = res.header['Content-Type'] || res.header['content-type'] || ''
          console.log('[检查] 文件检查响应:', {
            statusCode: res.statusCode,
            contentLength: contentLength,
            contentType: contentType
          })
          // 状态码应该是206(Partial Content)或200，并且有有效的大小
          const isVideo = contentType.includes('video') || contentType.includes('mp4')
          resolve((res.statusCode === 206 || res.statusCode === 200) && contentLength > 0 && isVideo)
        },
        fail: (err) => {
          console.error('[检查] GET请求失败:', err)
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

    console.log('[下载] 下载URL:', url)
    console.log('[下载] 开始下载，可能需要较长时间...')

    return new Promise((resolve, reject) => {
      wx.downloadFile({
        url: url,
        timeout: 60000,  // 60秒超时
        success: (res) => {
          console.log('[下载] 收到响应，状态码:', res.statusCode)
          console.log('[下载] 临时文件路径:', res.tempFilePath)
          console.log('[下载] 临时文件大小:', res.tempFileSize)

          if (res.statusCode === 200) {
            if (res.tempFileSize > 0) {
              console.log('[下载] ✅ 下载成功:', res.tempFilePath)
              resolve(res.tempFilePath)
            } else {
              console.error('[下载] ❌ 文件大小为0')
              reject(new Error('下载的文件大小为0，服务器可能尚未完成下载'))
            }
          } else if (res.statusCode === 404) {
            console.error('[下载] ❌ 404 - 文件不存在')
            reject(new Error('视频文件不存在，请稍后重试'))
          } else if (res.statusCode === 403) {
            console.error('[下载] ❌ 403 - 权限拒绝')
            reject(new Error('下载被拒绝，请检查Nginx配置'))
          } else {
            console.error('[下载] ❌ HTTP错误:', res.statusCode)
            reject(new Error(`下载失败: HTTP ${res.statusCode}`))
          }
        },
        fail: (err) => {
          console.error('[下载] 下载失败:', err)
          console.error('[下载] 错误详情:', JSON.stringify(err))

          // 判断错误类型
          if (err.errMsg && err.errMsg.includes('timeout')) {
            reject(new Error('下载超时，文件可能过大'))
          } else if (err.errMsg && err.errMsg.includes('fail')) {
            reject(new Error('网络错误，请检查网络连接'))
          } else {
            reject(new Error(err.errMsg || '下载失败'))
          }
        }
      })
    })
  },

  // 获取网络类型
  getNetworkType() {
    return new Promise((resolve) => {
      wx.getNetworkType({
        success: (res) => {
          resolve(res.networkType)
        },
        fail: () => {
          resolve('unknown')
        }
      })
    })
  }
})
