import { useState, useEffect } from 'react'
import { contributionsAPI } from '../services/api'

export default function Contributions() {
  const [contributions, setContributions] = useState([])
  const [campaignStats, setCampaignStats] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      contributionsAPI.list({ limit: 50 }),
      contributionsAPI.getByCampaign(),
    ])
      .then(([contribRes, campaignRes]) => {
        setContributions(contribRes.data)
        setCampaignStats(campaignRes.data)
      })
      .catch((error) => console.error('Error loading contributions:', error))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="loading">Loading contributions...</div>

  const totalContributions = contributions.reduce(
    (sum, c) => sum + Number(c.amount),
    0
  )

  return (
    <div className="contributions">
      <div className="page-header">
        <h1>Contributions</h1>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Contributions</h3>
          <div className="stat-value">
            ${totalContributions.toLocaleString()}
          </div>
          <div className="stat-label">{contributions.length} gifts</div>
        </div>
        <div className="stat-card">
          <h3>Average Gift</h3>
          <div className="stat-value">
            ${(totalContributions / contributions.length || 0).toFixed(2)}
          </div>
        </div>
      </div>

      {campaignStats.length > 0 && (
        <div className="detail-card">
          <h2>Contributions by Campaign</h2>
          <table className="data-table">
            <thead>
              <tr>
                <th>Campaign</th>
                <th>Count</th>
                <th>Total</th>
                <th>Average</th>
              </tr>
            </thead>
            <tbody>
              {campaignStats.map((stat, index) => (
                <tr key={index}>
                  <td>{stat.campaign}</td>
                  <td>{stat.count}</td>
                  <td className="highlight">
                    ${Number(stat.total).toLocaleString()}
                  </td>
                  <td>${Number(stat.average).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="detail-card">
        <h2>Recent Contributions</h2>
        <table className="data-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Constituent ID</th>
              <th>Amount</th>
              <th>Type</th>
              <th>Campaign</th>
              <th>Appeal</th>
            </tr>
          </thead>
          <tbody>
            {contributions.length > 0 ? (
              contributions.map((contribution) => (
                <tr key={contribution.contribution_id}>
                  <td>
                    {new Date(contribution.contribution_date).toLocaleDateString()}
                  </td>
                  <td>{contribution.constituent_id}</td>
                  <td className="highlight">
                    ${Number(contribution.amount).toLocaleString()}
                  </td>
                  <td>{contribution.contribution_type}</td>
                  <td>{contribution.campaign || 'N/A'}</td>
                  <td>{contribution.appeal || 'N/A'}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="6" className="no-data">
                  No contributions found
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
