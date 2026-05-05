const SPORTS = [
  { value: 'ironman',                   icon: '🏊', label: 'Ironman' },
  { value: 'half_ironman',              icon: '🚴', label: 'Half Ironman' },
  { value: 'triathlon_sprint_olympic',  icon: '🏅', label: 'Sprint / Olympic Tri' },
  { value: 'marathon',                  icon: '🏃', label: 'Marathon' },
  { value: 'ultra_trail',               icon: '⛰️', label: 'Ultra Trail' },
  { value: 'trail_running',             icon: '🌲', label: 'Trail Running' },
  { value: 'gran_fondo',                icon: '🚵', label: 'Gran Fondo' },
  { value: 'cycling_endurance',         icon: '🚴', label: 'Cycling Endurance' },
  { value: 'hyrox',                     icon: '🏋️', label: 'Hyrox' },
  { value: 'spartan',                   icon: '🛡️', label: 'Spartan Race' },
  { value: 'ocr',                       icon: '💪', label: 'OCR' },
  { value: 'duathlon',                  icon: '🔄', label: 'Duathlon' },
  { value: 'swimrun',                   icon: '🌊', label: 'Swimrun' },
]

const START_OPTIONS = [
  {
    value: 'immediately',
    icon: '⚡',
    label: 'Start immediately',
    desc: 'Begin gut training as soon as you receive your gels.',
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

  if (weeks < 4)  return { type: 'error',   text: `Only ${weeks} week(s) to your race — the minimum for gut training is 4 weeks. Please choose a different start or race date.` }
  if (weeks < 8)  return { type: 'warning', text: `${weeks} weeks until your race. A full protocol needs 8–16 weeks. Your plan will be compressed — results are possible but not guaranteed.` }
  if (weeks < 16) return { type: 'info',    text: `${weeks} weeks to go. You'll complete a solid protocol — a full 16 weeks is ideal, but this is workable.` }
  return null
}

export default function YourRace({ data, update }) {
  const warning = weeksWarning(data)

  return (
    <div className="step-content">
      <p className="step-eyebrow">Step 2 of 5</p>
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
              onClick={() => update({ sport_type: s.value })}
            >
              <span className="card-icon">{s.icon}</span>
              <span className="card-label">{s.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Race date + expected duration */}
      <div className="input-row" style={{ marginBottom: 28 }}>
        <div className="field-group">
          <label className="field-label">Race Date</label>
          <input
            className="field-input"
            type="date"
            value={data.race_date}
            min={new Date().toISOString().split('T')[0]}
            onChange={e => update({ race_date: e.target.value })}
          />
        </div>
        <div className="field-group">
          <label className="field-label">Expected Race Duration</label>
          <input
            className="field-input"
            type="number"
            min={0.5} max={30} step={0.5}
            placeholder="11.5"
            value={data.target_race_time_hours}
            onChange={e => update({ target_race_time_hours: e.target.value })}
          />
          <span className="field-hint">hours  (e.g. 11.5 for an Ironman)</span>
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
              onClick={() => update({ start_preference: o.value, preferred_start_date: null })}
            >
              <span className="card-icon">{o.icon}</span>
              <span className="card-text">
                <span className="card-label">{o.label}</span>
                <span className="card-desc">{o.desc}</span>
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Specific date picker */}
      {data.start_preference === 'specific_date' && (
        <div className="field-group" style={{ marginBottom: 16, maxWidth: 280 }}>
          <label className="field-label">Preferred Start Date</label>
          <input
            className="field-input"
            type="date"
            value={data.preferred_start_date || ''}
            min={new Date().toISOString().split('T')[0]}
            max={data.race_date || undefined}
            onChange={e => update({ preferred_start_date: e.target.value })}
          />
        </div>
      )}

      {/* Weeks warning */}
      {warning && (
        <div className={`alert alert-${warning.type}`}>{warning.text}</div>
      )}
    </div>
  )
}
