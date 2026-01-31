// 云函数：删除云存储中的视频
const cloud = require('wx-server-sdk')

cloud.init({
  env: cloud.DYNAMIC_CURRENT_ENV
})

exports.main = async (event, context) => {
  const { fileID } = event

  console.log('[删除] 收到删除请求')
  console.log('[删除] fileID:', fileID)

  try {
    // 删除文件
    const result = await cloud.deleteFile({
      fileList: [fileID]
    })

    console.log('[成功] 删除成功:', result)

    return {
      success: true,
      fileList: result.fileList
    }
  } catch (error) {
    console.error('[失败] 删除失败:', error)
    return {
      success: false,
      error: error.message || '删除失败'
    }
  }
}
