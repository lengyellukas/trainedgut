/**
 * Date-awareness helpers for the plan view.
 * All comparisons use local time at day granularity.
 */

function startOfDay(d) {
  const out = new Date(d)
  out.setHours(0, 0, 0, 0)
  return out
}

export function todayStart() {
  return startOfDay(new Date())
}

export function isWeekCurrent(week) {
  const today = todayStart()
  return today >= startOfDay(week.start_date) && today <= startOfDay(week.end_date)
}

export function isWeekFuture(week) {
  return todayStart() < startOfDay(week.start_date)
}

export function isWeekPast(week) {
  return todayStart() > startOfDay(week.end_date)
}

/** Index of the week containing today; 0 if before plan start, last index if after end. */
export function currentWeekIndex(weeks) {
  if (!weeks || weeks.length === 0) return 0
  const today = todayStart()
  for (let i = 0; i < weeks.length; i++) {
    if (today >= startOfDay(weeks[i].start_date) && today <= startOfDay(weeks[i].end_date)) {
      return i
    }
  }
  if (today < startOfDay(weeks[0].start_date)) return 0
  return weeks.length - 1
}

export function daysUntil(dateStr) {
  const target = startOfDay(dateStr)
  const today = todayStart()
  return Math.round((target - today) / (1000 * 60 * 60 * 24))
}
