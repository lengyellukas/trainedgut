/* ═══════════════════════════════════════════════════════════
   TrainedGut.com — Main JavaScript
   ═══════════════════════════════════════════════════════════ */

/* ── FORM SUBMISSION ──────────────────────────────────────── */
async function handleSignup(inputId, msgId, btnId, source) {
  const input = document.getElementById(inputId);
  const msg   = document.getElementById(msgId);
  const btn   = document.getElementById(btnId);
  const email = input.value.trim();

  // Clear previous state
  input.classList.remove('error');
  msg.className = 'form-message';
  msg.style.display = 'none';
  msg.textContent = '';

  // Client-side validation
  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    input.classList.add('error');
    input.focus();
    return;
  }

  // Loading state
  btn.disabled = true;
  btn.textContent = '...';

  try {
    const res  = await fetch('subscribe.php', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ email, source })
    });
    const data = await res.json();

    if (data.success) {
      input.parentElement.style.display = 'none';
      msg.className = 'form-message success';
      msg.textContent = '✓ ' + data.message;
      msg.style.display = 'block';
    } else {
      msg.className = 'form-message error-msg';
      msg.textContent = data.message || 'Something went wrong. Please try again.';
      msg.style.display = 'block';
      btn.disabled = false;
      btn.textContent = source === 'hero' ? 'Notify Me' : 'Get Early Access';
    }
  } catch (err) {
    msg.className = 'form-message error-msg';
    msg.textContent = 'Connection error. Please try again.';
    msg.style.display = 'block';
    btn.disabled = false;
    btn.textContent = source === 'hero' ? 'Notify Me' : 'Get Early Access';
  }
}

/* ── SCROLL ANIMATIONS ────────────────────────────────────── */
if (window.location.protocol === 'file:') {
  document.querySelectorAll('.fade-up').forEach(el => el.classList.add('visible'));
} else {
  const observer = new IntersectionObserver(entries => {
    entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
  }, { threshold: 0.12 });
  document.querySelectorAll('.fade-up').forEach(el => observer.observe(el));
}
