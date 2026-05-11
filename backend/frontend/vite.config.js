import { defineConfig } from 'vite'
import { resolve } from 'path'

const DIST = resolve(__dirname, '../static/dist')

export default defineConfig({
  build: {
    outDir: DIST,
    emptyOutDir: true,
    cssCodeSplit: false,
    rollupOptions: {
      input: resolve(__dirname, 'src/vendor-element-plus.js'),
      external: ['vue'],
      output: {
        format: 'iife',
        entryFileNames: 'vendor-element-plus.js',
        assetFileNames: 'vendor-element-plus[extname]',
        globals: { vue: 'Vue' },
      },
    },
  },
})
