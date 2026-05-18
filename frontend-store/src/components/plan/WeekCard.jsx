import FeedbackForm from './FeedbackForm'
import ExtraSessionForm from './ExtraSessionForm'
import { isWeekCurrent, isWeekFuture } from '../../utils/dateAware'

const SMALL_GEL_CARBS = 25
const LARGE_GEL_CARBS = 40

const GI_LABELS = { 0: 'No GI distress', 1: 'Mild GI', 2: 'Moderate GI', 3: 'Severe GI' }

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })
}

function formatDuration(opt) {
  const map = {
    '90min_to_2h': '90 min–2 h',
    '2h_to_3h':    '2–3 h',
    '3h_to_4h':    '3–4 h',
    '4h_to_6h':    '4–6 h',
    'over_6h':     '6 h+',
  }
  return map[opt] || opt
}

function formatLoggedAt(iso) {
  return new Date(iso).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })
}

function formatStartDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('en-GB', { weekday: 'short', day: 'numeric', month: 'short' })
}

function gelDisplayName(g) {
  return g.product_name || `${g.brand} ${g.size_label}`
}

function aggregateWeekGels(week) {
  // Sum gel quantities across all sessions + fueling windows in this week,
  // grouped by gel_id (or fallback) so each product appears once.
  const byKey = new Map()
  for (const session of week.sessions || []) {
    for (const w of session.fueling_windows || []) {
      for (const g of (w.gels || [])) {
        const key = g.gel_id || `${g.brand}|${g.carbs_g}|${g.size_label}`
        const existing = byKey.get(key)
        if (existing) existing.quantity += g.quantity
        else byKey.set(key, { ...g })
      }
    }
  }
  return Array.from(byKey.values()).sort((a, b) => a.carbs_g - b.carbs_g)
}

export default function WeekCard({ week, extraSessions = [], onExtrasChanged }) {
  const isCurrent = isWeekCurrent(week)
  const isFuture = isWeekFuture(week)
  const weekGels = aggregateWeekGels(week)
  const weekTotal = weekGels.reduce((s, g) => s + g.quantity, 0)

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
          {isCurrent && <span className="week-badge current">Current</span>}
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

      {weekGels.length > 0 && (
        <div className="week-gels">
          <p className="week-gels-title">Gels you'll need this week ({weekTotal})</p>
          <ul className="week-gels-list">
            {weekGels.map(g => (
              <li key={g.gel_id || `${g.brand}-${g.carbs_g}-${g.size_label}`}>
                <span className="week-gels-qty">{g.quantity}×</span>
                <span className="week-gels-product">{gelDisplayName(g)} <span className="week-gels-carbs">({g.carbs_g}g)</span></span>
              </li>
            ))}
          </ul>
        </div>
      )}

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
                  <th>Target</th>
                  <th>Actual</th>
                </tr>
              </thead>
              <tbody>
                {session.fueling_windows.map(w => (
                  <tr key={w.window_number}>
                    <td>T+{w.time_from_start_minutes} min</td>
                    <td>
                      {(w.gels || []).map((g, i) => (
                        <span key={i} className="gel-pill">
                          {g.quantity}× {gelDisplayName(g)} ({g.carbs_g}g)
                        </span>
                      ))}
                      {(!w.gels || w.gels.length === 0) && <span style={{ opacity: 0.3 }}>—</span>}
                    </td>
                    <td>{w.target_carbs_g}g</td>
                    <td>
                      {w.actual_carbs_g}g
                      {w.overshoot_g > 0 && (
                        <span className="overshoot-pill" title={`${w.overshoot_g}g over target due to whole-gel sizing`}>
                          +{w.overshoot_g}
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            <FeedbackForm
              weekNumber={week.week_number}
              sessionNumber={session.session_number}
              disabled={isFuture}
              availableAfter={isFuture ? formatStartDate(week.start_date) : null}
            />
          </div>
        ))}

        {extraSessions.length > 0 && (
          <div className="unplanned-list">
            <p className="unplanned-list-title">Unplanned sessions ({extraSessions.length})</p>
            {extraSessions.map(es => {
              const totalCarbs = es.n_small_gels_consumed * SMALL_GEL_CARBS + es.n_large_gels_consumed * LARGE_GEL_CARBS
              return (
                <div key={es.id} className="unplanned-item">
                  <div className="unplanned-row">
                    <span className="unplanned-badge">UNPLANNED</span>
                    <span className="unplanned-duration">{formatDuration(es.duration_option)}</span>
                    <span className="unplanned-logged">logged {formatLoggedAt(es.submitted_at)}</span>
                  </div>
                  <div className="unplanned-meta">
                    {es.n_large_gels_consumed > 0 && (
                      <span className="gel-pill">{es.n_large_gels_consumed}× large (40g)</span>
                    )}
                    {es.n_small_gels_consumed > 0 && (
                      <span className="gel-pill">{es.n_small_gels_consumed}× small (25g)</span>
                    )}
                    <span className="unplanned-carbs">{totalCarbs}g total</span>
                    <span className="unplanned-gi">· {GI_LABELS[es.gi_scale] ?? es.gi_scale}</span>
                  </div>
                </div>
              )
            })}
          </div>
        )}

        <div className="extra-session-wrap">
          <ExtraSessionForm
            weekNumber={week.week_number}
            onAdded={onExtrasChanged}
            disabled={isFuture}
            availableAfter={isFuture ? formatStartDate(week.start_date) : null}
          />
        </div>
      </div>
    </div>
  )
}
