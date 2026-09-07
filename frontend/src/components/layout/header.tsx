'use client';

import { usePathname } from 'next/navigation';

export function Header() {
  const pathname = usePathname();
  
  // Basic title generation from path
  const title = pathname === '/dashboard' ? 'Dashboard' : 
                pathname.split('/').filter(Boolean).map(s => s.charAt(0).toUpperCase() + s.slice(1)).join(' / ');

  return (
    <header className="bg-white border-b border-gray-200 h-16 flex items-center px-6">
      <h1 className="text-xl font-semibold text-gray-900">{title}</h1>
    </header>
  );
}
