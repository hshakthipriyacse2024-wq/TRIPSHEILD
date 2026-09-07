'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuthStore } from '@/store/auth-store';
import { Shield, LayoutDashboard, Map, AlertTriangle, RefreshCw, FlaskConical, Bot, Bell, BarChart3, Settings, LogOut } from 'lucide-react';
import { cn } from '@/lib/utils';

export function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuthStore();

  const navItems = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'My Journeys', href: '/journeys', icon: Map },
    { name: 'Disruptions', href: '/disruptions', icon: AlertTriangle },
    { name: 'Recovery Center', href: '/recovery', icon: RefreshCw },
    { name: 'What-If Simulator', href: '/simulator', icon: FlaskConical },
    { name: 'Guardian', href: '/guardian', icon: Bot },
    { name: 'Notifications', href: '/notifications', icon: Bell },
    { name: 'Analytics', href: '/analytics', icon: BarChart3 },
    { name: 'Settings', href: '/settings', icon: Settings },
  ];

  if (user?.role === 'ops_admin' || user?.role === 'sys_admin') {
    navItems.push({ name: 'Admin', href: '/admin', icon: Shield });
  }

  return (
    <div className="flex flex-col w-64 bg-white border-r border-gray-200 min-h-screen">
      <div className="flex items-center h-16 px-4 border-b border-gray-200">
        <Shield className="w-8 h-8 text-indigo-600" />
        <span className="ml-2 text-lg font-bold text-gray-900">TripShield AI</span>
      </div>
      <div className="flex-1 py-4 overflow-y-auto">
        <nav className="px-2 space-y-1">
          {navItems.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
            return (
              <Link key={item.name} href={item.href}
                className={cn(
                  'flex items-center px-2 py-2 text-sm font-medium rounded-md group',
                  isActive ? 'bg-indigo-50 text-indigo-600' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                )}
              >
                <item.icon className={cn('mr-3 flex-shrink-0 h-5 w-5', isActive ? 'text-indigo-600' : 'text-gray-400 group-hover:text-gray-500')} />
                {item.name}
              </Link>
            );
          })}
        </nav>
      </div>
      <div className="p-4 border-t border-gray-200">
        <div className="flex items-center">
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">{user?.full_name}</p>
            <p className="text-xs text-gray-500 truncate">{user?.email}</p>
          </div>
          <button onClick={logout} className="ml-2 p-1 text-gray-400 hover:text-gray-500">
            <LogOut className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
