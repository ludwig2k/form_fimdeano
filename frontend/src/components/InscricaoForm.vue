<template>
  <form class="space-y-5 bg-white/95 rounded-2xl shadow-xl p-6 sm:p-8" @submit.prevent="enviar">
    <div>
      <label class="block text-sm font-semibold text-confra-green mb-1">Nome completo *</label>
      <input
        v-model="form.nome_completo"
        type="text"
        required
        class="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-confra-red"
      />
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div>
        <label class="block text-sm font-semibold text-confra-green mb-1">CPF *</label>
        <input
          v-model="cpfDisplay"
          type="text"
          inputmode="numeric"
          maxlength="14"
          required
          placeholder="000.000.000-00"
          class="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-confra-red"
          @input="onCpfInput"
        />
      </div>
      <div>
        <label class="block text-sm font-semibold text-confra-green mb-1">E-mail *</label>
        <input
          v-model="form.email"
          type="email"
          required
          class="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-confra-red"
        />
      </div>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div>
        <label class="block text-sm font-semibold text-confra-green mb-1">Unidade de lotação *</label>
        <select
          v-model="form.unidade_id"
          required
          class="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-confra-red"
        >
          <option disabled value="">Selecione...</option>
          <option v-for="u in unidades" :key="u.id" :value="u.id">{{ u.nome }}</option>
        </select>
      </div>
      <div>
        <label class="block text-sm font-semibold text-confra-green mb-1">Anexo de lotação *</label>
        <select
          v-model="form.anexo_id"
          required
          class="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-confra-red"
        >
          <option disabled value="">Selecione...</option>
          <option v-for="a in anexos" :key="a.id" :value="a.id">{{ a.nome }}</option>
        </select>
      </div>
    </div>

    <div>
      <label class="block text-sm font-semibold text-confra-green mb-1">Comprovante de pagamento *</label>
      <input
        type="file"
        accept="image/png,image/jpeg,image/webp,application/pdf"
        required
        class="w-full rounded-lg border border-gray-300 px-3 py-2 bg-white file:mr-3 file:rounded-md file:border-0 file:bg-confra-red file:text-white file:px-3 file:py-1.5"
        @change="onFileChange"
      />
      <p class="text-xs text-gray-500 mt-1">Formatos aceitos: JPG, PNG, WEBP ou PDF. Tamanho máximo 5MB.</p>
    </div>

    <p v-if="erro" class="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">{{ erro }}</p>

    <button
      type="submit"
      :disabled="enviando"
      class="w-full bg-confra-red hover:bg-red-800 disabled:opacity-60 text-white font-semibold rounded-lg py-3 transition-colors"
    >
      {{ enviando ? 'Enviando...' : 'Confirmar inscrição' }}
    </button>
  </form>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import client from '../api/client'

const router = useRouter()

const unidades = ref([])
const anexos = ref([])
const cpfDisplay = ref('')
const erro = ref('')
const enviando = ref(false)
const arquivo = ref(null)

const form = reactive({
  nome_completo: '',
  cpf: '',
  email: '',
  unidade_id: '',
  anexo_id: '',
})

onMounted(async () => {
  const [uRes, aRes] = await Promise.all([client.get('/unidades'), client.get('/anexos')])
  unidades.value = uRes.data
  anexos.value = aRes.data
})

function onCpfInput(event) {
  const digits = event.target.value.replace(/\D/g, '').slice(0, 11)
  form.cpf = digits
  cpfDisplay.value = digits
    .replace(/(\d{3})(\d)/, '$1.$2')
    .replace(/(\d{3})(\d)/, '$1.$2')
    .replace(/(\d{3})(\d{1,2})$/, '$1-$2')
}

function onFileChange(event) {
  arquivo.value = event.target.files[0] || null
}

async function enviar() {
  erro.value = ''
  if (!arquivo.value) {
    erro.value = 'Selecione o comprovante de pagamento.'
    return
  }
  enviando.value = true
  try {
    const data = new FormData()
    data.append('nome_completo', form.nome_completo)
    data.append('cpf', form.cpf)
    data.append('email', form.email)
    data.append('unidade_id', form.unidade_id)
    data.append('anexo_id', form.anexo_id)
    data.append('comprovante', arquivo.value)

    const resp = await client.post('/inscricoes', data, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    router.push({ name: 'sucesso', params: { id: resp.data.id } })
  } catch (e) {
    const detail = e.response?.data?.detail
    erro.value = Array.isArray(detail) ? detail.join(' ') : detail || 'Não foi possível enviar sua inscrição. Tente novamente.'
  } finally {
    enviando.value = false
  }
}
</script>
