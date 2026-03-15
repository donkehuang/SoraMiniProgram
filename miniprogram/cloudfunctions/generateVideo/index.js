const cloud = require('wx-server-sdk')

cloud.init({
  env: cloud.DYNAMIC_CURRENT_ENV
})

const OpenAI = require('openai')

exports.main = async (event, context) => {
  const { prompt, seconds } = event

  try {
    // 初始化OpenAI客户端
    const client = new OpenAI({
      apiKey: 'your_openai_api_key_here' // 替换为你的OpenAI API密钥
    })

    // 调用Sora API生成视频
    const video = await client.videos.create({
      prompt: prompt,
      model: 'sora-2',
      seconds: seconds || '12',
      size: '720x1280'
    })

    // 等待视频生成完成并获取URL
    // 注意：实际使用时需要轮询检查视频状态
    // 这里简化处理，直接返回视频ID和URL
    const videoUrl = video.url || `https://sora.com/v/${video.id}`

    return {
      success: true,
      videoUrl: videoUrl,
      videoId: video.id
    }
  } catch (error) {
    console.error('生成视频失败:', error)
    return {
      success: false,
      error: error.message || '生成视频失败'
    }
  }
}
