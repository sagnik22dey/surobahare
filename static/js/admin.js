/* ============================================================
   Sur-O-Bahare — Admin Dashboard JS
   ============================================================ */
(function () {
    'use strict';

    /* ── STATE ── */
    let content = {};

    /* ── DOM REFS ── */
    const sidebar = document.getElementById('admSidebar');
    const sidebarOverlay = document.getElementById('admSidebarOverlay');
    const menuBtn = document.getElementById('admMenuBtn');
    const toastContainer = document.getElementById('admToastContainer');
    const confirmModal = document.getElementById('admConfirmModal');
    const confirmOkBtn = document.getElementById('admConfirmOk');
    const confirmCancelBtn = document.getElementById('admConfirmCancel');
    const confirmMsg = document.getElementById('admConfirmMsg');

    let confirmCallback = null;

    /* ═══════════════════════════════════════════════════════════
       SIDEBAR
    ═══════════════════════════════════════════════════════════ */
    if (menuBtn) {
        menuBtn.addEventListener('click', () => {
            const isOpen = sidebar.classList.toggle('open');
            menuBtn.classList.toggle('open', isOpen);
            sidebarOverlay.classList.toggle('show', isOpen);
        });
    }

    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', closeSidebar);
    }

    function closeSidebar() {
        sidebar.classList.remove('open');
        menuBtn && menuBtn.classList.remove('open');
        sidebarOverlay && sidebarOverlay.classList.remove('show');
    }

    /* ═══════════════════════════════════════════════════════════
       SECTION TABS / NAVIGATION
    ═══════════════════════════════════════════════════════════ */
    document.querySelectorAll('.adm-tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const target = btn.dataset.section;
            showSection(target);
            closeSidebar();
        });
    });

    document.querySelectorAll('.adm-sidebar-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const target = link.dataset.section;
            showSection(target);
            closeSidebar();
        });
    });

    function showSection(id) {
        document.querySelectorAll('.adm-section').forEach(s => s.classList.remove('active'));
        document.querySelectorAll('.adm-tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.adm-sidebar-link').forEach(l => l.classList.remove('active'));

        const sec = document.getElementById('section-' + id);
        if (sec) sec.classList.add('active');

        document.querySelectorAll(`[data-section="${id}"]`).forEach(el => el.classList.add('active'));

        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    /* ═══════════════════════════════════════════════════════════
       TOAST NOTIFICATIONS
    ═══════════════════════════════════════════════════════════ */
    function showToast(message, type = 'success', duration = 3500) {
        const icons = { success: 'ri-checkbox-circle-line', error: 'ri-error-warning-line', warning: 'ri-alert-line' };
        const toast = document.createElement('div');
        toast.className = `adm-toast ${type}`;
        toast.innerHTML = `<i class="${icons[type] || icons.success}"></i><span>${message}</span>`;
        toastContainer.appendChild(toast);
        requestAnimationFrame(() => {
            requestAnimationFrame(() => toast.classList.add('show'));
        });
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 350);
        }, duration);
    }

    /* ═══════════════════════════════════════════════════════════
       CONFIRM MODAL
    ═══════════════════════════════════════════════════════════ */
    function confirmAction(message, callback) {
        confirmMsg.textContent = message;
        confirmCallback = callback;
        confirmModal.classList.add('show');
    }

    confirmOkBtn && confirmOkBtn.addEventListener('click', () => {
        confirmModal.classList.remove('show');
        if (confirmCallback) { confirmCallback(); confirmCallback = null; }
    });

    confirmCancelBtn && confirmCancelBtn.addEventListener('click', () => {
        confirmModal.classList.remove('show');
        confirmCallback = null;
    });

    /* ═══════════════════════════════════════════════════════════
       API HELPERS
    ═══════════════════════════════════════════════════════════ */
    async function apiPut(path, body) {
        const res = await fetch('/admin' + path, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({ detail: 'Unknown error' }));
            throw new Error(err.detail || 'Save failed');
        }
        return res.json();
    }

    async function uploadImage(file) {
        const fd = new FormData();
        fd.append('file', file);
        const res = await fetch('/admin/upload-image', { method: 'POST', body: fd });
        if (!res.ok) {
            const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
            throw new Error(err.detail || 'Upload failed');
        }
        return (await res.json()).url;
    }

    function setSaving(btn, saving) {
        if (saving) {
            btn.dataset.origHtml = btn.innerHTML;
            btn.innerHTML = `<span class="adm-spinner"></span> Saving…`;
            btn.disabled = true;
        } else {
            btn.innerHTML = btn.dataset.origHtml || 'Save';
            btn.disabled = false;
        }
    }

    /* ═══════════════════════════════════════════════════════════
       IMAGE UPLOAD WIDGET
    ═══════════════════════════════════════════════════════════ */
    function initImageUpload(areaId, previewId, urlInputId) {
        const area = document.getElementById(areaId);
        const preview = document.getElementById(previewId);
        const urlInput = document.getElementById(urlInputId);
        if (!area) return;

        area.addEventListener('click', () => area.querySelector('input[type="file"]').click());

        area.querySelector('input[type="file"]').addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (!file) return;
            try {
                area.innerHTML = `<span class="adm-upload-placeholder"><i class="ri-loader-4-line"></i>Uploading…</span>`;
                const url = await uploadImage(file);
                if (urlInput) urlInput.value = url;
                if (preview) { preview.src = url; preview.classList.add('visible'); }
                area.innerHTML = `<span class="adm-upload-placeholder"><i class="ri-check-line"></i>Uploaded! Click to change</span><input type="file" accept="image/*">`;
                area.querySelector('input[type="file"]').addEventListener('change', arguments.callee);
                showToast('Image uploaded!', 'success');
            } catch (err) {
                area.innerHTML = `<span class="adm-upload-placeholder"><i class="ri-image-add-line"></i>Tap to upload image</span><input type="file" accept="image/*">`;
                area.querySelector('input[type="file"]').addEventListener('change', arguments.callee);
                showToast(err.message, 'error');
            }
        });

        // Drag & drop
        area.addEventListener('dragover', (e) => { e.preventDefault(); area.classList.add('drag-over'); });
        area.addEventListener('dragleave', () => area.classList.remove('drag-over'));
        area.addEventListener('drop', async (e) => {
            e.preventDefault();
            area.classList.remove('drag-over');
            const file = e.dataTransfer.files[0];
            if (file && file.type.startsWith('image/')) {
                try {
                    const url = await uploadImage(file);
                    if (urlInput) urlInput.value = url;
                    if (preview) { preview.src = url; preview.classList.add('visible'); }
                    showToast('Image uploaded!', 'success');
                } catch (err) {
                    showToast(err.message, 'error');
                }
            }
        });

        if (urlInput) {
            urlInput.addEventListener('input', () => {
                if (preview && urlInput.value) { preview.src = urlInput.value; preview.classList.add('visible'); }
                else if (preview) preview.classList.remove('visible');
            });
        }
    }

    /* ═══════════════════════════════════════════════════════════
       LOAD CONTENT & POPULATE FORMS
    ═══════════════════════════════════════════════════════════ */
    async function loadContent() {
        try {
            const res = await fetch('/admin/content');
            content = await res.json();
            populateAll();
        } catch (e) {
            showToast('Failed to load content. Refresh the page.', 'error');
        }
    }

    function val(id, value) {
        const el = document.getElementById(id);
        if (el) el.value = value !== undefined && value !== null ? value : '';
    }

    function checked(id, value) {
        const el = document.getElementById(id);
        if (el) el.checked = !!value;
    }

    function populateAll() {
        populateHero();
        populateMentor();
        populatePrograms();
        populateApproach();
        populateTestimonials();
        populateBanner();
        populateMeteor();
        populateContactInfo();
        populateFooterInfo();
        populateAboutPage();
        populateGalleryPage();
        populateContactPage();
        populateThankyouPage();
        populateMusicSettings();
    }

    /* ─── HERO ─────────────────────────────────────────────── */
    function populateHero() {
        const h = content.hero || {};
        val('hero_badge_en', h.badge?.en);
        val('hero_badge_bn', h.badge?.bn);
        val('hero_headline_en', h.headline?.en);
        val('hero_headline_bn', h.headline?.bn);
        val('hero_tagline_en', h.tagline?.en);
        val('hero_tagline_bn', h.tagline?.bn);
        val('hero_desc_en', h.description?.en);
        val('hero_desc_bn', h.description?.bn);
        val('hero_bg_url', h.bg_image_url);
        val('hero_cta1_label_en', h.cta_primary_label_en);
        val('hero_cta1_label_bn', h.cta_primary_label_bn);
        val('hero_cta1_link', h.cta_primary_link);
        val('hero_cta2_label_en', h.cta_secondary_label_en);
        val('hero_cta2_label_bn', h.cta_secondary_label_bn);
        val('hero_cta2_link', h.cta_secondary_link);
        const preview = document.getElementById('hero_bg_preview');
        if (preview && h.bg_image_url) { preview.src = h.bg_image_url; preview.classList.add('visible'); }
    }

    document.getElementById('heroSaveBtn')?.addEventListener('click', async (e) => {
        const btn = e.currentTarget;
        setSaving(btn, true);
        try {
            await apiPut('/hero', {
                badge_en: document.getElementById('hero_badge_en').value,
                badge_bn: document.getElementById('hero_badge_bn').value,
                headline_en: document.getElementById('hero_headline_en').value,
                headline_bn: document.getElementById('hero_headline_bn').value,
                tagline_en: document.getElementById('hero_tagline_en').value,
                tagline_bn: document.getElementById('hero_tagline_bn').value,
                description_en: document.getElementById('hero_desc_en').value,
                description_bn: document.getElementById('hero_desc_bn').value,
                bg_image_url: document.getElementById('hero_bg_url').value,
                cta_primary_label_en: document.getElementById('hero_cta1_label_en').value,
                cta_primary_label_bn: document.getElementById('hero_cta1_label_bn').value,
                cta_primary_link: document.getElementById('hero_cta1_link').value,
                cta_secondary_label_en: document.getElementById('hero_cta2_label_en').value,
                cta_secondary_label_bn: document.getElementById('hero_cta2_label_bn').value,
                cta_secondary_link: document.getElementById('hero_cta2_link').value,
            });
            showToast('Hero section saved!', 'success');
        } catch (err) { showToast(err.message, 'error'); }
        setSaving(btn, false);
    });

    /* ─── MENTOR ────────────────────────────────────────────── */
    function populateMentor() {
        const m = content.about_snapshot || {};
        val('mentor_title_en', m.title?.en);
        val('mentor_title_bn', m.title?.bn);
        val('mentor_name_en', m.mentor_name?.en);
        val('mentor_name_bn', m.mentor_name?.bn);
        val('mentor_role_en', m.mentor_role?.en);
        val('mentor_role_bn', m.mentor_role?.bn);
        val('mentor_bio_en', m.mentor_bio?.en);
        val('mentor_bio_bn', m.mentor_bio?.bn);
        val('mentor_photo_url', m.mentor_photo_url);
        val('mentor_qualifications', m.mentor_qualifications);
        val('mentor_link', m.mentor_link);
        const preview = document.getElementById('mentor_photo_preview');
        if (preview && m.mentor_photo_url) { preview.src = m.mentor_photo_url; preview.classList.add('visible'); }
    }

    document.getElementById('mentorSaveBtn')?.addEventListener('click', async (e) => {
        const btn = e.currentTarget;
        setSaving(btn, true);
        try {
            await apiPut('/mentor', {
                title_en: document.getElementById('mentor_title_en').value,
                title_bn: document.getElementById('mentor_title_bn').value,
                name_en: document.getElementById('mentor_name_en').value,
                name_bn: document.getElementById('mentor_name_bn').value,
                role_en: document.getElementById('mentor_role_en').value,
                role_bn: document.getElementById('mentor_role_bn').value,
                bio_en: document.getElementById('mentor_bio_en').value,
                bio_bn: document.getElementById('mentor_bio_bn').value,
                photo_url: document.getElementById('mentor_photo_url').value,
                qualifications: document.getElementById('mentor_qualifications').value,
                link: document.getElementById('mentor_link').value,
            });
            showToast('Mentor section saved!', 'success');
        } catch (err) { showToast(err.message, 'error'); }
        setSaving(btn, false);
    });

    /* ─── PROGRAMS ──────────────────────────────────────────── */
    let programsList = [];

    function populatePrograms() {
        const pt = content.programs_teaser || {};
        val('prog_title_en', pt.title?.en);
        val('prog_title_bn', pt.title?.bn);
        val('prog_subtitle_en', pt.subtitle?.en);
        val('prog_subtitle_bn', pt.subtitle?.bn);
        programsList = JSON.parse(JSON.stringify(pt.programs || []));
        renderProgramsList();
    }

    function renderProgramsList() {
        const container = document.getElementById('programsListContainer');
        if (!container) return;
        container.innerHTML = '';
        programsList.forEach((prog, i) => {
            const card = createProgramCard(prog, i);
            container.appendChild(card);
        });
    }

    function createProgramCard(prog, i) {
        const card = document.createElement('div');
        card.className = 'adm-item-card';
        card.dataset.idx = i;
        card.innerHTML = `
      <div class="adm-item-card-header">
        <span class="adm-item-drag-handle"><i class="ri-drag-move-2-line"></i></span>
        <span class="adm-item-num">${i + 1}</span>
        <span class="adm-item-title">${prog.title_en || 'New Program'}</span>
        <div class="adm-item-actions">
          <label style="cursor:pointer; margin-right: 8px;" title="Visible">
            <input type="checkbox" onchange="programsList[${i}].visible=this.checked" ${prog.visible !== false ? 'checked' : ''}>
          </label>
          <div class="adm-item-reorder-btns">
            <button onclick="admMoveItem('programs',${i},-1)" title="Move up"><i class="ri-arrow-up-s-line"></i></button>
            <button onclick="admMoveItem('programs',${i},1)" title="Move down"><i class="ri-arrow-down-s-line"></i></button>
          </div>
          <button class="adm-btn adm-btn-sm adm-btn-secondary adm-btn-icon" onclick="admToggleItem(this)" title="Expand">
            <i class="ri-pencil-line"></i>
          </button>
          <button class="adm-btn adm-btn-sm adm-btn-danger adm-btn-icon" onclick="admRemoveProgram(${i})" title="Remove">
            <i class="ri-delete-bin-line"></i>
          </button>
        </div>
      </div>
      <div class="adm-item-body">
        <div class="adm-grid-2">
          <div class="adm-form-group">
            <label class="adm-label">Title <span class="lang-tag">EN</span></label>
            <input class="adm-input" value="${esc(prog.title_en)}" oninput="programsList[${i}].title_en=this.value;this.closest('.adm-item-card').querySelector('.adm-item-title').textContent=this.value||'New Program'">
          </div>
          <div class="adm-form-group">
            <label class="adm-label">Title <span class="lang-tag bn">BN</span></label>
            <input class="adm-input" value="${esc(prog.title_bn)}" oninput="programsList[${i}].title_bn=this.value">
          </div>
        </div>
        <div class="adm-grid-2">
          <div class="adm-form-group">
            <label class="adm-label">Description <span class="lang-tag">EN</span></label>
            <textarea class="adm-textarea" oninput="programsList[${i}].desc_en=this.value">${esc(prog.desc_en)}</textarea>
          </div>
          <div class="adm-form-group">
            <label class="adm-label">Description <span class="lang-tag bn">BN</span></label>
            <textarea class="adm-textarea" oninput="programsList[${i}].desc_bn=this.value">${esc(prog.desc_bn)}</textarea>
          </div>
        </div>
        <div class="adm-form-group">
          <label class="adm-label">Icon (emoji)</label>
          <input class="adm-input" value="${esc(prog.icon || '🎵')}" style="max-width:120px" oninput="programsList[${i}].icon=this.value">
        </div>
        <div class="adm-form-group">
          <label class="adm-label">Image URL</label>
          <div class="adm-image-url-row">
            <input class="adm-input" id="prog_img_url_${i}" value="${esc(prog.image_url || '')}" oninput="programsList[${i}].image_url=this.value;admUpdateImgPreview('prog_img_prev_${i}',this.value)">
            <label class="adm-btn adm-btn-secondary adm-btn-sm" style="cursor:pointer">
              <i class="ri-upload-2-line"></i>
              <input type="file" accept="image/*" style="display:none" onchange="admUploadToField(this,'prog_img_url_${i}','prog_img_prev_${i}',${i},'programs')">
            </label>
          </div>
          <img id="prog_img_prev_${i}" src="${esc(prog.image_url || '')}" class="adm-image-preview ${prog.image_url ? 'visible' : ''}" alt="preview">
        </div>
      </div>
    `;
        return card;
    }

    window.admMoveItem = function (list, idx, dir) {
        const arr = list === 'programs' ? programsList : list === 'approach' ? approachList : list === 'testimonials' ? testimonialsList : list === 'meteor' ? meteorList : null;
        if (!arr) return;
        const newIdx = idx + dir;
        if (newIdx < 0 || newIdx >= arr.length) return;
        [arr[idx], arr[newIdx]] = [arr[newIdx], arr[idx]];
        if (list === 'programs') renderProgramsList();
        else if (list === 'approach') renderApproachList();
        else if (list === 'testimonials') renderTestimonialsList();
        else if (list === 'meteor') renderMeteorList();
    };

    window.admToggleItem = function (btn) {
        const body = btn.closest('.adm-item-card').querySelector('.adm-item-body');
        body.classList.toggle('expanded');
        const icon = btn.querySelector('i');
        icon.className = body.classList.contains('expanded') ? 'ri-arrow-up-s-line' : 'ri-pencil-line';
    };

    window.admRemoveProgram = function (i) {
        confirmAction('Remove this program?', () => {
            programsList.splice(i, 1);
            renderProgramsList();
        });
    };

    window.admUpdateImgPreview = function (previewId, url) {
        const el = document.getElementById(previewId);
        if (!el) return;
        if (url) { el.src = url; el.classList.add('visible'); }
        else el.classList.remove('visible');
    };

    window.admUploadToField = async function (input, urlFieldId, previewId, idx, section) {
        const file = input.files[0];
        if (!file) return;
        try {
            const url = await uploadImage(file);
            document.getElementById(urlFieldId).value = url;
            window.admUpdateImgPreview(previewId, url);
            if (section === 'programs') programsList[idx].image_url = url;
            else if (section === 'testimonials') testimonialsList[idx].photo_url = url;
            showToast('Image uploaded!', 'success');
        } catch (err) { showToast(err.message, 'error'); }
    };

    document.getElementById('addProgramBtn')?.addEventListener('click', () => {
        programsList.push({ id: 'p' + Date.now(), title_en: '', title_bn: '', desc_en: '', desc_bn: '', image_url: '', icon: '🎵', visible: true });
        renderProgramsList();
        setTimeout(() => {
            const cards = document.querySelectorAll('#programsListContainer .adm-item-card');
            const last = cards[cards.length - 1];
            if (last) { last.querySelector('.adm-item-body').classList.add('expanded'); last.scrollIntoView({ behavior: 'smooth', block: 'nearest' }); }
        }, 50);
    });

    document.getElementById('programsSaveBtn')?.addEventListener('click', async (e) => {
        const btn = e.currentTarget;
        setSaving(btn, true);
        try {
            await apiPut('/programs', {
                title_en: document.getElementById('prog_title_en').value,
                title_bn: document.getElementById('prog_title_bn').value,
                subtitle_en: document.getElementById('prog_subtitle_en').value,
                subtitle_bn: document.getElementById('prog_subtitle_bn').value,
                programs: programsList,
            });
            showToast('Programs section saved!', 'success');
        } catch (err) { showToast(err.message, 'error'); }
        setSaving(btn, false);
    });

    /* ─── TEACHING APPROACH ─────────────────────────────────── */
    let approachList = [];

    function populateApproach() {
        const ta = content.teaching_approach || {};
        val('approach_title_en', ta.title?.en);
        val('approach_title_bn', ta.title?.bn);
        val('approach_subtitle_en', ta.subtitle?.en);
        val('approach_subtitle_bn', ta.subtitle?.bn);
        approachList = JSON.parse(JSON.stringify(ta.points || []));
        renderApproachList();
    }

    function renderApproachList() {
        const container = document.getElementById('approachListContainer');
        if (!container) return;
        container.innerHTML = '';
        approachList.forEach((point, i) => {
            const card = document.createElement('div');
            card.className = 'adm-item-card';
            card.innerHTML = `
        <div class="adm-item-card-header">
          <span class="adm-item-drag-handle"><i class="ri-drag-move-2-line"></i></span>
          <span class="adm-item-num">${i + 1}</span>
          <span class="adm-item-title">${esc(point.en) || 'New Point'}</span>
          <div class="adm-item-actions">
            <label style="cursor:pointer; margin-right: 8px;" title="Visible">
              <input type="checkbox" onchange="approachList[${i}].visible=this.checked" ${point.visible !== false ? 'checked' : ''}>
            </label>
            <div class="adm-item-reorder-btns">
              <button onclick="admMoveItem('approach',${i},-1)"><i class="ri-arrow-up-s-line"></i></button>
              <button onclick="admMoveItem('approach',${i},1)"><i class="ri-arrow-down-s-line"></i></button>
            </div>
            <button class="adm-btn adm-btn-sm adm-btn-secondary adm-btn-icon" onclick="admToggleItem(this)"><i class="ri-pencil-line"></i></button>
            <button class="adm-btn adm-btn-sm adm-btn-danger adm-btn-icon" onclick="admRemoveApproach(${i})"><i class="ri-delete-bin-line"></i></button>
          </div>
        </div>
        <div class="adm-item-body">
          <div class="adm-grid-2">
            <div class="adm-form-group">
              <label class="adm-label">Text <span class="lang-tag">EN</span></label>
              <input class="adm-input" value="${esc(point.en)}" oninput="approachList[${i}].en=this.value;this.closest('.adm-item-card').querySelector('.adm-item-title').textContent=this.value||'New Point'">
            </div>
            <div class="adm-form-group">
              <label class="adm-label">Text <span class="lang-tag bn">BN</span></label>
              <input class="adm-input" value="${esc(point.bn)}" oninput="approachList[${i}].bn=this.value">
            </div>
          </div>
          <div class="adm-form-group">
            <label class="adm-label">Icon Class (Remix Icon)</label>
            <input class="adm-input" value="${esc(point.icon || 'ri-checkbox-circle-fill')}" placeholder="e.g. ri-star-line" oninput="approachList[${i}].icon=this.value">
          </div>
        </div>
      `;
            container.appendChild(card);
        });
    }

    window.admRemoveApproach = function (i) {
        confirmAction('Remove this approach point?', () => { approachList.splice(i, 1); renderApproachList(); });
    };

    document.getElementById('addApproachBtn')?.addEventListener('click', () => {
        approachList.push({ id: 't' + Date.now(), icon: 'ri-checkbox-circle-fill', en: '', bn: '', visible: true });
        renderApproachList();
        setTimeout(() => {
            const cards = document.querySelectorAll('#approachListContainer .adm-item-card');
            const last = cards[cards.length - 1];
            if (last) { last.querySelector('.adm-item-body').classList.add('expanded'); last.scrollIntoView({ behavior: 'smooth', block: 'nearest' }); }
        }, 50);
    });

    document.getElementById('approachSaveBtn')?.addEventListener('click', async (e) => {
        const btn = e.currentTarget;
        setSaving(btn, true);
        try {
            await apiPut('/teaching-approach', {
                title_en: document.getElementById('approach_title_en').value,
                title_bn: document.getElementById('approach_title_bn').value,
                subtitle_en: document.getElementById('approach_subtitle_en').value,
                subtitle_bn: document.getElementById('approach_subtitle_bn').value,
                points: approachList,
            });
            showToast('Teaching Approach saved!', 'success');
        } catch (err) { showToast(err.message, 'error'); }
        setSaving(btn, false);
    });

    /* ─── TESTIMONIALS ──────────────────────────────────────── */
    let testimonialsList = [];

    function populateTestimonials() {
        const t = content.testimonials || {};
        val('test_title_en', t.title?.en);
        val('test_title_bn', t.title?.bn);
        val('test_subtitle_en', t.subtitle?.en);
        val('test_subtitle_bn', t.subtitle?.bn);
        testimonialsList = JSON.parse(JSON.stringify(t.list || []));
        renderTestimonialsList();
    }

    function renderTestimonialsList() {
        const container = document.getElementById('testimonialsListContainer');
        if (!container) return;
        container.innerHTML = '';
        testimonialsList.forEach((t, i) => {
            const card = document.createElement('div');
            card.className = 'adm-item-card';
            const starsHtml = [1, 2, 3, 4, 5].map(n => `<button type="button" class="${n <= (t.rating || 5) ? 'active' : ''}" onclick="admSetRating(${i},${n})">★</button>`).join('');
            card.innerHTML = `
        <div class="adm-item-card-header">
          <span class="adm-item-drag-handle"><i class="ri-drag-move-2-line"></i></span>
          <span class="adm-item-num">${i + 1}</span>
          <span class="adm-item-title">${esc(t.author_en) || 'New Testimonial'}</span>
          <div class="adm-item-actions">
            <label style="cursor:pointer; margin-right: 8px;" title="Visible">
              <input type="checkbox" onchange="testimonialsList[${i}].visible=this.checked" ${t.visible !== false ? 'checked' : ''}>
            </label>
            <div class="adm-item-reorder-btns">
              <button onclick="admMoveItem('testimonials',${i},-1)"><i class="ri-arrow-up-s-line"></i></button>
              <button onclick="admMoveItem('testimonials',${i},1)"><i class="ri-arrow-down-s-line"></i></button>
            </div>
            <button class="adm-btn adm-btn-sm adm-btn-secondary adm-btn-icon" onclick="admToggleItem(this)"><i class="ri-pencil-line"></i></button>
            <button class="adm-btn adm-btn-sm adm-btn-danger adm-btn-icon" onclick="admRemoveTestimonial(${i})"><i class="ri-delete-bin-line"></i></button>
          </div>
        </div>
        <div class="adm-item-body">
          <div class="adm-form-group">
            <label class="adm-label">Author Name <span class="lang-tag">EN</span></label>
            <input class="adm-input" value="${esc(t.author_en)}" oninput="testimonialsList[${i}].author_en=this.value;this.closest('.adm-item-card').querySelector('.adm-item-title').textContent=this.value||'New Testimonial'">
          </div>
          <div class="adm-form-group">
            <label class="adm-label">Author Name <span class="lang-tag bn">BN</span></label>
            <input class="adm-input" value="${esc(t.author_bn)}" oninput="testimonialsList[${i}].author_bn=this.value">
          </div>
          <div class="adm-form-group">
            <label class="adm-label">Quote <span class="lang-tag">EN</span></label>
            <textarea class="adm-textarea" oninput="testimonialsList[${i}].quote_en=this.value">${esc(t.quote_en)}</textarea>
          </div>
          <div class="adm-form-group">
            <label class="adm-label">Quote <span class="lang-tag bn">BN</span></label>
            <textarea class="adm-textarea" oninput="testimonialsList[${i}].quote_bn=this.value">${esc(t.quote_bn)}</textarea>
          </div>
          <div class="adm-form-group">
            <label class="adm-label">Rating</label>
            <div class="adm-star-rating" id="stars_${i}">${starsHtml}</div>
          </div>
          <div class="adm-form-group">
            <label class="adm-label">Photo URL (optional)</label>
            <div class="adm-image-url-row">
              <input class="adm-input" id="test_photo_url_${i}" value="${esc(t.photo_url || '')}" oninput="testimonialsList[${i}].photo_url=this.value;admUpdateImgPreview('test_photo_prev_${i}',this.value)">
              <label class="adm-btn adm-btn-secondary adm-btn-sm" style="cursor:pointer">
                <i class="ri-upload-2-line"></i>
                <input type="file" accept="image/*" style="display:none" onchange="admUploadToField(this,'test_photo_url_${i}','test_photo_prev_${i}',${i},'testimonials')">
              </label>
            </div>
            <img id="test_photo_prev_${i}" src="${esc(t.photo_url || '')}" class="adm-image-preview ${t.photo_url ? 'visible' : ''}" alt="preview" style="border-radius:50%;width:80px;height:80px;object-fit:cover;">
          </div>
        </div>
      `;
            container.appendChild(card);
        });
    }

    window.admSetRating = function (i, rating) {
        testimonialsList[i].rating = rating;
        const container = document.getElementById(`stars_${i}`);
        if (!container) return;
        container.querySelectorAll('button').forEach((btn, n) => {
            btn.classList.toggle('active', n < rating);
        });
    };

    window.admRemoveTestimonial = function (i) {
        confirmAction('Remove this testimonial?', () => { testimonialsList.splice(i, 1); renderTestimonialsList(); });
    };

    document.getElementById('addTestimonialBtn')?.addEventListener('click', () => {
        testimonialsList.push({ id: 'test' + Date.now(), quote_en: '', quote_bn: '', author_en: '', author_bn: '', rating: 5, photo_url: '', visible: true });
        renderTestimonialsList();
        setTimeout(() => {
            const cards = document.querySelectorAll('#testimonialsListContainer .adm-item-card');
            const last = cards[cards.length - 1];
            if (last) { last.querySelector('.adm-item-body').classList.add('expanded'); last.scrollIntoView({ behavior: 'smooth', block: 'nearest' }); }
        }, 50);
    });

    document.getElementById('testimonialsSaveBtn')?.addEventListener('click', async (e) => {
        const btn = e.currentTarget;
        setSaving(btn, true);
        try {
            await apiPut('/testimonials', {
                title_en: document.getElementById('test_title_en').value,
                title_bn: document.getElementById('test_title_bn').value,
                subtitle_en: document.getElementById('test_subtitle_en').value,
                subtitle_bn: document.getElementById('test_subtitle_bn').value,
                list: testimonialsList,
            });
            showToast('Testimonials saved!', 'success');
        } catch (err) { showToast(err.message, 'error'); }
        setSaving(btn, false);
    });

    /* ─── ADMISSIONS BANNER ─────────────────────────────────── */
    function populateBanner() {
        const b = content.admissions_banner || {};
        checked('banner_visible', b.visible !== false);
        val('banner_title_en', b.title?.en);
        val('banner_title_bn', b.title?.bn);
        val('banner_desc_en', b.description?.en);
        val('banner_desc_bn', b.description?.bn);
        val('banner_urgency_en', b.urgency_text_en);
        val('banner_urgency_bn', b.urgency_text_bn);
        val('banner_seat_count', b.seat_count);
        val('banner_enroll_label_en', b.enroll_btn_label_en);
        val('banner_enroll_label_bn', b.enroll_btn_label_bn);
        val('banner_enroll_link', b.enroll_btn_link);
        val('banner_whatsapp_number', b.whatsapp_number);
        val('banner_whatsapp_msg', b.whatsapp_message);
        val('banner_whatsapp_label_en', b.whatsapp_btn_label_en);
        val('banner_whatsapp_label_bn', b.whatsapp_btn_label_bn);
    }

    document.getElementById('bannerSaveBtn')?.addEventListener('click', async (e) => {
        const btn = e.currentTarget;
        setSaving(btn, true);
        try {
            await apiPut('/admissions-banner', {
                visible: document.getElementById('banner_visible').checked,
                title_en: document.getElementById('banner_title_en').value,
                title_bn: document.getElementById('banner_title_bn').value,
                description_en: document.getElementById('banner_desc_en').value,
                description_bn: document.getElementById('banner_desc_bn').value,
                urgency_text_en: document.getElementById('banner_urgency_en').value,
                urgency_text_bn: document.getElementById('banner_urgency_bn').value,
                seat_count: document.getElementById('banner_seat_count').value,
                enroll_btn_label_en: document.getElementById('banner_enroll_label_en').value,
                enroll_btn_label_bn: document.getElementById('banner_enroll_label_bn').value,
                enroll_btn_link: document.getElementById('banner_enroll_link').value,
                whatsapp_number: document.getElementById('banner_whatsapp_number').value,
                whatsapp_message: document.getElementById('banner_whatsapp_msg').value,
                whatsapp_btn_label_en: document.getElementById('banner_whatsapp_label_en').value,
                whatsapp_btn_label_bn: document.getElementById('banner_whatsapp_label_bn').value,
            });
            showToast('Admissions Banner saved!', 'success');
        } catch (err) { showToast(err.message, 'error'); }
        setSaving(btn, false);
    });

    /* ─── METEOR HIGHLIGHTS ─────────────────────────────────── */
    let meteorList = [];

    function populateMeteor() {
        const m = content.meteor_highlights || {};
        val('meteor_title_en', m.title?.en);
        val('meteor_title_bn', m.title?.bn);
        meteorList = JSON.parse(JSON.stringify(m.items || []));
        renderMeteorList();
    }

    function renderMeteorList() {
        const container = document.getElementById('meteorListContainer');
        if (!container) return;
        container.innerHTML = '';
        meteorList.forEach((item, i) => {
            const card = document.createElement('div');
            card.className = 'adm-item-card';
            card.innerHTML = `
        <div class="adm-item-card-header">
          <span class="adm-item-drag-handle"><i class="ri-drag-move-2-line"></i></span>
          <span class="adm-item-num">${i + 1}</span>
          <span class="adm-item-title">${item.icon || '⭐'} ${esc(item.label_en) || 'New Highlight'}</span>
          <div class="adm-item-actions">
            <label style="cursor:pointer; margin-right: 8px;" title="Visible">
              <input type="checkbox" onchange="meteorList[${i}].visible=this.checked" ${item.visible !== false ? 'checked' : ''}>
            </label>
            <div class="adm-item-reorder-btns">
              <button onclick="admMoveItem('meteor',${i},-1)"><i class="ri-arrow-up-s-line"></i></button>
              <button onclick="admMoveItem('meteor',${i},1)"><i class="ri-arrow-down-s-line"></i></button>
            </div>
            <button class="adm-btn adm-btn-sm adm-btn-secondary adm-btn-icon" onclick="admToggleItem(this)"><i class="ri-pencil-line"></i></button>
            <button class="adm-btn adm-btn-sm adm-btn-danger adm-btn-icon" onclick="admRemoveMeteor(${i})"><i class="ri-delete-bin-line"></i></button>
          </div>
        </div>
        <div class="adm-item-body">
          <div class="adm-form-group">
            <label class="adm-label">Icon (emoji)</label>
            <input class="adm-input" value="${esc(item.icon || '⭐')}" style="max-width:100px" oninput="meteorList[${i}].icon=this.value">
          </div>
          <div class="adm-grid-2">
            <div class="adm-form-group">
              <label class="adm-label">Label <span class="lang-tag">EN</span></label>
              <input class="adm-input" value="${esc(item.label_en)}" oninput="meteorList[${i}].label_en=this.value;this.closest('.adm-item-card').querySelector('.adm-item-title').textContent=(meteorList[${i}].icon||'⭐')+' '+(this.value||'New Highlight')">
            </div>
            <div class="adm-form-group">
              <label class="adm-label">Label <span class="lang-tag bn">BN</span></label>
              <input class="adm-input" value="${esc(item.label_bn)}" oninput="meteorList[${i}].label_bn=this.value">
            </div>
          </div>
        </div>
      `;
            container.appendChild(card);
        });
    }

    window.admRemoveMeteor = function (i) {
        confirmAction('Remove this highlight?', () => { meteorList.splice(i, 1); renderMeteorList(); });
    };

    document.getElementById('addMeteorBtn')?.addEventListener('click', () => {
        meteorList.push({ id: 'h' + Date.now(), icon: '⭐', label_en: '', label_bn: '', visible: true });
        renderMeteorList();
        setTimeout(() => {
            const cards = document.querySelectorAll('#meteorListContainer .adm-item-card');
            const last = cards[cards.length - 1];
            if (last) { last.querySelector('.adm-item-body').classList.add('expanded'); last.scrollIntoView({ behavior: 'smooth', block: 'nearest' }); }
        }, 50);
    });

    document.getElementById('meteorSaveBtn')?.addEventListener('click', async (e) => {
        const btn = e.currentTarget;
        setSaving(btn, true);
        try {
            await apiPut('/meteor-highlights', {
                title_en: document.getElementById('meteor_title_en').value,
                title_bn: document.getElementById('meteor_title_bn').value,
                items: meteorList,
            });
            showToast('Highlights section saved!', 'success');
        } catch (err) { showToast(err.message, 'error'); }
        setSaving(btn, false);
    });

    /* ─── IMAGE URL INPUT PREVIEWS ──────────────────────────── */
    ['hero_bg_url', 'mentor_photo_url'].forEach(id => {
        const input = document.getElementById(id);
        if (!input) return;
        input.addEventListener('input', () => {
            const prevId = id === 'hero_bg_url' ? 'hero_bg_preview' : 'mentor_photo_preview';
            const prev = document.getElementById(prevId);
            if (prev) {
                prev.src = input.value;
                prev.classList.toggle('visible', !!input.value);
            }
        });
    });

    /* ─── HELPER: escape HTML ───────────────────────────────── */
    function esc(str) {
        if (!str) return '';
        return String(str).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }

    /* ═══════════════════════════════════════════════════════════
       CONTACT INFO
    ═══════════════════════════════════════════════════════════ */
    function populateContactInfo() {
        const ci = content.contact_info || {};
        val('ci_phone', ci.phone);
        val('ci_email', ci.email);
        val('ci_address_en', ci.address?.en);
        val('ci_address_bn', ci.address?.bn);
        val('ci_whatsapp_number', ci.whatsapp_number);
    }

    window.saveContactInfo = async function () {
        const btn = document.querySelector('#section-contact_info .adm-btn-primary');
        if (btn) setSaving(btn, true);
        try {
            await apiPut('/contact-info', {
                phone: document.getElementById('ci_phone').value,
                email: document.getElementById('ci_email').value,
                address_en: document.getElementById('ci_address_en').value,
                address_bn: document.getElementById('ci_address_bn').value,
                whatsapp_number: document.getElementById('ci_whatsapp_number').value,
            });
            showToast('Contact Info saved!', 'success');
        } catch (err) { showToast(err.message, 'error'); }
        if (btn) setSaving(btn, false);
    };

    /* ═══════════════════════════════════════════════════════════
       FOOTER INFO
    ═══════════════════════════════════════════════════════════ */
    function populateFooterInfo() {
        const fi = content.footer_info || {};
        val('fi_tagline_en', fi.tagline?.en);
        val('fi_tagline_bn', fi.tagline?.bn);
        val('fi_copy_en', fi.copyright?.en);
        val('fi_copy_bn', fi.copyright?.bn);
    }

    window.saveFooterInfo = async function () {
        const btn = document.querySelector('#section-footer_info .adm-btn-primary');
        if (btn) setSaving(btn, true);
        try {
            await apiPut('/footer-info', {
                tagline_en: document.getElementById('fi_tagline_en')?.value || '',
                tagline_bn: document.getElementById('fi_tagline_bn')?.value || '',
                copyright_en: document.getElementById('fi_copy_en').value,
                copyright_bn: document.getElementById('fi_copy_bn').value,
            });
            showToast('Footer saved!', 'success');
        } catch (err) { showToast(err.message, 'error'); }
        if (btn) setSaving(btn, false);
    };

    /* ═══════════════════════════════════════════════════════════
       ABOUT PAGE
    ═══════════════════════════════════════════════════════════ */
    function populateAboutPage() {
        const ap = content.about_page || {};
        val('ap_h_title_en', ap.hero_title?.en);
        val('ap_h_title_bn', ap.hero_title?.bn);
        val('ap_h_sub_en', ap.hero_subtitle?.en);
        val('ap_h_sub_bn', ap.hero_subtitle?.bn);
        val('ap_s_title_en', ap.story_title?.en);
        val('ap_s_title_bn', ap.story_title?.bn);
        val('ap_s_p1_en', ap.story_p1?.en);
        val('ap_s_p1_bn', ap.story_p1?.bn);
        val('ap_s_p2_en', ap.story_p2?.en);
        val('ap_s_p2_bn', ap.story_p2?.bn);
        val('ap_s_p3_en', ap.story_p3?.en);
        val('ap_s_p3_bn', ap.story_p3?.bn);
    }

    window.saveAboutPage = async function () {
        const btn = document.querySelector('#section-about_page .adm-btn-primary');
        if (btn) setSaving(btn, true);
        try {
            await apiPut('/about-page', {
                hero_title_en: document.getElementById('ap_h_title_en').value,
                hero_title_bn: document.getElementById('ap_h_title_bn').value,
                hero_subtitle_en: document.getElementById('ap_h_sub_en').value,
                hero_subtitle_bn: document.getElementById('ap_h_sub_bn').value,
                story_title_en: document.getElementById('ap_s_title_en').value,
                story_title_bn: document.getElementById('ap_s_title_bn').value,
                story_p1_en: document.getElementById('ap_s_p1_en').value,
                story_p1_bn: document.getElementById('ap_s_p1_bn').value,
                story_p2_en: document.getElementById('ap_s_p2_en').value,
                story_p2_bn: document.getElementById('ap_s_p2_bn').value,
                story_p3_en: document.getElementById('ap_s_p3_en').value,
                story_p3_bn: document.getElementById('ap_s_p3_bn').value,
            });
            showToast('About Page saved!', 'success');
        } catch (err) { showToast(err.message, 'error'); }
        if (btn) setSaving(btn, false);
    };

    /* ═══════════════════════════════════════════════════════════
       GALLERY PAGE
    ═══════════════════════════════════════════════════════════ */
    let galleryImagesList = [];

    function populateGalleryPage() {
        const gp = content.gallery_page || {};
        val('gp_h_title_en', gp.hero_title?.en);
        val('gp_h_title_bn', gp.hero_title?.bn);
        val('gp_h_sub_en', gp.hero_subtitle?.en);
        val('gp_h_sub_bn', gp.hero_subtitle?.bn);
        val('gp_s_title_en', gp.story_title?.en);
        val('gp_s_title_bn', gp.story_title?.bn);
        val('gp_s_desc_en', gp.story_desc?.en);
        val('gp_s_desc_bn', gp.story_desc?.bn);
        galleryImagesList = JSON.parse(JSON.stringify(gp.images || []));
        renderGalleryImages();
    }

    function renderGalleryImages() {
        const container = document.getElementById('gp_images_container');
        if (!container) return;
        container.innerHTML = '';
        galleryImagesList.forEach((img, i) => {
            const card = document.createElement('div');
            card.className = 'adm-item-card';
            card.innerHTML = `
        <div class="adm-item-card-header">
          <span class="adm-item-num">${i + 1}</span>
          <span class="adm-item-title">${esc(img.image_url) || 'New Image'}</span>
          <div class="adm-item-actions">
            <label style="cursor:pointer; margin-right: 8px;" title="Visible">
              <input type="checkbox" onchange="galleryImagesList[${i}].visible=this.checked" ${img.visible !== false ? 'checked' : ''}>
            </label>
            <button class="adm-btn adm-btn-sm adm-btn-danger adm-btn-icon" onclick="admRemoveGalleryImage(${i})">
              <i class="ri-delete-bin-line"></i>
            </button>
          </div>
        </div>
        <div class="adm-item-body expanded">
          <div class="adm-form-group">
            <label class="adm-label">Image URL</label>
            <div class="adm-image-url-row">
              <input class="adm-input" id="gp_img_url_${i}" value="${esc(img.image_url || '')}" oninput="galleryImagesList[${i}].image_url=this.value;admUpdateImgPreview('gp_img_prev_${i}',this.value)">
              <label class="adm-btn adm-btn-secondary adm-btn-sm" style="cursor:pointer">
                <i class="ri-upload-2-line"></i>
                <input type="file" accept="image/*" style="display:none" onchange="admUploadGalleryImg(this,${i})">
              </label>
            </div>
            <img id="gp_img_prev_${i}" src="${esc(img.image_url || '')}" class="adm-image-preview ${img.image_url ? 'visible' : ''}" alt="preview">
          </div>
        </div>
      `;
            container.appendChild(card);
        });
    }

    window.admRemoveGalleryImage = function (i) {
        confirmAction('Remove this image?', () => { galleryImagesList.splice(i, 1); renderGalleryImages(); });
    };

    window.admUploadGalleryImg = async function (input, i) {
        const file = input.files[0];
        if (!file) return;
        try {
            const url = await uploadImage(file);
            document.getElementById(`gp_img_url_${i}`).value = url;
            galleryImagesList[i].image_url = url;
            window.admUpdateImgPreview(`gp_img_prev_${i}`, url);
            showToast('Image uploaded!', 'success');
        } catch (err) { showToast(err.message, 'error'); }
    };

    window.addGalleryImage = function () {
        galleryImagesList.push({ id: 'img' + Date.now(), image_url: '', visible: true });
        renderGalleryImages();
    };

    window.saveGalleryPage = async function () {
        const btn = document.querySelector('#section-gallery_page .adm-btn-primary');
        if (btn) setSaving(btn, true);
        try {
            await apiPut('/gallery-page', {
                hero_title_en: document.getElementById('gp_h_title_en').value,
                hero_title_bn: document.getElementById('gp_h_title_bn').value,
                hero_subtitle_en: document.getElementById('gp_h_sub_en').value,
                hero_subtitle_bn: document.getElementById('gp_h_sub_bn').value,
                story_title_en: document.getElementById('gp_s_title_en').value,
                story_title_bn: document.getElementById('gp_s_title_bn').value,
                story_desc_en: document.getElementById('gp_s_desc_en').value,
                story_desc_bn: document.getElementById('gp_s_desc_bn').value,
                images: galleryImagesList,
            });
            showToast('Gallery Page saved!', 'success');
        } catch (err) { showToast(err.message, 'error'); }
        if (btn) setSaving(btn, false);
    };

    /* ═══════════════════════════════════════════════════════════
       CONTACT PAGE
    ═══════════════════════════════════════════════════════════ */
    function populateContactPage() {
        const cp = content.contact_page || {};
        val('cp_h_title_en', cp.hero_title?.en);
        val('cp_h_title_bn', cp.hero_title?.bn);
        val('cp_h_sub_en', cp.hero_subtitle?.en);
        val('cp_h_sub_bn', cp.hero_subtitle?.bn);
    }

    window.saveContactPage = async function () {
        const btn = document.querySelector('#section-contact_page .adm-btn-primary');
        if (btn) setSaving(btn, true);
        try {
            await apiPut('/contact-page', {
                hero_title_en: document.getElementById('cp_h_title_en').value,
                hero_title_bn: document.getElementById('cp_h_title_bn').value,
                hero_subtitle_en: document.getElementById('cp_h_sub_en').value,
                hero_subtitle_bn: document.getElementById('cp_h_sub_bn').value,
            });
            showToast('Contact Page saved!', 'success');
        } catch (err) { showToast(err.message, 'error'); }
        if (btn) setSaving(btn, false);
    };

    /* ═══════════════════════════════════════════════════════════
       THANK YOU PAGE
    ═══════════════════════════════════════════════════════════ */
    function populateThankyouPage() {
        const tp = content.thankyou_page || {};
        val('tp_title_en', tp.title?.en);
        val('tp_title_bn', tp.title?.bn);
        val('tp_msg_en', tp.message?.en);
        val('tp_msg_bn', tp.message?.bn);
    }

    window.saveThankyouPage = async function () {
        const btn = document.querySelector('#section-thankyou_page .adm-btn-primary');
        if (btn) setSaving(btn, true);
        try {
            await apiPut('/thankyou-page', {
                title_en: document.getElementById('tp_title_en').value,
                title_bn: document.getElementById('tp_title_bn').value,
                message_en: document.getElementById('tp_msg_en').value,
                message_bn: document.getElementById('tp_msg_bn').value,
            });
            showToast('Thank You Page saved!', 'success');
        } catch (err) { showToast(err.message, 'error'); }
        if (btn) setSaving(btn, false);
    };

    /* ═══════════════════════════════════════════════════════════
       MUSIC SETTINGS
    ═══════════════════════════════════════════════════════════ */
    function populateMusicSettings() {
        const ms = content.music_settings || {};
        val('ms_global_url', ms.global_default_url);
        val('ms_home_url', ms.home_music_url);
        val('ms_about_url', ms.about_music_url);
        val('ms_programs_url', ms.programs_music_url);
        val('ms_gallery_url', ms.gallery_music_url);
        val('ms_contact_url', ms.contact_music_url);
        val('ms_thankyou_url', ms.thankyou_music_url);
    }

    document.getElementById('musicSettingsSaveBtn')?.addEventListener('click', async (e) => {
        const btn = e.currentTarget;
        setSaving(btn, true);
        try {
            await apiPut('/music-settings', {
                global_default_url: document.getElementById('ms_global_url').value,
                home_music_url: document.getElementById('ms_home_url').value,
                about_music_url: document.getElementById('ms_about_url').value,
                programs_music_url: document.getElementById('ms_programs_url').value,
                gallery_music_url: document.getElementById('ms_gallery_url').value,
                contact_music_url: document.getElementById('ms_contact_url').value,
                thankyou_music_url: document.getElementById('ms_thankyou_url').value,
            });
            showToast('Music Settings saved!', 'success');
        } catch (err) { showToast(err.message, 'error'); }
        setSaving(btn, false);
    });

    window.uploadAudioField = async function (input, urlFieldId) {
        const file = input.files[0];
        if (!file) return;
        try {
            // Reusing uploadImage endpoint which accepts any file to S3
            const url = await uploadImage(file); 
            document.getElementById(urlFieldId).value = url;
            showToast('Audio uploaded!', 'success');
        } catch (err) { showToast(err.message, 'error'); }
    };

    /* ═══════════════════════════════════════════════════════════
       INIT
    ═══════════════════════════════════════════════════════════ */
    loadContent();
    showSection('hero');

})();
