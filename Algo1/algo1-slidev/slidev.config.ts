import { defineConfig } from 'slidev'

export default defineConfig({
  title: 'Algorithm 1 Presentation',
  theme: 'seriph',
  base: '/TEUKU_zikri/Algo1/',
  vite: {
    build: {
      outDir: '../../dist_Algo1',
      assetsDir: 'assets',
    },
    server: {
      fs: {
        strict: false,
      },
    },
  },
})
