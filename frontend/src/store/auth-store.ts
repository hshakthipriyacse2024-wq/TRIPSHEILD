import { create } from 'zustand';
import { User } from '@/types';
import { authApi } from '@/services/api';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (data: any) => Promise<void>;
  register: (data: any) => Promise<void>;
  logout: () => void;
  loadUser: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  token: typeof window !== 'undefined' ? localStorage.getItem('token') : null,
  isAuthenticated: typeof window !== 'undefined' ? Boolean(localStorage.getItem('token') && localStorage.getItem('token') !== 'undefined') : false,
  login: async (data) => {
    const res = await authApi.login(data);
    const token = res.data.access_token;
    const user = res.data.user;
    localStorage.setItem('token', token);
    set({ token, user, isAuthenticated: true });
  },
  register: async (data) => {
    const res = await authApi.register(data);
    const token = res.data.access_token;
    const user = res.data.user;
    localStorage.setItem('token', token);
    set({ token, user, isAuthenticated: true });
  },
  logout: () => {
    localStorage.removeItem('token');
    set({ token: null, user: null, isAuthenticated: false });
  },
  loadUser: async () => {
    const token = localStorage.getItem('token');
    if (!token || token === 'undefined') {
      set({ user: null, token: null, isAuthenticated: false });
      return;
    }
    try {
      const res = await authApi.getMe();
      set({ user: res.data, token, isAuthenticated: true });
    } catch {
      localStorage.removeItem('token');
      set({ user: null, token: null, isAuthenticated: false });
    }
  },
}));
