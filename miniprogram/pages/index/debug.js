Page({
  data: {
    testResults: []
  },

  testConnection() {
    const apiBaseUrl = 'http://localhost:5000'
    this.setData({ testResults: [] })

    // 测试1: 健康检查
    this.addTestResult('测试1: 健康检查', '进行中...')

    wx.request({
      url: `${apiBaseUrl}/api/health`,
      method: 'GET',
      success: (res) => {
        console.log('健康检查成功:', res)
        this.addTestResult('测试1: 健康检查', `✅ 成功 (状态码: ${res.statusCode})`)
      },
      fail: (err) => {
        console.error('健康检查失败:', err)
        this.addTestResult('测试1: 健康检查', `❌ 失败: ${JSON.stringify(err)}`)
      }
    })

    // 测试2: 生成视频（模拟）
    this.addTestResult('测试2: 视频生成请求', '进行中...')

    wx.request({
      url: `${apiBaseUrl}/api/generate-video`,
      method: 'POST',
      data: {
        prompt: '测试：一只可爱的小猫',
        seconds: '8'
      },
      header: {
        'content-type': 'application/json'
      },
      success: (res) => {
        console.log('视频生成请求成功:', res)
        const msg = res.statusCode === 200 ?
          `✅ 成功\n状态码: ${res.statusCode}\n响应: ${JSON.stringify(res.data)}` :
          `⚠️ 状态码: ${res.statusCode}\n响应: ${JSON.stringify(res.data)}`
        this.addTestResult('测试2: 视频生成请求', msg)
      },
      fail: (err) => {
        console.error('视频生成请求失败:', err)
        this.addTestResult('测试2: 视频生成请求', `❌ 失败: ${JSON.stringify(err)}`)
      }
    })
  },

  addTestResult(title, result) {
    const currentResults = [...this.data.testResults, { title, result }]
    this.setData({ testResults: currentResults })
  }
})
