<script setup>
import { computed, ref } from 'vue'

const AUTH_STORAGE_KEY = 'avito-dashboard-auth'
const DEMO_LOGIN = 'user'
const DEMO_PASSWORD = 'test'

const savedAuthState = window.localStorage.getItem(AUTH_STORAGE_KEY) === 'true'

const login = ref(DEMO_LOGIN)
const password = ref(DEMO_PASSWORD)
const authError = ref('')
const isAuthenticated = ref(savedAuthState)
const activeView = ref('account')
const avitoCheckPending = ref(false)
const avitoCheckResult = ref(null)
const avitoCheckError = ref('')
const avitoUploadPending = ref(false)
const avitoUploadError = ref('')
const avitoUploadMessage = ref('')
const avitoArchiveFile = ref(null)

const menuItems = [
  { id: 'account', label: 'Аккаунт' },
  { id: 'ads', label: 'Объявления' },
  { id: 'settings', label: 'Настройки' },
  { id: 'history', label: 'История' },
]

const sectionContent = {
  account: { eyebrow: 'Аккаунт', title: 'Проверка авторизации Avito' },
  ads: { eyebrow: 'Объявления', title: 'Пустая страница' },
  settings: { eyebrow: 'Настройки', title: 'Пустая страница' },
  history: { eyebrow: 'История', title: 'Пустая страница' },
}

const activeSection = computed(() => sectionContent[activeView.value])

function handleLogin() {
  if (login.value === DEMO_LOGIN && password.value === DEMO_PASSWORD) {
    isAuthenticated.value = true
    authError.value = ''
    window.localStorage.setItem(AUTH_STORAGE_KEY, 'true')
    return
  }

  authError.value = 'Неверный логин или пароль. Используйте user / test.'
}

function handleLogout() {
  isAuthenticated.value = false
  activeView.value = 'account'
  authError.value = ''
  password.value = DEMO_PASSWORD
  avitoCheckPending.value = false
  avitoCheckResult.value = null
  avitoCheckError.value = ''
  avitoUploadPending.value = false
  avitoUploadError.value = ''
  avitoUploadMessage.value = ''
  avitoArchiveFile.value = null
  window.localStorage.removeItem(AUTH_STORAGE_KEY)
}

function downloadAvitoAuthPackage() {
  const link = document.createElement('a')
  link.href = '/api/avito/auth-package/download'
  link.download = 'avito-local-auth-bundle.zip'
  document.body.append(link)
  link.click()
  link.remove()
}

function handleAvitoArchiveChange(event) {
  const [file] = event.target.files ?? []
  avitoArchiveFile.value = file ?? null
  avitoUploadError.value = ''
  avitoUploadMessage.value = file ? `Выбран архив: ${file.name}` : ''
}

async function uploadAvitoAuthArchive() {
  if (!avitoArchiveFile.value) {
    avitoUploadError.value = 'Сначала выберите zip-архив с локальной авторизацией Avito.'
    return
  }

  avitoUploadPending.value = true
  avitoUploadError.value = ''
  avitoUploadMessage.value = ''

  try {
    const formData = new FormData()
    formData.append('file', avitoArchiveFile.value)

    const response = await fetch('/api/avito/auth-package/upload', {
      method: 'POST',
      body: formData,
    })
    const payload = await response.json()
    if (!response.ok) {
      throw new Error(payload.detail || payload.message || `HTTP ${response.status}`)
    }

    avitoUploadMessage.value = payload.message
    await checkAvitoAuthorization()
  } catch (error) {
    avitoUploadError.value = error.message || 'Не удалось загрузить архив авторизации.'
    console.error(error)
  } finally {
    avitoUploadPending.value = false
  }
}

async function checkAvitoAuthorization() {
  avitoCheckPending.value = true
  avitoCheckError.value = ''

  try {
    const response = await fetch('/api/avito/auth-status')
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    avitoCheckResult.value = await response.json()
  } catch (error) {
    avitoCheckResult.value = null
    avitoCheckError.value = 'Не удалось получить ответ от FastAPI сервера.'
    console.error(error)
  } finally {
    avitoCheckPending.value = false
  }
}
</script>

<template>
  <div class="shell">
    <section v-if="!isAuthenticated" class="auth-layout">
      <div class="auth-card standalone-auth-card">
        <div class="auth-head">
          <p class="auth-label">Вход в панель</p>
          <h1>Avito Poster Web</h1>
          <p class="auth-caption">Временные тестовые данные: user / test</p>
        </div>

        <form class="auth-form" @submit.prevent="handleLogin">
          <label class="field">
            <span>Логин</span>
            <input v-model="login" type="text" autocomplete="username" />
          </label>

          <label class="field">
            <span>Пароль</span>
            <input v-model="password" type="password" autocomplete="current-password" />
          </label>

          <button type="submit" class="primary-button">Войти</button>
          <p v-if="authError" class="auth-error">{{ authError }}</p>
        </form>
      </div>
    </section>

    <section v-if="isAuthenticated" class="workspace">
      <header class="topbar">
        <div class="brand-block">
          <p class="brand-kicker">Тестовый контур</p>
          <strong>Avito Poster Web</strong>
        </div>

        <nav class="menu">
          <button
            v-for="item in menuItems"
            :key="item.id"
            type="button"
            class="menu-button"
            :class="{ active: activeView === item.id }"
            @click="activeView = item.id"
          >
            {{ item.label }}
          </button>
        </nav>

        <button type="button" class="ghost-button" @click="handleLogout">
          Выйти
        </button>
      </header>

      <section class="content-panel">
        <div class="content-copy">
          <p class="eyebrow">{{ activeSection.eyebrow }}</p>
          <h2>{{ activeSection.title }}</h2>
        </div>

        <div v-if="activeView === 'account'" class="account-actions">
          <div class="flow-card">
            <p class="status-label">Локальная авторизация</p>
            <h3>Авторизоваться на Avito</h3>
            <p class="flow-text">
              Более рациональный поток: пользователь входит в Avito на своём компьютере,
              а сайт получает только готовую сессию в архиве.
            </p>

            <div class="flow-actions">
              <button type="button" class="primary-button action-button" @click="downloadAvitoAuthPackage">
                Авторизоваться на Avito
              </button>

              <button type="button" class="ghost-button action-button" @click="checkAvitoAuthorization" :disabled="avitoCheckPending">
                {{ avitoCheckPending ? 'Проверяем...' : 'Проверить авторизацию Avito' }}
              </button>
            </div>

            <ol class="helper-list">
              <li>Скачайте архив со скриптом по кнопке выше.</li>
              <li>Запустите локально `python avito_local_auth.py` и войдите в Avito в открывшемся браузере.</li>
              <li>После входа нажмите Enter в консоли. Скрипт создаст `avito_auth_bundle.zip`.</li>
              <li>Загрузите этот архив ниже на сайт.</li>
            </ol>
          </div>

          <div class="upload-panel">
            <label class="upload-field">
              <span>Загрузить архив авторизации</span>
              <input type="file" accept=".zip,application/zip" @change="handleAvitoArchiveChange" />
            </label>

            <button type="button" class="primary-button action-button" @click="uploadAvitoAuthArchive" :disabled="avitoUploadPending">
              {{ avitoUploadPending ? 'Загружаем...' : 'Загрузить архив авторизации' }}
            </button>

            <p v-if="avitoUploadMessage" class="upload-message">{{ avitoUploadMessage }}</p>
            <p v-if="avitoUploadError" class="auth-error">{{ avitoUploadError }}</p>
          </div>

          <p v-if="avitoCheckError" class="auth-error">{{ avitoCheckError }}</p>

          <div v-if="avitoCheckResult" class="status-box">
            <p class="status-line">
              Авторизован:
              <strong>{{ avitoCheckResult.authorized ? 'true' : 'false' }}</strong>
            </p>
            <p v-if="avitoCheckResult.message" class="status-line">
              {{ avitoCheckResult.message }}
            </p>
            <p v-if="avitoCheckResult.display_name" class="status-line">
              Имя профиля: <strong>{{ avitoCheckResult.display_name }}</strong>
            </p>
            <p v-if="avitoCheckResult.rating_value" class="status-line">
              Рейтинг: <strong>{{ avitoCheckResult.rating_value }}</strong>
            </p>
          </div>
        </div>

        <div v-else class="empty-tab"></div>
      </section>
    </section>
  </div>
</template>
