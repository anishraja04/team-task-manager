import { createContext, useContext, useEffect, useState } from 'react'
import api from '../api/client'

// this context keeps the login state of the whole app in one place
const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  // when the page loads, check if the user is already logged in
  useEffect(() => {
    const token = localStorage.getItem('access')
    if (!token) {
      setLoading(false)
      return
    }
    api
      .get('/auth/me/')
      .then((res) => setUser(res.data))
      .catch(() => localStorage.clear())
      .finally(() => setLoading(false))
  }, [])

  const login = async (email, password) => {
    const { data } = await api.post('/auth/login/', { email, password })
    // save both tokens in the browser storage
    localStorage.setItem('access', data.access)
    localStorage.setItem('refresh', data.refresh)
    setUser(data.user)
    return data.user
  }

  const register = async (payload) => {
    const { data } = await api.post('/auth/register/', payload)
    localStorage.setItem('access', data.access)
    localStorage.setItem('refresh', data.refresh)
    setUser(data.user)
    return data.user
  }

  const logout = () => {
    localStorage.clear()
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
