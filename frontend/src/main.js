import {createApp} from 'vue'
import './style.css'
import App from './App.vue'
import router from "./routes.js";
import axiosInstance from "./api/axios.js";

// Always prepend app url


const app = createApp(App).use(router)
app.config.globalProperties.$axios = axiosInstance

app.mount('#app')
