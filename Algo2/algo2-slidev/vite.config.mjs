import { defineConfig } from 'vite'
import slidev from '@slidev/cli/plugin'

export default defineConfig({
  base: '/TEUKU_zikri/Algo2/',
  plugins: [slidev()],
  build: {
    outDir: '../../dist_Algo2',
    assetsDir: 'assets',
  },
})
