import { useState } from 'react'
import DateInput from '../DateInput'

const SPORTS = [
  { value: 'triathlon',                 icon: '🏊', label: 'Triathlon' },
  { value: 'running',                   icon: '🏃', label: 'Running' },
  { value: 'cycling',                   icon: '🚴', label: 'Cycling' },
  { value: 'obstacle_race',             icon: '🛡️', label: 'Obstacle Race' },
  { value: 'duathlon',                  icon: '🔄', label: 'Duathlon' },
  { value: 'swimming',                  icon: '🌊', label: 'Swimming' },
]

const START_OPTIONS = [
  {
    value: 'immediately',
    icon: '⚡',
    label: 'Ship immediately',
    desc: 'We ship your gels right away. Your protocol starts when they arrive.',
  },
  {
    value: 'specific_date',
    icon: '📅',
    label: 'Specific date',
    desc: 'Choose the exact date you want to begin your protocol.',
  },
  {
    value: 'optimal',
    icon: '🎯',
    label: 'Optimal (recommended)',
    desc: 'We calculate the ideal start date to complete a full 16-week protocol before your race.',
  },
]

const DURATION_MIN = 0.5
const DURATION_MAX = 30

function durationError(value) {
  if (!value) return null
  const n = parseFloat(value)
  if (isNaN(n)) return null
  if (n < DURATION_MIN) return `Race duration minimum is ${DURATION_MIN} hours.`
  if (n > DURATION_MAX) return `Race duration maximum is ${DURATION_MAX} hours.`
  return null
}

function weeksWarning(data) {
  const { race_date, start_preference, preferred_start_date } = data
  if (!race_date) return null

  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const race = new Date(race_date)

  let start = today
  if (start_preference === 'specific_date' && preferred_start_date) {
    start = new Date(preferred_start_date)
  } else if (start_preference === 'optimal') {
    const optimal = new Date(race)
    optimal.setDate(optimal.getDate() - 16 * 7)
    start = optimal > today ? optimal : today
  }

  const weeks = Math.floor((race - start) / (7 * 24 * 60 * 60 * 1000))

  if (weeks < 4)  return { type: 'error',   text: `Only ${weeks} week(s) to your race - the minimum for gut training is 4 weeks. Please choose a different start or race date.` }
  if (weeks < 8)  return { type: 'warning', text: `${weeks} weeks until your race. A full protocol needs 8–16 weeks. Your plan will be compressed - results are possible but not guaranteed.` }
  if (weeks < 16) return { type: 'info',    text: `${weeks} weeks to go. You'll complete a solid protocol - a full 16 weeks is ideal, but this is workable.` }
  return null
}

export default function YourRace({ data, update, stepNumber, totalSteps }) {
  const [touched, setTouched] = useState({})
  const touch = field => setTouched(t => ({ ...t, [field]: true }))

  const anyTouched = Object.keys(touched).length > 0
  const warning = weeksWarning(data)

  return (
    <div className="step-content">
      <p className="step-eyebrow">Step {stepNumber} of {totalSteps}</p>
      <h1 className="step-title">Your Race</h1>
      <p className="step-subtitle">
        Tell us about your target event so we can align the protocol with your race day.
      </p>

      {/* Sport type */}
      <div style={{ marginBottom: 28 }}>
        <p className="field-label" style={{ marginBottom: 10 }}>Sport</p>
        <div className="option-grid cols-4">
          {SPORTS.map(s => (
            <button
              key={s.value}
              className={`option-card ${data.sport_type === s.value ? 'selected' : ''}`}
              onClick={() => { touch('sport_type'); update({ sport_type: s.value }) }}
            >
              <span className="card-icon">{s.icon}</span>
              <span className="card-label">{s.label}</span>
            </button>
          ))}
        </div>
        {anyTouched && !data.sport_type && (
          <p className="field-error" style={{ marginTop: 8 }}>Please select your sport to continue.</p>
        )}
      </div>

      {/* Race date + expected duration */}
      <div className="input-row" style={{ marginBottom: 28 }}>
        <div className="field-group">
          <label className="field-label">Race Date</label>
          <DateInput
            value={data.race_date}
            onChange={v => { touch('race_date'); update({ race_date: v }) }}
            minDate={new Date()}
          />
          {anyTouched && !data.race_date && (
            <span className="field-error">Please select your race date.</span>
          )}
        </div>
        <div className="field-group">
          <label className="field-label">Expected Race Duration</label>
          <div className="input-suffix-wrap">
            <input
              className={`field-input${touched.duration && durationError(data.target_race_time_hours) ? ' field-input--error' : ''}`}
              type="number"
              inputMode="decimal"
              min={DURATION_MIN} max={DURATION_MAX} step={0.1}
              placeholder="11.5"
              value={data.target_race_time_hours}
              onChange={e => { touch('duration'); update({ target_race_time_hours: e.target.value }) }}
              onBlur={e => {
                touch('duration')
                const v = parseFloat(e.target.value)
                if (!isNaN(v)) update({ target_race_time_hours: Math.round(v * 10) / 10 })
              }}
            />
            <span className="input-suffix">hours</span>
          </div>
          <span className="field-hint">e.g. 11.5 for an Ironman</span>
          {anyTouched && !data.target_race_time_hours && (
            <span className="field-error">Please enter your expected race duration.</span>
          )}
          {touched.duration && durationError(data.target_race_time_hours) && (
            <span className="field-error">{durationError(data.target_race_time_hours)}</span>
          )}
        </div>
      </div>

      {/* Start preference */}
      <div style={{ marginBottom: 16 }}>
        <p className="field-label" style={{ marginBottom: 10 }}>When do you want to start?</p>
        <div className="option-grid cols-3">
          {START_OPTIONS.map(o => (
            <button
              key={o.value}
              className={`option-card horizontal ${data.start_preference === o.value ? 'selected' : ''}`}
              onClick={() => { touch('start_preference'); update({ start_preference: o.value, preferred_start_date: null }) }}
            >
              <span className="card-icon">{o.icon}</span>
              <span className="card-text">
                <span className="card-label">{o.label}</span>
                <span className="card-desc">{o.desc}</span>
              </span>
            </button>
          ))}
        </div>
        {anyTouched && !data.start_preference && (
          <p className="field-error" style={{ marginTop: 8 }}>Please select when you want to start.</p>
        )}
      </div>

      {/* Specific date picker */}
      {data.start_preference === 'specific_date' && (
        <div className="field-group" style={{ marginBottom: 16, maxWidth: 280 }}>
          <label className="field-label">Preferred Start Date</label>
          <DateInput
            value={data.preferred_start_date}
            onChange={v => { touch('preferred_start_date'); update({ preferred_start_date: v }) }}
            minDate={new Date()}
            maxDate={data.race_date ? new Date(data.race_date) : undefined}
          />
          {touched.preferred_start_date && !data.preferred_start_date && (
            <span className="field-error">Please select your preferred start date.</span>
          )}
        </div>
      )}

      {/* Weeks warning */}
      {warning && (
        <div className={`alert alert-${warning.type}`}>{warning.text}</div>
      )}
    </div>
  )
}
