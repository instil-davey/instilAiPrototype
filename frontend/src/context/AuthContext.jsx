import { createContext, useContext, useState, useEffect } from 'react'
import { authAPI } from '../services/api'

const AuthContext = createContext(null)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  // For prototype: No authentication needed
  const token = null
  const user = {
    id: 1,
    username: 'prototype_user',
    email: 'prototype@example.com',
    full_name: 'Prototype User'
  }
  const loading = false

  const login = async () => {
    // No-op for prototype
  }

  const logout = () => {
    // No-op for prototype
  }

  return (
    <AuthContext.Provider value={{ token, user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  )
}
