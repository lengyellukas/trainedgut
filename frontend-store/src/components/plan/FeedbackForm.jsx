import { useState } from 'react'
import { submitFeedback } from '../../api/client'

const CONSUMED_OPTIONS = [
  { value: 'less',       label: 'Less than planned', ratio: 0.5 },
  { value: 'as_planned', label: 'As planned',        ratio: 1.0 },
  { value: 'more',       label: 'More than planned', ratio: 1.5 },
]

const GI_OPTIONS = [
  { value: 0, label: 'None' },
  { value: 1, label: 'Mild' },
  { value: 2, label: 'Moderate' },
  { value: 3, label: 'Severe' },
]

export default function FeedbackForm({ email, weekNumber, sessionNumber }) {
  const [open, setOpen] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)
  const [consumedVsPlan, setConsumedVsPlan] = useState('as_planned')
  const [giScale, setGiScale] = useState(0)

  if (submitted) {
    return <div className="feedback-done">Feedback submitted. Thank you!</div>
  }

  if (!open) {
    return (
      <button className="feedback-toggle" onClick={() => setOpen(true)}>
        + Leave feedback for this session
      </button>
    )
  }

  async function handleSubmit() {
    setSubmitting(true)
    setError(null)
    const consumed = CONSUMED_OPTIONS.find(o => o.value === consumedVsPlan)
    try {
      await submitFeedback({
        email,
        week_number: weekNumber,
        session_number: sessionNumber,
        consumed_vs_plan: consumedVsPlan,
        consumed_ratio: consumed.ratio,
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
    <div className="feedback-form">
      <p className="feedback-title">Session feedback</p>

      <div className="feedback-field">
        <p className="feedback-label">How much did you take?</p>
        <div className="feedback-options">
          {CONSUMED_OPTIONS.map(opt => (
            <button
              key={opt.value}
              className={`feedback-opt ${consumedVsPlan === opt.value ? 'selected' : ''}`}
              onClick={() => setConsumedVsPlan(opt.value)}
            >
              {opt.label}
            </button>
          ))}
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

      <button className="feedback-submit" onClick={handleSubmit} disabled={submitting}>
        {submitting ? 'Submitting…' : 'Submit'}
      </button>
    </div>
  )
}
