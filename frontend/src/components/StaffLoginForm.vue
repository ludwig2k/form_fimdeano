<template>
  <div class="min-h-screen bg-confra-cream flex items-center justify-center px-4">
    <form class="max-w-sm w-full bg-white rounded-2xl shadow-xl p-8 space-y-4" @submit.prevent="entrar">
      <h1 class="text-xl font-bold text-confra-green text-center mb-2">{{ titulo }}</h1>
      <div>
        <label class="block text-sm font-semibold text-confra-green mb-1">Usuário</label>
        <input v-model="username" required class="w-full rounded-lg border border-gray-300 px-3 py-2" />
      </div>
      <div>
        <label class="block text-sm font-semibold text-confra-green mb-1">Senha</label>
        <input v-model="password" type="password" required class="w-full rounded-lg border border-gray-300 px-3 py-2" />
      </div>
      <p v-if="erro" class="text-sm text-red-600">{{ erro }}</p>
      <button
        type="submit"
        :disabled="entrando"
        class="w-full bg-confra-red hover:bg-red-800 disabled:opacity-60 text-white font-semibold rounded-lg py-3"
      >
        {{ entrando ? 'Entrando...' : 'Entrar' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import client from '../api/client'

const props = defineProps({
  titulo: { type: String, required: true },
  loginPath: { type: String, required: true },
  role: { type: String, required: true },
  redirectName: { type: String, required: true },
})

const router = useRouter()
const auth = useAuthStore()

const username = ref('')
const password = ref('')
const erro = ref('')
const entrando = ref(false)

async function entrar() {
  erro.value = ''
  entrando.value = true
  try {
    const data = new URLSearchParams()
    data.append('username', username.value)
    data.append('password', password.value)
    const resp = await client.post(props.loginPath, data, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    auth.setSession(resp.data.access_token, resp.data.role)
    router.push({ name: props.redirectName })
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Não foi possível entrar.'
  } finally {
    entrando.value = false
  }
}
</script>
