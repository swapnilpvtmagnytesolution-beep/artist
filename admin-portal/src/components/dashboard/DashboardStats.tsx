import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  ChartBarIcon,
  PhotoIcon,
  VideoCameraIcon,
  UserGroupIcon,
  CalendarDaysIcon,
  EyeIcon,
  ArrowUpIcon,
  ArrowDownIcon,
} from '@heroicons/react/24/outline';
import { DashboardAPI } from '../../services/apiClient';
import LoadingSpinner from '../common/LoadingSpinner';
import ErrorMessage from '../common/ErrorMessage';

interface DashboardStatsData {
  total_events: number;
  total_photos: number;
  total_videos: number;
  total_users: number;
  total_views: number;
  recent_events: number;
  active_users: number;
  storage_used: string;
  trends: {
    events: number;
    photos: number;
    videos: number;
    users: number;
    views: number;
  };
}

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ComponentType<any>;
  trend?: number;
  color: string;
  delay: number;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon: Icon, trend, color, delay }) => {
  const getTrendIcon = () => {
    if (trend === undefined) return null;
    return trend >= 0 ? (
      <ArrowUpIcon className="w-4 h-4 text-green-500" />
    ) : (
      <ArrowDownIcon className="w-4 h-4 text-red-500" />
    );
  };

  const getTrendColor = () => {
    if (trend === undefined) return '';
    return trend >= 0 ? 'text-green-500' : 'text-red-500';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 hover:shadow-md transition-shadow duration-200"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className={`p-3 rounded-lg ${color}`}>
            <Icon className="w-6 h-6 text-white" />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-600 dark:text-gray-400">{title}</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">{value}</p>
          </div>
        </div>
        {trend !== undefined && (
          <div className="flex items-center space-x-1">
            {getTrendIcon()}
            <span className={`text-sm font-medium ${getTrendColor()}`}>
              {Math.abs(trend)}%
            </span>
          </div>
        )}
      </div>
    </motion.div>
  );
};

const DashboardStats: React.FC = () => {
  const [stats, setStats] = useState<DashboardStatsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await DashboardAPI.getStats();
      setStats(data);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to fetch dashboard stats');
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num: number): string => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <ErrorMessage
        message={error}
        onRetry={fetchStats}
        className="h-64"
      />
    );
  }

  if (!stats) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 dark:text-gray-400">No data available</p>
      </div>
    );
  }

  const statCards = [
    {
      title: 'Total Events',
      value: formatNumber(stats.total_events),
      icon: CalendarDaysIcon,
      trend: stats.trends.events,
      color: 'bg-blue-500',
    },
    {
      title: 'Total Photos',
      value: formatNumber(stats.total_photos),
      icon: PhotoIcon,
      trend: stats.trends.photos,
      color: 'bg-green-500',
    },
    {
      title: 'Total Videos',
      value: formatNumber(stats.total_videos),
      icon: VideoCameraIcon,
      trend: stats.trends.videos,
      color: 'bg-purple-500',
    },
    {
      title: 'Total Users',
      value: formatNumber(stats.total_users),
      icon: UserGroupIcon,
      trend: stats.trends.users,
      color: 'bg-orange-500',
    },
    {
      title: 'Total Views',
      value: formatNumber(stats.total_views),
      icon: EyeIcon,
      trend: stats.trends.views,
      color: 'bg-pink-500',
    },
    {
      title: 'Storage Used',
      value: stats.storage_used,
      icon: ChartBarIcon,
      color: 'bg-indigo-500',
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard Overview</h2>
        <button
          onClick={fetchStats}
          className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors duration-200"
        >
          Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {statCards.map((card, index) => (
          <StatCard
            key={card.title}
            title={card.title}
            value={card.value}
            icon={card.icon}
            trend={card.trend}
            color={card.color}
            delay={index * 0.1}
          />
        ))}
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.6 }}
          className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6"
        >
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Recent Activity</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-400">Recent Events</span>
              <span className="text-sm font-medium text-gray-900 dark:text-white">
                {stats.recent_events}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-400">Active Users</span>
              <span className="text-sm font-medium text-gray-900 dark:text-white">
                {stats.active_users}
              </span>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.7 }}
          className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6"
        >
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">System Health</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-400">Server Status</span>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                Online
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-400">Database</span>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                Connected
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-400">Storage</span>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">
                {stats.storage_used}
              </span>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default DashboardStats;