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

const menuItems = [
  { id: 'account', label: 'Аккаунт' },
  { id: 'ads', label: 'Объявления' },
  { id: 'settings', label: 'Настройки' },
  { id: 'history', label: 'История' },
]

const sectionContent = {
  account: {
    eyebrow: 'Профиль',
    title: 'Центр управления аккаунтом',
    description:
      'Здесь позже можно будет показывать состояние авторизации Avito, имя профиля, рейтинг и результаты последней проверки сессии.',
    cards: [
      { title: 'Статус сессии', value: 'Готово к интеграции', hint: 'Подключим проверку из Python-скрипта.' },
      { title: 'Текущий режим', value: 'Тестовый доступ', hint: 'Логин user, пароль test.' },
      { title: 'Сервер', value: '89.169.38.182', hint: 'Целевая машина для размещения контейнера.' },
    ],
  },
  ads: {
    eyebrow: 'Объявления',
    title: 'Рабочая зона публикаций',
    description:
      'Этот раздел подготовлен под список объявлений, массовые действия, фильтрацию и дальнейший запуск сценариев размещения.',
    cards: [
      { title: 'Черновики', value: '0', hint: 'Подключим после серверной логики.' },
      { title: 'Активные объявления', value: '0', hint: 'Здесь появятся карточки и статусы.' },
      { title: 'Следующий шаг', value: 'Интеграция API/скриптов', hint: 'Интерфейс уже готов к расширению.' },
    ],
  },
  settings: {
    eyebrow: 'Настройки',
    title: 'Конфигурация панели',
    description:
      'Раздел зарезервирован под серверные адреса, пути к сессиям, параметры контейнера и рабочие флаги запуска.',
    cards: [
      { title: 'Тип развёртывания', value: 'Docker + Nginx', hint: 'Статическая сборка внутри контейнера.' },
      { title: 'Фронтенд', value: 'Vue 3 + Vite', hint: 'Один контейнер, один порт, быстрый деплой.' },
      { title: 'Следующий этап', value: 'Связка с backend', hint: 'Можно добавить REST API или WebSocket.' },
    ],
  },
  history: {
    eyebrow: 'История',
    title: 'Журнал действий',
    description:
      'Секция для будущего лога авторизаций, публикаций, изменений настроек и результатов фоновых задач.',
    cards: [
      { title: 'Последняя активность', value: 'Нет записей', hint: 'Логирование подключается позже.' },
      { title: 'Формат', value: 'Хронологическая лента', hint: 'Удобно для аудита и отладки.' },
      { title: 'Источники', value: 'UI + backend', hint: 'Сведём события в одно место.' },
    ],
  },
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
  window.localStorage.removeItem(AUTH_STORAGE_KEY)
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
          <p class="section-text">{{ activeSection.description }}</p>
        </div>

        <div class="card-grid">
          <article v-for="card in activeSection.cards" :key="card.title" class="info-card">
            <p class="card-title">{{ card.title }}</p>
            <strong class="card-value">{{ card.value }}</strong>
            <p class="card-hint">{{ card.hint }}</p>
          </article>
        </div>
      </section>
    </section>
  </div>
</template>
