import { defineConfig } from 'slidev'

export default defineConfig({
  title: 'Algorithm 2 Presentation: Behavioral Robot',
  theme: 'seriph',
  base: '/TEUKU_zikri/Algo2/',
  vite: {
    build: {
      outDir: '../../dist_Algo2',
      assetsDir: 'assets',
    },
    server: {
      fs: {
        strict: false,
      },
    },
  },
})