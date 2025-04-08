<template>
  <header class="app-header">
    <div class="header-container">
      <div class="logo-container">
        <router-link to="/">
          <img src="@/assets/logo.png" alt="Pelephone Logo" class="logo" />
        </router-link>
      </div>
      
      <nav class="navigation">
        <el-menu
          mode="horizontal"
          :router="true"
          :default-active="activeRoute"
        >
          <el-menu-item index="/dashboard" route="/dashboard">
            <i class="el-icon-s-home"></i>
            <span>{{ $t('nav.dashboard') }}</span>
          </el-menu-item>
          
          <el-menu-item 
            v-if="hasActiveSession" 
            index="/billing" 
            route="/billing"
          >
            <i class="el-icon-s-finance"></i>
            <span>{{ $t('nav.billing') }}</span>
          </el-menu-item>
          
          <el-menu-item 
            v-if="hasActiveSession" 
            index="/international" 
            route="/international"
          >
            <i class="el-icon-phone-outline"></i>
            <span>{{ $t('nav.international') }}</span>
          </el-menu-item>
          
          <el-menu-item 
            v-if="userRole === 'supervisor'" 
            index="/supervisor" 
            route="/supervisor"
          >
            <i class="el-icon-s-management"></i>
            <span>{{ $t('nav.supervisor') }}</span>
          </el-menu-item>
        </el-menu>
      </nav>
      
      <div class="user-controls">
        <el-dropdown trigger="click" @command="handleCommand">
          <span class="user-dropdown-link">
            <el-avatar icon="el-icon-user" size="small"></el-avatar>
            <span class="username">{{ currentUser.username }}</span>
            <i class="el-icon-arrow-down"></i>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">
                <i class="el-icon-user"></i>
                {{ $t('nav.profile') }}
              </el-dropdown-item>
              
              <el-dropdown-item divided>
                <span class="language-dropdown">
                  {{ $t('nav.language') }}:
                  <el-radio-group v-model="currentLanguage" size="small">
                    <el-radio-button label="en">EN</el-radio-button>
                    <el-radio-button label="he">HE</el-radio-button>
                  </el-radio-group>
                </span>
              </el-dropdown-item>
              
              <el-dropdown-item divided command="logout">
                <i class="el-icon-switch-button"></i>
                {{ $t('nav.logout') }}
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
  </header>
</template>

<script>
import { computed } from 'vue'
import { useStore } from 'vuex'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

export default {
  name: 'AppHeader',
  
  setup() {
    const store = useStore()
    const route = useRoute()
    const router = useRouter()
    const { locale } = useI18n()
    
    const currentUser = computed(() => store.getters.currentUser || {})
    const userRole = computed(() => store.getters.userRole)
    const hasActiveSession = computed(() => store.getters.hasActiveSession)
    
    const activeRoute = computed(() => route.path)
    
    const currentLanguage = computed({
      get: () => locale.value,
      set: (value) => {
        locale.value = value
        store.dispatch('setLanguage', value)
      }
    })
    
    const handleCommand = (command) => {
      if (command === 'logout') {
        store.dispatch('logout')
        router.push('/login')
      } else if (command === 'profile') {
        // Navigate to user profile page
      }
    }
    
    return {
      currentUser,
      userRole,
      hasActiveSession,
      activeRoute,
      currentLanguage,
      handleCommand
    }
  }
}
</script>

<style scoped>
.app-header {
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 60px;
  max-width: 1400px;
  margin: 0 auto;
}

.logo-container {
  width: 160px;
}

.logo {
  height: 40px;
  object-fit: contain;
}

.navigation {
  flex: 1;
  margin: 0 20px;
}

.user-dropdown-link {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.username {
  margin: 0 8px;
}

.language-dropdown {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* RTL support */
:deep([dir="rtl"]) .username {
  margin: 0 8px 0 8px;
}
</style>