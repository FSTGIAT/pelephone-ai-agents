import { $api } from '@/store'

export default {
  state: {
    billingRequests: [],
    billingResponses: {},
    customerBillHistory: null,
    availablePlans: null
  },
  mutations: {
    ADD_BILLING_REQUEST(state, request) {
      state.billingRequests.unshift(request)
    },
    SET_BILLING_RESPONSE(state, { requestId, response }) {
      state.billingResponses = {
        ...state.billingResponses,
        [requestId]: response
      }
    },
    SET_CUSTOMER_BILL_HISTORY(state, history) {
      state.customerBillHistory = history
    },
    SET_AVAILABLE_PLANS(state, plans) {
      state.availablePlans = plans
    },
    CLEAR_BILLING_DATA(state) {
      state.customerBillHistory = null
    }
  },
  actions: {
    async submitBillingRequest({ commit, dispatch, rootState }, { requestType, details }) {
      if (!rootState.session.activeSession) {
        throw new Error('No active session')
      }
      
      const sessionId = rootState.session.activeSession.session_id
      const customerId = rootState.session.currentCustomer.id
      
      dispatch('setLoading', true, { root: true })
      try {
        const response = await $api.post('/billing/requests', {
          customer_id: customerId,
          request_type: requestType,
          details
        }, {
          params: { session_id: sessionId }
        })
        
        // Add request to store
        commit('ADD_BILLING_REQUEST', {
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
          message: 'Failed to submit billing request',
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
            commit('SET_BILLING_RESPONSE', {
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
    
    async getCustomerBillHistory({ commit, dispatch, rootState }) {
      if (!rootState.session.currentCustomer) {
        throw new Error('No customer selected')
      }
      
      const customerId = rootState.session.currentCustomer.id
      
      dispatch('setLoading', true, { root: true })
      try {
        const response = await $api.get(`/customers/${customerId}/bills`)
        commit('SET_CUSTOMER_BILL_HISTORY', response.data)
        return response.data
      } catch (error) {
        dispatch('setError', {
          message: 'Failed to get billing history',
          details: error.response?.data?.detail || error.message
        }, { root: true })
        throw error
      } finally {
        dispatch('setLoading', false, { root: true })
      }
    },
    
    async getAvailablePlans({ commit, dispatch }) {
      dispatch('setLoading', true, { root: true })
      try {
        const response = await $api.get('/billing/plans')
        commit('SET_AVAILABLE_PLANS', response.data)
        return response.data
      } catch (error) {
        dispatch('setError', {
          message: 'Failed to get available plans',
          details: error.response?.data?.detail || error.message
        }, { root: true })
        throw error
      } finally {
        dispatch('setLoading', false, { root: true })
      }
    },
    
    clearBillingData({ commit }) {
      commit('CLEAR_BILLING_DATA')
    }
  },
  getters: {
    billingRequests: state => state.billingRequests,
    billingResponses: state => state.billingResponses,
    customerBillHistory: state => state.customerBillHistory,
    availablePlans: state => state.availablePlans,
    
    // Get a specific response by request ID
    getResponseByRequestId: state => requestId => state.billingResponses[requestId] || null
  }
}