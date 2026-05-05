const GENDERS = [
  { value: 'male',   icon: '♂', label: 'Male' },
  { value: 'female', icon: '♀', label: 'Female' },
  { value: 'other',  icon: '◎', label: 'Other' },
]

export default function AboutYou({ data, update }) {
  return (
    <div className="step-content">
      <p className="step-eyebrow">Step 1 of 5</p>
      <h1 className="step-title">About You</h1>
      <p className="step-subtitle">
        Your physical profile helps us calibrate the starting point and pacing of your gut training.
      </p>

      {/* Gender */}
      <div style={{ marginBottom: 28 }}>
        <p className="field-label" style={{ marginBottom: 10 }}>Gender</p>
        <div className="option-grid cols-3">
          {GENDERS.map(g => (
            <button
              key={g.value}
              className={`option-card ${data.gender === g.value ? 'selected' : ''}`}
              onClick={() => update({ gender: g.value })}
            >
              <span className="card-icon">{g.icon}</span>
              <span className="card-label">{g.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Age + Height + Weight */}
      <div className="input-row-3" style={{ marginBottom: 8 }}>
        <div className="field-group">
          <label className="field-label">Age</label>
          <input
            className="field-input"
            type="number"
            min={16} max={85}
            placeholder="32"
            value={data.age}
            onChange={e => update({ age: e.target.value })}
          />
          <span className="field-hint">years</span>
        </div>

        <div className="field-group">
          <label className="field-label">Body Weight</label>
          <input
            className="field-input"
            type="number"
            min={40} max={150}
            step={0.5}
            placeholder="70"
            value={data.body_weight_kg}
            onChange={e => update({ body_weight_kg: e.target.value })}
          />
          <span className="field-hint">kg</span>
        </div>

        <div className="field-group">
          <label className="field-label">Height</label>
          <input
            className="field-input"
            type="number"
            min={140} max={220}
            placeholder="178"
            value={data.height_cm}
            onChange={e => update({ height_cm: e.target.value })}
          />
          <span className="field-hint">cm</span>
        </div>
      </div>
    </div>
  )
}
