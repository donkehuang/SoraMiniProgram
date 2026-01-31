// pages/test/test.js
Page({
  data: {
    selectedVideo: false,
    videoPath: '',
    videoName: '',
    videoSize: '',
    cloudPath: 'test-videos',
    isUploading: false,
    uploadProgress: 0,
    uploadStatus: '',
    uploadSuccess: false,
    fileID: '',
    cloudURL: '',
    httpURL: '',
    errorMessage: ''
  },

  onCloudPathInput(e) {
    this.setData({
      cloudPath: e.detail.value
    })
  },

  selectVideo() {
    console.log('[测试] 选择视频')

    wx.chooseVideo({
      sourceType: ['album', 'camera'],
      maxDuration: 60,
      camera: 'back',
      success: (res) => {
        console.log('[测试] 视频选择成功:', res)

        const sizeMB = (res.size / 1024 / 1024).toFixed(2)
        const videoName = res.tempFilePath.split('/').pop() || 'video_' + Date.now() + '.mp4'

        this.setData({
          selectedVideo: true,
          videoPath: res.tempFilePath,
          videoName: videoName,
          videoSize: sizeMB + ' MB',
          uploadSuccess: false,
          fileID: '',
          cloudURL: '',
          httpURL: '',
          errorMessage: ''
        })

        wx.showToast({
          title: '视频已选择',
          icon: 'success'
        })
      },
      fail: (err) => {
        console.error('[测试] 选择视频失败:', err)
        wx.showToast({
          title: '选择失败',
          icon: 'none'
        })
      }
    })
  },

  async uploadToCloud() {
    console.log('[测试] 开始上传到云存储')

    this.setData({
      isUploading: true,
      uploadProgress: 0,
      uploadStatus: '准备上传...',
      errorMessage: ''
    })

    try {
      // 生成唯一的文件名
      const timestamp = Date.now()
      const random = Math.floor(Math.random() * 10000)
      const fileName = `video_${timestamp}_${random}.mp4`
      const cloudPath = `${this.data.cloudPath}/${fileName}`

      console.log('[测试] 云存储路径:', cloudPath)
      console.log('[测试] 本地路径:', this.data.videoPath)

      this.setData({
        uploadStatus: '正在上传...'
      })

      // 上传到云存储
      const result = await new Promise((resolve, reject) => {
        const uploadTask = wx.cloud.uploadFile({
          cloudPath: cloudPath,
          filePath: this.data.videoPath,
          success: (res) => {
            console.log('[测试] 上传成功:', res)
            resolve(res)
          },
          fail: (err) => {
            console.error('[测试] 上传失败:', err)
            reject(err)
          }
        })

        // 监听上传进度
        uploadTask.onProgressUpdate((res) => {
          console.log('[测试] 上传进度:', res.progress)
          this.setData({
            uploadProgress: res.progress,
            uploadStatus: `正在上传... ${res.progress}%`
          })
        })
      })

      // 获取文件下载链接
      this.setData({
        uploadStatus: '获取文件链接...'
      })

      const fileList = await wx.cloud.getTempFileURL({
        fileList: [result.fileID]
      })

      console.log('[测试] 文件链接:', fileList)

      this.setData({
        isUploading: false,
        uploadProgress: 100,
        uploadStatus: '上传完成！',
        uploadSuccess: true,
        fileID: result.fileID,
        cloudURL: result.fileID,
        httpURL: fileList.fileList[0].tempFileURL
      })

      wx.showToast({
        title: '上传成功！',
        icon: 'success'
      })

    } catch (error) {
      console.error('[测试] 上传出错:', error)

      this.setData({
        isUploading: false,
        errorMessage: error.errMsg || '上传失败，请重试'
      })

      wx.showToast({
        title: '上传失败',
        icon: 'none'
      })
    }
  },

  copyURL(e) {
    const url = e.currentTarget.dataset.url
    console.log('[测试] 复制URL:', url)

    wx.setClipboardData({
      data: url,
      success: () => {
        wx.showToast({
          title: '已复制到剪贴板',
          icon: 'success'
        })
      }
    })
  },

  reset() {
    console.log('[测试] 重置测试')
    this.setData({
      selectedVideo: false,
      videoPath: '',
      videoName: '',
      videoSize: '',
      isUploading: false,
      uploadProgress: 0,
      uploadStatus: '',
      uploadSuccess: false,
      fileID: '',
      cloudURL: '',
      httpURL: '',
      errorMessage: ''
    })
  }
})
