import WeekCard from './WeekCard'

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
}

function GelPackage({ pkg }) {
  return (
    <div className="gel-package">
      <div className="gel-package-title">Full Gel Package</div>
      <div className="gel-phase-row">
        <span className="gel-phase-name">Phase 1 — 100% glucose</span>
        <span className="gel-phase-count">
          {pkg.small_phase1_count}× small · {pkg.large_phase1_count}× large
        </span>
      </div>
      <div className="gel-phase-row">
        <span className="gel-phase-name">Phase 2 — 2:1 ratio</span>
        <span className="gel-phase-count">
          {pkg.small_phase2_count}× small · {pkg.large_phase2_count}× large
        </span>
      </div>
      <div className="gel-phase-row">
        <span className="gel-phase-name">Phase 3 — 1:0.8 ratio</span>
        <span className="gel-phase-count">
          {pkg.small_phase3_count}× small · {pkg.large_phase3_count}× large
        </span>
      </div>
      <div className="gel-total-row">
        <span className="gel-total-label">Total gels</span>
        <span className="gel-total-count">{pkg.total_gels}</span>
      </div>
    </div>
  )
}

function LockedWeeks({ weeks }) {
  if (weeks.length === 0) return null
  return (
    <div className="locked-weeks-section">
      <p className="section-heading">Weeks 2 – {weeks.length + 1}</p>
      <div className="locked-weeks-grid">
        {weeks.map(week => (
          <div key={week.week_number} className="locked-week-card">
            <div style={{ fontFamily: 'Bebas Neue, sans-serif', fontSize: 13, color: 'rgba(255,255,255,0.3)', marginBottom: 4 }}>
              Week {week.week_number}
            </div>
            <div style={{ fontFamily: 'Bebas Neue, sans-serif', fontSize: 18, color: 'white' }}>
              {new Date(week.start_date).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })}
            </div>
            <div style={{ fontSize: 13, color: 'var(--orange)', marginTop: 8 }}>
              {week.target_carbs_per_hour_g} g/hr
            </div>
          </div>
        ))}
      </div>
      <div className="locked-weeks-overlay">
        <span className="lock-icon">🔒</span>
        <div className="lock-title">{weeks.length} more weeks in your plan</div>
        <p className="lock-sub">
          Your full {weeks.length + 1}-week protocol — including every session, every gel, and your
          complete package — is ready. Unlock it to start training.
        </p>
        <button className="btn-unlock">Unlock full plan →</button>
      </div>
    </div>
  )
}

export default function PlanResult({ plan: response, onReset }) {
  if (!response) return null

  // Loading is handled by App, so here response is always set
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
  const [week1, ...lockedWeeks] = plan.weeks

  return (
    <div className="plan-shell">
      <div className="plan-topbar">
        <span className="plan-topbar-logo">TrainedGut</span>
        <button className="btn-reset" onClick={onReset}>← Start over</button>
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
          </div>
        </div>
      </div>

      <div className="plan-body">
        <p className="section-heading">Week 1 — Your first session</p>
        <WeekCard week={week1} />

        {lockedWeeks.length > 0 && <LockedWeeks weeks={lockedWeeks} />}

        <GelPackage pkg={plan.gel_package} />
      </div>
    </div>
  )
}
