/**
 * 微信云存储工具
 * 用于上传和删除文件
 * 注意：不重复初始化云开发，使用 app.js 中已初始化的云环境
 */

class CloudStorage {
  /**
   * 检查云开发是否可用
   */
  check() {
    if (!wx.cloud) {
      console.error('[云存储] 当前环境不支持云开发')
      return false
    }
    return true
  }

  /**
   * 上传本地文件到云存储
   * @param {string} filePath - 本地文件路径（临时路径）
   * @param {string} cloudPath - 云存储路径，例如：videos/20240128_001.mp4
   * @returns {Promise} 返回 {fileID, tempFileURL}
   */
  async uploadFile(filePath, cloudPath) {
    console.log('[云存储] 开始上传')
    console.log('[云存储] 本地路径:', filePath)
    console.log('[云存储] 云路径:', cloudPath)

    if (!this.check()) {
      throw new Error('云存储不可用')
    }

    return new Promise((resolve, reject) => {
      wx.cloud.uploadFile({
        cloudPath: cloudPath,
        filePath: filePath,
        success: (res) => {
          console.log('[云存储] 上传成功')
          console.log('[云存储] fileID:', res.fileID)
          console.log('[云存储] statusCode:', res.statusCode)

          // 获取临时下载链接
          wx.cloud.getTempFileURL({
            fileList: [res.fileID],
            success: (urlRes) => {
              console.log('[云存储] 下载URL:', urlRes.fileList[0].tempFileURL)
              resolve({
                fileID: res.fileID,
                tempFileURL: urlRes.fileList[0].tempFileURL,
                statusCode: res.statusCode
              })
            },
            fail: (err) => {
              console.error('[云存储] 获取URL失败:', err)
              // 即使获取URL失败，也返回fileID
              resolve({
                fileID: res.fileID,
                statusCode: res.statusCode
              })
            }
          })
        },
        fail: (err) => {
          console.error('[云存储] 上传失败:', err)
          reject(new Error(err.errMsg || '上传失败'))
        }
      })
    })
  }

  /**
   * 下载URL文件到本地临时路径
   * @param {string} url - 文件URL
   * @returns {Promise} 返回临时文件路径
   */
  async downloadFile(url) {
    console.log('[云存储] 开始下载:', url)

    return new Promise((resolve, reject) => {
      wx.downloadFile({
        url: url,
        success: (res) => {
          console.log('[云存储] 下载成功:', res.tempFilePath)
          resolve(res.tempFilePath)
        },
        fail: (err) => {
          console.error('[云存储] 下载失败:', err)
          reject(new Error(err.errMsg || '下载失败'))
        }
      })
    })
  }

  /**
   * 删除云存储文件
   * @param {string} fileID - 云文件ID
   * @returns {Promise}
   */
  async deleteFile(fileID) {
    console.log('[云存储] 删除文件:', fileID)

    return new Promise((resolve, reject) => {
      wx.cloud.deleteFile({
        fileList: [fileID],
        success: (res) => {
          console.log('[云存储] 删除成功:', res.fileList)
          resolve(res.fileList)
        },
        fail: (err) => {
          console.error('[云存储] 删除失败:', err)
          reject(new Error(err.errMsg || '删除失败'))
        }
      })
    })
  }

  /**
   * 获取文件下载链接
   * @param {string} fileID - 云文件ID
   * @returns {Promise} 返回下载URL
   */
  async getTempFileURL(fileID) {
    console.log('[云存储] 获取下载URL:', fileID)

    return new Promise((resolve, reject) => {
      wx.cloud.getTempFileURL({
        fileList: [fileID],
        success: (res) => {
          const url = res.fileList[0].tempFileURL
          console.log('[云存储] 获取URL成功:', url)
          resolve(url)
        },
        fail: (err) => {
          console.error('[云存储] 获取URL失败:', err)
          reject(new Error(err.errMsg || '获取URL失败'))
        }
      })
    })
  }
}

// 导出单例
const cloudStorage = new CloudStorage()

export default cloudStorage
