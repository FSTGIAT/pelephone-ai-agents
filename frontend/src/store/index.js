import { createStore } from 'vuex'
import axios from 'axios'

// Import modules
import auth from './modules/auth'
import session from './modules/session'
import billing from './modules/billing'
import international from './modules/international'

// API base URL
const apiUrl = process.env.VUE_APP_API_URL || '/api'

// Create axios instance
const api = axios.create({
  baseURL: apiUrl,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add request interceptor for auth token
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// Add response interceptor for error handling
api.interceptors.response.use(
  response => response,
  error => {
    // Handle 401 Unauthorized errors
    if (error.response && error.response.status === 401) {
      store.dispatch('logout')
    }
    return Promise.reject(error)
  }
)

// Create store
const store = createStore({
  state: {
    isLoading: false,
    error: null,
    language: localStorage.getItem('language') || 'en'
  },
  mutations: {
    SET_LOADING(state, isLoading) {
      state.isLoading = isLoading
    },
    SET_ERROR(state, error) {
      state.error = error
    },
    CLEAR_ERROR(state) {
      state.error = null
    },
    SET_LANGUAGE(state, language) {
      state.language = language
      localStorage.setItem('language', language)
    }
  },
  actions: {
    setLoading({ commit }, isLoading) {
      commit('SET_LOADING', isLoading)
    },
    setError({ commit }, error) {
      commit('SET_ERROR', error)
    },
    clearError({ commit }) {
      commit('CLEAR_ERROR')
    },
    setLanguage({ commit }, language) {
      commit('SET_LANGUAGE', language)
    }
  },
  getters: {
    isLoading: state => state.isLoading,
    error: state => state.error,
    language: state => state.language
  },
  modules: {
    auth,
    session,
    billing,
    international
  }
})

// Make API available to modules
export const $api = api

export default store