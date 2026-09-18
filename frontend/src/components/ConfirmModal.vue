<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center px-4 bg-black/50 backdrop-blur-sm">
    <div class="bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6">
      <h3 class="text-lg font-bold text-confra-green mb-2">{{ title }}</h3>
      <p class="text-gray-600 mb-6">{{ message }}</p>
      <div class="flex gap-3 justify-end">
        <button
          class="px-4 py-2 text-gray-500 font-semibold rounded-lg hover:bg-gray-100"
          @click="$emit('cancel')"
        >
          {{ cancelLabel }}
        </button>
        <button
          class="px-4 py-2 rounded-lg font-semibold text-white"
          :class="danger ? 'bg-confra-red hover:bg-red-800' : 'bg-confra-green hover:bg-green-800'"
          @click="$emit('confirm')"
        >
          {{ confirmLabel }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  message: { type: String, required: true },
  confirmLabel: { type: String, default: 'Confirmar' },
  cancelLabel: { type: String, default: 'Cancelar' },
  danger: { type: Boolean, default: false },
})
defineEmits(['confirm', 'cancel'])
</script>
