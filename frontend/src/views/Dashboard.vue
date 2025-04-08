<template>
  <div class="dashboard-container">
    <h1 class="page-title">{{ $t('dashboard.title') }}</h1>
    
    <el-row :gutter="20">
      <el-col :sm="24" :md="12" :lg="8">
        <el-card class="welcome-card">
          <template #header>
            <div class="welcome-header">
              <i class="el-icon-user"></i>
              <span>{{ $t('dashboard.welcome', { name: currentUser.full_name }) }}</span>
            </div>
          </template>
          
          <div class="session-status">
            <h3>{{ $t('dashboard.activeSession') }}</h3>
            
            <div v-if="hasActiveSession" class="active-session">
              <el-descriptions :column="1" border>
                <el-descriptions-item :label="$t('customer.id')">
                  {{ currentCustomer.id }}
                </el-descriptions-item>
                <el-descriptions-item :label="$t('customer.name')">
                  {{ currentCustomer.name }}
                </el-descriptions-item>
                <el-descriptions-item :label="$t('session.startTime')">
                  {{ formatDateTime(activeSession.start_time) }}
                </el-descriptions-item>
                <el-descriptions-item :label="$t('session.status')">
                  <el-tag type="success">{{ $t('session.active') }}</el-tag>
                </el-descriptions-item>
              </el-descriptions>
              
              <div class="session-actions">
                <el-button type="primary" @click="viewCustomer">
                  {{ $t('customer.profile') }}
                </el-button>
                <el-button type="danger" @click="endSession">
                  {{ $t('session.end') }}
                </el-button>
              </div>
            </div>
            
            <div v-else class="no-session">
              <p>{{ $t('dashboard.noActiveSession') }}</p>
              <el-button type="primary" @click="showCreateSessionDialog">
                {{ $t('dashboard.startSession') }}
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :sm="24" :md="12" :lg="8">
        <el-card class="quick-actions-card">
          <template #header>
            <div class="card-header">
              <i class="el-icon-menu"></i>
              <span>{{ $t('dashboard.quickActions') }}</span>
            </div>
          </template>
          
          <div class="quick-actions">
            <el-button v-if="hasActiveSession" @click="navigateTo('BillingAgent')" icon="el-icon-money">
              {{ $t('nav.billing') }}
            </el-button>
            <el-button v-if="hasActiveSession" @click="navigateTo('InternationalAgent')" icon="el-icon-phone">
              {{ $t('nav.international') }}
            </el-button>
            <el-button v-if="userRole === 'supervisor'" @click="navigateTo('SupervisorAgent')" icon="el-icon-s-tools">
              {{ $t('nav.supervisor') }}
            </el-button>
            <el-button @click="showCustomerSearch" icon="el-icon-search">
              {{ $t('customer.search') }}
            </el-button>
          </div>
        </el-card>
        
        <el-card class="recent-sessions-card" v-if="sessionHistory.length > 0">
          <template #header>
            <div class="card-header">
              <i class="el-icon-time"></i>
              <span>{{ $t('dashboard.recentSessions') }}</span>
            </div>
          </template>
          
          <el-table :data="sessionHistory" stripe style="width: 100%">
            <el-table-column prop="session_id" :label="$t('session.id')" width="80">
              <template #default="scope">
                {{ scope.row.session_id.substring(0, 8) }}...
              </template>
            </el-table-column>
            <el-table-column prop="customer_id" :label="$t('customer.id')" width="100" />
            <el-table-column :label="$t('session.startTime')" width="180">
              <template #default="scope">
                {{ formatDateTime(scope.row.start_time) }}
              </template>
            </el-table-column>
            <el-table-column :label="$t('common.actions')" width="100">
              <template #default="scope">
                <el-button size="small" @click="resumeSession(scope.row)">
                  {{ $t('common.open') }}
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      
      <el-col :sm="24" :lg="8">
        <el-card class="metrics-card">
          <template #header>
            <div class="card-header">
              <i class="el-icon-data-analysis"></i>
              <span>{{ $t('dashboard.metrics') }}</span>
            </div>
          </template>
          
          <div class="metrics">
            <!-- This would be filled with actual metrics in a real implementation -->
            <el-row :gutter="20">
              <el-col :span="12">
                <div class="metric-item">
                  <h3>{{ $t('dashboard.resolvedToday') }}</h3>
                  <div class="metric-value">12</div>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="metric-item">
                  <h3>{{ $t('dashboard.pendingRequests') }}</h3>
                  <div class="metric-value">5</div>
                </div>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <div class="metric-item">
                  <h3>{{ $t('dashboard.avgResolutionTime') }}</h3>
                  <div class="metric-value">4.2m</div>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="metric-item">
                  <h3>{{ $t('dashboard.satisfaction') }}</h3>
                  <div class="metric-value">92%</div>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- Create Session Dialog -->
    <el-dialog
      v-model="createSessionDialogVisible"
      :title="$t('session.create')"
      width="400px"
    >
      <el-form :model="sessionForm" label-width="120px">
        <el-form-item :label="$t('customer.id')">
          <el-input v-model="sessionForm.customerId" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="createSessionDialogVisible = false">
            {{ $t('common.cancel') }}
          </el-button>
          <el-button type="primary" @click="createSession" :loading="isLoading">
            {{ $t('session.start') }}
          </el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- Customer Search Dialog -->
    <el-dialog
      v-model="customerSearchDialogVisible"
      :title="$t('customer.search')"
      width="600px"
    >
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item>
          <el-input
            v-model="searchForm.query"
            :placeholder="$t('common.search')"
            @keyup.enter="searchCustomers"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="searchCustomers" :loading="isLoading">
            {{ $t('common.search') }}
          </el-button>
        </el-form-item>
      </el-form>
      
      <el-table
        v-if="customerSearchResults.length > 0"
        :data="customerSearchResults"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="id" :label="$t('customer.id')" width="100" />
        <el-table-column prop="name" :label="$t('customer.name')" />
        <el-table-column prop="plan" :label="$t('customer.plan')" />
        <el-table-column :label="$t('common.actions')" width="200">
          <template #default="scope">
            <el-button
              size="small"
              @click="startSessionWithCustomer(scope.row.id)"
              :loading="isLoading"
            >
              {{ $t('session.start') }}
            </el-button>
            <el-button
              size="small"
              type="primary"
              @click="viewCustomerDetail(scope.row.id)"
            >
              {{ $t('common.details') }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div v-else-if="searchAttempted" class="no-results">
        {{ $t('dashboard.noCustomersFound') }}
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'DashboardView',
  
  setup() {
    const store = useStore()
    const router = useRouter()
    const { t } = useI18n()
    
    // States
    const createSessionDialogVisible = ref(false)
    const customerSearchDialogVisible = ref(false)
    const sessionForm = ref({ customerId: '' })
    const searchForm = ref({ query: '' })
    const customerSearchResults = ref([])
    const searchAttempted = ref(false)
    
    // Computed properties
    const currentUser = computed(() => store.getters.currentUser || {})
    const isLoading = computed(() => store.getters.isLoading)
    const hasActiveSession = computed(() => store.getters.hasActiveSession)
    const activeSession = computed(() => store.getters.activeSession || {})
    const currentCustomer = computed(() => store.getters.currentCustomer || {})
    const sessionHistory = computed(() => store.getters.sessionHistory || [])
    const userRole = computed(() => store.getters.userRole)
    
    // Methods
    const formatDateTime = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return new Intl.DateTimeFormat('default', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }).format(date)
    }
    
    const showCreateSessionDialog = () => {
      sessionForm.value.customerId = ''
      createSessionDialogVisible.value = true
    }
    
    const createSession = async () => {
      if (!sessionForm.value.customerId) {
        ElMessage.warning(t('session.customerIdRequired'))
        return
      }
      
      try {
        await store.dispatch('createSession', sessionForm.value.customerId)
        createSessionDialogVisible.value = false
        ElMessage.success(t('session.created'))
      } catch (error) {
        console.error('Error creating session:', error)
        ElMessage.error(t('errors.session'))
      }
    }
    
    const endSession = async () => {
      try {
        await ElMessageBox.confirm(
          t('session.confirmEnd'),
          t('common.warning'),
          {
            confirmButtonText: t('common.yes'),
            cancelButtonText: t('common.no'),
            type: 'warning'
          }
        )
        
        await store.dispatch('endSession')
        ElMessage.success(t('session.ended'))
      } catch (error) {
        if (error !== 'cancel') {
          console.error('Error ending session:', error)
          ElMessage.error(t('errors.session'))
        }
      }
    }
    
    const viewCustomer = () => {
      router.push({
        name: 'CustomerProfile',
        params: { id: currentCustomer.value.id }
      })
    }
    
    const navigateTo = (routeName) => {
      router.push({ name: routeName })
    }
    
    const showCustomerSearch = () => {
      searchForm.value.query = ''
      customerSearchResults.value = []
      searchAttempted.value = false
      customerSearchDialogVisible.value = true
    }
    
    const searchCustomers = async () => {
      if (!searchForm.value.query) {
        ElMessage.warning(t('customer.searchRequired'))
        return
      }
      
      try {
        // In a real implementation, this would call the API
        searchAttempted.value = true
        
        // Mock data for demonstration
        customerSearchResults.value = [
          { id: '1001', name: 'John Doe', plan: 'Premium 100GB' },
          { id: '1002', name: 'Jane Smith', plan: 'Standard 20GB' },
          { id: '1003', name: 'Robert Johnson', plan: 'Unlimited Data' }
        ].filter(customer => 
          customer.name.toLowerCase().includes(searchForm.value.query.toLowerCase()) ||
          customer.id.includes(searchForm.value.query)
        )
      } catch (error) {
        console.error('Error searching customers:', error)
        ElMessage.error(t('errors.api'))
      }
    }
    
    const startSessionWithCustomer = async (customerId) => {
      try {
        await store.dispatch('createSession', customerId)
        customerSearchDialogVisible.value = false
        ElMessage.success(t('session.created'))
      } catch (error) {
        console.error('Error creating session:', error)
        ElMessage.error(t('errors.session'))
      }
    }
    
    const viewCustomerDetail = (customerId) => {
      router.push({
        name: 'CustomerProfile',
        params: { id: customerId }
      })
      customerSearchDialogVisible.value = false
    }
    
    const resumeSession = async (session) => {
      try {
        await store.dispatch('getSession', session.session_id)
        ElMessage.success(t('session.resumed'))
      } catch (error) {
        console.error('Error resuming session:', error)
        ElMessage.error(t('errors.session'))
      }
    }
    
    // Lifecycle hooks
    onMounted(() => {
      // Check for any existing sessions
      if (!hasActiveSession.value) {
        // This would normally fetch recent sessions from API
      }
    })
    
    return {
      // States
      createSessionDialogVisible,
      customerSearchDialogVisible,
      sessionForm,
      searchForm,
      customerSearchResults,
      searchAttempted,
      
      // Computed
      currentUser,
      isLoading,
      hasActiveSession,
      activeSession,
      currentCustomer,
      sessionHistory,
      userRole,
      
      // Methods
      formatDateTime,
      showCreateSessionDialog,
      createSession,
      endSession,
      viewCustomer,
      navigateTo,
      showCustomerSearch,
      searchCustomers,
      startSessionWithCustomer,
      viewCustomerDetail,
      resumeSession
    }
  }
}
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
}

.page-title {
  margin-bottom: 20px;
  font-weight: 500;
}

.welcome-card,
.quick-actions-card,
.metrics-card,
.recent-sessions-card {
  margin-bottom: 20px;
}

.welcome-header,
.card-header {
  display: flex;
  align-items: center;
}

.welcome-header i,
.card-header i {
  margin-right: 8px;
}

.session-status {
  margin-top: 10px;
}

.active-session {
  margin-top: 15px;
}

.session-actions {
  margin-top: 15px;
  display: flex;
  justify-content: space-between;
}

.no-session {
  text-align: center;
  padding: 20px 0;
}

.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.metrics {
  padding: 10px 0;
}

.metric-item {
  background-color: #f5f7fa;
  border-radius: 4px;
  padding: 10px;
  margin-bottom: 10px;
  text-align: center;
}

.metric-value {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
  margin-top: 5px;
}

.search-form {
  margin-bottom: 15px;
}

.no-results {
  text-align: center;
  padding: 20px;
  color: #909399;
}

/* RTL support */
:deep([dir="rtl"]) .welcome-header i,
:deep([dir="rtl"]) .card-header i {
  margin-right: 0;
  margin-left: 8px;
}
</style>