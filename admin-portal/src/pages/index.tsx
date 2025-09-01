import React, { useEffect } from 'react';
import { NextPage } from 'next';
import { useRouter } from 'next/router';
import Head from 'next/head';
import { useAuthStore } from '../store/authStore';
import LoadingSpinner from '../components/common/LoadingSpinner';

const HomePage: NextPage = () => {
  const router = useRouter();
  const { isAuthenticated, checkAuth } = useAuthStore();

  useEffect(() => {
    const handleRedirect = async () => {
      try {
        await checkAuth();
        
        // Redirect based on authentication status
        if (isAuthenticated) {
          router.replace('/dashboard');
        } else {
          router.replace('/auth/login');
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        router.replace('/auth/login');
      }
    };

    handleRedirect();
  }, [isAuthenticated, checkAuth, router]);

  return (
    <>
      <Head>
        <title>Eddits Admin Portal</title>
        <meta name="description" content="Admin portal for Eddits photo and video management by Meet Dudhwala" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <div className="mx-auto h-20 w-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center mb-6">
            <span className="text-2xl font-bold text-white">E</span>
          </div>
          <LoadingSpinner size="lg" text="Redirecting..." />
        </div>
      </div>
    </>
  );
};

export default HomePage;