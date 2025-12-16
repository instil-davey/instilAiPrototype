'use client';

import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  X,
  DollarSign,
  TrendingUp,
  Users,
  Calendar,
  Mail,
  Phone,
  MapPin,
  Award,
  Target,
  MessageSquare,
  Clock,
  Sparkles,
  AlertCircle,
  CheckCircle,
  Activity,
} from 'lucide-react';
import { format } from 'date-fns';
import { ConstituentBriefing } from '@/types/constituent';
import {
  BriefingSection,
  StatCard,
  TimelineItem,
  Badge,
  ProgressBar,
} from './BriefingSection';

interface ConstituentModalProps {
  constituentId: number;
  isOpen: boolean;
  onClose: () => void;
  onGenerateMessage?: (constituentId: number) => void;
}

export const ConstituentModal: React.FC<ConstituentModalProps> = ({
  constituentId,
  isOpen,
  onClose,
  onGenerateMessage,
}) => {
  const [briefing, setBriefing] = useState<ConstituentBriefing | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && constituentId) {
      fetchBriefing();
    }
  }, [isOpen, constituentId]);

  const fetchBriefing = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`/api/constituents/${constituentId}/briefing`);

      if (!response.ok) {
        throw new Error('Failed to fetch briefing');
      }

      const data = await response.json();
      setBriefing(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateMessage = () => {
    if (onGenerateMessage) {
      onGenerateMessage(constituentId);
    }
  };

  // Prevent body scroll when modal is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return format(new Date(dateString), 'MMM d, yyyy');
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'danger';
      case 'medium':
        return 'warning';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };

  const getActionIcon = (type: string) => {
    switch (type) {
      case 'call':
        return Phone;
      case 'email':
        return Mail;
      case 'meeting':
        return Calendar;
      case 'proposal':
        return Target;
      case 'thank-you':
        return Award;
      default:
        return MessageSquare;
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3, ease: 'easeOut' }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
            onClick={onClose}
          />

          {/* Modal */}
          <div className="fixed inset-0 z-50 overflow-hidden flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.3, ease: [0.34, 1.56, 0.64, 1] }}
              className="relative w-full max-w-6xl h-[90vh] bg-white rounded-2xl shadow-2xl overflow-hidden flex flex-col"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Header */}
              <div className="flex-shrink-0 px-8 py-6 bg-gradient-to-r from-blue-600 to-blue-700 text-white">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    {loading ? (
                      <div className="animate-pulse">
                        <div className="h-8 bg-white/20 rounded w-64 mb-2" />
                        <div className="h-4 bg-white/20 rounded w-48" />
                      </div>
                    ) : briefing ? (
                      <>
                        <h2 className="text-3xl font-bold mb-2">
                          {briefing.constituent.first_name} {briefing.constituent.last_name}
                        </h2>
                        <div className="flex flex-wrap items-center gap-4 text-blue-100">
                          {briefing.constituent.email && (
                            <div className="flex items-center gap-2">
                              <Mail className="w-4 h-4" />
                              <span className="text-sm">{briefing.constituent.email}</span>
                            </div>
                          )}
                          {briefing.constituent.phone && (
                            <div className="flex items-center gap-2">
                              <Phone className="w-4 h-4" />
                              <span className="text-sm">{briefing.constituent.phone}</span>
                            </div>
                          )}
                          {briefing.constituent.city && briefing.constituent.state && (
                            <div className="flex items-center gap-2">
                              <MapPin className="w-4 h-4" />
                              <span className="text-sm">
                                {briefing.constituent.city}, {briefing.constituent.state}
                              </span>
                            </div>
                          )}
                        </div>
                      </>
                    ) : null}
                  </div>
                  <button
                    onClick={onClose}
                    className="flex-shrink-0 w-10 h-10 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center transition-colors"
                    aria-label="Close modal"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>

                {/* Key Stats Bar */}
                {briefing && (
                  <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mt-6">
                    <div className="bg-white/10 backdrop-blur-sm rounded-lg px-4 py-3">
                      <p className="text-xs text-blue-100 mb-1">Total Given</p>
                      <p className="text-xl font-bold">
                        {formatCurrency(briefing.key_stats.total_given)}
                      </p>
                    </div>
                    <div className="bg-white/10 backdrop-blur-sm rounded-lg px-4 py-3">
                      <p className="text-xs text-blue-100 mb-1">Contributions</p>
                      <p className="text-xl font-bold">
                        {briefing.key_stats.total_contributions}
                      </p>
                    </div>
                    <div className="bg-white/10 backdrop-blur-sm rounded-lg px-4 py-3">
                      <p className="text-xs text-blue-100 mb-1">Interactions</p>
                      <p className="text-xl font-bold">
                        {briefing.key_stats.total_interactions}
                      </p>
                    </div>
                    <div className="bg-white/10 backdrop-blur-sm rounded-lg px-4 py-3">
                      <p className="text-xs text-blue-100 mb-1">Engagement</p>
                      <p className="text-xl font-bold">
                        {briefing.key_stats.engagement_score}%
                      </p>
                    </div>
                    <div className="bg-white/10 backdrop-blur-sm rounded-lg px-4 py-3">
                      <p className="text-xs text-blue-100 mb-1">Donor Tenure</p>
                      <p className="text-xl font-bold">
                        {briefing.key_stats.donor_tenure}
                      </p>
                    </div>
                  </div>
                )}
              </div>

              {/* Content */}
              <div className="flex-1 overflow-y-auto bg-gray-50 p-8">
                {loading ? (
                  <div className="flex items-center justify-center h-full">
                    <div className="text-center">
                      <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4" />
                      <p className="text-gray-600">Loading briefing...</p>
                    </div>
                  </div>
                ) : error ? (
                  <div className="flex items-center justify-center h-full">
                    <div className="text-center text-red-600">
                      <AlertCircle className="w-16 h-16 mx-auto mb-4" />
                      <p className="text-lg font-medium">Error loading briefing</p>
                      <p className="text-sm mt-2">{error}</p>
                    </div>
                  </div>
                ) : briefing ? (
                  <div className="space-y-6 max-w-5xl mx-auto">
                    {/* AI-Generated Summary */}
                    <BriefingSection
                      title="AI-Generated Summary"
                      icon={Sparkles}
                      delay={0}
                    >
                      <div className="prose prose-sm max-w-none">
                        <p className="text-gray-700 leading-relaxed">
                          {briefing.summary}
                        </p>
                      </div>
                    </BriefingSection>

                    {/* Giving Breakdown */}
                    <BriefingSection
                      title="Giving Breakdown"
                      icon={DollarSign}
                      delay={100}
                    >
                      <div className="space-y-6">
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                          <StatCard
                            label="Total Given"
                            value={formatCurrency(briefing.giving_breakdown.total_amount)}
                            icon={DollarSign}
                          />
                          <StatCard
                            label="Contributions"
                            value={briefing.giving_breakdown.contribution_count}
                            icon={TrendingUp}
                          />
                          <StatCard
                            label="Average Gift"
                            value={formatCurrency(briefing.giving_breakdown.average_gift)}
                            icon={Activity}
                          />
                          <StatCard
                            label="Largest Gift"
                            value={formatCurrency(briefing.giving_breakdown.largest_gift)}
                            icon={Award}
                          />
                        </div>

                        {/* By Type */}
                        <div>
                          <h4 className="text-sm font-medium text-gray-900 mb-3">
                            By Contribution Type
                          </h4>
                          <div className="space-y-3">
                            {briefing.giving_breakdown.by_type.map((item) => (
                              <ProgressBar
                                key={item.type}
                                label={`${item.type} (${item.count} gifts)`}
                                value={item.amount}
                                max={briefing.giving_breakdown.total_amount}
                              />
                            ))}
                          </div>
                        </div>

                        {/* Recent Contributions */}
                        <div>
                          <h4 className="text-sm font-medium text-gray-900 mb-3">
                            Recent Contributions
                          </h4>
                          <div className="space-y-2">
                            {briefing.giving_breakdown.recent_contributions.map((contrib) => (
                              <div
                                key={contrib.contribution_id}
                                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                              >
                                <div className="flex-1">
                                  <p className="text-sm font-medium text-gray-900">
                                    {formatDate(contrib.contribution_date)}
                                  </p>
                                  <p className="text-xs text-gray-500">
                                    {contrib.contribution_type} • {contrib.payment_method}
                                    {contrib.recurring && ' • Recurring'}
                                  </p>
                                </div>
                                <p className="text-lg font-bold text-gray-900">
                                  {formatCurrency(contrib.amount)}
                                </p>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    </BriefingSection>

                    {/* Engagement Timeline */}
                    <BriefingSection
                      title="Engagement Timeline"
                      icon={Clock}
                      delay={200}
                    >
                      <div className="space-y-6">
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                          <StatCard
                            label="Total Interactions"
                            value={briefing.engagement_timeline.total_interactions}
                          />
                          <StatCard
                            label="Frequency"
                            value={briefing.engagement_timeline.interaction_frequency}
                          />
                          <StatCard
                            label="Last Contact"
                            value={
                              briefing.engagement_timeline.last_contact
                                ? formatDate(briefing.engagement_timeline.last_contact)
                                : 'N/A'
                            }
                          />
                          <StatCard
                            label="Email Count"
                            value={
                              briefing.engagement_timeline.by_type.find(
                                (t) => t.type === 'Email'
                              )?.count || 0
                            }
                          />
                        </div>

                        {/* Recent Interactions */}
                        <div>
                          <h4 className="text-sm font-medium text-gray-900 mb-4">
                            Recent Activity
                          </h4>
                          <div className="space-y-0">
                            {briefing.engagement_timeline.recent_interactions.map(
                              (interaction, index) => (
                                <TimelineItem
                                  key={interaction.interaction_id}
                                  date={formatDate(interaction.interaction_date)}
                                  type={interaction.interaction_type}
                                  title={interaction.interaction_type}
                                  description={interaction.notes || undefined}
                                  staffMember={interaction.staff_member || undefined}
                                  icon={getActionIcon(interaction.interaction_type.toLowerCase())}
                                />
                              )
                            )}
                          </div>
                        </div>
                      </div>
                    </BriefingSection>

                    {/* Segment Explanation */}
                    <BriefingSection
                      title="Segment Classification"
                      icon={Users}
                      delay={300}
                    >
                      <div className="space-y-4">
                        <div>
                          <div className="flex items-center gap-3 mb-2">
                            <Badge variant="info" className="text-base px-3 py-1">
                              {briefing.segment.name}
                            </Badge>
                          </div>
                          <p className="text-gray-700">{briefing.segment.description}</p>
                        </div>
                        <div>
                          <h4 className="text-sm font-medium text-gray-900 mb-3">
                            Segment Criteria
                          </h4>
                          <ul className="space-y-2">
                            {briefing.segment.criteria.map((criterion, index) => (
                              <li key={index} className="flex items-start gap-2">
                                <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                                <span className="text-sm text-gray-700">{criterion}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </BriefingSection>

                    {/* Suggested Actions */}
                    <BriefingSection
                      title="Suggested Actions"
                      icon={Target}
                      delay={400}
                    >
                      <div className="space-y-4">
                        {briefing.suggested_actions.map((action, index) => {
                          const ActionIcon = getActionIcon(action.type);
                          return (
                            <div
                              key={index}
                              className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 hover:shadow-sm transition-all"
                            >
                              <div className="flex items-start gap-4">
                                <div className="flex-shrink-0 w-12 h-12 bg-blue-50 rounded-lg flex items-center justify-center">
                                  <ActionIcon className="w-6 h-6 text-blue-600" />
                                </div>
                                <div className="flex-1">
                                  <div className="flex items-center gap-2 mb-2">
                                    <h4 className="font-semibold text-gray-900">
                                      {action.title}
                                    </h4>
                                    <Badge variant={getPriorityColor(action.priority)}>
                                      {action.priority} priority
                                    </Badge>
                                  </div>
                                  <p className="text-sm text-gray-700 mb-2">
                                    {action.description}
                                  </p>
                                  <div className="bg-blue-50 border border-blue-100 rounded p-3 mt-3">
                                    <p className="text-xs font-medium text-blue-900 mb-1">
                                      Why this action?
                                    </p>
                                    <p className="text-xs text-blue-700">{action.reasoning}</p>
                                  </div>
                                </div>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </BriefingSection>
                  </div>
                ) : null}
              </div>

              {/* Footer CTA */}
              {briefing && !loading && (
                <div className="flex-shrink-0 px-8 py-6 bg-white border-t border-gray-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600">
                        Ready to reach out to {briefing.constituent.first_name}?
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        Generate a personalized message based on this briefing
                      </p>
                    </div>
                    <button
                      onClick={handleGenerateMessage}
                      className="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors flex items-center gap-2 shadow-lg shadow-blue-600/30 hover:shadow-xl hover:shadow-blue-600/40"
                    >
                      <MessageSquare className="w-5 h-5" />
                      Generate Message
                    </button>
                  </div>
                </div>
              )}
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
};
