// pages/about/about.js
Page({
  data: {},

  onLoad() {
    console.log('[关于] 页面加载')
  },

  copyEmail() {
    wx.setClipboardData({
      data: 'support@sora-video.com',
      success: () => {
        wx.showToast({
          title: '已复制邮箱',
          icon: 'success'
        })
      }
    })
  }
})
