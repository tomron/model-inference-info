import { defineConfig } from 'vite'

// https://vitejs.dev/config/
export default defineConfig({
  base: '/model-inference-info/',
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
  },
})
