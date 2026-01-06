/**
 * Loading state management for Album Poster
 * Handles loading overlays for form submissions and poster updates
 */

// Global loading state
let isLoading = false;
let scrollPosition = 0;

/**
 * Show the full-page loading overlay
 * @param {string} message - Main loading message
 * @param {string} subtext - Optional subtext
 */
function showLoading(message = 'Generating', subtext = 'Creating your custom poster...') {
    if (isLoading) return;
    isLoading = true;

    // Create overlay if it doesn't exist
    let overlay = document.getElementById('loading-overlay');
    if (!overlay) {
        overlay = createLoadingOverlay();
        document.body.appendChild(overlay);
    }

    // Update text
    const textEl = overlay.querySelector('.loading-text');
    const subtextEl = overlay.querySelector('.loading-subtext');
    if (textEl) textEl.textContent = message;
    if (subtextEl) subtextEl.textContent = subtext;

    // Store scroll position and prevent body scroll (mobile-friendly approach)
    scrollPosition = window.pageYOffset;
    document.body.classList.add('loading-active');
    document.body.style.top = `-${scrollPosition}px`;

    // Show overlay
    requestAnimationFrame(() => {
        overlay.classList.add('active');
    });
}

/**
 * Hide the full-page loading overlay
 */
function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.remove('active');
    }
    
    // Restore scroll position
    document.body.classList.remove('loading-active');
    document.body.style.top = '';
    window.scrollTo(0, scrollPosition);
    
    isLoading = false;
}

/**
 * Create the loading overlay element
 * @returns {HTMLElement}
 */
function createLoadingOverlay() {
    const overlay = document.createElement('div');
    overlay.id = 'loading-overlay';
    overlay.className = 'loading-overlay';
    
    // Prevent touch events from propagating on mobile
    overlay.addEventListener('touchmove', (e) => e.preventDefault(), { passive: false });
    
    overlay.innerHTML = `
        <div class="loading-icon">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/>
            </svg>
        </div>
        <div class="loading-spinner"></div>
        <div class="loading-text">Generating</div>
        <div class="loading-subtext">Creating your custom poster...</div>
        <div class="loading-progress">
            <div class="loading-progress-bar"></div>
        </div>
    `;
    return overlay;
}

/**
 * Show poster-specific loading indicator
 */
function showPosterLoading() {
    const posterContainer = document.querySelector('.poster-container');
    const controls = document.querySelector('.controls');
    
    if (posterContainer) {
        // Create mini loading overlay if not exists
        let posterLoading = posterContainer.querySelector('.poster-loading');
        if (!posterLoading) {
            posterLoading = document.createElement('div');
            posterLoading.className = 'poster-loading';
            posterLoading.innerHTML = '<div class="mini-spinner"></div>';
            posterContainer.style.position = 'relative';
            posterContainer.appendChild(posterLoading);
        }
        posterLoading.classList.add('active');
    }

    // Disable controls
    if (controls) {
        controls.classList.add('controls-disabled');
    }

    isLoading = true;
}

/**
 * Hide poster-specific loading indicator
 */
function hidePosterLoading() {
    const posterLoading = document.querySelector('.poster-loading');
    const controls = document.querySelector('.controls');

    if (posterLoading) {
        posterLoading.classList.remove('active');
    }

    if (controls) {
        controls.classList.remove('controls-disabled');
    }

    isLoading = false;
}

/**
 * Check if currently loading
 * @returns {boolean}
 */
function isCurrentlyLoading() {
    return isLoading;
}

/**
 * Initialize loading for form submissions
 */
function initFormLoading() {
    // Handle main poster generation form
    const form = document.querySelector('form.grid');
    if (form) {
        form.addEventListener('submit', function(e) {
            // Get artist and album values
            const artist = document.getElementById('artist')?.value?.trim();
            const album = document.getElementById('album')?.value?.trim();

            // Only show loading if at least one field has value
            if (artist || album) {
                showLoading('Generating', 'Fetching album data from Spotify...');
            }
        });
    }

    // Handle surprise button
    const surpriseButton = document.querySelector('.surprise-button');
    if (surpriseButton) {
        surpriseButton.addEventListener('click', function(e) {
            showLoading('Surprise!', 'Finding a random album for you...');
        });
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', initFormLoading);

// Export for use in other scripts
window.LoadingManager = {
    show: showLoading,
    hide: hideLoading,
    showPoster: showPosterLoading,
    hidePoster: hidePosterLoading,
    isLoading: isCurrentlyLoading
};