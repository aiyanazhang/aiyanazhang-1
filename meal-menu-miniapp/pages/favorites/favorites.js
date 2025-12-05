const api = require('../../utils/api')

Page({
  data: {
    favorites: []
  },

  onShow() {
    this.loadFavorites()
  },

  loadFavorites() {
    api.getFavorites()
      .then(favorites => {
        this.setData({ favorites })
      })
      .catch(err => {
        wx.showToast({
          title: err,
          icon: 'none'
        })
      })
  },

  deleteFavorite(e) {
    const id = e.currentTarget.dataset.id
    
    wx.showModal({
      title: '确认删除',
      content: '确定要删除这份收藏吗？',
      success: (res) => {
        if (res.confirm) {
          api.deleteFavorite(id)
            .then(() => {
              wx.showToast({
                title: '删除成功',
                icon: 'success'
              })
              this.loadFavorites()
            })
            .catch(err => {
              wx.showToast({
                title: err,
                icon: 'none'
              })
            })
        }
      }
    })
  }
})
