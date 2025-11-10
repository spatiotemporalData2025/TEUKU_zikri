import { defineConfig } from 'slidev'

export default defineConfig({
  title: 'Algorithm 1 Presentation',
  theme: 'serif',
  // use root base during development; change to your hosting subpath when deploying
  base: '/',
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
