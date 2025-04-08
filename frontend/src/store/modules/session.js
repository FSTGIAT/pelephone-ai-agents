import { $api } from '@/store'

export default {
  state: {
    activeSession: null,
    sessionHistory: [],
    currentCustomer: null
  },
  mutations: {
    SET_ACTIVE_SESSION(state, session) {
      state.activeSession = session
    },
    ADD_TO_SESSION_HISTORY(state, session) {
      // Add to beginning of array
      state.sessionHistory.unshift(session)
      // Keep only the most recent 10 sessions
      state.sessionHistory = state.sessionHistory.slice(0, 10)
    },
    SET_CURRENT_CUSTOMER(state, customer) {
      state.currentCustomer = customer
    },
    CLEAR_SESSION(state) {
      // If there's an active session, add it to history before clearing
      if (state.activeSession) {
        state.sessionHistory.unshift({
          ...state.activeSession,
          endTime: new Date().toISOString()
        })
        state.sessionHistory = state.sessionHistory.slice(0, 10)
      }
      
      state.activeSession = null
      state.currentCustomer = null
    }
  },
  actions: {
    async createSession({ commit, dispatch }, customerId) {
      dispatch('setLoading', true, { root: true })
      try {
        const response = await $api.post('/sessions', { customer_id: customerId })
        
        // Fetch customer details
        const customerResponse = await $api.get(`/customers/${customerId}`)
        
        commit('SET_CURRENT_CUSTOMER', customerResponse.data)
        commit('SET_ACTIVE_SESSION', response.data)
        
        return response.data
      } catch (error) {
        dispatch('setError', {
          message: 'Failed to create session',
          details: error.response?.data?.detail || error.message
        }, { root: true })
        throw error
      } finally {
        dispatch('setLoading', false, { root: true })
      }
    },
    
    async getSession({ commit, dispatch }, sessionId) {
      dispatch('setLoading', true, { root: true })
      try {
        const response = await $api.get(`/sessions/${sessionId}`)
        
        // Fetch customer details if not already loaded
        const customerId = response.data.customer_id
        const customerResponse = await $api.get(`/customers/${customerId}`)
        
        commit('SET_CURRENT_CUSTOMER', customerResponse.data)
        commit('SET_ACTIVE_SESSION', response.data)
        
        return response.data
      } catch (error) {
        dispatch('setError', {
          message: 'Failed to get session',
          details: error.response?.data?.detail || error.message
        }, { root: true })
        throw error
      } finally {
        dispatch('setLoading', false, { root: true })
      }
    },
    
    async endSession({ commit, state, dispatch }) {
      if (!state.activeSession) return
      
      dispatch('setLoading', true, { root: true })
      try {
        const sessionId = state.activeSession.session_id
        await $api.put(`/sessions/${sessionId}/end`)
        
        commit('ADD_TO_SESSION_HISTORY', {
          ...state.activeSession,
          endTime: new Date().toISOString()
        })
        commit('SET_ACTIVE_SESSION', null)
        commit('SET_CURRENT_CUSTOMER', null)
      } catch (error) {
        dispatch('setError', {
          message: 'Failed to end session',
          details: error.response?.data?.detail || error.message
        }, { root: true })
        throw error
      } finally {
        dispatch('setLoading', false, { root: true })
      }
    },
    
    clearSession({ commit }) {
      commit('CLEAR_SESSION')
    }
  },
  getters: {
    activeSession: state => state.activeSession,
    sessionHistory: state => state.sessionHistory,
    currentCustomer: state => state.currentCustomer,
    hasActiveSession: state => !!state.activeSession
  }
}