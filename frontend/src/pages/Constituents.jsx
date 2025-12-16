import { useState, useEffect } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { constituentsAPI, segmentsAPI } from '../services/api'

export default function Constituents() {
  const [constituents, setConstituents] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [typeFilter, setTypeFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const location = useLocation()
  const navigate = useNavigate()
  const initialSegment = new URLSearchParams(location.search).get('segment') || ''
  const [segmentFilter, setSegmentFilter] = useState(initialSegment)
  const [segmentOptions, setSegmentOptions] = useState([])

  const loadConstituents = () => {
    setLoading(true)
    constituentsAPI
      .list({
        search: search || undefined,
        constituent_type: typeFilter || undefined,
        status: statusFilter || undefined,
        segment_id: segmentFilter || undefined,
      })
      .then((response) => setConstituents(response.data))
      .catch((error) => console.error('Error loading constituents:', error))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    loadConstituents()
  }, [search, typeFilter, statusFilter, segmentFilter])

  useEffect(() => {
    segmentsAPI
      .getDefinitions()
      .then((response) => setSegmentOptions(response.data))
      .catch((error) => console.error('Error loading segments:', error))
  }, [])

  useEffect(() => {
    const params = new URLSearchParams()
    if (segmentFilter) {
      params.set('segment', segmentFilter)
    }
    navigate({ pathname: '/constituents', search: params.toString() }, { replace: true })
  }, [segmentFilter, navigate])

  return (
    <div className="constituents">
      <div className="page-header">
        <h1>Constituents</h1>
      </div>

      <div className="filters">
        <input
          type="text"
          placeholder="Search by name or email..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="search-input"
        />
        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="filter-select"
        >
          <option value="">All Types</option>
          <option value="donor">Donor</option>
          <option value="volunteer">Volunteer</option>
          <option value="board_member">Board Member</option>
          <option value="staff">Staff</option>
          <option value="other">Other</option>
        </select>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="filter-select"
        >
          <option value="">All Statuses</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
        <select
          value={segmentFilter}
          onChange={(e) => setSegmentFilter(e.target.value)}
          className="filter-select"
        >
          <option value="">All Segments</option>
          {segmentOptions.map((segment) => (
            <option key={segment.segment_id} value={segment.segment_id}>
              {segment.name} ({segment.constituent_count})
            </option>
          ))}
        </select>
      </div>

      {loading ? (
        <div className="loading">Loading constituents...</div>
      ) : (
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Type</th>
                <th>Status</th>
                <th>Location</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {constituents.length > 0 ? (
                constituents.map((constituent) => (
                  <tr key={constituent.constituent_id}>
                    <td>
                      <Link
                        to={`/constituents/${constituent.constituent_id}`}
                        className="table-link"
                      >
                        {constituent.first_name} {constituent.last_name}
                      </Link>
                    </td>
                    <td>{constituent.email}</td>
                    <td>
                      <span className={`badge badge-${constituent.constituent_type}`}>
                        {constituent.constituent_type}
                      </span>
                    </td>
                    <td>
                      <span className={`status-${constituent.status}`}>
                        {constituent.status}
                      </span>
                    </td>
                    <td>
                      {constituent.city}, {constituent.state}
                    </td>
                    <td>
                      <Link
                        to={`/constituents/${constituent.constituent_id}`}
                        className="btn-link"
                      >
                        View
                      </Link>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="6" className="no-data">
                    No constituents found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
