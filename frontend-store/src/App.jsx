import { useState, useCallback, useEffect } from 'react'
import StepIndicator from './components/StepIndicator'
import AboutYou from './components/steps/AboutYou'
import YourRace from './components/steps/YourRace'
import YourTraining from './components/steps/YourTraining'
import YourFueling from './components/steps/YourFueling'
import YourGels from './components/steps/YourGels'
import Review from './components/steps/Review'
import PlanResult from './components/plan/PlanResult'
import AuthScreen from './components/AuthScreen'
import MainMenu from './components/MainMenu'
import ProfileView from './components/ProfileView'
import { generatePlan, getMe, getExtraSessions, getActivePlan, deleteActivePlan, emailActivePlan } from './api/client'
import { FIELD_LIMITS } from './constants'
import { supabase } from './supabase'
import './styles/form.css'
import './styles/plan.css'

const STEPS = [
  { id: 'about',    label: 'About You' },
  { id: 'race',     label: 'Your Race' },
  { id: 'training', label: 'Training' },
  { id: 'fueling',  label: 'Fueling' },
  { id: 'gels',     label: 'Gels' },
  { id: 'review',   label: 'Review' },
]

const INITIAL_DATA = {
  // About You (height/gender are frontend-only - not sent to backend)
  //TODO: send them to backend so they might be eventually used based on czech nutrionist
  gender: '',
  birth_year: '',
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
  market: '',
  gel_brand: 'trainedgut',
}

function isStepValid(step, data) {
  switch (step) {
    case 0:
      return (
        !!data.gender &&
        Number(data.birth_year) >= FIELD_LIMITS.birth_year.min && Number(data.birth_year) <= FIELD_LIMITS.birth_year.max &&
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
      return !!data.market && !!data.gel_brand
    case 5:
      return true
    default:
      return true
  }
}

export default function App() {
  const [view, setView] = useState('menu')        // 'menu' | 'form' | 'plan' | 'profile'
  const [step, setStep] = useState(0)
  const [data, setData] = useState(INITIAL_DATA)
  const [plan, setPlan] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [session, setSession] = useState(null)
  const [authLoading, setAuthLoading] = useState(true)
  const [extraSessions, setExtraSessions] = useState([])
  const [profile, setProfile] = useState(null)
  const [toast, setToast] = useState(null)   // { message, kind: 'success'|'error' } | null
  const [confirm, setConfirm] = useState(null) // { title, message, confirmLabel, danger, onConfirm, onCancel } | null

  function showToast(message, kind = 'success') {
    setToast({ message, kind })
    window.setTimeout(() => setToast(null), 4000)
  }

  function showConfirm({ title, message, confirmLabel = 'Confirm', cancelLabel = 'Cancel', danger = false }) {
    return new Promise(resolve => {
      setConfirm({
        title, message, confirmLabel, cancelLabel, danger,
        onConfirm: () => { setConfirm(null); resolve(true) },
        onCancel:  () => { setConfirm(null); resolve(false) },
      })
    })
  }

  // ESC cancels an open confirm dialog
  useEffect(() => {
    if (!confirm) return
    const onKey = e => { if (e.key === 'Escape') confirm.onCancel() }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [confirm])

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)
      setAuthLoading(false)
    })
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, newSession) => {
      setSession(newSession)
    })
    return () => subscription.unsubscribe()
  }, [])

  // After login, ping /me so the backend lazy-creates the athlete row,
  // then restore the active plan and any logged extras
  useEffect(() => {
    if (!session) return
    refreshProfile()
    refreshExtraSessions()
    getActivePlan()
      .then(p => { if (p) setPlan(p) })
      .catch(err => console.error('getActivePlan failed:', err))
  }, [session?.user?.id])

  async function refreshProfile() {
    try {
      setProfile(await getMe())
    } catch (err) {
      console.error('getMe failed:', err)
    }
  }

  async function refreshExtraSessions() {
    try {
      setExtraSessions(await getExtraSessions())
    } catch (err) {
      console.error('getExtraSessions failed:', err)
    }
  }

  async function handleLogout() {
    await supabase.auth.signOut()
    setPlan(null)
    setProfile(null)
    setExtraSessions([])
    setStep(0)
    setData(INITIAL_DATA)
    setView('menu')
  }

  function handleMenuSelect(target) {
    if (target === 'form') setStep(0)
    setView(target)
  }

  function goToMenu() {
    setView('menu')
  }

  async function handleEmailPlan(weekNumber = null) {
    try {
      const result = await emailActivePlan({ weekNumber })
      const what = weekNumber != null ? `Week ${weekNumber}` : 'Full plan'
      showToast(`${what} emailed to ${result.email}. Check your inbox.`, 'success')
    } catch (err) {
      showToast(`Could not send the email. ${err.message || ''}`, 'error')
    }
  }

  async function handleCancelPlan() {
    const ok = await showConfirm({
      title: 'End plan early?',
      message: 'All sessions, feedback and unplanned-session logs for this plan will be permanently removed. You can generate a new plan afterwards.',
      confirmLabel: 'End plan',
      danger: true,
    })
    if (!ok) return
    try {
      await deleteActivePlan()
      setPlan(null)
      setExtraSessions([])
      setView('menu')
    } catch (err) {
      showToast(`Could not cancel the plan. ${err.message || ''}`, 'error')
    }
  }

  const update = useCallback(fields => setData(prev => ({ ...prev, ...fields })), [])
  const next = useCallback(() => setStep(s => Math.min(s + 1, STEPS.length - 1)), [])
  const back = useCallback(() => setStep(s => Math.max(s - 1, 0)), [])

  // Enter key advances to next step (when valid and not on the Review step)
  useEffect(() => {
    if (view !== 'form') return
    const isLastStep = step === STEPS.length - 1
    if (isLastStep || !isStepValid(step, data)) return

    function onKey(e) {
      if (e.key !== 'Enter' || e.repeat) return
      if (e.target.tagName === 'TEXTAREA' || e.target.tagName === 'BUTTON') return
      if (e.target.closest('.react-datepicker, .react-datepicker__input-container')) return
      e.preventDefault()
      next()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [view, step, data, next])

  async function handleGenerate() {
    setLoading(true)
    setError(null)
    try {
      const result = await generatePlan(data)
      if (result.status === 'too_short' || !result.plan) {
        // Backend refused to build a plan — keep the user on Review with a clear message
        setError(result.status_message || 'Plan could not be generated.')
        return
      }
      setPlan(result)
      setView('plan')
      refreshExtraSessions()
      refreshProfile()
    } catch (err) {
      setError(`Could not generate the plan. ${err.message || 'Unknown error.'}`)
    } finally {
      setLoading(false)
    }
  }


  const toastEl = toast && (
    <div className={`toast toast--${toast.kind}`} role="status" aria-live="polite">
      <span className="toast-msg">{toast.message}</span>
      <button className="toast-close" onClick={() => setToast(null)} aria-label="Dismiss">×</button>
    </div>
  )

  const confirmEl = confirm && (
    <div className="confirm-backdrop" onMouseDown={confirm.onCancel} role="dialog" aria-modal="true">
      <div className="confirm-dialog" onMouseDown={e => e.stopPropagation()}>
        <h3 className="confirm-title">{confirm.title}</h3>
        <p className="confirm-message">{confirm.message}</p>
        <div className="confirm-actions">
          <button className="confirm-btn confirm-btn--cancel" onClick={confirm.onCancel}>
            {confirm.cancelLabel}
          </button>
          <button
            className={`confirm-btn ${confirm.danger ? 'confirm-btn--danger' : 'confirm-btn--primary'}`}
            onClick={confirm.onConfirm}
            autoFocus
          >
            {confirm.confirmLabel}
          </button>
        </div>
      </div>
    </div>
  )

  const overlays = (<>{toastEl}{confirmEl}</>)

  if (authLoading) {
    return (
      <>
        <div className="loading-screen"><div className="spinner" /></div>
        {overlays}
      </>
    )
  }

  if (!session) {
    return <>{<AuthScreen />}{overlays}</>
  }

  if (loading) {
    return (
      <>
        <div className="loading-screen">
          <div className="spinner" />
          <div className="loading-title">Building your plan…</div>
          <div className="loading-sub">Calculating your week-by-week protocol</div>
        </div>
        {overlays}
      </>
    )
  }

  if (view === 'menu') {
    return (
      <>
        <MainMenu
          email={session.user.email}
          hasPlan={!!plan}
          onSelect={handleMenuSelect}
          onLogout={handleLogout}
        />
        {overlays}
      </>
    )
  }

  if (view === 'profile') {
    return (
      <>
        <ProfileView
          email={session.user.email}
          profile={profile}
          onProfileChange={setProfile}
          onShowToast={showToast}
          onBack={goToMenu}
          onLogout={handleLogout}
        />
        {overlays}
      </>
    )
  }

  if (view === 'plan') {
    return (
      <>
        <PlanResult
          plan={plan}
          extraSessions={extraSessions}
          onExtrasChanged={refreshExtraSessions}
          onReset={goToMenu}
          onLogout={handleLogout}
          onCancel={handleCancelPlan}
          onEmail={handleEmailPlan}
        />
        {overlays}
      </>
    )
  }

  // view === 'form'
  const totalSteps = STEPS.length
  const stepProps = { data, update, stepNumber: step + 1, totalSteps }
  const stepComponents = [
    <AboutYou {...stepProps} />,
    <YourRace {...stepProps} />,
    <YourTraining {...stepProps} />,
    <YourFueling {...stepProps} />,
    <YourGels {...stepProps} />,
    <Review {...stepProps} onGenerate={handleGenerate} loading={loading} error={error} />,
  ]

  const isLast = step === STEPS.length - 1
  const valid = isStepValid(step, data)

  return (
    <>
      <div className="store-shell">
        <header className="store-header">
          <span className="store-logo">Trained<span>Gut</span></span>
          <StepIndicator steps={STEPS} current={step} />
          <div style={{ display: 'flex', gap: 8 }}>
            <button className="btn-logout" onClick={goToMenu}>← Menu</button>
            <button className="btn-logout" onClick={handleLogout} title={session.user.email}>Log out</button>
          </div>
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
      {overlays}
    </>
  )
}
