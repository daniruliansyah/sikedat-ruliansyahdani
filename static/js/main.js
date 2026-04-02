/* ============================================================
   SIKEDAT — main.js
   Global JavaScript untuk semua halaman
   ============================================================ */

/* ── Live Clock ── */
function updateClock() {
  const el = document.getElementById('live-clock');
  if (!el) return;
  const now = new Date();
  const pad = n => String(n).padStart(2, '0');
  el.textContent = `${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;
}
setInterval(updateClock, 1000);
updateClock();

/* ── Hide loading overlay on page show (back navigation) ── */
window.addEventListener('pageshow', () => {
  const overlay = document.getElementById('loadingOverlay');
  if (overlay) overlay.classList.add('hidden');
});

/* ── Auto-dismiss flash messages ── */
document.querySelectorAll('.flash .alert').forEach(el => {
  setTimeout(() => {
    el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    el.style.opacity = '0';
    el.style.transform = 'translateY(-8px)';
    setTimeout(() => el.remove(), 500);
  }, 5000);
});

/* ── Stagger animation on page load ── */
document.querySelectorAll('.fade-in').forEach((el, i) => {
  if (!el.style.animationDelay) {
    el.style.animationDelay = (i * 0.04) + 's';
  }
});

/* ── Sidebar active state highlight ── */
const currentPath = window.location.pathname;
document.querySelectorAll('.nav-item').forEach(item => {
  if (item.getAttribute('href') && item.getAttribute('href') === currentPath) {
    item.classList.add('active');
  }
});

/* ── Smooth number counter animation for stat values ── */
function animateCounter(el, target, duration = 1200) {
  const start = 0;
  const step = target / (duration / 16);
  let current = start;
  const timer = setInterval(() => {
    current = Math.min(current + step, target);
    el.textContent = Math.floor(current).toLocaleString();
    if (current >= target) clearInterval(timer);
  }, 16);
}

document.querySelectorAll('.stat-value').forEach(el => {
  const raw = el.textContent.replace(/[^0-9]/g, '');
  const num = parseInt(raw);
  if (!isNaN(num) && num > 0 && num < 100000) {
    el.textContent = '0';
    const obs = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        animateCounter(el, num);
        obs.disconnect();
      }
    });
    obs.observe(el);
  }
});

/* ── Progress bar animation on scroll ── */
document.querySelectorAll('.progress-fill').forEach(el => {
  const target = el.style.width;
  el.style.width = '0';
  const obs = new IntersectionObserver(([entry]) => {
    if (entry.isIntersecting) {
      setTimeout(() => { el.style.width = target; }, 200);
      obs.disconnect();
    }
  });
  obs.observe(el);
});

/* ── Tooltip on hover (title attribute) ── */
document.querySelectorAll('[title]').forEach(el => {
  el.style.cursor = 'default';
});

/* ── Table row hover highlight ── */
document.querySelectorAll('tbody tr').forEach(row => {
  row.style.transition = 'background 0.12s ease';
});

/* ── Card hover elevation ── */
document.querySelectorAll('.stat-card').forEach(card => {
  card.addEventListener('mouseenter', () => {
    card.style.boxShadow = '0 8px 32px rgba(0,0,0,0.5)';
  });
  card.addEventListener('mouseleave', () => {
    card.style.boxShadow = '';
  });
});

/* ── Prevent double-submit on all forms ── */
document.querySelectorAll('form').forEach(form => {
  form.addEventListener('submit', function () {
    this.querySelectorAll('button[type="submit"]').forEach(btn => {
      setTimeout(() => { btn.disabled = true; }, 50);
    });
  });
});