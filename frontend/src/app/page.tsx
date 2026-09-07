'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/auth-store';

export default function Page() {
  const router = useRouter();
  const { isAuthenticated, loadUser } = useAuthStore();

  useEffect(() => {
    loadUser().finally(() => {
      if (useAuthStore.getState().isAuthenticated) {
        router.push('/dashboard');
      } else {
        router.push('/login');
      }
    });
  }, [router, loadUser]);

  return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
}
