function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })
}

function formatDuration(opt) {
  const map = { '90min_to_2h': '90 min–2 h', '2h_to_3h': '2–3 h', '3h_to_4h': '3–4 h', over_4h: '4 h+' }
  return map[opt] || opt
}

export default function WeekCard({ week }) {
  return (
    <div className="week-card">
      <div className="week-card-header">
        <div>
          <div className="week-number-label">Week {week.week_number}</div>
          <div className="week-dates">
            {formatDate(week.start_date)} – {formatDate(week.end_date)}
          </div>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          {week.is_consolidation && <span className="week-badge hold">Hold Week</span>}
        </div>
      </div>

      <div className="week-stats">
        <div className="week-stat">
          <div className="week-stat-label">Target</div>
          <div className="week-stat-value">
            {week.target_carbs_per_hour_g}
            <span className="week-stat-unit"> g/hr</span>
          </div>
        </div>
        <div className="week-stat">
          <div className="week-stat-label">Gel Ratio</div>
          <div style={{ fontSize: 13, color: 'var(--gold)', marginTop: 4, lineHeight: 1.3 }}>
            {week.gel_ratio}
          </div>
        </div>
        <div className="week-stat">
          <div className="week-stat-label">Sessions</div>
          <div className="week-stat-value">{week.sessions.length}</div>
        </div>
      </div>

      <div className="session-list">
        {week.sessions.map(session => (
          <div key={session.session_number} className="session-item">
            <div className="session-title">
              Session {session.session_number} · {formatDuration(session.duration_option)} ·{' '}
              {session.n_fueling_windows} gel intakes · {session.total_actual_carbs_g}g total
            </div>
            <table className="windows-table">
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Gels</th>
                  <th>Carbs</th>
                </tr>
              </thead>
              <tbody>
                {session.fueling_windows.map(w => (
                  <tr key={w.window_number}>
                    <td>T+{w.time_from_start_minutes} min</td>
                    <td>
                      {w.n_large_gels > 0 && (
                        <span className="gel-pill">{w.n_large_gels}× large (40g)</span>
                      )}
                      {w.n_small_gels > 0 && (
                        <span className="gel-pill">{w.n_small_gels}× small (25g)</span>
                      )}
                      {w.gel_count === 0 && <span style={{ opacity: 0.3 }}>—</span>}
                    </td>
                    <td>{w.actual_carbs_g}g</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ))}
      </div>
    </div>
  )
}
