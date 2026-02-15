import { defineConfig } from 'vite'
import { copyFileSync, mkdirSync } from 'fs'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  base: mode === 'production' ? '/model-inference-info/' : '/',
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
  },
  publicDir: 'public',
  plugins: [
    {
      name: 'copy-data',
      closeBundle() {
        // Copy data directory to dist
        mkdirSync('dist/data', { recursive: true })
        copyFileSync('data/pricing.json', 'dist/data/pricing.json')
        copyFileSync('data/schema.json', 'dist/data/schema.json')
      }
    }
  ]
}))
