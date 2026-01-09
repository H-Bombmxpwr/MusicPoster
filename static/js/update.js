/**
 * Poster color and style update functionality
 * Handles real-time poster customization via AJAX
 */

// Track pending requests to prevent duplicate calls
let pendingRequest = null;

function updatePosterColor(color, isBackground = false, isText = false) {
    // Get current state from hidden fields
    const artist = document.getElementById('current-artist')?.value;
    const album = document.getElementById('current-album')?.value;
    let backgroundColor = document.getElementById('current-background-color')?.value;
    let textColor = document.getElementById('current-text-color')?.value;
    const tabulated = document.getElementById('tabulated')?.checked || false;
    const dotted = document.getElementById('dotted')?.checked || false;

    if (!artist || !album) {
        console.error('Missing artist or album information');
        return;
    }

    // Check if a valid color string was passed (not NaN, not undefined, not null)
    // Using typeof check because isNaN('#ff0000') returns true (tries to convert string to number)
    const hasValidColor = color !== undefined && color !== null && typeof color === 'string' && color.startsWith('#');

    // Update colors based on which was changed
    if (isBackground && hasValidColor) {
        backgroundColor = color;
        // Update hidden field immediately
        document.getElementById('current-background-color').value = backgroundColor;
    }
    if (isText && hasValidColor) {
        textColor = color;
        // Update hidden field immediately
        document.getElementById('current-text-color').value = textColor;
    }

    // Cancel any pending request
    if (pendingRequest) {
        pendingRequest.abort();
    }

    // Prepare request data
    const postData = {
        artist: artist,
        album: album,
        background: backgroundColor,
        text: textColor,
        tabulated: tabulated,
        dotted: dotted
    };

    console.log('Sending update request:', postData);

    // Show loading state
    showPosterLoading();

    // Create AbortController for this request
    const controller = new AbortController();
    pendingRequest = controller;

    // Send update request
    fetch('/update-poster', {
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
            const posterImg = document.getElementById('poster-img');
            if (posterImg) {
                posterImg.src = data.img_data;
            }

            // Update download link
            const downloadLink = document.getElementById('download-link');
            if (downloadLink) {
                downloadLink.href = data.img_data;
                const formattedAlbumName = album.replace(/\s+/g, '_');
                downloadLink.setAttribute('download', `${formattedAlbumName}.png`);
            }

            // Update hidden form data for submission
            const imgDataInput = document.getElementById('img_data');
            if (imgDataInput) {
                imgDataInput.value = data.img_data;
            }
        } else {
            console.error('No img_data in response');
        }
        
        hidePosterLoading();
    })
    .catch(error => {
        pendingRequest = null;
        
        if (error.name === 'AbortError') {
            // Request was cancelled, ignore
            console.log('Request aborted');
            return;
        }
        
        console.error('Error updating poster:', error);
        hidePosterLoading();
    });
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