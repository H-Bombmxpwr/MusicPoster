/**
 * Custom Color Picker Component
 * A beautiful, accessible color picker with HSV control
 */

class ColorPicker {
    constructor() {
        this.modal = null;
        this.currentColor = { h: 0, s: 100, v: 100 };
        this.originalColor = '#ffffff';
        this.callback = null;
        this.isBackground = false;
        this.recentColors = this.loadRecentColors();
        
        this.isDraggingArea = false;
        this.isDraggingHue = false;

        this.init();
    }

    init() {
        this.createModal();
        this.bindEvents();
    }

    createModal() {
        // Create overlay
        this.overlay = document.createElement('div');
        this.overlay.className = 'color-picker-modal-overlay';
        this.overlay.innerHTML = `
            <div class="color-picker-modal">
                <div class="color-picker-header">
                    <span class="color-picker-title">Choose Color</span>
                    <button class="color-picker-close" aria-label="Close">
                        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                        </svg>
                    </button>
                </div>
                
                <div class="color-picker-area" id="cp-area">
                    <div class="color-picker-area-gradient"></div>
                    <div class="color-picker-area-cursor" id="cp-area-cursor"></div>
                </div>
                
                <div class="color-picker-hue" id="cp-hue">
                    <div class="color-picker-hue-cursor" id="cp-hue-cursor"></div>
                </div>
                
                <div class="color-picker-preview-row">
                    <div class="color-picker-preview" id="cp-preview"></div>
                    <div class="color-picker-input-group">
                        <div class="color-picker-input-label">Hex Color</div>
                        <input type="text" class="color-picker-hex-input" id="cp-hex" maxlength="7" placeholder="#FFFFFF">
                    </div>
                </div>
                
                <div class="color-picker-recent" id="cp-recent-container">
                    <div class="color-picker-recent-label">Recent Colors</div>
                    <div class="color-picker-recent-colors" id="cp-recent"></div>
                </div>
                
                <div class="color-picker-buttons">
                    <button class="color-picker-btn color-picker-btn-cancel" id="cp-cancel">Cancel</button>
                    <button class="color-picker-btn color-picker-btn-apply" id="cp-apply">Apply</button>
                </div>
            </div>
        `;

        document.body.appendChild(this.overlay);

        // Cache elements
        this.modal = this.overlay.querySelector('.color-picker-modal');
        this.area = document.getElementById('cp-area');
        this.areaCursor = document.getElementById('cp-area-cursor');
        this.hueSlider = document.getElementById('cp-hue');
        this.hueCursor = document.getElementById('cp-hue-cursor');
        this.preview = document.getElementById('cp-preview');
        this.hexInput = document.getElementById('cp-hex');
        this.recentContainer = document.getElementById('cp-recent');
        this.cancelBtn = document.getElementById('cp-cancel');
        this.applyBtn = document.getElementById('cp-apply');
        this.closeBtn = this.overlay.querySelector('.color-picker-close');
    }

    bindEvents() {
        // Close button
        this.closeBtn.addEventListener('click', () => this.close());
        this.cancelBtn.addEventListener('click', () => this.close());
        
        // Apply button
        this.applyBtn.addEventListener('click', () => this.apply());

        // Click outside to close
        this.overlay.addEventListener('click', (e) => {
            if (e.target === this.overlay) {
                this.close();
            }
        });

        // Escape key to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.overlay.classList.contains('active')) {
                this.close();
            }
            if (e.key === 'Enter' && this.overlay.classList.contains('active')) {
                this.apply();
            }
        });

        // Color area interactions
        this.area.addEventListener('mousedown', (e) => this.startAreaDrag(e));
        this.area.addEventListener('touchstart', (e) => this.startAreaDrag(e), { passive: false });

        // Hue slider interactions
        this.hueSlider.addEventListener('mousedown', (e) => this.startHueDrag(e));
        this.hueSlider.addEventListener('touchstart', (e) => this.startHueDrag(e), { passive: false });

        // Global mouse/touch move and up
        document.addEventListener('mousemove', (e) => this.onDrag(e));
        document.addEventListener('touchmove', (e) => this.onDrag(e), { passive: false });
        document.addEventListener('mouseup', () => this.stopDrag());
        document.addEventListener('touchend', () => this.stopDrag());

        // Hex input
        this.hexInput.addEventListener('input', (e) => this.onHexInput(e));
        this.hexInput.addEventListener('blur', () => this.validateHexInput());
    }

    open(initialColor, callback, isBackground = false) {
        this.callback = callback;
        this.isBackground = isBackground;
        this.originalColor = initialColor || '#ffffff';
        
        // Parse initial color
        const hsv = this.hexToHsv(this.originalColor);
        this.currentColor = hsv;

        // Update title
        const title = this.overlay.querySelector('.color-picker-title');
        title.textContent = isBackground ? 'Background Color' : 'Text Color';

        // Update UI
        this.updateFromHsv();
        this.renderRecentColors();

        // Show modal
        this.overlay.classList.add('active');
    }

    close() {
        this.overlay.classList.remove('active');
        this.callback = null;
    }

    apply() {
        const hex = this.hsvToHex(this.currentColor.h, this.currentColor.s, this.currentColor.v);
        
        // Save to recent colors
        this.addRecentColor(hex);

        // Call callback
        if (this.callback) {
            this.callback(hex);
        }

        this.close();
    }

    // Drag handling
    startAreaDrag(e) {
        e.preventDefault();
        this.isDraggingArea = true;
        this.updateAreaFromEvent(e);
    }

    startHueDrag(e) {
        e.preventDefault();
        this.isDraggingHue = true;
        this.updateHueFromEvent(e);
    }

    onDrag(e) {
        if (this.isDraggingArea) {
            e.preventDefault();
            this.updateAreaFromEvent(e);
        }
        if (this.isDraggingHue) {
            e.preventDefault();
            this.updateHueFromEvent(e);
        }
    }

    stopDrag() {
        this.isDraggingArea = false;
        this.isDraggingHue = false;
    }

    updateAreaFromEvent(e) {
        const rect = this.area.getBoundingClientRect();
        const clientX = e.touches ? e.touches[0].clientX : e.clientX;
        const clientY = e.touches ? e.touches[0].clientY : e.clientY;

        let x = (clientX - rect.left) / rect.width;
        let y = (clientY - rect.top) / rect.height;

        x = Math.max(0, Math.min(1, x));
        y = Math.max(0, Math.min(1, y));

        this.currentColor.s = x * 100;
        this.currentColor.v = (1 - y) * 100;

        this.updateFromHsv();
    }

    updateHueFromEvent(e) {
        const rect = this.hueSlider.getBoundingClientRect();
        const clientX = e.touches ? e.touches[0].clientX : e.clientX;

        let x = (clientX - rect.left) / rect.width;
        x = Math.max(0, Math.min(1, x));

        this.currentColor.h = x * 360;
        this.updateFromHsv();
    }

    updateFromHsv() {
        const { h, s, v } = this.currentColor;

        // Update area background (hue)
        const hueColor = this.hsvToHex(h, 100, 100);
        this.area.style.backgroundColor = hueColor;

        // Update area cursor position
        const areaRect = this.area.getBoundingClientRect();
        this.areaCursor.style.left = `${s}%`;
        this.areaCursor.style.top = `${100 - v}%`;

        // Update hue cursor position
        this.hueCursor.style.left = `${(h / 360) * 100}%`;
        this.hueCursor.style.backgroundColor = hueColor;

        // Update preview and hex
        const hex = this.hsvToHex(h, s, v);
        this.preview.style.backgroundColor = hex;
        this.hexInput.value = hex.toUpperCase();

        // Update area cursor color for visibility
        this.areaCursor.style.backgroundColor = hex;
    }

    onHexInput(e) {
        let value = e.target.value;
        
        // Auto-add # if missing
        if (value && !value.startsWith('#')) {
            value = '#' + value;
            e.target.value = value;
        }

        // Validate and update if valid
        if (/^#[0-9A-Fa-f]{6}$/.test(value)) {
            const hsv = this.hexToHsv(value);
            this.currentColor = hsv;
            this.updateFromHsv();
        }
    }

    validateHexInput() {
        const value = this.hexInput.value;
        if (!/^#[0-9A-Fa-f]{6}$/.test(value)) {
            // Reset to current color
            const hex = this.hsvToHex(this.currentColor.h, this.currentColor.s, this.currentColor.v);
            this.hexInput.value = hex.toUpperCase();
        }
    }

    // Recent colors
    loadRecentColors() {
        try {
            const stored = localStorage.getItem('colorPickerRecent');
            return stored ? JSON.parse(stored) : [];
        } catch {
            return [];
        }
    }

    saveRecentColors() {
        try {
            localStorage.setItem('colorPickerRecent', JSON.stringify(this.recentColors));
        } catch {
            // Ignore storage errors
        }
    }

    addRecentColor(hex) {
        // Remove if already exists
        this.recentColors = this.recentColors.filter(c => c.toLowerCase() !== hex.toLowerCase());
        
        // Add to front
        this.recentColors.unshift(hex);
        
        // Keep only last 8
        this.recentColors = this.recentColors.slice(0, 8);
        
        this.saveRecentColors();
    }

    renderRecentColors() {
        if (this.recentColors.length === 0) {
            document.getElementById('cp-recent-container').style.display = 'none';
            return;
        }

        document.getElementById('cp-recent-container').style.display = 'block';
        
        this.recentContainer.innerHTML = this.recentColors.map(color => `
            <div class="color-picker-recent-color" 
                 style="background-color: ${color};" 
                 data-color="${color}"
                 title="${color}"></div>
        `).join('');

        // Bind click events
        this.recentContainer.querySelectorAll('.color-picker-recent-color').forEach(el => {
            el.addEventListener('click', () => {
                const color = el.dataset.color;
                const hsv = this.hexToHsv(color);
                this.currentColor = hsv;
                this.updateFromHsv();
            });
        });
    }

    // Color conversion utilities
    hexToHsv(hex) {
        // Remove #
        hex = hex.replace('#', '');
        
        const r = parseInt(hex.substring(0, 2), 16) / 255;
        const g = parseInt(hex.substring(2, 4), 16) / 255;
        const b = parseInt(hex.substring(4, 6), 16) / 255;

        const max = Math.max(r, g, b);
        const min = Math.min(r, g, b);
        const d = max - min;

        let h = 0;
        const s = max === 0 ? 0 : (d / max) * 100;
        const v = max * 100;

        if (d !== 0) {
            switch (max) {
                case r:
                    h = ((g - b) / d + (g < b ? 6 : 0)) * 60;
                    break;
                case g:
                    h = ((b - r) / d + 2) * 60;
                    break;
                case b:
                    h = ((r - g) / d + 4) * 60;
                    break;
            }
        }

        return { h, s, v };
    }

    hsvToHex(h, s, v) {
        s = s / 100;
        v = v / 100;

        const c = v * s;
        const x = c * (1 - Math.abs(((h / 60) % 2) - 1));
        const m = v - c;

        let r, g, b;

        if (h < 60) { r = c; g = x; b = 0; }
        else if (h < 120) { r = x; g = c; b = 0; }
        else if (h < 180) { r = 0; g = c; b = x; }
        else if (h < 240) { r = 0; g = x; b = c; }
        else if (h < 300) { r = x; g = 0; b = c; }
        else { r = c; g = 0; b = x; }

        r = Math.round((r + m) * 255);
        g = Math.round((g + m) * 255);
        b = Math.round((b + m) * 255);

        return '#' + [r, g, b].map(x => x.toString(16).padStart(2, '0')).join('');
    }
}

// Create global instance
let colorPickerInstance = null;

function openColorPicker(initialColor, callback, isBackground = false) {
    if (!colorPickerInstance) {
        colorPickerInstance = new ColorPicker();
    }
    colorPickerInstance.open(initialColor, callback, isBackground);
}

// Export for global use
window.openColorPicker = openColorPicker;