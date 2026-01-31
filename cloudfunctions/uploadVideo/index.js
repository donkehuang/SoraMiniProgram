// 云函数：上传视频到云存储
const cloud = require('wx-server-sdk')

cloud.init({
  env: cloud.DYNAMIC_CURRENT_ENV
})

exports.main = async (event, context) => {
  const { fileData, cloudPath } = event

  console.log('[上传] 收到上传请求')
  console.log('[上传] cloudPath:', cloudPath)
  console.log('[上传] fileData 长度:', fileData.length)

  try {
    // 上传文件到云存储
    const result = await cloud.uploadFile({
      cloudPath: cloudPath,  // 云存储路径
      fileContent: fileData  // 文件内容（Base64或Buffer）
    })

    console.log('[成功] 上传成功:', result)
    console.log('[成功] fileID:', result.fileID)

    return {
      success: true,
      fileID: result.fileID,
      cloudPath: cloudPath
    }
  } catch (error) {
    console.error('[失败] 上传失败:', error)
    return {
      success: false,
      error: error.message || '上传失败'
    }
  }
}
