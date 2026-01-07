/**
 * Download Modal Component
 * Handles poster download with resolution, format, and DPI options
 */

class DownloadModal {
    constructor() {
        this.modal = null;
        this.isOpen = false;
        
        // Default options
        this.options = {
            resolution: 'high',
            format: 'png',
            dpi: 300
        };
        
        // Resolution presets info
        this.resolutions = {
            low: { name: 'Low', width: 370, height: 600, desc: 'Web preview' },
            medium: { name: 'Medium', width: 740, height: 1200, desc: 'Standard' },
            high: { name: 'High', width: 1480, height: 2400, desc: 'Print ready' },
            ultra: { name: 'Ultra', width: 2220, height: 3600, desc: 'Large print' }
        };
        
        this.init();
    }
    
    init() {
        this.createModal();
        this.bindEvents();
    }
    
    createModal() {
        const overlay = document.createElement('div');
        overlay.className = 'download-modal-overlay';
        overlay.id = 'download-modal';
        
        overlay.innerHTML = `
            <div class="download-modal">
                <div class="download-modal-header">
                    <h3 class="download-modal-title">
                        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/>
                        </svg>
                        Download Options
                    </h3>
                    <button class="download-modal-close" aria-label="Close">
                        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                        </svg>
                    </button>
                </div>
                
                <!-- Resolution Selection -->
                <div class="download-option-group">
                    <label class="download-option-label">Resolution</label>
                    <div class="resolution-options">
                        ${Object.entries(this.resolutions).map(([key, val]) => `
                            <div class="resolution-card ${key === this.options.resolution ? 'selected' : ''}" data-resolution="${key}">
                                <div class="resolution-card-name">${val.name}</div>
                                <div class="resolution-card-size">${val.width} × ${val.height}</div>
                            </div>
                        `).join('')}
                    </div>
                </div>
                
                <!-- Format Selection -->
                <div class="download-option-group">
                    <label class="download-option-label">Format</label>
                    <div class="format-options">
                        <div class="format-card selected" data-format="png">
                            <div class="format-card-icon">
                                <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/>
                                </svg>
                            </div>
                            <div class="format-card-info">
                                <div class="format-card-name">PNG</div>
                                <div class="format-card-desc">Lossless, transparent</div>
                            </div>
                        </div>
                        <div class="format-card" data-format="svg">
                            <div class="format-card-icon">
                                <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                                </svg>
                            </div>
                            <div class="format-card-info">
                                <div class="format-card-name">SVG</div>
                                <div class="format-card-desc">Vector, scalable</div>
                            </div>
                        </div>
                    </div>
                    <div class="svg-note" id="svg-note">
                        ⚠️ SVG exports the layout as vector graphics. Album art is embedded as an image link.
                    </div>
                </div>
                
                <!-- DPI Selection (PNG only) -->
                <div class="download-option-group" id="dpi-group">
                    <label class="download-option-label">Print Quality (DPI)</label>
                    <div class="dpi-container">
                        <div class="dpi-header">
                            <span class="dpi-label">Dots per inch</span>
                            <span class="dpi-value" id="dpi-value">300 DPI</span>
                        </div>
                        <input type="range" class="dpi-slider" id="dpi-slider" 
                               min="72" max="600" step="1" value="300">
                        <div class="dpi-presets">
                            <span class="dpi-preset" data-dpi="72">72 (Screen)</span>
                            <span class="dpi-preset" data-dpi="150">150 (Draft)</span>
                            <span class="dpi-preset" data-dpi="300">300 (Print)</span>
                            <span class="dpi-preset" data-dpi="600">600 (Pro)</span>
                        </div>
                    </div>
                </div>
                
                <!-- Info Box -->
                <div class="download-info">
                    <span class="download-info-icon">📐</span>
                    <div class="download-info-text" id="download-info-text">
                        Output: <strong>1480 × 2400 px</strong> at <strong>300 DPI</strong>
                        <br>Estimated file size: ~2-4 MB
                    </div>
                </div>
                
                <!-- Download Button -->
                <button class="download-modal-btn" id="download-btn">
                    <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/>
                    </svg>
                    <span>Download Poster</span>
                </button>
            </div>
        `;
        
        document.body.appendChild(overlay);
        this.modal = overlay;
        
        // Cache elements
        this.dpiSlider = document.getElementById('dpi-slider');
        this.dpiValue = document.getElementById('dpi-value');
        this.dpiGroup = document.getElementById('dpi-group');
        this.svgNote = document.getElementById('svg-note');
        this.infoText = document.getElementById('download-info-text');
        this.downloadBtn = document.getElementById('download-btn');
    }
    
    bindEvents() {
        // Close button
        this.modal.querySelector('.download-modal-close').addEventListener('click', () => this.close());
        
        // Click outside to close
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) this.close();
        });
        
        // Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) this.close();
        });
        
        // Resolution cards
        this.modal.querySelectorAll('.resolution-card').forEach(card => {
            card.addEventListener('click', () => {
                this.modal.querySelectorAll('.resolution-card').forEach(c => c.classList.remove('selected'));
                card.classList.add('selected');
                this.options.resolution = card.dataset.resolution;
                this.updateInfo();
            });
        });
        
        // Format cards
        this.modal.querySelectorAll('.format-card').forEach(card => {
            card.addEventListener('click', () => {
                this.modal.querySelectorAll('.format-card').forEach(c => c.classList.remove('selected'));
                card.classList.add('selected');
                this.options.format = card.dataset.format;
                this.updateFormatUI();
                this.updateInfo();
            });
        });
        
        // DPI slider
        this.dpiSlider.addEventListener('input', (e) => {
            this.options.dpi = parseInt(e.target.value);
            this.dpiValue.textContent = `${this.options.dpi} DPI`;
            this.updateInfo();
        });
        
        // DPI presets
        this.modal.querySelectorAll('.dpi-preset').forEach(preset => {
            preset.addEventListener('click', () => {
                const dpi = parseInt(preset.dataset.dpi);
                this.options.dpi = dpi;
                this.dpiSlider.value = dpi;
                this.dpiValue.textContent = `${dpi} DPI`;
                this.updateInfo();
            });
        });
        
        // Download button
        this.downloadBtn.addEventListener('click', () => this.download());
    }
    
    updateFormatUI() {
        if (this.options.format === 'svg') {
            this.dpiGroup.style.display = 'none';
            this.svgNote.classList.add('visible');
        } else {
            this.dpiGroup.style.display = 'block';
            this.svgNote.classList.remove('visible');
        }
    }
    
    updateInfo() {
        const res = this.resolutions[this.options.resolution];
        
        if (this.options.format === 'svg') {
            this.infoText.innerHTML = `
                Output: <strong>SVG Vector</strong> (scalable to any size)
                <br>Text and shapes remain sharp at any scale
            `;
        } else {
            // Estimate file size (rough calculation)
            const pixels = res.width * res.height;
            const baseSizeMB = pixels / 1000000 * 0.8; // ~0.8 bytes per pixel for PNG
            const dpiMultiplier = this.options.dpi / 300;
            const estimatedSize = (baseSizeMB * dpiMultiplier).toFixed(1);
            
            this.infoText.innerHTML = `
                Output: <strong>${res.width} × ${res.height} px</strong> at <strong>${this.options.dpi} DPI</strong>
                <br>Estimated file size: ~${estimatedSize}-${(estimatedSize * 1.5).toFixed(1)} MB
            `;
        }
    }
    
    open() {
        this.isOpen = true;
        this.modal.classList.add('active');
        document.body.style.overflow = 'hidden';
        this.updateInfo();
    }
    
    close() {
        this.isOpen = false;
        this.modal.classList.remove('active');
        document.body.style.overflow = '';
    }
    
    async download() {
        // Get current poster data
        const artist = document.getElementById('current-artist')?.value;
        const album = document.getElementById('current-album')?.value;
        const backgroundColor = document.getElementById('current-background-color')?.value || '#FFFFFF';
        const textColor = document.getElementById('current-text-color')?.value || '#000000';
        const tabulated = document.getElementById('tabulated')?.checked || false;
        const dotted = document.getElementById('dotted')?.checked || false;
        
        if (!artist || !album) {
            alert('Missing poster data');
            return;
        }
        
        // Show loading state
        this.downloadBtn.classList.add('loading');
        this.downloadBtn.innerHTML = '<div class="btn-spinner"></div><span>Generating...</span>';
        this.downloadBtn.disabled = true;
        
        try {
            const response = await fetch('/download-poster', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    artist,
                    album,
                    background: backgroundColor,
                    text: textColor,
                    tabulated,
                    dotted,
                    resolution: this.options.resolution,
                    format: this.options.format,
                    dpi: this.options.dpi
                })
            });
            
            if (!response.ok) throw new Error('Download failed');
            
            const data = await response.json();
            
            if (data.type === 'svg') {
                // Download SVG
                this.downloadFile(data.data, data.filename, 'image/svg+xml');
            } else {
                // Download PNG
                this.downloadDataURL(data.data, data.filename);
            }
            
            // Success - close modal after short delay
            setTimeout(() => this.close(), 500);
            
        } catch (error) {
            console.error('Download error:', error);
            alert('Failed to generate poster. Please try again.');
        } finally {
            // Reset button
            this.downloadBtn.classList.remove('loading');
            this.downloadBtn.innerHTML = `
                <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/>
                </svg>
                <span>Download Poster</span>
            `;
            this.downloadBtn.disabled = false;
        }
    }
    
    downloadDataURL(dataURL, filename) {
        const link = document.createElement('a');
        link.href = dataURL;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
    
    downloadFile(content, filename, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }
}

// Create global instance
let downloadModal = null;

function openDownloadModal() {
    if (!downloadModal) {
        downloadModal = new DownloadModal();
    }
    downloadModal.open();
}

// Export for global use
window.openDownloadModal = openDownloadModal;