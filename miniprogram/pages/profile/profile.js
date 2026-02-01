// pages/profile/profile.js
Page({
  data: {
    userInfo: null
  },

  onLoad() {
    console.log('[我的] 页面加载')
    this.checkLogin()
  },

  onShow() {
    console.log('[我的] 页面显示')
    this.checkLogin()
  },

  checkLogin() {
    // 检查是否已登录
    const userInfo = wx.getStorageSync('userInfo')
    if (userInfo) {
      this.setData({ userInfo })
      console.log('[我的] 已登录:', userInfo)
    }
  },

  onGetUserInfo(e) {
    console.log('[我的] 获取用户信息:', e)

    if (e.detail.userInfo) {
      const userInfo = e.detail.userInfo
      this.setData({ userInfo })

      // 保存到本地存储
      wx.setStorageSync('userInfo', userInfo)

      // 保存到云数据库（可选）
      this.saveUserInfo(userInfo)

      wx.showToast({
        title: '登录成功',
        icon: 'success'
      })
    } else {
      wx.showToast({
        title: '登录失败',
        icon: 'none'
      })
    }
  },

  async saveUserInfo(userInfo) {
    try {
      // TODO: 保存用户信息到云数据库
      // const db = wx.cloud.database()
      // await db.collection('users').add({
      //   data: {
      //     nickName: userInfo.nickName,
      //     avatarUrl: userInfo.avatarUrl,
      //     createTime: new Date()
      //   }
      // })
      console.log('[我的] 用户信息保存成功')
    } catch (error) {
      console.error('[我的] 保存用户信息失败:', error)
    }
  },

  goToDocs() {
    wx.navigateTo({
      url: '/pages/docs/docs'
    })
  },

  goToAbout() {
    wx.navigateTo({
      url: '/pages/about/about'
    })
  },

  clearCache() {
    wx.showModal({
      title: '清除缓存',
      content: '确定要清除所有缓存吗？',
      success: (res) => {
        if (res.confirm) {
          wx.clearStorageSync({
            success: () => {
              this.setData({ userInfo: null })
              wx.showToast({
                title: '缓存已清除',
                icon: 'success'
              })
            }
          })
        }
      }
    })
  }
})
