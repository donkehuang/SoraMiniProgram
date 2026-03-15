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
    console.log('[getVideos] 开始获取视频列表')
    
    // 从数据库查询视频列表
    const result = await db.collection('videos')
      .orderBy('createTime', 'desc')
      .limit(50)
      .get()
    
    console.log('[getVideos] 查询到视频数量:', result.data.length)
    
    // 为每个视频生成新的临时访问链接
    const videoList = result.data
    const fileIDs = videoList.map(video => video.fileID).filter(id => id) // 过滤掉空的fileID
    
    console.log('[getVideos] 有效fileID数量:', fileIDs.length)
    
    if (fileIDs.length === 0) {
      console.log('[getVideos] 没有有效的视频文件ID，返回空列表')
      return {
        success: true,
        data: []
      }
    }
    
    // 批量获取临时链接
    console.log('[getVideos] 开始获取临时链接...')
    const tempURLResult = await cloud.getTempFileURL({
      fileList: fileIDs
    })
    
    console.log('[getVideos] 获取到临时链接数量:', tempURLResult.fileList.length)
    
    // 将临时链接附加到视频数据上
    const videosWithURL = videoList.map((video, index) => {
      const fileID = video.fileID
      const tempFileURL = fileID ? (tempURLResult.fileList.find(f => f.fileID === fileID)?.tempFileURL || video.httpURL) : video.httpURL
      
      return {
        ...video,
        tempFileURL: tempFileURL,
        // 保留原始的 httpURL 字段用于显示
        originalURL: video.httpURL
      }
    })
    
    console.log('[getVideos] 返回视频数量:', videosWithURL.length)
    
    return {
      success: true,
      data: videosWithURL,
      count: videosWithURL.length
    }
    
  } catch (error) {
    console.error('[getVideos] 错误详情:', error)
    return {
      success: false,
      error: error.message,
      detail: error.errMsg || JSON.stringify(error)
    }
  }
}
