import React, { ReactNode } from 'react';
import { LucideIcon } from 'lucide-react';

interface BriefingSectionProps {
  title: string;
  icon?: LucideIcon;
  children: ReactNode;
  className?: string;
  delay?: number;
}

export const BriefingSection: React.FC<BriefingSectionProps> = ({
  title,
  icon: Icon,
  children,
  className = '',
  delay = 0,
}) => {
  return (
    <div
      className={`bg-white rounded-xl border border-gray-200 overflow-hidden animate-slide-up ${className}`}
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="px-6 py-4 border-b border-gray-100 bg-gray-50">
        <div className="flex items-center gap-3">
          {Icon && (
            <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
              <Icon className="w-4 h-4 text-blue-600" />
            </div>
          )}
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        </div>
      </div>
      <div className="px-6 py-5">{children}</div>
    </div>
  );
};

interface StatCardProps {
  label: string;
  value: string | number;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  icon?: LucideIcon;
  className?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  label,
  value,
  trend,
  trendValue,
  icon: Icon,
  className = '',
}) => {
  const trendColors = {
    up: 'text-green-600 bg-green-50',
    down: 'text-red-600 bg-red-50',
    neutral: 'text-gray-600 bg-gray-50',
  };

  return (
    <div className={`bg-gray-50 rounded-lg p-4 ${className}`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm text-gray-600 mb-1">{label}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          {trend && trendValue && (
            <div className={`inline-flex items-center gap-1 mt-2 px-2 py-1 rounded-full text-xs font-medium ${trendColors[trend]}`}>
              {trend === 'up' && '↑'}
              {trend === 'down' && '↓'}
              {trend === 'neutral' && '→'}
              {trendValue}
            </div>
          )}
        </div>
        {Icon && (
          <div className="flex-shrink-0 w-10 h-10 bg-white rounded-lg flex items-center justify-center">
            <Icon className="w-5 h-5 text-gray-600" />
          </div>
        )}
      </div>
    </div>
  );
};

interface TimelineItemProps {
  date: string;
  type: string;
  title: string;
  description?: string;
  staffMember?: string;
  icon?: LucideIcon;
}

export const TimelineItem: React.FC<TimelineItemProps> = ({
  date,
  type,
  title,
  description,
  staffMember,
  icon: Icon,
}) => {
  return (
    <div className="flex gap-4 group">
      <div className="flex flex-col items-center">
        <div className="flex-shrink-0 w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center group-hover:bg-blue-200 transition-colors">
          {Icon ? (
            <Icon className="w-5 h-5 text-blue-600" />
          ) : (
            <div className="w-3 h-3 bg-blue-600 rounded-full" />
          )}
        </div>
        <div className="w-0.5 h-full bg-gray-200 mt-2" />
      </div>
      <div className="flex-1 pb-6">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-xs font-medium text-blue-600 bg-blue-50 px-2 py-1 rounded">
            {type}
          </span>
          <span className="text-xs text-gray-500">{date}</span>
        </div>
        <h4 className="font-medium text-gray-900 mb-1">{title}</h4>
        {description && (
          <p className="text-sm text-gray-600 mb-2">{description}</p>
        )}
        {staffMember && (
          <p className="text-xs text-gray-500">Contact: {staffMember}</p>
        )}
      </div>
    </div>
  );
};

interface BadgeProps {
  children: ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'default',
  className = '',
}) => {
  const variants = {
    default: 'bg-gray-100 text-gray-700',
    success: 'bg-green-100 text-green-700',
    warning: 'bg-yellow-100 text-yellow-700',
    danger: 'bg-red-100 text-red-700',
    info: 'bg-blue-100 text-blue-700',
  };

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${variants[variant]} ${className}`}
    >
      {children}
    </span>
  );
};

interface ProgressBarProps {
  value: number;
  max: number;
  label?: string;
  showPercentage?: boolean;
  className?: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  max,
  label,
  showPercentage = true,
  className = '',
}) => {
  const percentage = Math.round((value / max) * 100);

  return (
    <div className={className}>
      {(label || showPercentage) && (
        <div className="flex justify-between items-center mb-2">
          {label && <span className="text-sm text-gray-600">{label}</span>}
          {showPercentage && (
            <span className="text-sm font-medium text-gray-900">{percentage}%</span>
          )}
        </div>
      )}
      <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
        <div
          className="bg-blue-600 h-full rounded-full transition-all duration-500 ease-out"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};
