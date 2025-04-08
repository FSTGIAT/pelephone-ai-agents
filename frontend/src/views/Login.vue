<template>
  <div class="login-container">
    <el-card class="login-card">
      <div class="logo-container">
        <img src="@/assets/logo.png" alt="Pelephone Logo" class="logo" />
      </div>
      <h1>{{ $t('login.title') }}</h1>
      
      <el-form 
        ref="loginForm"
        :model="loginForm"
        :rules="loginRules"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            :placeholder="$t('login.username')"
            prefix-icon="el-icon-user"
            autocomplete="username"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            :placeholder="$t('login.password')"
            prefix-icon="el-icon-lock"
            type="password"
            autocomplete="current-password"
            show-password
          />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            native-type="submit"
            :loading="isLoading"
            class="login-button"
          >
            {{ $t('login.submit') }}
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="language-selector">
        <el-radio-group v-model="currentLanguage" size="small">
          <el-radio-button label="en">English</el-radio-button>
          <el-radio-button label="he">עברית</el-radio-button>
        </el-radio-group>
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'

export default {
  name: 'LoginView',
  
  setup() {
    const store = useStore()
    const router = useRouter()
    const { locale, t } = useI18n()
    const loginForm = ref({
      username: '',
      password: ''
    })
    
    const loginRules = {
      username: [
        { required: true, message: t('login.usernameRequired'), trigger: 'blur' }
      ],
      password: [
        { required: true, message: t('login.passwordRequired'), trigger: 'blur' }
      ]
    }
    
    const isLoading = computed(() => store.getters.isLoading)
    
    const currentLanguage = computed({
      get: () => locale.value,
      set: (value) => {
        locale.value = value
        store.dispatch('setLanguage', value)
      }
    })
    
    const handleLogin = async () => {
      try {
        await store.dispatch('login', loginForm.value)
        ElMessage.success('Login successful')
        router.push({ name: 'Dashboard' })
      } catch (error) {
        console.error('Login error:', error)
        ElMessage.error(t('login.error'))
      }
    }
    
    onMounted(() => {
      // Reset any previous auth state
      store.dispatch('clearError')
    })
    
    return {
      loginForm,
      loginRules,
      isLoading,
      currentLanguage,
      handleLogin
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f7fa;
}

.login-card {
  width: 400px;
  padding: 20px;
  text-align: center;
}

.logo-container {
  margin-bottom: 20px;
}

.logo {
  max-width: 180px;
  height: auto;
}

.login-button {
  width: 100%;
}

.language-selector {
  margin-top: 20px;
}

h1 {
  margin-bottom: 2rem;
  color: #303133;
  font-weight: 500;
}
</style>