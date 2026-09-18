<template>
  <div>
    <h3 class="font-semibold text-confra-green mb-2">{{ titulo }}</h3>
    <form class="flex gap-2 mb-3" @submit.prevent="adicionar">
      <input
        v-model="novoNome"
        placeholder="Nome"
        class="flex-1 rounded-lg border border-gray-300 px-3 py-1.5 text-sm"
      />
      <button class="bg-confra-green text-white px-3 py-1.5 rounded-lg text-sm font-semibold">Adicionar</button>
    </form>
    <ul class="space-y-1">
      <li
        v-for="item in itens"
        :key="item.id"
        class="flex items-center justify-between text-sm border-b border-gray-100 py-1"
      >
        <span :class="{ 'text-gray-400 line-through': !item.ativo }">{{ item.nome }}</span>
        <button class="text-xs font-semibold underline" :class="item.ativo ? 'text-red-600' : 'text-green-700'" @click="alternar(item)">
          {{ item.ativo ? 'Desativar' : 'Ativar' }}
        </button>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import client from '../api/client'

const props = defineProps({
  titulo: { type: String, required: true },
  resource: { type: String, required: true },
})

const itens = ref([])
const novoNome = ref('')

async function carregar() {
  const resp = await client.get(`/admin/${props.resource}`)
  itens.value = resp.data.map((i) => ({ ...i, ativo: i.ativo ?? true }))
}

async function adicionar() {
  if (!novoNome.value.trim()) return
  await client.post(`/admin/${props.resource}`, { nome: novoNome.value })
  novoNome.value = ''
  await carregar()
}

async function alternar(item) {
  await client.patch(`/admin/${props.resource}/${item.id}/ativo`, null, { params: { ativo: !item.ativo } })
  await carregar()
}

onMounted(carregar)
</script>
