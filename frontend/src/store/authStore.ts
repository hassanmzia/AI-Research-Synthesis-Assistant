import { create } from 'zustand';
import { authAPI } from '../services/api';
import { AuthState, RegisterData, User } from '../types';

export const useAuthStore = create<AuthState>((set) => ({
  user: JSON.parse(localStorage.getItem('arsa_user') || 'null'),
  token: localStorage.getItem('arsa_token'),
  isAuthenticated: !!localStorage.getItem('arsa_token'),

  login: async (username: string, password: string) => {
    const response = await authAPI.login({ username, password });
    const { user, token } = response.data;
    localStorage.setItem('arsa_token', token);
    localStorage.setItem('arsa_user', JSON.stringify(user));
    set({ user, token, isAuthenticated: true });
  },

  register: async (data: RegisterData) => {
    const response = await authAPI.register(data);
    const { user, token } = response.data;
    localStorage.setItem('arsa_token', token);
    localStorage.setItem('arsa_user', JSON.stringify(user));
    set({ user, token, isAuthenticated: true });
  },

  logout: () => {
    localStorage.removeItem('arsa_token');
    localStorage.removeItem('arsa_user');
    set({ user: null, token: null, isAuthenticated: false });
  },

  updateUser: async (data: Partial<User>) => {
    const response = await authAPI.updateMe(data);
    const user = response.data;
    localStorage.setItem('arsa_user', JSON.stringify(user));
    set({ user });
  },
}));
