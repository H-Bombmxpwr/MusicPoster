/**
 * Download Modal functionality
 * Provides options for downloading posters at different resolutions and formats
 */

// Modal state
let downloadModalOpen = false;
let selectedResolution = 'high';
let selectedFormat = 'png';
let selectedDpi = 300;

/**
 * Open the download options modal
 */
function openDownloadModal() {
    // Check if modal already exists
    let modal = document.getElementById('download-modal-overlay');
    
    if (!modal) {
        // Create modal if it doesn't exist
        modal = createDownloadModal();
        document.body.appendChild(modal);
    }
    
    // Show modal with animation
    requestAnimationFrame(() => {
        modal.classList.add('active');
    });
    
    downloadModalOpen = true;
    
    // Prevent body scroll
    document.body.style.overflow = 'hidden';
}

/**
 * Close the download options modal
 */
function closeDownloadModal() {
    const modal = document.getElementById('download-modal-overlay');
    if (modal) {
        modal.classList.remove('active');
        
        // Remove after animation
        setTimeout(() => {
            // Restore body scroll
            document.body.style.overflow = '';
        }, 300);
    }
    
    downloadModalOpen = false;
}

/**
 * Create the download modal HTML
 */
function createDownloadModal() {
    const overlay = document.createElement('div');
    overlay.className = 'download-modal-overlay';
    overlay.id = 'download-modal-overlay';
    overlay.onclick = function(e) {
        if (e.target === overlay) closeDownloadModal();
    };
    
    overlay.innerHTML = `
        <div class="download-modal">
            <div class="download-modal-header">
                <div class="download-modal-title">
                    <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/>
                    </svg>
                    Download Options
                </div>
                <button class="download-modal-close" onclick="closeDownloadModal()">
                    <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                    </svg>
                </button>
            </div>
            
            <!-- Resolution Options -->
            <div class="download-option-group">
                <span class="download-option-label">Resolution</span>
                <div class="resolution-options">
                    <div class="resolution-card" data-resolution="low" onclick="selectResolution('low')">
                        <div class="resolution-card-name">Low</div>
                        <div class="resolution-card-size">370×600</div>
                    </div>
                    <div class="resolution-card" data-resolution="medium" onclick="selectResolution('medium')">
                        <div class="resolution-card-name">Medium</div>
                        <div class="resolution-card-size">740×1200</div>
                    </div>
                    <div class="resolution-card selected" data-resolution="high" onclick="selectResolution('high')">
                        <div class="resolution-card-name">High</div>
                        <div class="resolution-card-size">1480×2400</div>
                    </div>
                </div>
            </div>
            
            <!-- Format Options -->
            <div class="download-option-group">
                <span class="download-option-label">Format</span>
                <div class="format-options">
                    <div class="format-card selected" data-format="png" onclick="selectFormat('png')">
                        <div class="format-card-icon">
                            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/>
                            </svg>
                        </div>
                        <div class="format-card-info">
                            <div class="format-card-name">PNG</div>
                            <div class="format-card-desc">Best for printing</div>
                        </div>
                    </div>
                    <div class="format-card" data-format="svg" onclick="selectFormat('svg')">
                        <div class="format-card-icon">
                            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path d="M12 3L1 9l11 6 9-4.91V17h2V9L12 3z"/>
                            </svg>
                        </div>
                        <div class="format-card-info">
                            <div class="format-card-name">SVG</div>
                            <div class="format-card-desc">Vector format</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- DPI Slider (only for PNG) -->
            <div class="download-option-group" id="dpi-option-group">
                <span class="download-option-label">Print Quality</span>
                <div class="dpi-container">
                    <div class="dpi-header">
                        <span class="dpi-label">DPI</span>
                        <span class="dpi-value" id="dpi-value">300</span>
                    </div>
                    <input type="range" class="dpi-slider" id="dpi-slider" 
                           min="72" max="600" value="300" step="1"
                           oninput="updateDpi(this.value)">
                    <div class="dpi-presets">
                        <span class="dpi-preset" onclick="setDpi(72)">72 (Web)</span>
                        <span class="dpi-preset" onclick="setDpi(150)">150</span>
                        <span class="dpi-preset" onclick="setDpi(300)">300 (Print)</span>
                        <span class="dpi-preset" onclick="setDpi(600)">600 (Pro)</span>
                    </div>
                </div>
            </div>
            
            <!-- Info Box -->
            <div class="download-info">
                <span class="download-info-icon">💡</span>
                <span class="download-info-text">
                    <strong>High resolution</strong> at <strong>300 DPI</strong> is recommended for printing posters.
                </span>
            </div>
            
            <!-- Download Button -->
            <button class="download-modal-btn" id="modal-download-btn" onclick="downloadWithOptions()">
                <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/>
                </svg>
                Download Poster
            </button>
            
            <div class="svg-note" id="svg-note">
                Note: SVG may not include all visual effects from the original.
            </div>
        </div>
    `;
    
    return overlay;
}

/**
 * Select resolution option
 */
function selectResolution(resolution) {
    selectedResolution = resolution;
    
    // Update UI
    document.querySelectorAll('.resolution-card').forEach(card => {
        card.classList.remove('selected');
    });
    document.querySelector(`.resolution-card[data-resolution="${resolution}"]`)?.classList.add('selected');
}

/**
 * Select format option
 */
function selectFormat(format) {
    selectedFormat = format;
    
    // Update UI
    document.querySelectorAll('.format-card').forEach(card => {
        card.classList.remove('selected');
    });
    document.querySelector(`.format-card[data-format="${format}"]`)?.classList.add('selected');
    
    // Show/hide DPI slider based on format
    const dpiGroup = document.getElementById('dpi-option-group');
    const svgNote = document.getElementById('svg-note');
    
    if (format === 'svg') {
        if (dpiGroup) dpiGroup.style.display = 'none';
        if (svgNote) svgNote.classList.add('visible');
    } else {
        if (dpiGroup) dpiGroup.style.display = 'block';
        if (svgNote) svgNote.classList.remove('visible');
    }
}

/**
 * Update DPI value display
 */
function updateDpi(value) {
    selectedDpi = parseInt(value);
    const dpiValue = document.getElementById('dpi-value');
    if (dpiValue) {
        dpiValue.textContent = value;
    }
}

/**
 * Set DPI to a preset value
 */
function setDpi(value) {
    selectedDpi = value;
    const slider = document.getElementById('dpi-slider');
    const dpiValue = document.getElementById('dpi-value');
    
    if (slider) slider.value = value;
    if (dpiValue) dpiValue.textContent = value;
}

/**
 * Download poster with selected options
 */
function downloadWithOptions() {
    const downloadBtn = document.getElementById('modal-download-btn');

    // Use PosterState if available for consistent state
    let postData;
    if (window.PosterState) {
        PosterState.syncFromForm();
        postData = PosterState.getState();
    } else {
        // Fallback to reading from DOM directly
        postData = {
            artist: document.getElementById('current-artist')?.value,
            album: document.getElementById('current-album')?.value,
            background: document.getElementById('current-background-color')?.value,
            text: document.getElementById('current-text-color')?.value,
            tabulated: document.getElementById('tabulated')?.checked || false,
            dotted: document.getElementById('dotted')?.checked || false,
            custom_cover_url: document.getElementById('edit-cover-url')?.value.trim() || null,
            removed_tracks: [],
            custom_tracks: {}
        };
    }

    if (!postData.artist || !postData.album) {
        console.error('Missing artist or album information');
        return;
    }

    // Add download-specific options
    postData.resolution = selectedResolution;
    postData.format = selectedFormat;
    postData.dpi = selectedDpi;

    // Show loading state
    if (downloadBtn) {
        downloadBtn.classList.add('loading');
        downloadBtn.innerHTML = '<div class="btn-spinner"></div> Generating...';
        downloadBtn.disabled = true;
    }
    
    fetch('/download-poster', {
        method: 'POST',
        body: JSON.stringify(postData),
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) throw new Error('Download failed');
        return response.json();
    })
    .then(data => {
        if (data.type === 'svg') {
            // Download SVG
            const blob = new Blob([data.data], { type: 'image/svg+xml' });
            const url = URL.createObjectURL(blob);
            triggerDownload(url, data.filename);
            URL.revokeObjectURL(url);
        } else {
            // Download PNG
            triggerDownload(data.data, data.filename);
        }
        
        // Close modal
        closeDownloadModal();
    })
    .catch(error => {
        console.error('Error downloading poster:', error);
        alert('Failed to download poster. Please try again.');
    })
    .finally(() => {
        // Reset button state
        if (downloadBtn) {
            downloadBtn.classList.remove('loading');
            downloadBtn.innerHTML = `
                <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/>
                </svg>
                Download Poster
            `;
            downloadBtn.disabled = false;
        }
    });
}

/**
 * Trigger file download
 */
function triggerDownload(url, filename) {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Close modal on Escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && downloadModalOpen) {
        closeDownloadModal();
    }
});