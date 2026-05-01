import re

def patch_admin_html():
    filepath = "templates/admin.html"
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Insert Sidebar Nav Items
    sidebar_insert = """
          <a href="#" class="adm-sidebar-link" data-section="contact_info"><i class="ri-contacts-line"></i> Contact Info</a>
          <a href="#" class="adm-sidebar-link" data-section="footer_info"><i class="ri-layout-bottom-line"></i> Footer</a>
          <a href="#" class="adm-sidebar-link" data-section="about_page"><i class="ri-information-line"></i> About Page</a>
          <a href="#" class="adm-sidebar-link" data-section="gallery_page"><i class="ri-image-line"></i> Gallery Page</a>
          <a href="#" class="adm-sidebar-link" data-section="contact_page"><i class="ri-contacts-book-line"></i> Contact Page</a>
          <a href="#" class="adm-sidebar-link" data-section="thankyou_page"><i class="ri-thumb-up-line"></i> Thank You Page</a>
"""
    if "data-section=\"contact_info\"" not in content:
        # Find where to insert in sidebar
        pattern = r'(<a href="#" class="adm-sidebar-link" data-section="meteor">\s*<i class="ri-sparkling-line"></i> Highlights Bar\s*</a>)'
        content = re.sub(pattern, r'\1' + sidebar_insert, content)

    # 2. Insert Panels
    panels_insert = """
        <!-- CONTACT INFO PANEL -->
        <div id="contact_info" class="adm-panel">
          <div class="adm-panel-header">
            <h2>Contact Info (Global)</h2>
            <button class="adm-btn adm-btn-primary" onclick="saveContactInfo()">Save Contact Info</button>
          </div>
          <div class="adm-card">
            <div class="adm-form-group">
              <label class="adm-label">Phone Number</label>
              <input type="text" class="adm-input" id="ci_phone">
            </div>
            <div class="adm-form-group">
              <label class="adm-label">Email Address</label>
              <input type="text" class="adm-input" id="ci_email">
            </div>
            <div class="adm-form-group">
              <label class="adm-label">Address (English)</label>
              <input type="text" class="adm-input" id="ci_address_en">
            </div>
            <div class="adm-form-group">
              <label class="adm-label">Address (Bengali)</label>
              <input type="text" class="adm-input" id="ci_address_bn">
            </div>
            <div class="adm-form-group">
              <label class="adm-label">WhatsApp Number (e.g., 917908875949)</label>
              <input type="text" class="adm-input" id="ci_whatsapp_number">
            </div>
          </div>
        </div>

        <!-- FOOTER INFO PANEL -->
        <div id="footer_info" class="adm-panel">
          <div class="adm-panel-header">
            <h2>Footer Content</h2>
            <button class="adm-btn adm-btn-primary" onclick="saveFooterInfo()">Save Footer</button>
          </div>
          <div class="adm-card">
            <div class="adm-form-group">
              <label class="adm-label">Copyright Text (English)</label>
              <input type="text" class="adm-input" id="fi_copy_en">
            </div>
            <div class="adm-form-group">
              <label class="adm-label">Copyright Text (Bengali)</label>
              <input type="text" class="adm-input" id="fi_copy_bn">
            </div>
          </div>
        </div>

        <!-- ABOUT PAGE PANEL -->
        <div id="about_page" class="adm-panel">
          <div class="adm-panel-header">
            <h2>About Page Content</h2>
            <button class="adm-btn adm-btn-primary" onclick="saveAboutPage()">Save About Page</button>
          </div>
          <div class="adm-card">
            <h3>Hero Section</h3>
            <div class="adm-grid-2">
              <div class="adm-form-group"><label class="adm-label">Title (EN)</label><input type="text" class="adm-input" id="ap_h_title_en"></div>
              <div class="adm-form-group"><label class="adm-label">Title (BN)</label><input type="text" class="adm-input" id="ap_h_title_bn"></div>
            </div>
            <div class="adm-grid-2">
              <div class="adm-form-group"><label class="adm-label">Subtitle (EN)</label><textarea class="adm-input" id="ap_h_sub_en" rows="2"></textarea></div>
              <div class="adm-form-group"><label class="adm-label">Subtitle (BN)</label><textarea class="adm-input" id="ap_h_sub_bn" rows="2"></textarea></div>
            </div>
            <hr>
            <h3>My Story</h3>
            <div class="adm-grid-2">
              <div class="adm-form-group"><label class="adm-label">Story Title (EN)</label><input type="text" class="adm-input" id="ap_s_title_en"></div>
              <div class="adm-form-group"><label class="adm-label">Story Title (BN)</label><input type="text" class="adm-input" id="ap_s_title_bn"></div>
            </div>
            <div class="adm-grid-2">
              <div class="adm-form-group"><label class="adm-label">Paragraph 1 (EN)</label><textarea class="adm-input" id="ap_s_p1_en" rows="4"></textarea></div>
              <div class="adm-form-group"><label class="adm-label">Paragraph 1 (BN)</label><textarea class="adm-input" id="ap_s_p1_bn" rows="4"></textarea></div>
            </div>
            <div class="adm-grid-2">
              <div class="adm-form-group"><label class="adm-label">Paragraph 2 (EN)</label><textarea class="adm-input" id="ap_s_p2_en" rows="4"></textarea></div>
              <div class="adm-form-group"><label class="adm-label">Paragraph 2 (BN)</label><textarea class="adm-input" id="ap_s_p2_bn" rows="4"></textarea></div>
            </div>
            <div class="adm-grid-2">
              <div class="adm-form-group"><label class="adm-label">Paragraph 3 (EN)</label><textarea class="adm-input" id="ap_s_p3_en" rows="4"></textarea></div>
              <div class="adm-form-group"><label class="adm-label">Paragraph 3 (BN)</label><textarea class="adm-input" id="ap_s_p3_bn" rows="4"></textarea></div>
            </div>
          </div>
        </div>

        <!-- GALLERY PAGE PANEL -->
        <div id="gallery_page" class="adm-panel">
          <div class="adm-panel-header">
            <h2>Gallery Page Content</h2>
            <button class="adm-btn adm-btn-primary" onclick="saveGalleryPage()">Save Gallery Page</button>
          </div>
          <div class="adm-card">
            <h3>Hero Section</h3>
            <div class="adm-grid-2">
              <div class="adm-form-group"><label class="adm-label">Title (EN)</label><input type="text" class="adm-input" id="gp_h_title_en"></div>
              <div class="adm-form-group"><label class="adm-label">Title (BN)</label><input type="text" class="adm-input" id="gp_h_title_bn"></div>
            </div>
            <div class="adm-grid-2">
              <div class="adm-form-group"><label class="adm-label">Subtitle (EN)</label><textarea class="adm-input" id="gp_h_sub_en" rows="2"></textarea></div>
              <div class="adm-form-group"><label class="adm-label">Subtitle (BN)</label><textarea class="adm-input" id="gp_h_sub_bn" rows="2"></textarea></div>
            </div>
            <hr>
            <h3>Story Info</h3>
            <div class="adm-grid-2">
              <div class="adm-form-group"><label class="adm-label">Story Title (EN)</label><input type="text" class="adm-input" id="gp_s_title_en"></div>
              <div class="adm-form-group"><label class="adm-label">Story Title (BN)</label><input type="text" class="adm-input" id="gp_s_title_bn"></div>
            </div>
            <div class="adm-grid-2">
              <div class="adm-form-group"><label class="adm-label">Description (EN)</label><textarea class="adm-input" id="gp_s_desc_en" rows="3"></textarea></div>
              <div class="adm-form-group"><label class="adm-label">Description (BN)</label><textarea class="adm-input" id="gp_s_desc_bn" rows="3"></textarea></div>
            </div>
            <hr>
            <h3>Images</h3>
            <div id="gp_images_container"></div>
            <button class="adm-btn adm-btn-secondary" onclick="addGalleryImage()" style="margin-top: 1rem">+ Add Image</button>
          </div>
        </div>

        <!-- CONTACT PAGE PANEL -->
        <div id="contact_page" class="adm-panel">
          <div class="adm-panel-header">
            <h2>Contact Page Content</h2>
            <button class="adm-btn adm-btn-primary" onclick="saveContactPage()">Save Contact Page</button>
          </div>
          <div class="adm-card">
            <h3>Hero Section</h3>
            <div class="adm-grid-2">
              <div class="adm-form-group"><label class="adm-label">Title (EN)</label><input type="text" class="adm-input" id="cp_h_title_en"></div>
              <div class="adm-form-group"><label class="adm-label">Title (BN)</label><input type="text" class="adm-input" id="cp_h_title_bn"></div>
            </div>
            <div class="adm-grid-2">
              <div class="adm-form-group"><label class="adm-label">Subtitle (EN)</label><textarea class="adm-input" id="cp_h_sub_en" rows="2"></textarea></div>
              <div class="adm-form-group"><label class="adm-label">Subtitle (BN)</label><textarea class="adm-input" id="cp_h_sub_bn" rows="2"></textarea></div>
            </div>
          </div>
        </div>

        <!-- THANKYOU PAGE PANEL -->
        <div id="thankyou_page" class="adm-panel">
          <div class="adm-panel-header">
            <h2>Thank You Page Content</h2>
            <button class="adm-btn adm-btn-primary" onclick="saveThankyouPage()">Save Thank You Page</button>
          </div>
          <div class="adm-card">
            <div class="adm-grid-2">
              <div class="adm-form-group"><label class="adm-label">Title (EN)</label><input type="text" class="adm-input" id="tp_title_en"></div>
              <div class="adm-form-group"><label class="adm-label">Title (BN)</label><input type="text" class="adm-input" id="tp_title_bn"></div>
            </div>
            <div class="adm-grid-2">
              <div class="adm-form-group"><label class="adm-label">Message (EN)</label><textarea class="adm-input" id="tp_msg_en" rows="3"></textarea></div>
              <div class="adm-form-group"><label class="adm-label">Message (BN)</label><textarea class="adm-input" id="tp_msg_bn" rows="3"></textarea></div>
            </div>
          </div>
        </div>
"""
    if "id=\"contact_info\" class=\"adm-panel\"" not in content:
        # Find where to insert panels
        pattern2 = r'(</main>\s*</div>)'
        content = re.sub(pattern2, panels_insert + r'\n\1', content)

    # 3. Insert load/save logic
    js_logic_insert = """
      // --- CONTACT INFO ---
      function renderContactInfo() {
        const ci = g_content.contact_info || {};
        const address = ci.address || {};
        document.getElementById('ci_phone').value = ci.phone || '';
        document.getElementById('ci_email').value = ci.email || '';
        document.getElementById('ci_address_en').value = address.en || '';
        document.getElementById('ci_address_bn').value = address.bn || '';
        document.getElementById('ci_whatsapp_number').value = ci.whatsapp_number || '';
      }
      async function saveContactInfo() {
        const payload = {
          phone: document.getElementById('ci_phone').value,
          email: document.getElementById('ci_email').value,
          address_en: document.getElementById('ci_address_en').value,
          address_bn: document.getElementById('ci_address_bn').value,
          whatsapp_number: document.getElementById('ci_whatsapp_number').value
        };
        await saveSection("/admin/contact-info", payload);
      }

      // --- FOOTER INFO ---
      function renderFooterInfo() {
        const fi = g_content.footer_info || {};
        const copy = fi.copyright || {};
        document.getElementById('fi_copy_en').value = copy.en || '';
        document.getElementById('fi_copy_bn').value = copy.bn || '';
      }
      async function saveFooterInfo() {
        const payload = {
          copyright_en: document.getElementById('fi_copy_en').value,
          copyright_bn: document.getElementById('fi_copy_bn').value
        };
        await saveSection("/admin/footer-info", payload);
      }

      // --- ABOUT PAGE ---
      function renderAboutPage() {
        const ap = g_content.about_page || {};
        document.getElementById('ap_h_title_en').value = (ap.hero_title||{}).en || '';
        document.getElementById('ap_h_title_bn').value = (ap.hero_title||{}).bn || '';
        document.getElementById('ap_h_sub_en').value = (ap.hero_subtitle||{}).en || '';
        document.getElementById('ap_h_sub_bn').value = (ap.hero_subtitle||{}).bn || '';
        document.getElementById('ap_s_title_en').value = (ap.story_title||{}).en || '';
        document.getElementById('ap_s_title_bn').value = (ap.story_title||{}).bn || '';
        document.getElementById('ap_s_p1_en').value = (ap.story_p1||{}).en || '';
        document.getElementById('ap_s_p1_bn').value = (ap.story_p1||{}).bn || '';
        document.getElementById('ap_s_p2_en').value = (ap.story_p2||{}).en || '';
        document.getElementById('ap_s_p2_bn').value = (ap.story_p2||{}).bn || '';
        document.getElementById('ap_s_p3_en').value = (ap.story_p3||{}).en || '';
        document.getElementById('ap_s_p3_bn').value = (ap.story_p3||{}).bn || '';
      }
      async function saveAboutPage() {
        await saveSection("/admin/about-page", {
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
          story_p3_bn: document.getElementById('ap_s_p3_bn').value
        });
      }

      // --- GALLERY PAGE ---
      function renderGalleryPage() {
        const gp = g_content.gallery_page || {};
        document.getElementById('gp_h_title_en').value = (gp.hero_title||{}).en || '';
        document.getElementById('gp_h_title_bn').value = (gp.hero_title||{}).bn || '';
        document.getElementById('gp_h_sub_en').value = (gp.hero_subtitle||{}).en || '';
        document.getElementById('gp_h_sub_bn').value = (gp.hero_subtitle||{}).bn || '';
        document.getElementById('gp_s_title_en').value = (gp.story_title||{}).en || '';
        document.getElementById('gp_s_title_bn').value = (gp.story_title||{}).bn || '';
        document.getElementById('gp_s_desc_en').value = (gp.story_desc||{}).en || '';
        document.getElementById('gp_s_desc_bn').value = (gp.story_desc||{}).bn || '';
        
        const container = document.getElementById('gp_images_container');
        container.innerHTML = '';
        const images = gp.images || [];
        images.forEach(img => addGalleryImageUI(img.id, img.image_url));
      }
      function addGalleryImageUI(id, url) {
        const div = document.createElement('div');
        div.className = 'adm-list-item';
        div.innerHTML = `
          <input type="hidden" class="gp_img_id" value="${id || ''}">
          <div class="adm-grid-1" style="grid-template-columns: 1fr auto auto;">
            <input type="text" class="adm-input gp_img_url" value="${url || ''}" placeholder="Image URL">
            <button class="adm-btn adm-btn-secondary" onclick="document.getElementById('gp_img_upload_${id}').click()"><i class="ri-upload-2-line"></i></button>
            <input type="file" id="gp_img_upload_${id}" style="display:none;" onchange="uploadImageGallery(this, this.previousElementSibling.previousElementSibling)">
            <button class="adm-btn adm-btn-danger" onclick="this.parentElement.parentElement.remove()"><i class="ri-delete-bin-line"></i></button>
          </div>
        `;
        document.getElementById('gp_images_container').appendChild(div);
      }
      function addGalleryImage() {
        addGalleryImageUI('img_' + Date.now(), '');
      }
      async function uploadImageGallery(fileInput, urlInput) {
        if (!fileInput.files.length) return;
        try {
          const url = await uploadMedia(fileInput.files[0]);
          urlInput.value = url;
          showToast('Image uploaded', 'success');
        } catch (e) {
          showToast(e.message, 'error');
        }
      }
      async function saveGalleryPage() {
        const images = [];
        document.querySelectorAll('#gp_images_container .adm-list-item').forEach(el => {
          images.push({
            id: el.querySelector('.gp_img_id').value,
            image_url: el.querySelector('.gp_img_url').value
          });
        });
        await saveSection("/admin/gallery-page", {
          hero_title_en: document.getElementById('gp_h_title_en').value,
          hero_title_bn: document.getElementById('gp_h_title_bn').value,
          hero_subtitle_en: document.getElementById('gp_h_sub_en').value,
          hero_subtitle_bn: document.getElementById('gp_h_sub_bn').value,
          story_title_en: document.getElementById('gp_s_title_en').value,
          story_title_bn: document.getElementById('gp_s_title_bn').value,
          story_desc_en: document.getElementById('gp_s_desc_en').value,
          story_desc_bn: document.getElementById('gp_s_desc_bn').value,
          images: images
        });
      }

      // --- CONTACT PAGE ---
      function renderContactPage() {
        const cp = g_content.contact_page || {};
        document.getElementById('cp_h_title_en').value = (cp.hero_title||{}).en || '';
        document.getElementById('cp_h_title_bn').value = (cp.hero_title||{}).bn || '';
        document.getElementById('cp_h_sub_en').value = (cp.hero_subtitle||{}).en || '';
        document.getElementById('cp_h_sub_bn').value = (cp.hero_subtitle||{}).bn || '';
      }
      async function saveContactPage() {
        await saveSection("/admin/contact-page", {
          hero_title_en: document.getElementById('cp_h_title_en').value,
          hero_title_bn: document.getElementById('cp_h_title_bn').value,
          hero_subtitle_en: document.getElementById('cp_h_sub_en').value,
          hero_subtitle_bn: document.getElementById('cp_h_sub_bn').value
        });
      }

      // --- THANKYOU PAGE ---
      function renderThankyouPage() {
        const tp = g_content.thankyou_page || {};
        document.getElementById('tp_title_en').value = (tp.title||{}).en || '';
        document.getElementById('tp_title_bn').value = (tp.title||{}).bn || '';
        document.getElementById('tp_msg_en').value = (tp.message||{}).en || '';
        document.getElementById('tp_msg_bn').value = (tp.message||{}).bn || '';
      }
      async function saveThankyouPage() {
        await saveSection("/admin/thankyou-page", {
          title_en: document.getElementById('tp_title_en').value,
          title_bn: document.getElementById('tp_title_bn').value,
          message_en: document.getElementById('tp_msg_en').value,
          message_bn: document.getElementById('tp_msg_bn').value
        });
      }
"""
    if "function renderContactInfo()" not in content:
        # Insert before initAll()
        pattern3 = r'(function initAll\(\) \{)'
        content = re.sub(pattern3, js_logic_insert + r'\n      \1', content)
        
        # Also need to call these in populateAll()
        populate_insert = """
        renderContactInfo();
        renderFooterInfo();
        renderAboutPage();
        renderGalleryPage();
        renderContactPage();
        renderThankyouPage();
"""
        pattern4 = r'(renderMeteorHighlights\(\);\n      \})'
        content = re.sub(pattern4, r'renderMeteorHighlights();\n' + populate_insert + r'      }', content)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
        
    print("Patched admin.html successfully.")

if __name__ == "__main__":
    patch_admin_html()
