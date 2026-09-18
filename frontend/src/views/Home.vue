<template>
  <div class="min-h-screen bg-confra-cream">
    <header class="bg-gradient-to-br from-confra-green via-confra-red to-confra-gold text-white">
      <div class="max-w-5xl mx-auto px-4 py-16 text-center">
        <p class="uppercase tracking-widest text-sm text-white/80 mb-2">SEAD • Gerência de Gestão e Desenvolvimento de Pessoas</p>
        <h1 class="text-4xl sm:text-5xl font-extrabold mb-4">Confraternização de Fim de Ano</h1>
        <p class="text-lg sm:text-xl text-white/90">
          18 de dezembro de 2026 (sexta-feira) • 16h às 22h
        </p>
        <p class="text-white/90">Salão de Eventos ASMEGO — Rua 72 c/ BR-153, Jardim Goiás, Goiânia-GO</p>
      </div>
    </header>

    <section class="max-w-3xl mx-auto px-4 py-8 mt-8">
      <div class="bg-white rounded-2xl shadow-xl p-6 sm:p-8 text-center">
        <h2 class="text-xl font-bold text-confra-green mb-2">Pagamento da inscrição</h2>
        <p class="text-gray-600 mb-4">Valor da inscrição: <strong>R$ {{ valorInscricao }}</strong></p>
        <div class="w-48 h-48 mx-auto bg-gray-100 border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center text-gray-400 text-sm">
          QR Code PIX
        </div>
        <p class="text-xs text-gray-400 mt-3">
          * Substitua pela imagem real do QR Code PIX fornecido pela SEAD.
        </p>
      </div>
    </section>

    <section id="inscricao" class="max-w-3xl mx-auto px-4 py-8 pb-16">
      <h2 class="text-2xl font-bold text-confra-green mb-6 text-center">Formulário de Inscrição</h2>
      <InscricaoForm />
    </section>
  </div>
</template>

<script setup>
import InscricaoForm from '../components/InscricaoForm.vue'

const valorInscricao = import.meta.env.VITE_VALOR_INSCRICAO || '0,00'
</script>
