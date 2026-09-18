<template>
  <div class="min-h-screen bg-confra-cream">
    <header class="bg-confra-green text-white px-4 py-4 flex items-center justify-between">
      <h1 class="text-lg font-bold">Painel Administrativo — Confraternização SEAD</h1>
      <button class="text-sm underline" @click="sair">Sair</button>
    </header>

    <Transition name="toast">
      <div
        v-if="mensagem"
        class="fixed top-4 left-1/2 -translate-x-1/2 z-50 max-w-md w-[calc(100%-2rem)] rounded-lg shadow-lg px-4 py-3 text-sm font-semibold flex items-start gap-2"
        :class="mensagem.tipo === 'erro' ? 'bg-red-600 text-white' : 'bg-confra-green text-white'"
      >
        <span class="flex-1">{{ mensagem.texto }}</span>
        <button class="text-white/80 hover:text-white" @click="mensagem = null">✕</button>
      </div>
    </Transition>

    <main class="max-w-5xl mx-auto px-4 py-6 space-y-8">
      <section>
        <div class="flex gap-2 mb-4 flex-wrap">
          <button
            v-for="f in filtros"
            :key="f.value"
            class="px-4 py-1.5 rounded-full text-sm font-semibold"
            :class="filtroAtual === f.value ? 'bg-confra-red text-white' : 'bg-white text-confra-green border border-confra-green/30'"
            @click="mudarFiltro(f.value)"
          >
            {{ f.label }}
          </button>
        </div>

        <p v-if="carregando" class="text-gray-500">Carregando...</p>
        <p v-else-if="inscricoes.length === 0" class="text-gray-500">Nenhuma inscrição encontrada.</p>

        <div class="space-y-3">
          <div v-for="i in inscricoes" :key="i.id" class="bg-white rounded-xl shadow p-4">
            <div class="flex flex-wrap items-start justify-between gap-2">
              <div>
                <p class="font-semibold text-confra-green">{{ i.nome_completo }}</p>
                <p class="text-sm text-gray-500">CPF {{ i.cpf }} • {{ i.email }}</p>
                <p class="text-sm text-gray-500">{{ i.unidade.nome }} — {{ i.anexo.nome }}</p>
              </div>
              <span
                class="text-xs font-semibold px-2 py-1 rounded-full h-fit"
                :class="{
                  'bg-yellow-100 text-yellow-800': i.status === 'pendente',
                  'bg-green-100 text-green-800': i.status === 'aprovado',
                  'bg-red-100 text-red-800': i.status === 'rejeitado',
                }"
              >
                {{ i.status }}
              </span>
            </div>

            <p v-if="i.motivo_rejeicao" class="text-sm text-red-600 mt-2">Motivo: {{ i.motivo_rejeicao }}</p>
            <p v-if="i.checked_in_at" class="text-sm text-green-700 mt-2">
              Check-in realizado em {{ new Date(i.checked_in_at).toLocaleString('pt-BR') }}
            </p>

            <div class="flex gap-3 mt-3 flex-wrap">
              <button class="text-sm text-confra-red font-semibold underline" @click="verComprovante(i.id)">
                Ver comprovante
              </button>
              <button
                v-if="i.status !== 'aprovado'"
                class="text-sm bg-confra-green text-white px-3 py-1.5 rounded-lg font-semibold"
                @click="pedirConfirmacao('aprovar', i.id)"
              >
                Aprovar
              </button>
              <button
                v-if="i.status !== 'rejeitado'"
                class="text-sm bg-confra-red text-white px-3 py-1.5 rounded-lg font-semibold"
                @click="abrirRejeicao(i.id)"
              >
                Rejeitar
              </button>
              <button
                class="text-sm text-gray-500 font-semibold underline ml-auto"
                @click="pedirConfirmacao('excluir', i.id)"
              >
                Excluir
              </button>
            </div>
          </div>
        </div>
      </section>

      <section class="bg-white rounded-xl shadow p-4">
        <button class="font-semibold text-confra-green" @click="mostrarCatalogo = !mostrarCatalogo">
          {{ mostrarCatalogo ? '▾' : '▸' }} Gerenciar unidades e anexos de lotação
        </button>

        <div v-if="mostrarCatalogo" class="grid grid-cols-1 sm:grid-cols-2 gap-6 mt-4">
          <CatalogoManager titulo="Unidades" resource="unidades" />
          <CatalogoManager titulo="Anexos" resource="anexos" />
        </div>
      </section>
    </main>

    <Transition name="modal">
      <ConfirmModal
        v-if="confirmacaoAlvo"
        :title="tituloConfirmacao"
        :message="mensagemConfirmacao"
        :confirm-label="confirmacaoAlvo.tipo === 'excluir' ? 'Excluir' : 'Aprovar'"
        :danger="confirmacaoAlvo.tipo === 'excluir'"
        @confirm="confirmarAcao"
        @cancel="confirmacaoAlvo = null"
      />
    </Transition>

    <Transition name="modal">
      <div v-if="rejeicaoAlvo" class="fixed inset-0 z-50 flex items-center justify-center px-4 bg-black/50 backdrop-blur-sm">
        <div class="bg-white rounded-2xl shadow-2xl p-6 max-w-sm w-full">
          <h3 class="text-lg font-bold text-confra-green mb-2">Motivo da rejeição</h3>
          <textarea
            v-model="motivoRejeicao"
            rows="3"
            class="w-full rounded-lg border border-gray-300 px-3 py-2"
            placeholder="Ex: valor do comprovante não confere com o valor da inscrição."
          ></textarea>
          <div class="flex gap-3 mt-4 justify-end">
            <button class="px-4 py-2 text-gray-500 font-semibold rounded-lg hover:bg-gray-100" @click="rejeicaoAlvo = null">
              Cancelar
            </button>
            <button class="px-4 py-2 bg-confra-red text-white rounded-lg font-semibold" @click="confirmarRejeicao">
              Confirmar
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import client from '../api/client'
import CatalogoManager from '../components/CatalogoManager.vue'
import ConfirmModal from '../components/ConfirmModal.vue'

const router = useRouter()
const auth = useAuthStore()

const filtros = [
  { label: 'Pendentes', value: 'pendente' },
  { label: 'Aprovadas', value: 'aprovado' },
  { label: 'Rejeitadas', value: 'rejeitado' },
  { label: 'Todas', value: '' },
]

const filtroAtual = ref('pendente')
const inscricoes = ref([])
const carregando = ref(true)
const mostrarCatalogo = ref(false)
const rejeicaoAlvo = ref(null)
const motivoRejeicao = ref('')
const mensagem = ref(null)
const confirmacaoAlvo = ref(null)
let mensagemTimeout = null

const tituloConfirmacao = computed(() =>
  confirmacaoAlvo.value?.tipo === 'excluir' ? 'Excluir inscrição' : 'Aprovar inscrição'
)
const mensagemConfirmacao = computed(() =>
  confirmacaoAlvo.value?.tipo === 'excluir'
    ? 'Tem certeza que deseja excluir esta inscrição? Essa ação não pode ser desfeita.'
    : 'Um e-mail com o QR Code de entrada será enviado ao servidor. Deseja continuar?'
)

function avisar(tipo, texto) {
  mensagem.value = { tipo, texto }
  clearTimeout(mensagemTimeout)
  mensagemTimeout = setTimeout(() => {
    mensagem.value = null
  }, 6000)
}

function mensagemErro(erro, padrao) {
  const detail = erro.response?.data?.detail
  return Array.isArray(detail) ? detail.join(' ') : detail || padrao
}

async function carregar() {
  carregando.value = true
  const params = filtroAtual.value ? { status_filtro: filtroAtual.value } : {}
  const resp = await client.get('/admin/inscricoes', { params })
  inscricoes.value = resp.data
  carregando.value = false
}

function mudarFiltro(valor) {
  filtroAtual.value = valor
  carregar()
}

async function verComprovante(id) {
  const resp = await client.get(`/admin/inscricoes/${id}/comprovante`, { responseType: 'blob' })
  const url = URL.createObjectURL(resp.data)
  window.open(url, '_blank')
}

function pedirConfirmacao(tipo, id) {
  confirmacaoAlvo.value = { tipo, id }
}

async function confirmarAcao() {
  const { tipo, id } = confirmacaoAlvo.value
  confirmacaoAlvo.value = null
  if (tipo === 'excluir') {
    await executarExclusao(id)
  } else {
    await executarAprovacao(id)
  }
}

async function executarExclusao(id) {
  try {
    await client.delete(`/admin/inscricoes/${id}`)
    avisar('sucesso', 'Inscrição excluída.')
    await carregar()
  } catch (e) {
    avisar('erro', mensagemErro(e, 'Não foi possível excluir a inscrição.'))
  }
}

async function executarAprovacao(id) {
  try {
    const resp = await client.post(`/admin/inscricoes/${id}/aprovar`)
    if (resp.data.email_enviado === false) {
      avisar('erro', 'Inscrição aprovada, mas o e-mail de confirmação falhou ao enviar. Verifique a configuração de SMTP.')
    } else {
      avisar('sucesso', 'Inscrição aprovada e e-mail enviado.')
    }
    await carregar()
  } catch (e) {
    avisar('erro', mensagemErro(e, 'Não foi possível aprovar a inscrição.'))
  }
}

function abrirRejeicao(id) {
  rejeicaoAlvo.value = id
  motivoRejeicao.value = ''
}

async function confirmarRejeicao() {
  if (!motivoRejeicao.value.trim()) return
  try {
    const resp = await client.post(`/admin/inscricoes/${rejeicaoAlvo.value}/rejeitar`, { motivo: motivoRejeicao.value })
    rejeicaoAlvo.value = null
    if (resp.data.email_enviado === false) {
      avisar('erro', 'Inscrição rejeitada, mas o e-mail ao servidor falhou ao enviar. Verifique a configuração de SMTP.')
    } else {
      avisar('sucesso', 'Inscrição rejeitada e e-mail enviado.')
    }
    await carregar()
  } catch (e) {
    avisar('erro', mensagemErro(e, 'Não foi possível rejeitar a inscrição.'))
  }
}

function sair() {
  auth.logout()
  router.push({ name: 'admin-login' })
}

onMounted(carregar)
</script>
