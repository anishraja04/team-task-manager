import axios from 'axios'

// create one axios instance so that all the api calls use the same base url
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
})

// add the jwt token in every request header
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// if the token expires, automatically try to refresh it using the refresh token
api.interceptors.response.use(
  (res) => res,
  async (err) => {
    const original = err.config
    if (err.response?.status === 401 && !original._retry) {
      original._retry = true
      const refresh = localStorage.getItem('refresh')
      if (refresh) {
        try {
          const { data } = await axios.post(
            `${import.meta.env.VITE_API_URL || '/api'}/auth/token/refresh/`,
            { refresh }
          )
          localStorage.setItem('access', data.access)
          original.headers.Authorization = `Bearer ${data.access}`
          return api(original)
        } catch {
          // if refresh also fails then logout the user
          localStorage.clear()
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(err)
  }
)

export default api
