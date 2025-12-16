import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { dashboardAPI, segmentsAPI } from '../services/api'

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [recentActivity, setRecentActivity] = useState(null)
  const [loading, setLoading] = useState(true)
  const [segments, setSegments] = useState([])
  const navigate = useNavigate()

  useEffect(() => {
    Promise.all([
      dashboardAPI.getStats(),
      dashboardAPI.getRecentActivity(),
      segmentsAPI.getSuggestions({ limit: 4, per_segment: 4 }),
    ])
      .then(([statsRes, activityRes, segmentsRes]) => {
        setStats(statsRes.data)
        setRecentActivity(activityRes.data)
        setSegments(segmentsRes.data)
      })
      .catch((error) => console.error('Error loading dashboard:', error))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="loading">Loading dashboard...</div>

  return (
    <div className="dashboard">
      <h1>Dashboard</h1>

      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Constituents</h3>
          <div className="stat-value">{stats?.total_constituents || 0}</div>
          <div className="stat-label">
            {stats?.active_constituents || 0} active
          </div>
        </div>

        <div className="stat-card">
          <h3>Total Contributions</h3>
          <div className="stat-value">
            ${Number(stats?.total_contributions || 0).toLocaleString()}
          </div>
          <div className="stat-label">
            ${Number(stats?.contributions_this_year || 0).toLocaleString()} this
            year
          </div>
        </div>

        <div className="stat-card">
          <h3>Average Gift</h3>
          <div className="stat-value">
            ${Number(stats?.average_contribution || 0).toLocaleString()}
          </div>
        </div>

        <div className="stat-card">
          <h3>Open Opportunities</h3>
          <div className="stat-value">{stats?.open_opportunities || 0}</div>
          <div className="stat-label">
            ${Number(stats?.weighted_pipeline || 0).toLocaleString()} weighted
            value
          </div>
        </div>

        <div className="stat-card">
          <h3>This Month</h3>
          <div className="stat-value">
            ${Number(stats?.contributions_this_month || 0).toLocaleString()}
          </div>
          <div className="stat-label">Contributions</div>
        </div>

        <div className="stat-card">
          <h3>Recent Interactions</h3>
          <div className="stat-value">{stats?.recent_interactions || 0}</div>
          <div className="stat-label">Last 30 days</div>
        </div>
      </div>

      <div className="activity-section">
        <div className="activity-column">
          <h2>Recent Contributions</h2>
          <div className="activity-list">
            {recentActivity?.recent_contributions?.length > 0 ? (
              recentActivity.recent_contributions.map((contribution) => (
                <div key={contribution.id} className="activity-item">
                  <div className="activity-title">
                    {contribution.constituent_name}
                  </div>
                  <div className="activity-meta">
                    ${Number(contribution.amount).toLocaleString()} •{' '}
                    {new Date(contribution.date).toLocaleDateString()}
                  </div>
                </div>
              ))
            ) : (
              <p className="no-data">No recent contributions</p>
            )}
          </div>
        </div>

        <div className="activity-column">
          <h2>Recent Interactions</h2>
          <div className="activity-list">
            {recentActivity?.recent_interactions?.length > 0 ? (
              recentActivity.recent_interactions.map((interaction) => (
                <div key={interaction.id} className="activity-item">
                  <div className="activity-title">{interaction.subject}</div>
                  <div className="activity-meta">
                    {interaction.constituent_name} • {interaction.type} •{' '}
                    {new Date(interaction.date).toLocaleDateString()}
                  </div>
                </div>
              ))
            ) : (
              <p className="no-data">No recent interactions</p>
            )}
          </div>
        </div>
      </div>

      <div className="segment-section">
        <div className="segment-header">
          <h2>AI Segment Opportunities</h2>
          <p>Click a segment to jump to the prioritized constituent list.</p>
        </div>
        <div className="segment-grid">
          {segments.map((segment) => (
            <div
              key={segment.segment_id}
              className="segment-card"
              role="button"
              tabIndex={0}
              onClick={() => navigate(`/constituents?segment=${segment.segment_id}`)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  navigate(`/constituents?segment=${segment.segment_id}`)
                }
              }}
            >
              <div className="segment-card-header">
                <h3>{segment.name}</h3>
                <span className="segment-count">{segment.metrics.count || segment.constituents.length} constituents</span>
              </div>
              <p className="segment-description">{segment.description}</p>
              {segment.constituents?.length > 0 && (
                <ul className="segment-constituents">
                  {segment.constituents.slice(0, 3).map((constituent) => (
                    <li key={constituent.constituent_id}>
                      {constituent.name}
                      {constituent.metrics?.lifetime_giving
                        ? ` • $${Number(constituent.metrics.lifetime_giving).toLocaleString()}`
                        : ''}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
