import { createStore } from 'vuex'

export default createStore({
  state: {
    user: null,
    isAuthenticated: false
  },
  getters: {
    getUser: state => state.user,
    isAuthenticated: state => state.isAuthenticated
  },
  mutations: {
    setUser(state, user) {
      state.user = user
      state.isAuthenticated = !!user
    },
    logout(state) {
      state.user = null
      state.isAuthenticated = false
    }
  },
  actions: {
    login({ commit }, user) {
      commit('setUser', user)
    },
    logout({ commit }) {
      commit('logout')
    }
  }
}) 