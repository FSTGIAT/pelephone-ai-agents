<template>
  <div class="billing-agent-container">
    <div class="page-header">
      <h1>{{ $t('billing.title') }}</h1>
      <el-tag v-if="currentCustomer" size="large" type="success">
        {{ $t('customer.id') }}: {{ currentCustomer.id }} - {{ currentCustomer.name }}
      </el-tag>
    </div>
    
    <el-alert
      v-if="!hasActiveSession"
      type="warning"
      :closable="false"
      show-icon
    >
      {{ $t('billing.noActiveSession') }}
      <el-button size="small" type="primary" @click="navigateToDashboard">
        {{ $t('dashboard.startSession') }}
      </el-button>
    </el-alert>
    
    <div v-if="hasActiveSession" class="agent-content">
      <el-row :gutter="20">
        <el-col :md="12" :lg="16">
          <el-card class="main-card">
            <el-tabs v-model="activeTab">
              <el-tab-pane :label="$t('billing.inquiry')" name="inquiry">
                <BillingInquiry 
                  :customer="currentCustomer" 
                  @submit-request="handleBillingRequest" 
                />
              </el-tab-pane>
              
              <el-tab-pane :label="$t('billing.discrepancy')" name="discrepancy">
                <UsageDiscrepancy 
                  :customer="currentCustomer" 
                  @submit-request="handleBillingRequest" 
                />
              </el-tab-pane>
              
              <el-tab-pane :label="$t('billing.refund')" name="refund">
                <RefundRequest 
                  :customer="currentCustomer" 
                  @submit-request="handleBillingRequest" 
                />
              </el-tab-pane>
              
              <el-tab-pane :label="$t('billing.planChange')" name="planChange">
                <PlanChange 
                  :customer="currentCustomer" 
                  :available-plans="availablePlans"
                  @submit-request="handleBillingRequest" 
                />
              </el-tab-pane>
              
              <el-tab-pane :label="$t('billing.history')" name="history">
                <BillingHistory 
                  :customer="currentCustomer" 
                  :billing-history="customerBillHistory" 
                  @load-history="loadBillingHistory"
                />
              </el-tab-pane>
            </el-tabs>
          </el-card>
        </el-col>
        
        <el-col :md="12" :lg="8">
          <el-card class="recent-activity-card">
            <template #header>
              <div class="card-header">
                <span>{{ $t('billing.recentActivity') }}</span>
              </div>
            </template>
            
            <div v-if="billingRequests.length === 0" class="no-activity">
              {{ $t('billing.noRecentActivity') }}
            </div>
            
            <div v-else class="activity-list">
              <el-timeline>
                <el-timeline-item
                  v-for="request in billingRequests"
                  :key="request.requestId"
                  :timestamp="formatTime(request.timestamp)"
                  :type="getRequestTypeIcon(request.type)"
                >
                  <div class="activity-item">
                    <div class="activity-header">
                      <strong>{{ $t(`billing.${request.type}`) }}</strong>
                      <el-tag
                        size="small"
                        :type="getStatusType(getResponseStatus(request.requestId))"
                      >
                        {{ getResponseStatus(request.requestId) || 'pending' }}
                      </el-tag>
                    </div>
                    <div class="activity-details">
                      {{ getRequestSummary(request) }}
                    </div>
                    <div v-if="getResponseByRequestId(request.requestId)" class="activity-response">
                      <strong>{{ $t('billing.response') }}:</strong>
                      {{ getResponseSummary(getResponseByRequestId(request.requestId)) }}
                    </div>
                  </div>
                </el-timeline-item>
              </el-timeline>
            </div>
          </el-card>
          
          <el-card class="customer-summary-card">
            <template #header>
              <div class="card-header">
                <span>{{ $t('customer.summary') }}</span>
              </div>
            </template>
            
            <el-descriptions :column="1" border>
              <el-descriptions-item :label="$t('customer.plan')">
                {{ currentCustomer.plan }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('customer.monthlyCharge')">
                ${{ currentCustomer.monthly_charge }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('customer.contractEnd')">
                {{ formatDate(currentCustomer.contract_end_date) }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('customer.paymentStatus')">
                <el-tag
                  :type="currentCustomer.payment_status === 'current' ? 'success' : 'danger'"
                >
                  {{ currentCustomer.payment_status }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item :label="$t('billing.lastBill')">
                ${{ currentCustomer.last_bill_amount }}
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'

// Import components
import BillingInquiry from '@/components/billing/BillingInquiry.vue'
import UsageDiscrepancy from '@/components/billing/UsageDiscrepancy.vue'
import RefundRequest from '@/components/billing/RefundRequest.vue'
import PlanChange from '@/components/billing/PlanChange.vue'
import BillingHistory from '@/components/billing/BillingHistory.vue'

export default {
  name: 'BillingAgentView',
  
  components: {
    BillingInquiry,
    UsageDiscrepancy,
    RefundRequest,
    PlanChange,
    BillingHistory
  },
  
  setup() {
    const store = useStore()
    const router = useRouter()
    const { t } = useI18n()
    
    // State
    const activeTab = ref('inquiry')
    
    // Computed properties
    const hasActiveSession = computed(() => store.getters.hasActiveSession)
    const currentCustomer = computed(() => store.getters.currentCustomer || {})
    const isLoading = computed(() => store.getters.isLoading)
    const billingRequests = computed(() => store.getters.billingRequests || [])
    const customerBillHistory = computed(() => store.getters.customerBillHistory || [])
    const availablePlans = computed(() => store.getters.availablePlans || [])
    
    // Methods
    const navigateToDashboard = () => {
      router.push({ name: 'Dashboard' })
    }
    
    const formatTime = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return new Intl.DateTimeFormat('default', {
        hour: '2-digit',
        minute: '2-digit'
      }).format(date)
    }
    
    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return new Intl.DateTimeFormat('default', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      }).format(date)
    }
    
    const handleBillingRequest = async (requestType, details) => {
      try {
        await store.dispatch('submitBillingRequest', {
          requestType,
          details
        })
        ElMessage.success(t('billing.requestSubmitted'))
      } catch (error) {
        console.error('Error submitting billing request:', error)
        ElMessage.error(t('errors.api'))
      }
    }
    
    const loadBillingHistory = async () => {
      try {
        await store.dispatch('getCustomerBillHistory')
      } catch (error) {
        console.error('Error loading billing history:', error)
        ElMessage.error(t('errors.api'))
      }
    }
    
    const getResponseByRequestId = (requestId) => {
      return store.getters.getResponseByRequestId(requestId)
    }
    
    const getResponseStatus = (requestId) => {
      const response = getResponseByRequestId(requestId)
      return response ? response.status : 'pending'
    }
    
    const getStatusType = (status) => {
      switch(status) {
        case 'completed':
        case 'success':
          return 'success'
        case 'pending':
          return 'warning'
        case 'error':
          return 'danger'
        default:
          return 'info'
      }
    }
    
    const getRequestTypeIcon = (type) => {
      switch(type) {
        case 'inquiry':
          return 'info'
        case 'discrepancy':
          return 'warning'
        case 'refund':
          return 'danger'
        case 'planChange':
          return 'success'
        default:
          return 'primary'
      }
    }
    
    const getRequestSummary = (request) => {
      // Create a human-readable summary based on request type and details
      switch(request.type) {
        case 'inquiry':
          return t(`billing.inquiryTypes.${request.details.inquiryType || 'general'}`)
        case 'discrepancy':
          return `${t('billing.reportedAmount')}: $${request.details.reportedAmount}, ${t('billing.billedAmount')}: $${request.details.billedAmount}`
        case 'refund':
          return `${t('billing.amount')}: $${request.details.amount} - ${t('billing.reason')}: ${t(`billing.refundTypes.${request.details.reason}`)}`
        case 'planChange':
          return `${t('billing.fromPlan')}: ${request.details.currentPlan} ${t('common.to')} ${request.details.newPlan}`
        default:
          return JSON.stringify(request.details)
      }
    }
    
    const getResponseSummary = (response) => {
      if (!response) return ''
      
      if (response.response && response.response.message) {
        return response.response.message
      }
      
      return response.status
    }
    
    // Lifecycle hooks
    onMounted(async () => {
      if (hasActiveSession.value) {
        try {
          // Load available plans and billing history
          await store.dispatch('getAvailablePlans')
        } catch (error) {
          console.error('Error loading initial billing data:', error)
        }
      }
    })
    
    return {
      activeTab,
      hasActiveSession,
      currentCustomer,
      isLoading,
      billingRequests,
      customerBillHistory,
      availablePlans,
      navigateToDashboard,
      formatTime,
      formatDate,
      handleBillingRequest,
      loadBillingHistory,
      getResponseByRequestId,
      getResponseStatus,
      getStatusType,
      getRequestTypeIcon,
      getRequestSummary,
      getResponseSummary
    }
  }
}
</script>

<style scoped>
.billing-agent-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.agent-content {
  margin-top: 20px;
}

.main-card,
.recent-activity-card,
.customer-summary-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.no-activity {
  text-align: center;
  padding: 20px 0;
  color: #909399;
}

.activity-list {
  max-height: 400px;
  overflow-y: auto;
}

.activity-item {
  margin-bottom: 10px;
}

.activity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
}

.activity-details {
  font-size: 14px;
  margin-bottom: 5px;
}

.activity-response {
  font-size: 14px;
  background-color: #f5f7fa;
  padding: 5px;
  border-radius: 4px;
  margin-top: 5px;
}

/* RTL support */
:deep([dir="rtl"]) .page-header {
  flex-direction: row-reverse;
}

:deep([dir="rtl"]) .activity-header {
  flex-direction: row-reverse;
}
</style>