import { defineConfig } from 'vite'
import slidev from '@slidev/cli/vite'

export default defineConfig({
  plugins: [slidev()],
  base: '/TEUKU_zikri/algo2/',   // ← ini penting!
})
