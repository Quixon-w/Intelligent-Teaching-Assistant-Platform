import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    host: '0.0.0.0',
    port: 3000,
    open: true,
    proxy: {
      '/api': {
        // target: 'http://192.168.1.1:8080',
        // 改为后端运行ip+端口号
        changeOrigin: true,
      },
      '/ai': {
        // target: 'http://192.168.1.2:9001',
        // 同上
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/ai/, ''),
      }
    },
  },
})
