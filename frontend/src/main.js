import { createApp } from 'vue'
import App from './app/App.vue'
import { router } from './app/providers/router'
import { pinia } from './app/providers/store'
import './app/styles/main.css'

const app = createApp(App)

app.use(router)
app.use(pinia)

app.mount('#app')

