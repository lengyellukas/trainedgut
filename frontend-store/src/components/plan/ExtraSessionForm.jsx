import { useState } from 'react'
import { submitExtraSession } from '../../api/client'

const DURATIONS = [
  { value: '90min_to_2h', label: '90 min – 2 h' },
  { value: '2h_to_3h',    label: '2 – 3 h'      },
  { value: '3h_to_4h',    label: '3 – 4 h'      },
  { value: '4h_to_6h',    label: '4 – 6 h'      },
  { value: 'over_6h',     label: '6 h +'        },
]

const GI_OPTIONS = [
  { value: 0, label: 'None' },
  { value: 1, label: 'Mild' },
  { value: 2, label: 'Moderate' },
  { value: 3, label: 'Severe' },
]

export default function ExtraSessionForm({ email, weekNumber }) {
  const [open, setOpen] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)
  const [duration, setDuration] = useState('')
  const [smallGels, setSmallGels] = useState(0)
  const [largeGels, setLargeGels] = useState(0)
  const [giScale, setGiScale] = useState(0)

  function reset() {
    setOpen(false)
    setSubmitted(false)
    setDuration('')
    setSmallGels(0)
    setLargeGels(0)
    setGiScale(0)
    setError(null)
  }

  if (submitted) {
    return (
      <div className="extra-session-done">
        Unplanned session logged. <button className="extra-session-link" onClick={reset}>Log another</button>
      </div>
    )
  }

  if (!open) {
    return (
      <button className="extra-session-toggle" onClick={() => setOpen(true)}>
        + Log an unplanned session for this week
      </button>
    )
  }

  const valid = !!duration

  async function handleSubmit() {
    if (!valid) return
    setSubmitting(true)
    setError(null)
    try {
      await submitExtraSession({
        email,
        week_number: weekNumber,
        duration_option: duration,
        n_small_gels_consumed: Number(smallGels) || 0,
        n_large_gels_consumed: Number(largeGels) || 0,
        gi_scale: giScale,
      })
      setSubmitted(true)
    } catch {
      setError('Could not submit. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="extra-session-form">
      <div className="extra-session-header">
        <p className="feedback-title">Log unplanned session</p>
        <button className="extra-session-close" onClick={() => setOpen(false)}>×</button>
      </div>

      <div className="feedback-field">
        <p className="feedback-label">Duration</p>
        <div className="feedback-options">
          {DURATIONS.map(d => (
            <button
              key={d.value}
              className={`feedback-opt ${duration === d.value ? 'selected' : ''}`}
              onClick={() => setDuration(d.value)}
            >
              {d.label}
            </button>
          ))}
        </div>
      </div>

      <div className="extra-gel-row">
        <div className="extra-gel-field">
          <label className="feedback-label">Small gels consumed (25g)</label>
          <input
            type="number"
            className="extra-gel-input"
            min="0"
            value={smallGels}
            onChange={e => setSmallGels(e.target.value)}
          />
        </div>
        <div className="extra-gel-field">
          <label className="feedback-label">Large gels consumed (40g)</label>
          <input
            type="number"
            className="extra-gel-input"
            min="0"
            value={largeGels}
            onChange={e => setLargeGels(e.target.value)}
          />
        </div>
      </div>

      <div className="feedback-field">
        <p className="feedback-label">GI distress during the session?</p>
        <div className="feedback-options">
          {GI_OPTIONS.map(opt => (
            <button
              key={opt.value}
              className={`feedback-opt ${giScale === opt.value ? 'selected' : ''}`}
              onClick={() => setGiScale(opt.value)}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      {error && <p className="feedback-error">{error}</p>}

      <button className="feedback-submit" onClick={handleSubmit} disabled={submitting || !valid}>
        {submitting ? 'Submitting…' : 'Log session'}
      </button>
    </div>
  )
}
