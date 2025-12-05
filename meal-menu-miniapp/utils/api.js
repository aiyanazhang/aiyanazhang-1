const app = getApp()

const API_BASE = app.globalData.apiBaseUrl

function request(url, method = 'GET', data = null) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${API_BASE}${url}`,
      method: method,
      data: data,
      header: {
        'content-type': 'application/json'
      },
      success(res) {
        if (res.data.success) {
          resolve(res.data.data)
        } else {
          reject(res.data.message || '请求失败')
        }
      },
      fail(err) {
        reject(err.errMsg || '网络错误')
      }
    })
  })
}

function getDishes() {
  return request('/dishes')
}

function addDish(name, category) {
  return request('/dishes', 'POST', { name, category })
}

function generateMenu() {
  return request('/generate-menu')
}

function addFavorite(menu) {
  return request('/favorites', 'POST', { menu })
}

function getFavorites() {
  return request('/favorites')
}

function deleteFavorite(id) {
  return request(`/favorites/${id}`, 'DELETE')
}

module.exports = {
  getDishes,
  addDish,
  generateMenu,
  addFavorite,
  getFavorites,
  deleteFavorite
}
