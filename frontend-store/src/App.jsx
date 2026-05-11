import { useState, useCallback } from 'react'
import StepIndicator from './components/StepIndicator'
import AboutYou from './components/steps/AboutYou'
import YourRace from './components/steps/YourRace'
import YourTraining from './components/steps/YourTraining'
import YourFueling from './components/steps/YourFueling'
import Review from './components/steps/Review'
import PlanResult from './components/plan/PlanResult'
import { generatePlan } from './api/client'
import { FIELD_LIMITS } from './constants'
import './styles/form.css'
import './styles/plan.css'

const STEPS = [
  { id: 'about',    label: 'About You' },
  { id: 'race',     label: 'Your Race' },
  { id: 'training', label: 'Training' },
  { id: 'fueling',  label: 'Fueling' },
  { id: 'review',   label: 'Review' },
]

const INITIAL_DATA = {
  // About You (height/gender are frontend-only 3 not sent to backend)
  gender: '',
  age: '',
  height_cm: '',
  body_weight_kg: '',
  // Your Race
  sport_type: '',
  race_date: '',
  target_race_time_hours: '',
  start_preference: '',
  preferred_start_date: null,
  // Your Training
  long_sessions: [{ duration_option: '' }],
  // Your Fueling
  carb_tolerance_option: '',
  gi_history: '',
}

function isStepValid(step, data) {
  switch (step) {
    case 0:
      return (
        !!data.gender &&
        Number(data.age) >= FIELD_LIMITS.age.min && Number(data.age) <= FIELD_LIMITS.age.max &&
        Number(data.body_weight_kg) >= FIELD_LIMITS.body_weight_kg.min && Number(data.body_weight_kg) <= FIELD_LIMITS.body_weight_kg.max &&
        Number(data.height_cm) >= FIELD_LIMITS.height_cm.min && Number(data.height_cm) <= FIELD_LIMITS.height_cm.max
      )
    case 1:
      if (!data.sport_type || !data.race_date || !data.target_race_time_hours || !data.start_preference) return false
      if (data.start_preference === 'specific_date' && !data.preferred_start_date) return false
      return true
    case 2:
      return data.long_sessions.length >= 1 && data.long_sessions.every(s => !!s.duration_option)
    case 3:
      return !!data.carb_tolerance_option && !!data.gi_history
    case 4:
      return true
    default:
      return true
  }
}

export default function App() {
  const [step, setStep] = useState(0)
  const [data, setData] = useState(INITIAL_DATA)
  const [plan, setPlan] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const update = useCallback(fields => setData(prev => ({ ...prev, ...fields })), [])
  const next = useCallback(() => setStep(s => Math.min(s + 1, STEPS.length - 1)), [])
  const back = useCallback(() => setStep(s => Math.max(s - 1, 0)), [])

  async function handleGenerate() {
    setLoading(true)
    setError(null)
    try {
      const result = await generatePlan(data)
      setPlan(result)
    } catch (err) {
      setError('Could not reach the server. Make sure the backend is running on localhost:8000.')
    } finally {
      setLoading(false)
    }
  }

  function handleReset() {
    setPlan(null)
    setStep(0)
    setData(INITIAL_DATA)
  }

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="spinner" />
        <div className="loading-title">Building your plan…</div>
        <div className="loading-sub">Calculating your week-by-week protocol</div>
      </div>
    )
  }

  if (plan) {
    return <PlanResult plan={plan} onReset={handleReset} />
  }

  const stepComponents = [
    <AboutYou data={data} update={update} />,
    <YourRace data={data} update={update} />,
    <YourTraining data={data} update={update} />,
    <YourFueling data={data} update={update} />,
    <Review data={data} onGenerate={handleGenerate} loading={loading} error={error} />,
  ]

  const isLast = step === STEPS.length - 1
  const valid = isStepValid(step, data)

  return (
    <div className="store-shell">
      <header className="store-header">
        <span className="store-logo">Trained<span>Gut</span></span>
        <StepIndicator steps={STEPS} current={step} />
      </header>

      <main className="store-main">
        {stepComponents[step]}
      </main>

      {!isLast && (
        <footer className="store-footer">
          {step > 0 && (
            <button className="btn-back" onClick={back}>← Back</button>
          )}
          <button className="btn-next" onClick={next} disabled={!valid}>
            {step === STEPS.length - 2 ? 'Review →' : 'Next →'}
          </button>
        </footer>
      )}
    </div>
  )
}
