'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import Image from 'next/image';
import {
  HomeIcon,
  CalendarIcon,
  PhotoIcon,
  UsersIcon,
  ChartBarIcon,
  CogIcon,
  ShieldCheckIcon,
  BellIcon,
  MagnifyingGlassIcon,
  Bars3Icon,
  XMarkIcon,
  UserCircleIcon,
  ArrowRightOnRectangleIcon,
} from '@heroicons/react/24/outline';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuthStore } from '@/store/authStore';
import { useNotificationStore } from '@/store/notificationStore';
import NotificationDropdown from '@/components/ui/NotificationDropdown';
import UserDropdown from '@/components/ui/UserDropdown';

interface AdminLayoutProps {
  children: React.ReactNode;
  title?: string;
}

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
  { name: 'Events', href: '/events', icon: CalendarIcon },
  { name: 'Media', href: '/media', icon: PhotoIcon },
  { name: 'Users', href: '/users', icon: UsersIcon },
  { name: 'Analytics', href: '/analytics', icon: ChartBarIcon },
  { name: 'Security', href: '/security', icon: ShieldCheckIcon },
  { name: 'Settings', href: '/settings', icon: CogIcon },
];

const AdminLayout: React.FC<AdminLayoutProps> = ({ children, title }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const router = useRouter();
  const { user, logout } = useAuthStore();
  const { notifications, unreadCount } = useNotificationStore();

  // Close sidebar on route change
  useEffect(() => {
    const handleRouteChange = () => setSidebarOpen(false);
    router.events.on('routeChangeStart', handleRouteChange);
    return () => router.events.off('routeChangeStart', handleRouteChange);
  }, [router.events]);

  // Handle search
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/search?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  const handleLogout = async () => {
    await logout();
    router.push('/login');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile sidebar */}
      <AnimatePresence>
        {sidebarOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-40 bg-gray-600 bg-opacity-75 lg:hidden"
              onClick={() => setSidebarOpen(false)}
            />
            
            {/* Sidebar */}
            <motion.div
              initial={{ x: '-100%' }}
              animate={{ x: 0 }}
              exit={{ x: '-100%' }}
              transition={{ type: 'tween', duration: 0.3 }}
              className="fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-xl lg:hidden"
            >
              <SidebarContent onClose={() => setSidebarOpen(false)} />
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
        <div className="flex min-h-0 flex-1 flex-col bg-white shadow-lg">
          <SidebarContent />
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top navigation */}
        <div className="sticky top-0 z-30 bg-white shadow-sm border-b border-gray-200">
          <div className="flex h-16 items-center justify-between px-4 sm:px-6 lg:px-8">
            {/* Mobile menu button */}
            <button
              type="button"
              className="lg:hidden p-2 text-gray-500 hover:text-gray-600"
              onClick={() => setSidebarOpen(true)}
            >
              <Bars3Icon className="h-6 w-6" />
            </button>

            {/* Page title */}
            <div className="flex-1 lg:flex-none">
              <h1 className="text-xl font-semibold text-gray-900">
                {title || 'Admin Portal'}
              </h1>
            </div>

            {/* Search bar */}
            <div className="hidden md:block flex-1 max-w-md mx-8">
              <form onSubmit={handleSearch} className="relative">
                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                  <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="block w-full rounded-lg border-gray-300 pl-10 pr-3 py-2 text-sm placeholder-gray-500 focus:border-primary-500 focus:ring-primary-500"
                  placeholder="Search events, users, media..."
                />
              </form>
            </div>

            {/* Right side actions */}
            <div className="flex items-center space-x-4">
              {/* Notifications */}
              <NotificationDropdown
                notifications={notifications}
                unreadCount={unreadCount}
              />

              {/* User menu */}
              <UserDropdown user={user} onLogout={handleLogout} />
            </div>
          </div>
        </div>

        {/* Page content */}
        <main className="flex-1">
          <div className="py-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

interface SidebarContentProps {
  onClose?: () => void;
}

const SidebarContent: React.FC<SidebarContentProps> = ({ onClose }) => {
  const router = useRouter();

  return (
    <>
      {/* Logo */}
      <div className="flex h-16 items-center justify-between px-6 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="flex-shrink-0">
            <div className="h-8 w-8 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg flex items-center justify-center">
              <PhotoIcon className="h-5 w-5 text-white" />
            </div>
          </div>
          <div>
            <h2 className="text-lg font-bold text-gray-900">Eddits</h2>
            <p className="text-xs text-gray-500">Admin Portal</p>
          </div>
        </div>
        
        {/* Close button for mobile */}
        {onClose && (
          <button
            type="button"
            className="lg:hidden p-2 text-gray-400 hover:text-gray-600"
            onClick={onClose}
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-2">
        {navigation.map((item) => {
          const isActive = router.pathname.startsWith(item.href);
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`
                group flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors
                ${
                  isActive
                    ? 'bg-primary-50 text-primary-700 border-r-2 border-primary-500'
                    : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                }
              `}
            >
              <item.icon
                className={`
                  mr-3 h-5 w-5 flex-shrink-0
                  ${
                    isActive
                      ? 'text-primary-500'
                      : 'text-gray-400 group-hover:text-gray-500'
                  }
                `}
              />
              {item.name}
            </Link>
          );
        })}
      </nav>

      {/* Bottom section */}
      <div className="border-t border-gray-200 p-4">
        <div className="flex items-center space-x-3 text-sm text-gray-500">
          <div className="h-2 w-2 bg-green-400 rounded-full"></div>
          <span>System Online</span>
        </div>
        <div className="mt-2 text-xs text-gray-400">
          Version 1.0.0
        </div>
      </div>
    </>
  );
};

export default AdminLayout;