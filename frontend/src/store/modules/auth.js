import { $api } from '@/store'

export default {
  state: {
    token: localStorage.getItem('token') || null,
    user: JSON.parse(localStorage.getItem('user')) || null
  },
  mutations: {
    SET_AUTH(state, { token, user }) {
      state.token = token
      state.user = user
      localStorage.setItem('token', token)
      localStorage.setItem('user', JSON.stringify(user))
    },
    CLEAR_AUTH(state) {
      state.token = null
      state.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  },
  actions: {
    async login({ commit, dispatch }, credentials) {
      dispatch('setLoading', true, { root: true })
      try {
        // Format credentials for token endpoint
        const formData = new FormData()
        formData.append('username', credentials.username)
        formData.append('password', credentials.password)
        
        // Get token
        const response = await $api.post('/token', formData)
        const token = response.data.access_token
        
        // Get user info
        const userResponse = await $api.get('/users/me', {
          headers: { Authorization: `Bearer ${token}` }
        })
        
        // Set auth data
        commit('SET_AUTH', {
          token,
          user: userResponse.data
        })
        
        return response.data
      } catch (error) {
        dispatch('setError', {
          message: 'Login failed',
          details: error.response?.data?.detail || error.message
        }, { root: true })
        throw error
      } finally {
        dispatch('setLoading', false, { root: true })
      }
    },
    
    logout({ commit }) {
      commit('CLEAR_AUTH')
    },
    
    checkAuth({ state, commit }) {
      if (!state.token) {
        commit('CLEAR_AUTH')
        return false
      }
      
      // Token validation could be implemented here
      // For now, we'll just check if the token exists
      
      return true
    }
  },
  getters: {
    isAuthenticated: state => !!state.token,
    currentUser: state => state.user,
    userRole: state => state.user?.role || 'agent',
    token: state => state.token
  }
}