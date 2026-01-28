/**
 * Eyedropper tool for picking colors from the poster image
 */

let eyedropperActive = false;
let eyedropperTarget = null; // 'background' or 'text'
let eyedropperCanvas = null;
let eyedropperCtx = null;

/**
 * Activate eyedropper mode
 * @param {string} target - 'background' or 'text'
 */
function activateEyedropper(target) {
    eyedropperTarget = target;
    eyedropperActive = true;

    // Add eyedropper cursor to poster
    const posterImg = document.getElementById('poster-img');
    if (posterImg) {
        posterImg.style.cursor = 'crosshair';
        posterImg.classList.add('eyedropper-active');
    }

    // Show eyedropper indicator
    showEyedropperIndicator(target);

    // Create hidden canvas for color sampling
    createSamplingCanvas();
}

/**
 * Deactivate eyedropper mode
 */
function deactivateEyedropper() {
    eyedropperActive = false;
    eyedropperTarget = null;

    const posterImg = document.getElementById('poster-img');
    if (posterImg) {
        posterImg.style.cursor = '';
        posterImg.classList.remove('eyedropper-active');
    }

    hideEyedropperIndicator();
}

/**
 * Show indicator that eyedropper is active
 */
function showEyedropperIndicator(target) {
    hideEyedropperIndicator();

    const indicator = document.createElement('div');
    indicator.className = 'eyedropper-indicator';
    indicator.id = 'eyedropper-indicator';
    indicator.innerHTML = `
        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M20.71 5.63l-2.34-2.34a1 1 0 00-1.41 0l-3.12 3.12-1.41-1.41-1.42 1.42 1.42 1.41-9.19 9.19a1 1 0 000 1.41l2.34 2.34a1 1 0 001.41 0l9.19-9.19 1.41 1.42 1.42-1.42-1.41-1.41 3.12-3.12a1 1 0 000-1.42z"/>
        </svg>
        <span>Click on the poster to pick a ${target} color</span>
        <button onclick="deactivateEyedropper()">Cancel</button>
    `;

    document.body.appendChild(indicator);

    requestAnimationFrame(() => {
        indicator.classList.add('active');
    });
}

/**
 * Hide eyedropper indicator
 */
function hideEyedropperIndicator() {
    const indicator = document.getElementById('eyedropper-indicator');
    if (indicator) {
        indicator.remove();
    }
}

/**
 * Create canvas for sampling colors from image
 */
function createSamplingCanvas() {
    const posterImg = document.getElementById('poster-img');
    if (!posterImg) return;

    // Create canvas if needed
    if (!eyedropperCanvas) {
        eyedropperCanvas = document.createElement('canvas');
        eyedropperCtx = eyedropperCanvas.getContext('2d', { willReadFrequently: true });
    }
}

/**
 * Sample color from image at given coordinates
 */
function sampleColorFromImage(img, x, y) {
    // Set canvas size to match image natural size
    eyedropperCanvas.width = img.naturalWidth;
    eyedropperCanvas.height = img.naturalHeight;

    // Draw image to canvas
    eyedropperCtx.drawImage(img, 0, 0);

    // Calculate the actual pixel coordinates
    const rect = img.getBoundingClientRect();
    const scaleX = img.naturalWidth / rect.width;
    const scaleY = img.naturalHeight / rect.height;

    const pixelX = Math.floor((x - rect.left) * scaleX);
    const pixelY = Math.floor((y - rect.top) * scaleY);

    // Get pixel data
    try {
        const pixel = eyedropperCtx.getImageData(pixelX, pixelY, 1, 1).data;
        const hex = '#' +
            pixel[0].toString(16).padStart(2, '0') +
            pixel[1].toString(16).padStart(2, '0') +
            pixel[2].toString(16).padStart(2, '0');
        return hex;
    } catch (e) {
        console.error('Error sampling color:', e);
        return null;
    }
}

/**
 * Handle click on poster when eyedropper is active
 */
function handleEyedropperClick(event) {
    if (!eyedropperActive) return;

    const posterImg = document.getElementById('poster-img');
    if (!posterImg || event.target !== posterImg) return;

    event.preventDefault();
    event.stopPropagation();

    const color = sampleColorFromImage(posterImg, event.clientX, event.clientY);

    if (color) {
        // Apply the color
        if (eyedropperTarget === 'background') {
            updatePosterColor(color, true, false);
        } else if (eyedropperTarget === 'text') {
            updatePosterColor(color, false, true);
        }

        // Show feedback
        showColorPickedFeedback(color);
    }

    // Deactivate eyedropper
    deactivateEyedropper();
}

/**
 * Show feedback when color is picked
 */
function showColorPickedFeedback(color) {
    const feedback = document.createElement('div');
    feedback.className = 'color-picked-feedback';
    feedback.innerHTML = `
        <div class="picked-color-swatch" style="background-color: ${color}"></div>
        <span>Color applied: ${color.toUpperCase()}</span>
    `;

    document.body.appendChild(feedback);

    requestAnimationFrame(() => {
        feedback.classList.add('active');
    });

    setTimeout(() => {
        feedback.classList.remove('active');
        setTimeout(() => feedback.remove(), 300);
    }, 2000);
}

// Set up event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Listen for clicks on poster
    document.addEventListener('click', handleEyedropperClick, true);

    // ESC to cancel eyedropper
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && eyedropperActive) {
            deactivateEyedropper();
        }
    });
});

// Export for global use
window.activateEyedropper = activateEyedropper;
window.deactivateEyedropper = deactivateEyedropper;
