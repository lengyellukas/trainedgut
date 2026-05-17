import { useState } from 'react'
import WeekCard from './WeekCard'
import { currentWeekIndex, daysUntil } from '../../utils/dateAware'

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
}

const PHASE_LABEL = {
  1: 'Phase 1 - 100% glucose',
  2: 'Phase 2 - 2:1 ratio',
  3: 'Phase 3 - 1:0.8 ratio',
}

function GelPackage({ pkg }) {
  // Group by phase for display
  const byPhase = { 1: [], 2: [], 3: [] }
  for (const item of pkg.items || []) {
    if (byPhase[item.ratio_phase]) byPhase[item.ratio_phase].push(item)
  }

  return (
    <div className="gel-package">
      <div className="gel-package-title">Full Gel Package</div>
      {[1, 2, 3].map(phase => (
        byPhase[phase].length > 0 && (
          <div key={phase} className="gel-phase-block">
            <div className="gel-phase-name">{PHASE_LABEL[phase]}</div>
            {byPhase[phase].map(item => (
              <div key={item.gel_id} className="gel-phase-row">
                <span className="gel-phase-product">
                  {item.brand} {item.size_label} ({item.carbs_g}g)
                </span>
                <span className="gel-phase-count">{item.quantity}×</span>
              </div>
            ))}
          </div>
        )
      ))}
      <div className="gel-total-row">
        <span className="gel-total-label">Total gels</span>
        <span className="gel-total-count">{pkg.total_gels}</span>
      </div>
    </div>
  )
}

export default function PlanResult({ plan: response, extraSessions = [], onExtrasChanged, onReset, onLogout, onCancel }) {
  const [weekIdx, setWeekIdx] = useState(() => currentWeekIndex(response?.plan?.weeks))

  if (!response) return null

  if (response.status === 'too_short') {
    return (
      <div className="plan-shell">
        <div className="plan-topbar">
          <span className="plan-topbar-logo">TrainedGut</span>
          <button className="btn-reset" onClick={onReset}>← Start over</button>
        </div>
        <div className="too-short-card">
          <div className="too-short-icon">⏱️</div>
          <div className="too-short-title">Not enough time</div>
          <p className="too-short-msg">{response.status_message}</p>
          <button className="btn-unlock" onClick={onReset}>← Adjust your details</button>
        </div>
      </div>
    )
  }

  const { plan } = response
  const totalWeeks = plan.weeks.length
  const week = plan.weeks[weekIdx]
  const todayWeekIdx = currentWeekIndex(plan.weeks)
  const isCurrentWeekDisplayed = weekIdx === todayWeekIdx
  const daysToRace = daysUntil(plan.race_date)

  return (
    <div className="plan-shell">
      <div className="plan-topbar">
        <span className="plan-topbar-logo">TrainedGut</span>
        <div style={{ display: 'flex', gap: 12 }}>
          <button className="btn-reset" onClick={onReset}>← Menu</button>
          {onLogout && <button className="btn-reset" onClick={onLogout}>Log out</button>}
        </div>
      </div>

      <div className="plan-header">
        {response.status === 'starts_late' && (
          <div className="plan-status-banner starts-late">
            {response.status_message}
          </div>
        )}

        <h1 className="plan-hero-title">
          Your<br /><span>plan</span><br />is ready
        </h1>

        <div className="plan-meta">
          <div className="plan-meta-item">
            <span className="plan-meta-label">Total weeks</span>
            <span className="plan-meta-value">{plan.total_weeks}</span>
          </div>
          <div className="plan-meta-item">
            <span className="plan-meta-label">Starting</span>
            <span className="plan-meta-value">{plan.starting_carbs_per_hour_g}<span className="plan-meta-unit"> g/hr</span></span>
          </div>
          <div className="plan-meta-item">
            <span className="plan-meta-label">Peak target</span>
            <span className="plan-meta-value">{plan.race_target_carbs_per_hour_g}<span className="plan-meta-unit"> g/hr</span></span>
          </div>
          <div className="plan-meta-item">
            <span className="plan-meta-label">Race date</span>
            <span className="plan-meta-value" style={{ fontSize: 18, marginTop: 4 }}>{formatDate(plan.race_date)}</span>
            {daysToRace > 0 && (
              <span className="plan-meta-sub">in {daysToRace} {daysToRace === 1 ? 'day' : 'days'}</span>
            )}
            {daysToRace === 0 && <span className="plan-meta-sub">race day!</span>}
            {daysToRace < 0 && <span className="plan-meta-sub">{-daysToRace} {-daysToRace === 1 ? 'day' : 'days'} ago</span>}
          </div>
        </div>
      </div>

      <div className="plan-body">
        <div className="week-nav">
          <button
            className="week-nav-btn"
            onClick={() => setWeekIdx(i => i - 1)}
            disabled={weekIdx === 0}
          >
            ← Prev
          </button>
          <span className="week-nav-label">
            Week {weekIdx + 1} of {totalWeeks}
            {isCurrentWeekDisplayed && <span className="week-nav-current"> · current</span>}
          </span>
          <button
            className="week-nav-btn"
            onClick={() => setWeekIdx(i => i + 1)}
            disabled={weekIdx === totalWeeks - 1}
          >
            Next →
          </button>
        </div>

        <WeekCard
          week={week}
          extraSessions={extraSessions.filter(es => es.week_number === week.week_number)}
          onExtrasChanged={onExtrasChanged}
        />

        <GelPackage pkg={plan.gel_package} />

        {onCancel && (
          <div className="plan-cancel-zone">
            <button className="btn-cancel-plan" onClick={onCancel}>
              End plan early
            </button>
            <p className="plan-cancel-hint">
              Ends the active plan and removes all session feedback and unplanned-session logs.
              You can then generate a new plan.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
