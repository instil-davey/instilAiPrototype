export interface Constituent {
  constituent_id: number;
  first_name: string;
  last_name: string;
  email: string | null;
  phone: string | null;
  address: string | null;
  city: string | null;
  state: string | null;
  zip_code: string | null;
  constituent_type: string;
  total_lifetime_giving: number;
  created_date: string;
  created_at: string;
  updated_at: string;
}

export interface Contribution {
  contribution_id: number;
  constituent_id: number;
  campaign_id: number | null;
  contribution_date: string;
  amount: number;
  contribution_type: string;
  payment_method: string;
  recurring: boolean;
  dedication_name: string | null;
  dedication_type: string | null;
  acknowledgment_sent: boolean;
  created_at: string;
  updated_at: string;
}

export interface Interaction {
  interaction_id: number;
  constituent_id: number;
  interaction_date: string;
  interaction_type: string;
  notes: string | null;
  staff_member: string | null;
  created_at: string;
  updated_at: string;
}

export interface Opportunity {
  opportunity_id: number;
  constituent_id: number;
  opportunity_name: string;
  opportunity_type: string;
  stage: string;
  expected_amount: number | null;
  probability: number | null;
  expected_close_date: string | null;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export interface Segment {
  name: string;
  description: string;
  criteria: string[];
}

export interface GivingBreakdown {
  total_amount: number;
  contribution_count: number;
  average_gift: number;
  largest_gift: number;
  recent_contributions: Contribution[];
  by_type: {
    type: string;
    amount: number;
    count: number;
  }[];
  by_campaign: {
    campaign_name: string;
    amount: number;
    count: number;
  }[];
}

export interface EngagementTimeline {
  total_interactions: number;
  recent_interactions: Interaction[];
  interaction_frequency: string;
  last_contact: string | null;
  by_type: {
    type: string;
    count: number;
  }[];
}

export interface SuggestedAction {
  type: 'call' | 'email' | 'meeting' | 'proposal' | 'thank-you';
  priority: 'high' | 'medium' | 'low';
  title: string;
  description: string;
  reasoning: string;
}

export interface ConstituentBriefing {
  constituent: Constituent;
  summary: string;
  key_stats: {
    total_given: number;
    total_contributions: number;
    total_interactions: number;
    engagement_score: number;
    donor_tenure: string;
  };
  giving_breakdown: GivingBreakdown;
  engagement_timeline: EngagementTimeline;
  segment: Segment;
  suggested_actions: SuggestedAction[];
  active_opportunities: Opportunity[];
}
