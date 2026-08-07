import express from 'express'
import path from 'path'
import { fileURLToPath } from 'url'
import { createProxyMiddleware } from 'http-proxy-middleware'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const app = express()
const PORT = process.env.PORT || 5173
const API_URL = process.env.API_URL || 'http://localhost:8000'

app.use(
  '/api',
  createProxyMiddleware({
    target: `${API_URL}/api`,
    changeOrigin: true,
  })
)

app.use(express.static(path.join(__dirname, 'dist')))

app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'dist', 'index.html'))
})

app.listen(PORT, () => {
  console.log(`Frontend serving on port ${PORT}, proxying /api to ${API_URL}`)
})
