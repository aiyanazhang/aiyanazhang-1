const api = require('../../utils/api')

Page({
  data: {
    menu: null,
    loading: false
  },

  onLoad() {
    this.generateNewMenu()
  },

  generateNewMenu() {
    this.setData({ loading: true })
    
    api.generateMenu()
      .then(menu => {
        this.setData({
          menu: menu,
          loading: false
        })
      })
      .catch(err => {
        this.setData({ loading: false })
        wx.showToast({
          title: err,
          icon: 'none'
        })
      })
  },

  saveToFavorites() {
    if (!this.data.menu) {
      wx.showToast({
        title: '请先生成菜单',
        icon: 'none'
      })
      return
    }

    api.addFavorite(this.data.menu)
      .then(() => {
        wx.showToast({
          title: '收藏成功',
          icon: 'success'
        })
      })
      .catch(err => {
        wx.showToast({
          title: err,
          icon: 'none'
        })
      })
  }
})
