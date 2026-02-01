// 上传背景视频到云存储的工具脚本
// 在微信开发者工具的 Console 中运行

/**
 * 使用说明：
 * 1. 打开微信开发者工具
 * 2. 打开调试器 -> Console
 * 3. 复制下面的代码并执行
 */

// 方法1：从本地文件上传（推荐）
function uploadBackgroundVideo() {
  console.log('[上传] 开始上传背景视频到云存储...')
  
  wx.cloud.uploadFile({
    cloudPath: 'background/background.mp4', // 云存储路径
    filePath: '/assets/background.mp4', // 本地文件路径
    success: res => {
      console.log('✅ [上传成功]')
      console.log('FileID:', res.fileID)
      console.log('')
      console.log('请将以下 FileID 复制保存：')
      console.log(res.fileID)
      console.log('')
      console.log('接下来执行：getBackgroundVideoURL()')
      
      // 自动保存到本地存储
      wx.setStorageSync('backgroundVideoFileID', res.fileID)
    },
    fail: err => {
      console.error('❌ [上传失败]', err)
    }
  })
}

// 方法2：获取临时 URL
function getBackgroundVideoURL() {
  const fileID = wx.getStorageSync('backgroundVideoFileID')
  
  if (!fileID) {
    console.error('请先运行 uploadBackgroundVideo() 上传视频')
    return
  }
  
  console.log('[获取URL] 正在获取临时访问链接...')
  
  wx.cloud.getTempFileURL({
    fileList: [fileID],
    success: res => {
      const url = res.fileList[0].tempFileURL
      console.log('✅ [获取成功]')
      console.log('')
      console.log('临时URL（有效期12小时）:')
      console.log(url)
      console.log('')
      console.log('请复制上面的 URL，粘贴到 index.js 的 backgroundVideoUrl 中')
      
      // 保存 URL
      wx.setStorageSync('backgroundVideoURL', url)
    },
    fail: err => {
      console.error('❌ [获取失败]', err)
    }
  })
}

// 方法3：获取永久下载链接（需要云函数）
function getBackgroundVideoDownloadURL() {
  const fileID = wx.getStorageSync('backgroundVideoFileID')
  
  if (!fileID) {
    console.error('请先运行 uploadBackgroundVideo() 上传视频')
    return
  }
  
  console.log('[永久链接] 正在获取永久下载链接...')
  console.log('FileID:', fileID)
  console.log('')
  console.log('请在云开发控制台中：')
  console.log('1. 找到文件：background/background.mp4')
  console.log('2. 右键 -> 获取临时链接')
  console.log('3. 或设置为公开读，获取永久链接')
}

// 导出函数到全局
window.uploadBackgroundVideo = uploadBackgroundVideo
window.getBackgroundVideoURL = getBackgroundVideoURL
window.getBackgroundVideoDownloadURL = getBackgroundVideoDownloadURL

console.log('====================================')
console.log('背景视频上传工具已加载')
console.log('====================================')
console.log('')
console.log('使用步骤：')
console.log('1. 运行：uploadBackgroundVideo()')
console.log('2. 等待上传完成')
console.log('3. 运行：getBackgroundVideoURL()')
console.log('4. 复制 URL 到 index.js')
console.log('')
console.log('====================================')
