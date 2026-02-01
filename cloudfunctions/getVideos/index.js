// 云函数：获取视频列表及其可访问的临时链接
// cloudfunctions/getVideos/index.js

const cloud = require('wx-server-sdk')

cloud.init({
  env: cloud.DYNAMIC_CURRENT_ENV
})

const db = cloud.database()

exports.main = async (event, context) => {
  try {
    const wxContext = cloud.getWXContext()
    
    // 从数据库查询视频列表
    const result = await db.collection('videos')
      .orderBy('createTime', 'desc')
      .limit(50)
      .get()
    
    // 为每个视频生成新的临时访问链接
    const videoList = result.data
    const fileIDs = videoList.map(video => video.fileID)
    
    if (fileIDs.length === 0) {
      return {
        success: true,
        data: []
      }
    }
    
    // 批量获取临时链接
    const tempURLResult = await cloud.getTempFileURL({
      fileList: fileIDs
    })
    
    // 将临时链接附加到视频数据上
    const videosWithURL = videoList.map((video, index) => {
      return {
        ...video,
        tempFileURL: tempURLResult.fileList[index].tempFileURL,
        // 保留原始的 httpURL 字段用于显示
        originalURL: video.httpURL
      }
    })
    
    return {
      success: true,
      data: videosWithURL,
      count: videosWithURL.length
    }
    
  } catch (error) {
    console.error('获取视频列表失败:', error)
    return {
      success: false,
      error: error.message
    }
  }
}
