<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center px-4 bg-black/50 backdrop-blur-sm">
    <div class="bg-white rounded-2xl shadow-2xl w-full max-w-sm p-8 text-center" :class="corBorda">
      <p class="text-5xl mb-3">{{ ok ? '✅' : '⚠️' }}</p>
      <p class="font-bold text-xl text-confra-green">{{ mensagem }}</p>
      <template v-if="nomeCompleto">
        <p class="mt-3 text-lg">{{ nomeCompleto }}</p>
        <p class="text-sm text-gray-500">{{ unidade }} — {{ anexo }}</p>
      </template>
      <button
        class="mt-6 w-full bg-confra-green text-white font-semibold rounded-lg py-3"
        @click="$emit('fechar')"
      >
        Escanear próximo
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  ok: { type: Boolean, required: true },
  mensagem: { type: String, required: true },
  nomeCompleto: { type: String, default: null },
  unidade: { type: String, default: null },
  anexo: { type: String, default: null },
})
defineEmits(['fechar'])

const corBorda = computed(() => (props.ok ? 'border-t-8 border-green-500' : 'border-t-8 border-yellow-500'))
</script>
