import { useState } from 'react'
import { FIELD_LIMITS } from '../../constants'

const GENDERS = [
  { value: 'male',   icon: '♂', label: 'Male' },
  { value: 'female', icon: '♀', label: 'Female' },
  { value: 'other',  icon: '◎', label: 'Prefer not to say' },
]

const blockNonInteger = e => ['.', '-', 'e', 'E', '+'].includes(e.key) && e.preventDefault()

function rangeError(field, value) {
  if (!value && value !== 0) return null
  const n = Number(value)
  const { min, max, label, unit } = FIELD_LIMITS[field]
  if (n < min) return `${label} minimum is ${min} ${unit}.`
  if (n > max) return `${label} maximum is ${max} ${unit}.`
  return null
}

export default function AboutYou({ data, update }) {
  const [touched, setTouched] = useState({})

  const handleChange = (field, value) => {
    setTouched(t => ({ ...t, [field]: true }))
    update({ [field]: value })
  }

  return (
    <div className="step-content">
      <p className="step-eyebrow">Step 1 of 5</p>
      <h1 className="step-title">About You</h1>
      <p className="step-subtitle">
        Your physical profile helps us calibrate the starting point and pacing of your gut training.
      </p>

      {/* Email */}
      <div className="field-group" style={{ marginBottom: 28 }}>
        <label className="field-label">Email address</label>
        <input
          className={`field-input${touched.email && (!data.email || !data.email.includes('@')) ? ' field-input--error' : ''}`}
          type="email"
          placeholder="you@example.com"
          value={data.email}
          onChange={e => handleChange('email', e.target.value)}
        />
        {touched.email && (!data.email || !data.email.includes('@')) && (
          <span className="field-error">Please enter a valid email address.</span>
        )}
      </div>

      {/* Biological sex */}
      <div style={{ marginBottom: 28 }}>
        <p className="field-label" style={{ marginBottom: 10 }}>Biological sex</p>
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
        {Object.keys(touched).length > 0 && !data.gender && (
          <p className="field-error" style={{ marginTop: 8 }}>Please select your biological sex to continue.</p>
        )}
      </div>

      {/* Age + Height + Weight */}
      <div className="input-row-3" style={{ marginBottom: 8 }}>
        <div className="field-group">
          <label className="field-label">Age</label>
          <div className="input-suffix-wrap">
            <input
              className={`field-input${touched.age && rangeError('age', data.age) ? ' field-input--error' : ''}`}
              type="number"
              min={FIELD_LIMITS.age.min} max={FIELD_LIMITS.age.max}
              placeholder="32"
              value={data.age}
              onKeyDown={blockNonInteger}
              onChange={e => handleChange('age', e.target.value)}
            />
            <span className="input-suffix">years</span>
          </div>
          {touched.age && rangeError('age', data.age) && (
            <span className="field-error">{rangeError('age', data.age)}</span>
          )}
        </div>

        <div className="field-group">
          <label className="field-label">Body Weight</label>
          <div className="input-suffix-wrap">
            <input
              className={`field-input${touched.body_weight_kg && rangeError('body_weight_kg', data.body_weight_kg) ? ' field-input--error' : ''}`}
              type="number"
              min={FIELD_LIMITS.body_weight_kg.min} max={FIELD_LIMITS.body_weight_kg.max}
              placeholder="70"
              value={data.body_weight_kg}
              onKeyDown={blockNonInteger}
              onChange={e => handleChange('body_weight_kg', e.target.value)}
            />
            <span className="input-suffix">kg</span>
          </div>
          {touched.body_weight_kg && rangeError('body_weight_kg', data.body_weight_kg) && (
            <span className="field-error">{rangeError('body_weight_kg', data.body_weight_kg)}</span>
          )}
        </div>

        <div className="field-group">
          <label className="field-label">Height</label>
          <div className="input-suffix-wrap">
            <input
              className={`field-input${touched.height_cm && rangeError('height_cm', data.height_cm) ? ' field-input--error' : ''}`}
              type="number"
              min={FIELD_LIMITS.height_cm.min} max={FIELD_LIMITS.height_cm.max}
              placeholder="178"
              value={data.height_cm}
              onKeyDown={blockNonInteger}
              onChange={e => handleChange('height_cm', e.target.value)}
            />
            <span className="input-suffix">cm</span>
          </div>
          {touched.height_cm && rangeError('height_cm', data.height_cm) && (
            <span className="field-error">{rangeError('height_cm', data.height_cm)}</span>
          )}
        </div>
      </div>
    </div>
  )
}
