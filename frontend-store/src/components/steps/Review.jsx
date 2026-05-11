const SPORT_LABELS = {
  triathlon: 'Triathlon',
  running: 'Running',
  cycling: 'Cycling',
obstacle_race: 'Obstacle Race',duathlon: 'Duathlon', swimming: 'Swimming',
}
const GENDER_LABELS     = { male: 'Male', female: 'Female', other: 'Prefer not to say' }
const START_LABELS      = { immediately: 'Ship immediately', specific_date: 'Specific date', optimal: 'Optimal (16 wks before race)' }
const CARB_LABELS       = {
  never_used: "Don't use gels",
  occasional_one_gel: 'Occasional - 1 gel (~20 g/hr)',
  regular_one_two: 'Regular - 1–2 gels (~45 g/hr)',
  comfortable_two_plus: 'Comfortable - 2+ gels (~70 g/hr)',
}
const GI_LABELS         = { none: 'No GI issues', occasional: 'Occasional issues', frequent: 'Frequent issues' }
const DURATION_LABELS   = { '90min_to_2h': '90 min–2 h', '2h_to_3h': '2–3 h', '3h_to_4h': '3–4 h', '4h_to_6h': '4–6 h', over_6h: '6 h+' }

function Row({ label, value }) {
  return (
    <div className="review-row">
      <span className="review-key">{label}</span>
      <span className="review-val">{value || '-'}</span>
    </div>
  )
}

export default function Review({ data, onGenerate, loading, error }) {
  const sessions = data.long_sessions.map((s, i) =>
    `Session ${i + 1}: ${DURATION_LABELS[s.duration_option] || '-'}`
  ).join(' · ')

  return (
    <div className="step-content">
      <p className="step-eyebrow">Step 5 of 5</p>
      <h1 className="step-title">Review</h1>
      <p className="step-subtitle">
        Everything looks right? Generate your personalised protocol below.
      </p>

      <div className="review-grid">
        <div className="review-block">
          <p className="review-section-label">About You</p>
          <Row label="Biological sex"  value={GENDER_LABELS[data.gender]} />
          <Row label="Age"     value={data.age ? `${data.age} yrs` : null} />
          <Row label="Weight"  value={data.body_weight_kg ? `${data.body_weight_kg} kg` : null} />
          <Row label="Height"  value={data.height_cm ? `${data.height_cm} cm` : null} />
        </div>

        <div className="review-block">
          <p className="review-section-label">Your Race</p>
          <Row label="Sport"     value={SPORT_LABELS[data.sport_type]} />
          <Row label="Race date" value={data.race_date} />
          <Row label="Duration"  value={data.target_race_time_hours ? `${data.target_race_time_hours} h` : null} />
          <Row label="Start"     value={
            data.start_preference === 'specific_date' && data.preferred_start_date
              ? `${START_LABELS[data.start_preference]} · ${data.preferred_start_date}`
              : START_LABELS[data.start_preference]
          } />
        </div>

        <div className="review-block">
          <p className="review-section-label">Your Training</p>
          {data.long_sessions.map((s, i) => (
            <Row key={i} label={`Session ${i + 1}`} value={DURATION_LABELS[s.duration_option]} />
          ))}
        </div>

        <div className="review-block">
          <p className="review-section-label">Your Fueling</p>
          <Row label="Current intake" value={CARB_LABELS[data.carb_tolerance_option]} />
          <Row label="GI history"     value={GI_LABELS[data.gi_history]} />
        </div>
      </div>

      {error && <div className="alert alert-error" style={{ marginBottom: 16 }}>{error}</div>}

      <button className="btn-generate" onClick={onGenerate} disabled={loading}>
        {loading ? 'Building your plan…' : 'Generate my plan →'}
      </button>
      <p className="generate-note">
        Week 1 is shown immediately · Full plan unlocked after purchase
      </p>
    </div>
  )
}
