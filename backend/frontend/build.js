import { build } from 'vite'
import { resolve } from 'path'
import { fileURLToPath } from 'url'

const __dirname = resolve(fileURLToPath(import.meta.url), '..')
const DIST = resolve(__dirname, '../static/dist')

async function main() {
  // 1. 构建 Element Plus vendor
  await build({
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

  // 2. 构建 ECharts vendor
  await build({
    build: {
      outDir: DIST,
      emptyOutDir: false,
      rollupOptions: {
        input: resolve(__dirname, 'src/vendor-echarts.js'),
        output: {
          format: 'iife',
          entryFileNames: 'vendor-echarts.js',
        },
      },
    },
  })

  console.log('✓ 所有 vendor 构建完成')
}

main().catch(e => {
  console.error('构建失败:', e)
  process.exit(1)
})
