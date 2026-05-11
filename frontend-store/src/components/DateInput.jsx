import { useState, useEffect } from 'react'
import DatePicker from 'react-datepicker'
import 'react-datepicker/dist/react-datepicker.css'
import { parseISO, format } from 'date-fns'

function useIsTouch() {
  const [isTouch, setIsTouch] = useState(
    () => window.matchMedia('(pointer: coarse)').matches
  )
  useEffect(() => {
    const mq = window.matchMedia('(pointer: coarse)')
    const handler = e => setIsTouch(e.matches)
    mq.addEventListener('change', handler)
    return () => mq.removeEventListener('change', handler)
  }, [])
  return isTouch
}

const toDate   = iso => iso ? parseISO(iso) : null
const fromDate = d   => d ? format(d, 'yyyy-MM-dd') : ''

export default function DateInput({ value, onChange, minDate, maxDate, placeholder }) {
  const isTouch = useIsTouch()

  if (isTouch) {
    return (
      <input
        className="field-input"
        type="date"
        value={value || ''}
        min={minDate ? fromDate(minDate) : undefined}
        max={maxDate ? fromDate(maxDate) : undefined}
        onChange={e => onChange(e.target.value)}
      />
    )
  }

  return (
    <DatePicker
      className="field-input"
      selected={toDate(value)}
      onChange={d => onChange(fromDate(d))}
      dateFormat="dd/MM/yyyy"
      minDate={minDate}
      maxDate={maxDate}
      placeholderText={placeholder || 'DD/MM/YYYY'}
    />
  )
}
