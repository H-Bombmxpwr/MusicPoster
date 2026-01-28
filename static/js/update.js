/**
 * Poster color and style update functionality
 * Uses centralized PosterState for consistency
 */

// Track pending requests to prevent duplicate calls
let pendingRequest = null;

/**
 * Update poster with current state
 * @param {string|null} color - Color to update (or null for format-only changes)
 * @param {boolean} isBackground - Whether this is a background color change
 * @param {boolean} isText - Whether this is a text color change
 */
function updatePosterColor(color, isBackground = false, isText = false) {
    // Ensure PosterState is initialized
    if (!window.PosterState || !PosterState.artist) {
        console.error('PosterState not initialized');
        return;
    }

    // Sync current form state
    PosterState.syncFromForm();

    // Check if a valid color string was passed
    const hasValidColor = color !== undefined && color !== null && typeof color === 'string' && color.startsWith('#');

    // Update colors based on which was changed
    if (isBackground && hasValidColor) {
        PosterState.set('backgroundColor', color);
    }
    if (isText && hasValidColor) {
        PosterState.set('textColor', color);
    }

    // Update checkbox states
    PosterState.set('tabulated', document.getElementById('tabulated')?.checked || false);
    PosterState.set('dotted', document.getElementById('dotted')?.checked || false);

    // Cancel any pending request
    if (pendingRequest) {
        pendingRequest.abort();
    }

    // Get full state for API call
    const postData = PosterState.getState();

    console.log('Sending update request:', postData);

    // Show loading state
    showPosterLoading();

    // Create AbortController for this request
    const controller = new AbortController();
    pendingRequest = controller;

    // Use the custom endpoint that preserves all state
    fetch('/update-poster-custom', {
        method: 'POST',
        body: JSON.stringify(postData),
        headers: {
            'Content-Type': 'application/json'
        },
        signal: controller.signal
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok: ' + response.status);
        }
        return response.json();
    })
    .then(data => {
        pendingRequest = null;
        console.log('Received response with img_data:', !!data.img_data);

        if (data.img_data) {
            updatePosterDisplay(data.img_data);

            // Update color palette if new colors were returned
            if (data.colors) {
                updateColorPalette(data.colors);
            }
        } else {
            console.error('No img_data in response');
        }

        hidePosterLoading();
    })
    .catch(error => {
        pendingRequest = null;

        if (error.name === 'AbortError') {
            console.log('Request aborted');
            return;
        }

        console.error('Error updating poster:', error);
        hidePosterLoading();
    });
}

/**
 * Update poster image display
 */
function updatePosterDisplay(imgData) {
    const posterImg = document.getElementById('poster-img');
    if (posterImg) {
        posterImg.src = imgData;
    }

    // Update download link
    const downloadLink = document.getElementById('download-link');
    if (downloadLink) {
        downloadLink.href = imgData;
        const albumName = PosterState.customAlbum || PosterState.album || 'poster';
        const formattedAlbumName = albumName.replace(/\s+/g, '_');
        downloadLink.setAttribute('download', `${formattedAlbumName}.png`);
    }

    // Update hidden form data for submission
    const imgDataInput = document.getElementById('img_data');
    if (imgDataInput) {
        imgDataInput.value = imgData;
    }
}

/**
 * Update color palette with new colors
 */
function updateColorPalette(colors) {
    if (!colors || !Array.isArray(colors)) return;

    // Update background colors
    const bgContainer = document.getElementById('backgroundColors');
    if (bgContainer) {
        // Keep existing squares but update colors
        const squares = bgContainer.querySelectorAll('.color-square');
        colors.forEach((color, i) => {
            if (squares[i]) {
                squares[i].style.backgroundColor = color;
                squares[i].setAttribute('onclick', `updatePosterColor('${color}', true, false)`);
                squares[i].setAttribute('title', `Set background to ${color}`);
            }
        });
    }

    // Update text colors
    const textContainer = document.getElementById('textColors');
    if (textContainer) {
        const squares = textContainer.querySelectorAll('.color-square');
        colors.forEach((color, i) => {
            if (squares[i]) {
                squares[i].style.backgroundColor = color;
                squares[i].setAttribute('onclick', `updatePosterColor('${color}', false, true)`);
                squares[i].setAttribute('title', `Set text to ${color}`);
            }
        });
    }
}

/**
 * Show loading state on poster
 */
function showPosterLoading() {
    const posterImg = document.getElementById('poster-img');
    const loadingOverlay = document.getElementById('poster-loading');

    if (posterImg) {
        posterImg.style.opacity = '0.5';
        posterImg.style.transition = 'opacity 0.2s ease';
    }

    if (loadingOverlay) {
        loadingOverlay.style.display = 'flex';
        loadingOverlay.classList.add('active');
    }
}

/**
 * Hide loading state on poster
 */
function hidePosterLoading() {
    const posterImg = document.getElementById('poster-img');
    const loadingOverlay = document.getElementById('poster-loading');

    if (posterImg) {
        posterImg.style.opacity = '1';
    }

    if (loadingOverlay) {
        loadingOverlay.style.display = 'none';
        loadingOverlay.classList.remove('active');
    }
}

// Initialize download link functionality
document.addEventListener('DOMContentLoaded', function() {
    const downloadLink = document.getElementById('download-link');
    const posterImg = document.getElementById('poster-img');

    if (downloadLink && posterImg) {
        // Ensure download link has correct initial href
        downloadLink.href = posterImg.src;
    }
});
