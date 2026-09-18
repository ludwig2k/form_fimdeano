<template>
  <div class="min-h-screen bg-confra-cream">
    <header class="bg-confra-green text-white px-4 py-4 flex items-center justify-between">
      <h1 class="text-lg font-bold">Check-in — Confraternização SEAD</h1>
      <button class="text-sm underline" @click="sair">Sair</button>
    </header>

    <main class="max-w-md mx-auto px-4 py-6">
      <div v-if="!cameraDisponivel" class="flex flex-col items-center gap-3">
        <button
          class="bg-confra-green text-white px-5 py-3 rounded-lg font-semibold w-full"
          :disabled="abrindoCamera"
          @click="abrirCamera"
        >
          {{ abrindoCamera ? 'Abrindo câmera...' : '📷 Abrir câmera' }}
        </button>
        <p v-if="erroCamera" class="text-sm text-yellow-800 bg-yellow-50 border border-yellow-300 rounded-lg px-3 py-2 w-full">
          Não foi possível acessar a câmera ({{ erroCamera }}). Use a leitura manual abaixo.
        </p>
        <p v-else class="text-xs text-gray-500">
          No celular, o navegador só libera a câmera depois desse toque.
        </p>
      </div>

      <div id="qr-reader" class="rounded-xl overflow-hidden shadow mt-4 min-h-[280px]" :class="{ hidden: !cameraDisponivel }"></div>

      <form class="mt-4 bg-white rounded-xl shadow p-4 flex gap-2" @submit.prevent="validarManual">
        <input
          v-model="codigoManual"
          type="text"
          placeholder="Colar/digitar o código do QR Code"
          class="flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm"
        />
        <button class="bg-confra-green text-white px-3 py-2 rounded-lg text-sm font-semibold">Validar</button>
      </form>

      <Transition name="modal">
        <ResultModal
          v-if="resultado"
          :ok="resultado.ok"
          :mensagem="resultado.mensagem"
          :nome-completo="resultado.nome_completo"
          :unidade="resultado.unidade"
          :anexo="resultado.anexo"
          @fechar="continuarEscaneando"
        />
      </Transition>
    </main>
  </div>
</template>

<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Html5Qrcode } from 'html5-qrcode'
import { useAuthStore } from '../stores/auth'
import client from '../api/client'
import ResultModal from '../components/ResultModal.vue'

const router = useRouter()
const auth = useAuthStore()

const resultado = ref(null)
const erroCamera = ref('')
const cameraDisponivel = ref(false)
const abrindoCamera = ref(false)
const codigoManual = ref('')
let scanner = null
let processando = false

async function validarToken(qrToken) {
  if (processando || !qrToken) return
  processando = true
  try {
    const resp = await client.post('/checkin/validar', { qr_token: qrToken })
    resultado.value = resp.data
    if (scanner && cameraDisponivel.value) {
      await scanner.pause(true)
    }
  } catch (e) {
    resultado.value = { ok: false, mensagem: 'Erro ao validar QR Code.' }
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

async function abrirCamera() {
  erroCamera.value = ''
  abrindoCamera.value = true
  // Mostra a div ANTES de iniciar a câmera: o html5-qrcode mede o tamanho do
  // container nesse momento para criar o <video>, e se a div ainda estiver
  // escondida (display:none) o vídeo nasce com tamanho zero — a câmera liga
  // (permissão concedida) mas nada aparece na tela.
  cameraDisponivel.value = true
  await nextTick()
  try {
    await scanner.start(
      { facingMode: 'environment' },
      { fps: 10, qrbox: { width: 250, height: 250 } },
      (decodedText) => validarToken(decodedText),
      () => {}
    )
  } catch (e) {
    cameraDisponivel.value = false
    erroCamera.value = e?.message || String(e)
  } finally {
    abrindoCamera.value = false
  }
}

function sair() {
  auth.logout()
  router.push({ name: 'checkin-login' })
}

onMounted(() => {
  scanner = new Html5Qrcode('qr-reader')
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
