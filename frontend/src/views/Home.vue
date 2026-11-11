<template>
  <div class="relative min-h-screen bg-confra-cream">
    <!-- Fundo fixo em div própria (background-attachment: fixed não funciona no iOS) -->
    <div
      class="fixed inset-0 z-0 bg-cover bg-center pointer-events-none"
      :style="{ backgroundImage: `url(${fundoHome})` }"
      aria-hidden="true"
    >
      <!-- Faixa central bege: colagem colorida só nas laterais, conteúdo sobre fundo neutro -->
      <div
        class="absolute inset-y-0 left-1/2 -translate-x-1/2 w-full max-w-[70rem]"
        style="background: linear-gradient(to right, transparent, #fdf8ef 2.5rem, #fdf8ef calc(100% - 2.5rem), transparent)"
      ></div>
    </div>

    <div class="relative">
    <header class="text-white px-4 pt-10 sm:pt-16">
      <div class="max-w-4xl mx-auto px-6 py-10 sm:py-12 text-center rounded-3xl bg-confra-green/90 shadow-2xl backdrop-blur-sm">
        <p class="uppercase tracking-widest text-sm text-white/80 mb-2">SEAD • Gerência de Gestão e Desenvolvimento de Pessoas</p>
        <h1 class="text-4xl sm:text-5xl font-extrabold mb-4">Confraternização de Fim de Ano</h1>
        <p class="text-lg sm:text-xl text-white/90">
          18 de dezembro de 2026 (sexta-feira)
        </p>
        <p class="text-2xl sm:text-3xl font-extrabold text-confra-gold my-2">
          12h às 18h
        </p>
        <p class="text-white/90 mb-6">Salão de Eventos ASMEGO — Rua 72 c/ BR-153, Jardim Goiás, Goiânia-GO</p>
        <p class="max-w-2xl mx-auto text-white/95 leading-relaxed">
          Depois de mais um ano de muito trabalho, chegou a hora de comemorar nossas conquistas:
          encontro com colegas e amigos, chopp gelado, comida saborosa e muita música boa!
        </p>
      </div>
    </header>

    <section class="max-w-3xl mx-auto px-4 py-12">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
        <div v-for="destaque in destaques" :key="destaque.texto" class="bg-white rounded-xl shadow p-6 text-center">
          <p class="text-4xl mb-3">{{ destaque.emoji }}</p>
          <p class="font-bold text-confra-green">{{ destaque.texto }}</p>
        </div>
      </div>
    </section>

    <section class="max-w-3xl mx-auto px-4 py-8">
      <div class="bg-white rounded-2xl shadow-xl p-6 sm:p-8">
        <h2 class="text-xl font-bold text-confra-green mb-4 text-center">Valores da contribuição</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div
            class="rounded-xl border-2 p-4 text-center"
            :class="loteAtivo === 1 ? 'border-confra-red bg-red-50' : 'border-gray-200 opacity-60'"
          >
            <p class="text-xs font-semibold uppercase tracking-wide text-gray-500">1º lote</p>
            <p class="text-2xl font-extrabold text-confra-green my-1">R$ 30,00</p>
            <p v-if="loteAtivo === 1" class="text-xs font-bold text-confra-red mt-2">VALOR ATUAL</p>
          </div>
          <div
            class="rounded-xl border-2 p-4 text-center"
            :class="loteAtivo === 2 ? 'border-confra-red bg-red-50' : 'border-gray-200 opacity-60'"
          >
            <p class="text-xs font-semibold uppercase tracking-wide text-gray-500">2º lote</p>
            <p class="text-2xl font-extrabold text-confra-green my-1">R$ 40,00</p>
            <p v-if="loteAtivo === 2" class="text-xs font-bold text-confra-red mt-2">VALOR ATUAL</p>
          </div>
        </div>
      </div>
    </section>

    <section class="max-w-3xl mx-auto px-4 py-8">
      <div class="bg-white rounded-2xl shadow-xl p-6 sm:p-8 text-center">
        <h2 class="text-xl font-bold text-confra-green mb-2">Pagamento da contribuição</h2>
        <p class="text-gray-600 mb-4">
          Valor atual: <strong>R$ {{ loteAtivo === 1 ? '30,00' : '40,00' }}</strong>
        </p>
        <button
          type="button"
          class="block mx-auto cursor-zoom-in rounded-xl focus:outline-none focus:ring-2 focus:ring-confra-red"
          aria-label="Ampliar QR Code PIX"
          @click="pixAmpliado = true"
        >
          <img
            :src="pixQrCode"
            alt="QR Code PIX para pagamento da inscrição"
            class="w-56 h-56 rounded-lg border border-gray-200 p-2 bg-white"
          />
        </button>
        <p class="text-sm text-gray-500 mt-3">Escaneie o QR Code no app do seu banco.</p>
        <p class="text-xs text-gray-400 mt-1">Toque na imagem para ampliar.</p>

        <div class="mt-6 pt-5 border-t border-gray-200">
          <p class="text-sm text-gray-600 mb-2">Se preferir, copie a chave PIX (e-mail):</p>
          <div class="flex items-center justify-center gap-2 flex-wrap">
            <span class="font-mono font-semibold text-confra-green bg-gray-100 rounded-lg px-3 py-2 break-all select-all">
              {{ CHAVE_PIX }}
            </span>
            <button
              type="button"
              class="px-4 py-2 rounded-lg font-semibold text-white transition-colors"
              :class="chaveCopiada ? 'bg-confra-green' : 'bg-confra-red hover:bg-red-800'"
              @click="copiarChavePix"
            >
              {{ chaveCopiada ? 'Copiado!' : 'Copiar' }}
            </button>
          </div>
          <p class="text-xs text-gray-500 mt-2">Favorecido: Fernando Dias da Silva</p>
        </div>
      </div>
    </section>

    <Transition name="modal">
      <div
        v-if="pixAmpliado"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm cursor-zoom-out"
        role="dialog"
        aria-modal="true"
        aria-label="QR Code PIX ampliado"
        @click="pixAmpliado = false"
      >
        <div class="relative">
          <img
            :src="pixQrCode"
            alt="QR Code PIX para pagamento da inscrição"
            class="w-[min(90vw,90vh,40rem)] h-auto rounded-xl bg-white p-3 shadow-2xl"
          />
          <button
            type="button"
            class="absolute -top-3 -right-3 w-10 h-10 rounded-full bg-white text-confra-green text-2xl font-bold leading-none shadow-lg hover:bg-gray-100"
            aria-label="Fechar"
            @click.stop="pixAmpliado = false"
          >
            &times;
          </button>
        </div>
      </div>
    </Transition>

    <section id="inscricao" class="max-w-3xl mx-auto px-4 py-8 pb-16">
      <h2 class="text-2xl font-bold text-white mb-6 text-center bg-confra-green/90 rounded-xl shadow py-3">Formulário de Inscrição</h2>
      <InscricaoForm />
    </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import InscricaoForm from '../components/InscricaoForm.vue'
import fundoHome from '../assets/fundo-home.jpg'
import pixQrCode1Lote from '../assets/pix-qrcode-1lote.png'
import pixQrCode2Lote from '../assets/pix-qrcode-2lote.png'

const destaques = [
  { emoji: '🍻', texto: 'Open bar e Open food!' },
  { emoji: '🎶', texto: 'Muita música boa' },
]

// 1º lote até 03/11/2026 (inclusive); 2º lote a partir de 04/11/2026, 00h no horário de Brasília.
const DATA_CORTE_LOTE = new Date('2026-11-04T00:00:00-03:00')
const agora = ref(Date.now())
const loteAtivo = computed(() => (agora.value < DATA_CORTE_LOTE.getTime() ? 1 : 2))
// Valor e QR Code do PIX acompanham o lote vigente.
const pixQrCode = computed(() => (loteAtivo.value === 1 ? pixQrCode1Lote : pixQrCode2Lote))

// Quem estiver com a página aberta na virada troca de lote sem precisar recarregar.
let timerVirada = null
function agendarViradaDeLote() {
  const restante = DATA_CORTE_LOTE.getTime() - Date.now()
  if (restante <= 0) return
  // setTimeout não aceita mais de ~24,8 dias; reagenda em etapas se faltar mais que isso.
  timerVirada = setTimeout(() => {
    agora.value = Date.now()
    agendarViradaDeLote()
  }, Math.min(restante + 1000, 2 ** 31 - 1))
}

const CHAVE_PIX = 'fdds.sgi@gmail.com'
const chaveCopiada = ref(false)
let timerCopiada = null

async function copiarChavePix() {
  try {
    await navigator.clipboard.writeText(CHAVE_PIX)
  } catch {
    // Fallback para navegadores sem Clipboard API (ou fora de HTTPS).
    const campo = document.createElement('textarea')
    campo.value = CHAVE_PIX
    campo.style.position = 'fixed'
    campo.style.opacity = '0'
    document.body.appendChild(campo)
    campo.select()
    document.execCommand('copy')
    document.body.removeChild(campo)
  }
  chaveCopiada.value = true
  clearTimeout(timerCopiada)
  timerCopiada = setTimeout(() => (chaveCopiada.value = false), 2000)
}

const pixAmpliado = ref(false)

function fecharComEsc(event) {
  if (event.key === 'Escape') pixAmpliado.value = false
}
onMounted(() => {
  window.addEventListener('keydown', fecharComEsc)
  agendarViradaDeLote()
})
onBeforeUnmount(() => {
  window.removeEventListener('keydown', fecharComEsc)
  clearTimeout(timerVirada)
})
</script>
