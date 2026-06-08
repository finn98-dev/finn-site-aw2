// Nav: shadow on scroll + mobile toggle
const nav     = document.getElementById('mainNav');
const burger  = document.getElementById('burger');
const navLinks = document.getElementById('navLinks');

if (nav) {
  window.addEventListener('scroll', () => {
    nav.classList.toggle('scrolled', window.scrollY > 8);
  }, { passive: true });
}

if (burger && navLinks) {
  burger.addEventListener('click', () => {
    const open = navLinks.classList.toggle('open');
    burger.classList.toggle('open', open);
    burger.setAttribute('aria-expanded', open);
  });

  document.addEventListener('click', (e) => {
    if (!burger.contains(e.target) && !navLinks.contains(e.target)) {
      navLinks.classList.remove('open');
      burger.classList.remove('open');
      burger.setAttribute('aria-expanded', false);
    }
  });
}

// Scroll reveal with staggered delay per group
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.08, rootMargin: '0px 0px -28px 0px' });

// Group siblings for stagger
const revealEls = document.querySelectorAll('.reveal');
const seen = new Map();

revealEls.forEach(el => {
  const parent = el.parentElement;
  const idx = seen.get(parent) ?? 0;
  el.style.transitionDelay = `${idx * 90}ms`;
  seen.set(parent, idx + 1);
  observer.observe(el);
});
