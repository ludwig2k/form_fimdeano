<template>
  <StaffLoginForm
    titulo="Painel Administrativo"
    login-path="/admin/login"
    role="admin"
    redirect-name="admin-dashboard"
  />
</template>

<script setup>
import StaffLoginForm from '../components/StaffLoginForm.vue'
</script>
