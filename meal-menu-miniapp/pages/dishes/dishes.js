const api = require('../../utils/api')

Page({
  data: {
    dishes: [],
    showAddDialog: false,
    newDishName: '',
    newDishCategory: 'dish'
  },

  onShow() {
    this.loadDishes()
  },

  loadDishes() {
    api.getDishes()
      .then(dishes => {
        this.setData({ dishes })
      })
      .catch(err => {
        wx.showToast({
          title: err,
          icon: 'none'
        })
      })
  },

  showAddForm() {
    this.setData({ 
      showAddDialog: true,
      newDishName: '',
      newDishCategory: 'dish'
    })
  },

  hideAddForm() {
    this.setData({ showAddDialog: false })
  },

  onNameInput(e) {
    this.setData({ newDishName: e.detail.value })
  },

  onCategoryChange(e) {
    this.setData({ newDishCategory: e.detail.value })
  },

  submitNewDish() {
    if (!this.data.newDishName.trim()) {
      wx.showToast({
        title: '请输入菜品名称',
        icon: 'none'
      })
      return
    }

    api.addDish(this.data.newDishName.trim(), this.data.newDishCategory)
      .then(() => {
        wx.showToast({
          title: '添加成功',
          icon: 'success'
        })
        this.hideAddForm()
        this.loadDishes()
      })
      .catch(err => {
        wx.showToast({
          title: err,
          icon: 'none'
        })
      })
  }
})
