import { createApp } from 'vue'
import { createPinia } from 'pinia'
import '@/assets/style.css'
import App from '@/App.vue'
import router from '@/router'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import { createLoggerPlugin } from '@/utils/logger'

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)
const app = createApp(App)

app.use(router)
app.use(pinia)
app.use(createLoggerPlugin())
app.mount('#app')
