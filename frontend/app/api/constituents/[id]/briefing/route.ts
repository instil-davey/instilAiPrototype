import { NextRequest, NextResponse } from 'next/server';
import { ConstituentBriefing } from '@/types/constituent';

// Mock data generator for demonstration
// In production, this would fetch from your Python backend
function generateMockBriefing(id: string): ConstituentBriefing {
  const constituentId = parseInt(id);

  // Mock constituent data
  const constituents = [
    {
      constituent_id: 1,
      first_name: 'Sarah',
      last_name: 'Chen',
      email: 'sarah.chen@email.com',
      phone: '555-0123',
      address: '123 Oak Street',
      city: 'San Francisco',
      state: 'CA',
      zip_code: '94102',
      constituent_type: 'Major Donor',
      total_lifetime_giving: 45000,
      created_date: '2020-03-15',
      created_at: '2020-03-15T10:00:00Z',
      updated_at: '2024-11-15T14:30:00Z',
    },
    {
      constituent_id: 2,
      first_name: 'Michael',
      last_name: 'Rodriguez',
      email: 'michael.r@email.com',
      phone: '555-0456',
      address: '456 Elm Avenue',
      city: 'Austin',
      state: 'TX',
      zip_code: '78701',
      constituent_type: 'Donor',
      total_lifetime_giving: 8500,
      created_date: '2021-06-20',
      created_at: '2021-06-20T09:00:00Z',
      updated_at: '2024-11-18T16:45:00Z',
    },
  ];

  const constituent = constituents.find(c => c.constituent_id === constituentId) || constituents[0];

  const briefing: ConstituentBriefing = {
    constituent,
    summary: `${constituent.first_name} ${constituent.last_name} is a ${constituent.constituent_type.toLowerCase()} who has been supporting our organization since ${new Date(constituent.created_date).getFullYear()}. They have shown consistent engagement through both financial contributions and active participation in our programs. Their giving pattern demonstrates a strong commitment to our mission, with a focus on annual campaigns and special initiatives. Recent interactions indicate continued interest in expanding their involvement, particularly in mentorship and advocacy opportunities.`,
    key_stats: {
      total_given: constituent.total_lifetime_giving,
      total_contributions: constituent.constituent_type === 'Major Donor' ? 23 : 12,
      total_interactions: constituent.constituent_type === 'Major Donor' ? 47 : 18,
      engagement_score: constituent.constituent_type === 'Major Donor' ? 92 : 78,
      donor_tenure: `${Math.floor((Date.now() - new Date(constituent.created_date).getTime()) / (1000 * 60 * 60 * 24 * 365))} years`,
    },
    giving_breakdown: {
      total_amount: constituent.total_lifetime_giving,
      contribution_count: constituent.constituent_type === 'Major Donor' ? 23 : 12,
      average_gift: constituent.total_lifetime_giving / (constituent.constituent_type === 'Major Donor' ? 23 : 12),
      largest_gift: constituent.constituent_type === 'Major Donor' ? 15000 : 2500,
      recent_contributions: [
        {
          contribution_id: 1,
          constituent_id: constituent.constituent_id,
          campaign_id: 1,
          contribution_date: '2024-10-15',
          amount: 5000,
          contribution_type: 'Donation',
          payment_method: 'Credit Card',
          recurring: false,
          dedication_name: null,
          dedication_type: null,
          acknowledgment_sent: true,
          created_at: '2024-10-15T10:00:00Z',
          updated_at: '2024-10-15T10:00:00Z',
        },
        {
          contribution_id: 2,
          constituent_id: constituent.constituent_id,
          campaign_id: 2,
          contribution_date: '2024-08-20',
          amount: 2500,
          contribution_type: 'Donation',
          payment_method: 'Check',
          recurring: false,
          dedication_name: null,
          dedication_type: null,
          acknowledgment_sent: true,
          created_at: '2024-08-20T10:00:00Z',
          updated_at: '2024-08-20T10:00:00Z',
        },
        {
          contribution_id: 3,
          constituent_id: constituent.constituent_id,
          campaign_id: 1,
          contribution_date: '2024-05-10',
          amount: 1000,
          contribution_type: 'Donation',
          payment_method: 'Credit Card',
          recurring: true,
          dedication_name: null,
          dedication_type: null,
          acknowledgment_sent: true,
          created_at: '2024-05-10T10:00:00Z',
          updated_at: '2024-05-10T10:00:00Z',
        },
      ],
      by_type: [
        { type: 'Donation', amount: constituent.total_lifetime_giving * 0.85, count: 20 },
        { type: 'Sponsorship', amount: constituent.total_lifetime_giving * 0.10, count: 2 },
        { type: 'Event', amount: constituent.total_lifetime_giving * 0.05, count: 1 },
      ],
      by_campaign: [
        { campaign_name: 'Annual Fund 2024', amount: constituent.total_lifetime_giving * 0.40, count: 8 },
        { campaign_name: 'Capital Campaign', amount: constituent.total_lifetime_giving * 0.35, count: 3 },
        { campaign_name: 'Emergency Relief', amount: constituent.total_lifetime_giving * 0.25, count: 12 },
      ],
    },
    engagement_timeline: {
      total_interactions: constituent.constituent_type === 'Major Donor' ? 47 : 18,
      recent_interactions: [
        {
          interaction_id: 1,
          constituent_id: constituent.constituent_id,
          interaction_date: '2024-11-10',
          interaction_type: 'Meeting',
          notes: 'Discussed upcoming capital campaign and potential major gift opportunity. Very enthusiastic about the new community center project.',
          staff_member: 'John Smith',
          created_at: '2024-11-10T14:00:00Z',
          updated_at: '2024-11-10T14:00:00Z',
        },
        {
          interaction_id: 2,
          constituent_id: constituent.constituent_id,
          interaction_date: '2024-10-15',
          interaction_type: 'Email',
          notes: 'Sent thank you note for recent contribution. Received warm response and request for quarterly impact report.',
          staff_member: 'Jane Doe',
          created_at: '2024-10-15T09:00:00Z',
          updated_at: '2024-10-15T09:00:00Z',
        },
        {
          interaction_id: 3,
          constituent_id: constituent.constituent_id,
          interaction_date: '2024-09-22',
          interaction_type: 'Event',
          notes: 'Attended annual gala. Brought two guests. Participated in live auction.',
          staff_member: 'Sarah Johnson',
          created_at: '2024-09-22T19:00:00Z',
          updated_at: '2024-09-22T19:00:00Z',
        },
        {
          interaction_id: 4,
          constituent_id: constituent.constituent_id,
          interaction_date: '2024-08-05',
          interaction_type: 'Phone Call',
          notes: 'Follow-up call regarding volunteer opportunities. Interested in mentorship program.',
          staff_member: 'John Smith',
          created_at: '2024-08-05T11:00:00Z',
          updated_at: '2024-08-05T11:00:00Z',
        },
      ],
      interaction_frequency: constituent.constituent_type === 'Major Donor' ? 'Weekly' : 'Monthly',
      last_contact: '2024-11-10',
      by_type: [
        { type: 'Email', count: 25 },
        { type: 'Phone Call', count: 12 },
        { type: 'Meeting', count: 8 },
        { type: 'Event', count: 5 },
      ],
    },
    segment: {
      name: constituent.constituent_type === 'Major Donor' ? 'High-Value Engaged Donors' : 'Active Supporters',
      description: constituent.constituent_type === 'Major Donor'
        ? 'Donors who have contributed $25,000+ lifetime and maintain regular engagement with the organization'
        : 'Regular donors who contribute consistently and show interest in organizational activities',
      criteria: constituent.constituent_type === 'Major Donor'
        ? [
            'Total lifetime giving > $25,000',
            'Active engagement in last 90 days',
            'Attended 2+ events in past year',
            'Responded to personal outreach',
          ]
        : [
            'Total lifetime giving > $5,000',
            'Made contribution in last 6 months',
            'Opened recent email communications',
          ],
    },
    suggested_actions: [
      {
        type: 'meeting',
        priority: 'high',
        title: 'Schedule Discovery Meeting',
        description: 'Set up a one-on-one meeting to discuss expanded giving opportunities',
        reasoning: `Based on recent positive interactions and ${constituent.first_name}'s expressed interest in the capital campaign, now is an ideal time to explore a larger gift commitment. Their engagement score of ${constituent.constituent_type === 'Major Donor' ? 92 : 78}% indicates strong organizational affinity.`,
      },
      {
        type: 'proposal',
        priority: 'high',
        title: 'Submit Capital Campaign Proposal',
        description: `Prepare customized proposal for $${constituent.constituent_type === 'Major Donor' ? '50,000' : '15,000'} gift`,
        reasoning: 'Their giving history and current capacity indicators suggest readiness for a significant commitment to the capital campaign.',
      },
      {
        type: 'thank-you',
        priority: 'medium',
        title: 'Send Personal Thank You',
        description: 'Executive director to send handwritten note acknowledging recent support',
        reasoning: 'Recent $5,000 contribution warrants high-touch stewardship to reinforce donor value and strengthen relationship.',
      },
    ],
    active_opportunities: [
      {
        opportunity_id: 1,
        constituent_id: constituent.constituent_id,
        opportunity_name: 'Capital Campaign - Community Center',
        opportunity_type: 'Major Gift',
        stage: 'Cultivation',
        expected_amount: constituent.constituent_type === 'Major Donor' ? 50000 : 15000,
        probability: 75,
        expected_close_date: '2025-03-31',
        description: 'Multi-year pledge for new community center construction',
        created_at: '2024-10-01T10:00:00Z',
        updated_at: '2024-11-15T14:00:00Z',
      },
    ],
  };

  return briefing;
}

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params;

    // In production, this would call your Python backend:
    // const response = await fetch(`http://backend:5000/api/constituents/${id}/briefing`);
    // const data = await response.json();

    // For now, return mock data
    const briefing = generateMockBriefing(id);

    return NextResponse.json(briefing);
  } catch (error) {
    console.error('Error fetching constituent briefing:', error);
    return NextResponse.json(
      { error: 'Failed to fetch constituent briefing' },
      { status: 500 }
    );
  }
}
