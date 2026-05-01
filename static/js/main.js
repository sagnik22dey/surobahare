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

    /* ── 6. BACKGROUND MUSIC ── */
    const bgAudio = document.getElementById('bg-audio');
    const musicToggleBtn = document.getElementById('music-toggle-btn');
    const musicIcon = document.getElementById('music-icon');

    if (bgAudio && musicToggleBtn) {
        const isMuted = localStorage.getItem('sob_music_muted') === 'true';

        if (!isMuted) {
            bgAudio.muted = false;
            const playPromise = bgAudio.play();
            if (playPromise !== undefined) {
                playPromise.catch(() => {
                    bgAudio.muted = true;
                    musicToggleBtn.classList.add('muted');
                    musicIcon.className = 'ri-volume-mute-line';
                });
            }
        } else {
            bgAudio.muted = true;
            musicToggleBtn.classList.add('muted');
            musicIcon.className = 'ri-volume-mute-line';
        }

        musicToggleBtn.addEventListener('click', () => {
            if (bgAudio.muted || bgAudio.paused) {
                bgAudio.muted = false;
                bgAudio.play();
                musicToggleBtn.classList.remove('muted');
                musicIcon.className = 'ri-volume-up-line';
                localStorage.setItem('sob_music_muted', 'false');
            } else {
                bgAudio.muted = true;
                bgAudio.pause();
                musicToggleBtn.classList.add('muted');
                musicIcon.className = 'ri-volume-mute-line';
                localStorage.setItem('sob_music_muted', 'true');
            }
        });
    }

    /* ── 7. TESTIMONIAL SLIDER ── */
    const track = document.getElementById('testimonial-track');
    const dotsContainer = document.getElementById('testimonial-dots');
    const prevBtn = document.getElementById('testimonial-prev');
    const nextBtn = document.getElementById('testimonial-next');

    if (track && dotsContainer) {
        const slides = Array.from(track.querySelectorAll('.testimonial-slide'));
        let current = 0;
        let autoTimer = null;

        function getSlidesPerView() {
            if (window.innerWidth <= 768) return 1;
            if (window.innerWidth <= 1024) return 2;
            return 3;
        }

        function totalPages() {
            return Math.max(1, Math.ceil(slides.length / getSlidesPerView()));
        }

        function buildDots() {
            dotsContainer.innerHTML = '';
            for (let i = 0; i < totalPages(); i++) {
                const dot = document.createElement('button');
                dot.className = 'testimonial-dot' + (i === 0 ? ' active' : '');
                dot.setAttribute('aria-label', 'Go to slide ' + (i + 1));
                dot.addEventListener('click', () => goTo(i));
                dotsContainer.appendChild(dot);
            }
        }

        function updateDots() {
            const page = Math.floor(current / getSlidesPerView());
            dotsContainer.querySelectorAll('.testimonial-dot').forEach((d, i) => {
                d.classList.toggle('active', i === page);
            });
        }

        function updateArrows() {
            if (prevBtn) prevBtn.disabled = current === 0;
            if (nextBtn) nextBtn.disabled = current >= slides.length - getSlidesPerView();
        }

        function goTo(slideIndex) {
            const spv = getSlidesPerView();
            const maxIndex = Math.max(0, slides.length - spv);
            current = Math.max(0, Math.min(slideIndex * spv, maxIndex));
            const pct = (current / slides.length) * 100;
            track.style.transform = 'translateX(-' + pct + '%)';
            updateDots();
            updateArrows();
        }

        function slideBy(dir) {
            const spv = getSlidesPerView();
            const maxIndex = Math.max(0, slides.length - spv);
            current = Math.max(0, Math.min(current + dir * spv, maxIndex));
            const pct = (current / slides.length) * 100;
            track.style.transform = 'translateX(-' + pct + '%)';
            updateDots();
            updateArrows();
        }

        function startAuto() {
            clearInterval(autoTimer);
            autoTimer = setInterval(() => {
                const spv = getSlidesPerView();
                if (current >= slides.length - spv) {
                    current = 0;
                    track.style.transform = 'translateX(0%)';
                    updateDots();
                    updateArrows();
                } else {
                    slideBy(1);
                }
            }, 5000);
        }

        function resetAuto() {
            startAuto();
        }

        if (prevBtn) prevBtn.addEventListener('click', () => { slideBy(-1); resetAuto(); });
        if (nextBtn) nextBtn.addEventListener('click', () => { slideBy(1);  resetAuto(); });

        /* Touch/swipe support */
        let touchStartX = 0;
        track.addEventListener('touchstart', e => { touchStartX = e.touches[0].clientX; }, { passive: true });
        track.addEventListener('touchend', e => {
            const diff = touchStartX - e.changedTouches[0].clientX;
            if (Math.abs(diff) > 50) {
                slideBy(diff > 0 ? 1 : -1);
                resetAuto();
            }
        }, { passive: true });

        /* Re-init on resize */
        let resizeTimer;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(() => {
                current = 0;
                track.style.transform = 'translateX(0%)';
                buildDots();
                updateArrows();
            }, 200);
        });

        buildDots();
        updateArrows();
        if (slides.length > getSlidesPerView()) startAuto();
    }

})();
