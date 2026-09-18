<template>
  <div class="min-h-screen bg-confra-cream">
    <header class="bg-confra-green text-white px-4 py-4 flex items-center justify-between">
      <h1 class="text-lg font-bold">Check-in — Confraternização SEAD</h1>
      <button class="text-sm underline" @click="sair">Sair</button>
    </header>

    <main class="max-w-md mx-auto px-4 py-6">
      <div id="qr-reader" class="rounded-xl overflow-hidden shadow" :class="{ hidden: !cameraDisponivel }"></div>

      <p v-if="erroCamera" class="mt-4 text-sm text-yellow-800 bg-yellow-50 border border-yellow-300 rounded-lg px-3 py-2">
        Não foi possível acessar a câmera ({{ erroCamera }}). Use a leitura manual abaixo.
      </p>

      <form class="mt-4 bg-white rounded-xl shadow p-4 flex gap-2" @submit.prevent="validarManual">
        <input
          v-model="codigoManual"
          type="text"
          placeholder="Colar/digitar o código do QR Code"
          class="flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm"
        />
        <button class="bg-confra-green text-white px-3 py-2 rounded-lg text-sm font-semibold">Validar</button>
      </form>

      <div v-if="resultado" class="mt-6 rounded-xl p-6 text-center shadow" :class="corResultado">
        <p class="text-3xl mb-2">{{ resultado.ok ? '✅' : '⚠️' }}</p>
        <p class="font-bold text-lg">{{ resultado.mensagem }}</p>
        <template v-if="resultado.nome_completo">
          <p class="mt-2">{{ resultado.nome_completo }}</p>
          <p class="text-sm text-gray-600">{{ resultado.unidade }} — {{ resultado.anexo }}</p>
        </template>
        <button class="mt-4 text-sm underline font-semibold" @click="continuarEscaneando">
          Escanear próximo
        </button>
      </div>
    </main>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Html5Qrcode } from 'html5-qrcode'
import { useAuthStore } from '../stores/auth'
import client from '../api/client'

const router = useRouter()
const auth = useAuthStore()

const resultado = ref(null)
const erroCamera = ref('')
const cameraDisponivel = ref(false)
const codigoManual = ref('')
let scanner = null
let processando = false

const corResultado = ref('bg-white')

async function validarToken(qrToken) {
  if (processando || !qrToken) return
  processando = true
  try {
    const resp = await client.post('/checkin/validar', { qr_token: qrToken })
    resultado.value = resp.data
    corResultado.value = resp.data.ok ? 'bg-green-50 border border-green-300' : 'bg-yellow-50 border border-yellow-300'
    if (scanner && cameraDisponivel.value) {
      await scanner.pause(true)
    }
  } catch (e) {
    resultado.value = { ok: false, mensagem: 'Erro ao validar QR Code.' }
    corResultado.value = 'bg-red-50 border border-red-300'
  } finally {
    processando = false
  }
}

function validarManual() {
  const codigo = codigoManual.value.trim()
  codigoManual.value = ''
  validarToken(codigo)
}

function continuarEscaneando() {
  resultado.value = null
  if (scanner && cameraDisponivel.value) {
    scanner.resume()
  }
}

function sair() {
  auth.logout()
  router.push({ name: 'checkin-login' })
}

onMounted(async () => {
  scanner = new Html5Qrcode('qr-reader')
  try {
    await scanner.start(
      { facingMode: 'environment' },
      { fps: 10, qrbox: { width: 250, height: 250 } },
      (decodedText) => validarToken(decodedText),
      () => {}
    )
    cameraDisponivel.value = true
  } catch (e) {
    erroCamera.value = e?.message || String(e)
  }
})

onBeforeUnmount(async () => {
  if (scanner && cameraDisponivel.value) {
    try {
      await scanner.stop()
    } catch (e) {
      /* ignore */
    }
  }
})
</script>
