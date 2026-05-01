/* ============================================================
   Sur-O-Bahare — Main JS
   • Language toggle (EN ↔ বাং)
   • Hamburger menu
   • Scroll animations (IntersectionObserver)
   • Navbar shadow on scroll
   • Form validation (contact page)
   ============================================================ */

(function () {
    'use strict';

    /* ── 1. LANGUAGE TOGGLE ── */
    const html = document.documentElement;
    const langToggle = document.getElementById('lang-toggle');
    const LANG_KEY = 'sob_lang';

    function applyLang(lang) {
        html.setAttribute('data-lang', lang);
        localStorage.setItem(LANG_KEY, lang);

        // Swap all elements that have data-en / data-bn
        document.querySelectorAll('[data-en]').forEach(el => {
            el.textContent = lang === 'bn'
                ? (el.getAttribute('data-bn') || el.getAttribute('data-en'))
                : el.getAttribute('data-en');
        });

        // Update toggle button active state
        if (langToggle) {
            langToggle.querySelector('.lang-en').classList.toggle('active', lang === 'en');
            langToggle.querySelector('.lang-bn').classList.toggle('active', lang === 'bn');
        }
    }

    // Restore saved language on load
    const savedLang = localStorage.getItem(LANG_KEY) || 'en';
    applyLang(savedLang);

    if (langToggle) {
        langToggle.addEventListener('click', () => {
            const current = html.getAttribute('data-lang') || 'en';
            applyLang(current === 'en' ? 'bn' : 'en');
        });
    }

    /* ── 2. HAMBURGER MENU ── */
    const hamburger = document.getElementById('hamburger');
    const navLinks = document.getElementById('nav-links');

    if (hamburger && navLinks) {
        hamburger.addEventListener('click', () => {
            const isOpen = navLinks.classList.toggle('open');
            hamburger.classList.toggle('open', isOpen);
            hamburger.setAttribute('aria-expanded', isOpen);
        });

        // Close menu when a nav link is clicked
        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                navLinks.classList.remove('open');
                hamburger.classList.remove('open');
                hamburger.setAttribute('aria-expanded', 'false');
            });
        });

        // Close on outside click
        document.addEventListener('click', (e) => {
            if (!hamburger.contains(e.target) && !navLinks.contains(e.target)) {
                navLinks.classList.remove('open');
                hamburger.classList.remove('open');
                hamburger.setAttribute('aria-expanded', 'false');
            }
        });
    }

    /* ── 3. NAVBAR SHADOW ON SCROLL ── */
    const navbar = document.getElementById('navbar');
    if (navbar) {
        window.addEventListener('scroll', () => {
            navbar.classList.toggle('scrolled', window.scrollY > 10);
        }, { passive: true });
    }

    /* ── 4. FADE-IN ON SCROLL (IntersectionObserver) ── */
    const fadeEls = document.querySelectorAll('.fade-in');
    if (fadeEls.length && 'IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.12 });

        fadeEls.forEach(el => observer.observe(el));
    } else {
        // Fallback: show all immediately
        fadeEls.forEach(el => el.classList.add('visible'));
    }

    /* ── 5. CONTACT FORM VALIDATION ── */
    const enrollForm = document.getElementById('enroll-form');
    if (enrollForm) {
        enrollForm.addEventListener('submit', function (e) {
            let valid = true;

            // Clear previous errors
            this.querySelectorAll('.form-error').forEach(el => el.classList.remove('visible'));
            this.querySelectorAll('input, select').forEach(el => el.classList.remove('error'));

            // Required field check
            this.querySelectorAll('[required]').forEach(field => {
                if (!field.value.trim()) {
                    valid = false;
                    field.classList.add('error');
                    const err = document.getElementById(field.id + '-error');
                    if (err) err.classList.add('visible');
                }
            });

            // Mobile: 10-digit Indian number
            const mobile = document.getElementById('mobile');
            if (mobile && mobile.value.trim()) {
                const digits = mobile.value.replace(/\D/g, '');
                if (digits.length !== 10) {
                    valid = false;
                    mobile.classList.add('error');
                    const err = document.getElementById('mobile-error');
                    if (err) {
                        err.textContent = 'Please enter a valid 10-digit mobile number.';
                        err.classList.add('visible');
                    }
                }
            }

            if (!valid) e.preventDefault();
        });
    }

})();
