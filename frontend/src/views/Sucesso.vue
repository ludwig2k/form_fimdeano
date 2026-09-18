<template>
  <div class="min-h-screen bg-confra-cream flex items-center justify-center px-4">
    <div class="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center">
      <div class="text-5xl mb-4">✅</div>
      <h1 class="text-2xl font-bold text-confra-green mb-2">Inscrição enviada!</h1>
      <p class="text-gray-600 mb-4">
        Recebemos sua inscrição e o comprovante de pagamento. Nossa equipe vai conferir e você
        receberá um e-mail de confirmação com o QR Code de entrada assim que for aprovado.
      </p>
      <p class="text-sm text-gray-400">Número da inscrição: #{{ id }}</p>
      <router-link to="/" class="inline-block mt-6 text-confra-red font-semibold hover:underline">
        Voltar à página inicial
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()
const id = route.params.id
</script>
