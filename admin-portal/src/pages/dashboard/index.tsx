import React, { useEffect, useState } from 'react';
import { NextPage } from 'next';
import Head from 'next/head';
import { motion } from 'framer-motion';
import AdminLayout from '../../components/layout/AdminLayout';
import DashboardStats from '../../components/dashboard/DashboardStats';
import { useAuthStore } from '../../store/authStore';
import { useRouter } from 'next/router';
import LoadingSpinner from '../../components/common/LoadingSpinner';

const DashboardPage: NextPage = () => {
  const { user, isAuthenticated, checkAuth } = useAuthStore();
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      try {
        await checkAuth();
      } catch (error) {
        console.error('Auth check failed:', error);
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, [checkAuth]);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/auth/login');
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <LoadingSpinner size="xl" text="Loading dashboard..." />
      </div>
    );
  }

  if (!isAuthenticated) {
    return null; // Will redirect to login
  }

  return (
    <>
      <Head>
        <title>Dashboard - Eddits Admin Portal</title>
        <meta name="description" content="Admin dashboard for Eddits photo and video management" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <AdminLayout>
        <div className="space-y-8">
          {/* Welcome Section */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl shadow-lg p-8 text-white"
          >
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold mb-2">
                  Welcome back, {user?.first_name || user?.username}!
                </h1>
                <p className="text-blue-100 text-lg">
                  Here's what's happening with your events and media today.
                </p>
              </div>
              <div className="hidden md:block">
                <div className="text-right">
                  <p className="text-blue-100 text-sm">
                    {new Date().toLocaleDateString('en-US', {
                      weekday: 'long',
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                    })}
                  </p>
                  <p className="text-blue-100 text-sm">
                    {new Date().toLocaleTimeString('en-US', {
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </p>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Dashboard Stats */}
          <DashboardStats />

          {/* Quick Actions */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.8 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6"
          >
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">
              Quick Actions
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <button
                onClick={() => router.push('/events/create')}
                className="p-4 text-left bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors duration-200 group"
              >
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-blue-500 rounded-lg">
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                  </div>
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400">
                      Create Event
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Add new event
                    </p>
                  </div>
                </div>
              </button>

              <button
                onClick={() => router.push('/events')}
                className="p-4 text-left bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg hover:bg-green-100 dark:hover:bg-green-900/30 transition-colors duration-200 group"
              >
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-green-500 rounded-lg">
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white group-hover:text-green-600 dark:group-hover:text-green-400">
                      Manage Events
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      View all events
                    </p>
                  </div>
                </div>
              </button>

              <button
                onClick={() => router.push('/users')}
                className="p-4 text-left bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg hover:bg-purple-100 dark:hover:bg-purple-900/30 transition-colors duration-200 group"
              >
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-purple-500 rounded-lg">
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                    </svg>
                  </div>
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white group-hover:text-purple-600 dark:group-hover:text-purple-400">
                      Manage Users
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      User management
                    </p>
                  </div>
                </div>
              </button>

              <button
                onClick={() => router.push('/security')}
                className="p-4 text-left bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg hover:bg-orange-100 dark:hover:bg-orange-900/30 transition-colors duration-200 group"
              >
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-orange-500 rounded-lg">
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                    </svg>
                  </div>
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white group-hover:text-orange-600 dark:group-hover:text-orange-400">
                      Security
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Security settings
                    </p>
                  </div>
                </div>
              </button>
            </div>
          </motion.div>

          {/* Recent Activity */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 1.0 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6"
          >
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Recent Activity
              </h3>
              <button
                onClick={() => router.push('/activity')}
                className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium"
              >
                View All
              </button>
            </div>
            <div className="space-y-4">
              <div className="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    New event created: "Wedding Photography"
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">2 hours ago</p>
                </div>
              </div>
              <div className="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    50 photos uploaded to "Birthday Party"
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">4 hours ago</p>
                </div>
              </div>
              <div className="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    New user registered: john.doe@example.com
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">6 hours ago</p>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </AdminLayout>
    </>
  );
};

export default DashboardPage;