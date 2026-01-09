/**
 * Text editing functionality for poster customization
 * Allows users to edit individual text components on the poster
 */

// Track editor state
let trackEditorOpen = false;
let customTracks = {};
let tracksData = {};

/**
 * Initialize track editor on page load
 */
document.addEventListener('DOMContentLoaded', function() {
    // Load tracks data from JSON
    const tracksDataElement = document.getElementById('tracks-data');
    if (tracksDataElement) {
        try {
            tracksData = JSON.parse(tracksDataElement.textContent);
        } catch (e) {
            console.error('Error parsing tracks data:', e);
            tracksData = {};
        }
    }
    
    populateTrackEditor();
});

/**
 * Toggle track editor visibility with smooth animation
 */
function toggleTrackEditor() {
    const trackEditor = document.getElementById('track-editor');
    const toggleIcon = document.getElementById('track-toggle-icon');
    const toggleText = document.getElementById('track-toggle-text');
    
    if (!trackEditor) return;
    
    trackEditorOpen = !trackEditorOpen;
    
    if (trackEditorOpen) {
        // Show the editor
        trackEditor.style.display = 'block';
        // Force reflow to enable transition
        trackEditor.offsetHeight;
        trackEditor.style.maxHeight = '600px';
        trackEditor.style.opacity = '1';
        
        if (toggleIcon) {
            toggleIcon.style.transform = 'rotate(180deg)';
        }
        if (toggleText) {
            toggleText.textContent = 'Hide Tracklist';
        }
    } else {
        // Hide the editor
        trackEditor.style.maxHeight = '0';
        trackEditor.style.opacity = '0';
        
        // Wait for transition to complete before hiding
        setTimeout(() => {
            trackEditor.style.display = 'none';
        }, 400);
        
        if (toggleIcon) {
            toggleIcon.style.transform = 'rotate(0deg)';
        }
        if (toggleText) {
            toggleText.textContent = 'Edit Tracklist';
        }
    }
}

/**
 * Populate track editor with track input fields and existing track names
 */
function populateTrackEditor() {
    const trackList = document.getElementById('track-list');
    const trackCount = parseInt(document.getElementById('track-count')?.value || 0);
    
    if (!trackList || trackCount === 0) return;
    
    trackList.innerHTML = '';
    
    // Convert tracks object to array for easier iteration
    const tracksArray = Object.entries(tracksData);
    
    for (let i = 1; i <= Math.min(trackCount, 30); i++) {
        // Get the track name from the data if it exists
        let trackName = '';
        if (tracksArray[i - 1]) {
            trackName = tracksArray[i - 1][1]; // Get the track name
            // Clean up the track name (remove parentheses, etc.)
            trackName = trackName.replace(/[\(\[].*?[\)\]]/g, '').trim();
        }
        
        const trackField = document.createElement('div');
        trackField.className = 'track-field';
        trackField.innerHTML = `
            <label for="track-${i}">${i}.</label>
            <input type="text" 
                   id="track-${i}" 
                   value="${escapeHtml(trackName)}"
                   placeholder="Track ${i} name..."
                   data-track-num="${i}">
        `;
        trackList.appendChild(trackField);
    }
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Apply all custom text changes and regenerate poster
 */
function applyCustomChanges() {
    // Get current state - READ from hidden fields that are always up to date
    const artist = document.getElementById('current-artist')?.value;
    const album = document.getElementById('current-album')?.value;
    const backgroundColor = document.getElementById('current-background-color')?.value;
    const textColor = document.getElementById('current-text-color')?.value;
    const tabulated = document.getElementById('tabulated')?.checked || false;
    const dotted = document.getElementById('dotted')?.checked || false;

    // Get custom text values
    const customArtist = document.getElementById('edit-artist')?.value.trim();
    const customAlbum = document.getElementById('edit-album')?.value.trim();
    const customDate = document.getElementById('edit-date')?.value.trim();
    const customLabel = document.getElementById('edit-label')?.value.trim();

    // Get custom track values
    const trackInputs = document.querySelectorAll('[data-track-num]');
    customTracks = {};
    trackInputs.forEach(input => {
        const trackNum = input.getAttribute('data-track-num');
        const trackValue = input.value.trim();
        if (trackValue) {
            customTracks[trackNum] = trackValue;
        }
    });

    // Validate required fields
    if (!artist || !album) {
        console.error('Missing required artist or album information');
        showErrorFeedback('Missing required information');
        return;
    }

    // Debug log to verify colors are being sent
    console.log('Applying custom changes with:', {
        artist: artist,
        album: album,
        background: backgroundColor,
        text: textColor,
        tabulated: tabulated,
        dotted: dotted
    });

    // Show loading state
    showLoadingState();

    // Prepare request data
    const postData = {
        artist: artist,
        album: album,
        background: backgroundColor,
        text: textColor,
        tabulated: tabulated,
        dotted: dotted,
        custom_artist: customArtist || null,
        custom_album: customAlbum || null,
        custom_date: customDate || null,
        custom_label: customLabel || null,
        custom_tracks: customTracks
    };

    // Send update request
    fetch('/update-poster-custom', {
        method: 'POST',
        body: JSON.stringify(postData),
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
    })
    .then(data => {
        if (data.img_data) {
            updatePosterImage(data.img_data);
            
            // Show success feedback
            showSuccessFeedback();
        }
    })
    .catch(error => {
        console.error('Error applying custom changes:', error);
        hideLoadingState();
        showErrorFeedback('Failed to apply changes. Please try again.');
    });
}

/**
 * Update poster image and related elements
 */
function updatePosterImage(imgData) {
    const posterImg = document.getElementById('poster-img');
    const downloadLink = document.getElementById('download-link');
    const imgDataInput = document.getElementById('img_data');
    
    if (posterImg) {
        posterImg.src = imgData;
    }
    
    if (downloadLink) {
        downloadLink.href = imgData;
        const albumName = document.getElementById('edit-album')?.value || 
                         document.getElementById('current-album')?.value || 'poster';
        const formattedAlbumName = albumName.replace(/\s+/g, '_');
        downloadLink.setAttribute('download', `${formattedAlbumName}.png`);
    }
    
    if (imgDataInput) {
        imgDataInput.value = imgData;
    }
    
    hideLoadingState();
}

/**
 * Show loading state
 */
function showLoadingState() {
    const posterImg = document.getElementById('poster-img');
    const loadingOverlay = document.getElementById('poster-loading');
    
    if (posterImg) {
        posterImg.style.opacity = '0.5';
        posterImg.style.transition = 'opacity 0.3s ease';
    }
    
    if (loadingOverlay) {
        loadingOverlay.classList.add('active');
    }
}

/**
 * Hide loading state
 */
function hideLoadingState() {
    const posterImg = document.getElementById('poster-img');
    const loadingOverlay = document.getElementById('poster-loading');
    
    if (posterImg) {
        posterImg.style.opacity = '1';
    }
    
    if (loadingOverlay) {
        loadingOverlay.classList.remove('active');
    }
}

/**
 * Show success feedback
 */
function showSuccessFeedback() {
    const applyBtn = document.querySelector('.apply-changes-btn');
    if (!applyBtn) return;
    
    const originalText = applyBtn.textContent;
    
    applyBtn.textContent = '✓ Applied!';
    applyBtn.style.background = '#00d26a';
    applyBtn.style.transition = 'all 0.3s ease';
    
    setTimeout(() => {
        applyBtn.textContent = originalText;
        applyBtn.style.background = '';
    }, 2000);
}

/**
 * Show error feedback
 */
function showErrorFeedback(message) {
    const applyBtn = document.querySelector('.apply-changes-btn');
    if (!applyBtn) return;
    
    const originalText = applyBtn.textContent;
    
    applyBtn.textContent = '✗ Error';
    applyBtn.style.background = '#ff4757';
    applyBtn.style.transition = 'all 0.3s ease';
    
    setTimeout(() => {
        applyBtn.textContent = originalText;
        applyBtn.style.background = '';
    }, 2000);
    
    console.error(message);
}