<template>
  <div class="min-h-screen bg-confra-cream flex items-center justify-center px-4 py-10">
    <div class="max-w-md w-full bg-white rounded-2xl shadow-xl p-8">
      <template v-if="carregando">
        <p class="text-center text-gray-500">Carregando...</p>
      </template>

      <template v-else-if="erroCarregar">
        <p class="text-center text-red-600">{{ erroCarregar }}</p>
      </template>

      <template v-else-if="enviado">
        <div class="text-center">
          <div class="text-5xl mb-4">✅</div>
          <h1 class="text-xl font-bold text-confra-green mb-2">Comprovante reenviado!</h1>
          <p class="text-gray-600">Sua inscrição voltou para análise da equipe organizadora.</p>
        </div>
      </template>

      <template v-else>
        <h1 class="text-xl font-bold text-confra-green mb-2">Reenviar comprovante</h1>
        <p class="text-gray-600 mb-1">Olá, {{ info.nome_completo }}.</p>
        <p class="bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-3 py-2 mb-4">
          Motivo da rejeição: {{ info.motivo_rejeicao }}
        </p>

        <form @submit.prevent="enviar" class="space-y-4">
          <input
            type="file"
            accept="image/png,image/jpeg,image/webp,application/pdf"
            required
            class="w-full rounded-lg border border-gray-300 px-3 py-2 bg-white file:mr-3 file:rounded-md file:border-0 file:bg-confra-red file:text-white file:px-3 file:py-1.5"
            @change="onFileChange"
          />
          <p v-if="erroEnvio" class="text-sm text-red-600">{{ erroEnvio }}</p>
          <button
            type="submit"
            :disabled="enviando"
            class="w-full bg-confra-red hover:bg-red-800 disabled:opacity-60 text-white font-semibold rounded-lg py-3"
          >
            {{ enviando ? 'Enviando...' : 'Reenviar comprovante' }}
          </button>
        </form>
      </template>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import client from '../api/client'

const route = useRoute()
const token = route.params.token

const carregando = ref(true)
const erroCarregar = ref('')
const info = ref({})
const arquivo = ref(null)
const enviando = ref(false)
const erroEnvio = ref('')
const enviado = ref(false)

onMounted(async () => {
  try {
    const resp = await client.get(`/inscricoes/reenvio/${token}`)
    if (resp.data.status !== 'rejeitado') {
      erroCarregar.value = 'Esta inscrição não está aguardando reenvio de comprovante.'
    } else {
      info.value = resp.data
    }
  } catch (e) {
    erroCarregar.value = 'Link inválido ou expirado.'
  } finally {
    carregando.value = false
  }
})

function onFileChange(event) {
  arquivo.value = event.target.files[0] || null
}

async function enviar() {
  erroEnvio.value = ''
  if (!arquivo.value) {
    erroEnvio.value = 'Selecione o novo comprovante.'
    return
  }
  enviando.value = true
  try {
    const data = new FormData()
    data.append('comprovante', arquivo.value)
    await client.post(`/inscricoes/reenvio/${token}`, data, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    enviado.value = true
  } catch (e) {
    erroEnvio.value = e.response?.data?.detail || 'Não foi possível reenviar o comprovante.'
  } finally {
    enviando.value = false
  }
}
</script>
