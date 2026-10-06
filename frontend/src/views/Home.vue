<template>
  <div class="relative min-h-screen bg-confra-cream">
    <!-- Fundo fixo em div própria (background-attachment: fixed não funciona no iOS) -->
    <div
      class="fixed inset-0 z-0 bg-cover bg-center pointer-events-none"
      :style="{ backgroundImage: `url(${fundoHome})` }"
      aria-hidden="true"
    ></div>

    <div class="relative">
    <header class="text-white px-4 pt-10 sm:pt-16">
      <div class="max-w-4xl mx-auto px-6 py-10 sm:py-12 text-center rounded-3xl bg-confra-green/90 shadow-2xl backdrop-blur-sm">
        <p class="uppercase tracking-widest text-sm text-white/80 mb-2">SEAD • Gerência de Gestão e Desenvolvimento de Pessoas</p>
        <h1 class="text-4xl sm:text-5xl font-extrabold mb-4">Confraternização de Fim de Ano</h1>
        <p class="text-lg sm:text-xl text-white/90">
          18 de dezembro de 2026 (sexta-feira) • 16h às 22h
        </p>
        <p class="text-white/90 mb-6">Salão de Eventos ASMEGO — Rua 72 c/ BR-153, Jardim Goiás, Goiânia-GO</p>
        <p class="max-w-2xl mx-auto text-white/95 leading-relaxed">
          Depois de mais um ano de muito trabalho, chegou a hora de comemorar nossas conquistas:
          encontro com colegas e amigos, chopp gelado, comida saborosa e muito pagode no pé!
          Uma tardezinha e noite pensadas pra gente celebrar quem faz a SEAD acontecer:
          <strong>você</strong>.
        </p>
      </div>
    </header>

    <section class="max-w-5xl mx-auto px-4 py-12">
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <div v-for="destaque in destaques" :key="destaque.texto" class="bg-white rounded-xl shadow p-6 text-center">
          <p class="text-4xl mb-3">{{ destaque.emoji }}</p>
          <p class="font-bold text-confra-green">{{ destaque.texto }}</p>
        </div>
      </div>
      <p class="text-center text-gray-700 mt-6 max-w-2xl mx-auto bg-white/90 rounded-xl shadow px-4 py-3">
        Teremos <strong>duas bandas de pagode</strong> e uma <strong>atração surpresa</strong>
        para animar nossa festa!
      </p>
    </section>

    <section class="max-w-3xl mx-auto px-4 py-8">
      <div class="bg-white rounded-2xl shadow-xl p-6 sm:p-8">
        <h2 class="text-xl font-bold text-confra-green mb-4 text-center">Valores da inscrição</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div
            class="rounded-xl border-2 p-4 text-center"
            :class="loteAtivo === 1 ? 'border-confra-red bg-red-50' : 'border-gray-200 opacity-60'"
          >
            <p class="text-xs font-semibold uppercase tracking-wide text-gray-500">1º lote</p>
            <p class="text-2xl font-extrabold text-confra-green my-1">R$ 30,00</p>
            <p class="text-sm text-gray-500">até 06/11/2026</p>
            <p v-if="loteAtivo === 1" class="text-xs font-bold text-confra-red mt-2">VALOR ATUAL</p>
          </div>
          <div
            class="rounded-xl border-2 p-4 text-center"
            :class="loteAtivo === 2 ? 'border-confra-red bg-red-50' : 'border-gray-200 opacity-60'"
          >
            <p class="text-xs font-semibold uppercase tracking-wide text-gray-500">2º lote</p>
            <p class="text-2xl font-extrabold text-confra-green my-1">R$ 40,00</p>
            <p class="text-sm text-gray-500">após 06/11/2026</p>
            <p v-if="loteAtivo === 2" class="text-xs font-bold text-confra-red mt-2">VALOR ATUAL</p>
          </div>
        </div>
      </div>
    </section>

    <section class="max-w-3xl mx-auto px-4 py-8">
      <div class="bg-white rounded-2xl shadow-xl p-6 sm:p-8 text-center">
        <h2 class="text-xl font-bold text-confra-green mb-2">Pagamento da inscrição</h2>
        <p class="text-gray-600 mb-4">
          Valor atual: <strong>R$ {{ loteAtivo === 1 ? '30,00' : '40,00' }}</strong>
        </p>
        <img
          :src="pixQrCode"
          alt="QR Code PIX para pagamento da inscrição"
          class="w-56 h-56 mx-auto rounded-lg border border-gray-200 p-2 bg-white"
        />
        <p class="text-sm text-gray-500 mt-3">Escaneie o QR Code no app do seu banco.</p>
      </div>
    </section>

    <section id="inscricao" class="max-w-3xl mx-auto px-4 py-8 pb-16">
      <h2 class="text-2xl font-bold text-white mb-6 text-center bg-confra-green/90 rounded-xl shadow py-3">Formulário de Inscrição</h2>
      <InscricaoForm />
    </section>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import InscricaoForm from '../components/InscricaoForm.vue'
import fundoHome from '../assets/fundo-home.jpg'
import pixQrCode from '../assets/pix-qrcode.png'

const destaques = [
  { emoji: '🍻', texto: 'Open bar e Open food!' },
  { emoji: '🎶', texto: 'Muita música boa' },
  { emoji: '🎉', texto: 'Você será liberado 12h para preparação para festa!' },
]

// 1º lote até 06/11/2026 (inclusive); 2º lote a partir de 07/11/2026.
const DATA_CORTE_LOTE = new Date('2026-11-07T00:00:00')
const loteAtivo = computed(() => (new Date() < DATA_CORTE_LOTE ? 1 : 2))
</script>
