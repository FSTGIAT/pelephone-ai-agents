<template>
  <footer class="app-footer">
    <div class="footer-container">
      <div class="footer-content">
        <p class="copyright">{{ $t('app.footer') }}</p>
        <div class="version-info">v0.1.0</div>
      </div>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'AppFooter'
}
</script>

<style scoped>
.app-footer {
  background-color: #f5f7fa;
  padding: 15px 0;
  margin-top: auto;
}

.footer-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
}

.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.copyright {
  margin: 0;
  font-size: 14px;
  color: #606266;
}

.version-info {
  font-size: 12px;
  color: #909399;
}
</style>