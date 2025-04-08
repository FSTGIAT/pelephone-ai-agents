import { $api } from '@/store'

export default {
  state: {
    internationalRequests: [],
    internationalResponses: {},
    customerInternationalUsage: null,
    internationalPackages: null
  },
  mutations: {
    ADD_INTERNATIONAL_REQUEST(state, request) {
      state.internationalRequests.unshift(request)
    },
    SET_INTERNATIONAL_RESPONSE(state, { requestId, response }) {
      state.internationalResponses = {
        ...state.internationalResponses,
        [requestId]: response
      }
    },
    SET_CUSTOMER_INTERNATIONAL_USAGE(state, usage) {
      state.customerInternationalUsage = usage
    },
    SET_INTERNATIONAL_PACKAGES(state, packages) {
      state.internationalPackages = packages
    },
    CLEAR_INTERNATIONAL_DATA(state) {
      state.customerInternationalUsage = null
    }
  },
  actions: {
    async submitInternationalRequest({ commit, dispatch, rootState }, { requestType, details }) {
      if (!rootState.session.activeSession) {
        throw new Error('No active session')
      }
      
      const sessionId = rootState.session.activeSession.session_id
      const customerId = rootState.session.currentCustomer.id
      
      dispatch('setLoading', true, { root: true })
      try {
        const response = await $api.post('/international/requests', {
          customer_id: customerId,
          request_type: requestType,
          details
        }, {
          params: { session_id: sessionId }
        })
        
        // Add request to store
        commit('ADD_INTERNATIONAL_REQUEST', {
          requestId: response.data.request_id,
          type: requestType,
          details,
          timestamp: new Date().toISOString(),
          status: 'pending'
        })
        
        // Start polling for response
        dispatch('pollForResponse', response.data.request_id)
        
        return response.data
      } catch (error) {
        dispatch('setError', {
          message: 'Failed to submit international request',
          details: error.response?.data?.detail || error.message
        }, { root: true })
        throw error
      } finally {
        dispatch('setLoading', false, { root: true })
      }
    },
    
    async pollForResponse({ commit, dispatch }, requestId) {
      // Poll every 2 seconds for up to 30 seconds
      let attempts = 0
      const maxAttempts = 15
      
      const checkResponse = async () => {
        attempts++
        try {
          const response = await $api.get(`/responses/${requestId}`)
          
          if (response.data.status !== 'pending') {
            // Response received
            commit('SET_INTERNATIONAL_RESPONSE', {
              requestId,
              response: response.data
            })
            return true
          }
          
          // Still pending
          if (attempts >= maxAttempts) {
            // Timeout
            dispatch('setError', {
              message: 'Request timed out',
              details: 'The system is taking longer than expected to process your request.'
            }, { root: true })
            return true
          }
          
          // Try again after delay
          setTimeout(checkResponse, 2000)
          return false
        } catch (error) {
          // Error checking response
          console.error('Error polling for response:', error)
          if (attempts >= maxAttempts) {
            dispatch('setError', {
              message: 'Failed to get response',
              details: error.response?.data?.detail || error.message
            }, { root: true })
            return true
          }
          
          // Try again after delay
          setTimeout(checkResponse, 2000)
          return false
        }
      }
      
      checkResponse()
    },
    
    async getCustomerInternationalUsage({ commit, dispatch, rootState }) {
      if (!rootState.session.currentCustomer) {
        throw new Error('No customer selected')
      }
      
      const customerId = rootState.session.currentCustomer.id
      
      dispatch('setLoading', true, { root: true })
      try {
        const response = await $api.get(`/customers/${customerId}/international-usage`)
        commit('SET_CUSTOMER_INTERNATIONAL_USAGE', response.data)
        return response.data
      } catch (error) {
        dispatch('setError', {
          message: 'Failed to get international usage',
          details: error.response?.data?.detail || error.message
        }, { root: true })
        throw error
      } finally {
        dispatch('setLoading', false, { root: true })
      }
    },
    
    async getInternationalPackages({ commit, dispatch }) {
      dispatch('setLoading', true, { root: true })
      try {
        const response = await $api.get('/international/packages')
        commit('SET_INTERNATIONAL_PACKAGES', response.data)
        return response.data
      } catch (error) {
        dispatch('setError', {
          message: 'Failed to get international packages',
          details: error.response?.data?.detail || error.message
        }, { root: true })
        throw error
      } finally {
        dispatch('setLoading', false, { root: true })
      }
    },
    
    clearInternationalData({ commit }) {
      commit('CLEAR_INTERNATIONAL_DATA')
    }
  },
  getters: {
    internationalRequests: state => state.internationalRequests,
    internationalResponses: state => state.internationalResponses,
    customerInternationalUsage: state => state.customerInternationalUsage,
    internationalPackages: state => state.internationalPackages,
    
    // Get a specific response by request ID
    getResponseByRequestId: state => requestId => state.internationalResponses[requestId] || null
  }
}