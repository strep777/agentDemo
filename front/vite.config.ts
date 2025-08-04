import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: 5173,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:3000',
        changeOrigin: true,
        timeout: 60000,  // 增加超时时间到60秒
        secure: false,
        configure: (proxy, options) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            // 确保Authorization header被传递
            if (req.headers.authorization) {
              proxyReq.setHeader('Authorization', req.headers.authorization)
            }
          })
          // 处理流式响应
          proxy.on('proxyRes', (proxyRes, req, res) => {
            if (req.url?.includes('/chat/stream')) {
              // 为流式响应设置更长的超时
              proxyRes.headers['connection'] = 'keep-alive'
              proxyRes.headers['cache-control'] = 'no-cache'
            }
          })
        }
      },
      '/socket.io': {
        target: 'http://localhost:3000',
        changeOrigin: true,
        ws: true,
        timeout: 60000  // 增加超时时间
      }
    }
  }
}) 