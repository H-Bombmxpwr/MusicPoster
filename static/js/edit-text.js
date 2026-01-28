/**
 * Text editing functionality for poster customization
 * Uses centralized PosterState for consistency
 */

// Track editor state
let trackEditorOpen = false;
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

    for (let i = 1; i <= trackCount; i++) {
        // Get the track name from the data if it exists
        let trackName = '';
        if (tracksArray[i - 1]) {
            trackName = tracksArray[i - 1][1]; // Get the track name
            // Clean up the track name (same rules as backend)
            trackName = cleanTrackName(trackName);
        }

        // Check if track is removed (from PosterState if available)
        const isRemoved = window.PosterState ? PosterState.isTrackRemoved(i) : false;

        const trackField = document.createElement('div');
        trackField.className = 'track-field' + (isRemoved ? ' removed' : '');
        trackField.id = `track-field-${i}`;
        trackField.innerHTML = `
            <label for="track-${i}">${i}.</label>
            <input type="text"
                   id="track-${i}"
                   value="${escapeHtml(trackName)}"
                   placeholder="Track ${i} name..."
                   data-track-num="${i}"
                   ${isRemoved ? 'disabled' : ''}>
            <button type="button"
                    class="track-remove-btn ${isRemoved ? 'restore' : ''}"
                    onclick="toggleTrackRemoval(${i})"
                    title="${isRemoved ? 'Restore track' : 'Remove track'}">
                ${isRemoved ?
                    '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>' :
                    '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>'
                }
            </button>
        `;
        trackList.appendChild(trackField);
    }
}

/**
 * Toggle track removal state
 */
function toggleTrackRemoval(trackNum) {
    const trackNumStr = String(trackNum);
    const trackField = document.getElementById(`track-field-${trackNum}`);
    const trackInput = document.getElementById(`track-${trackNum}`);
    const removeBtn = trackField?.querySelector('.track-remove-btn');

    // Use PosterState if available
    const isCurrentlyRemoved = window.PosterState ?
        PosterState.isTrackRemoved(trackNum) :
        trackField?.classList.contains('removed');

    if (isCurrentlyRemoved) {
        // Restore track
        if (window.PosterState) {
            PosterState.restoreTrack(trackNum);
        }
        if (trackField) trackField.classList.remove('removed');
        if (trackInput) trackInput.disabled = false;
        if (removeBtn) {
            removeBtn.classList.remove('restore');
            removeBtn.title = 'Remove track';
            removeBtn.innerHTML = '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>';
        }
    } else {
        // Remove track
        if (window.PosterState) {
            PosterState.removeTrack(trackNum);
        }
        if (trackField) trackField.classList.add('removed');
        if (trackInput) trackInput.disabled = true;
        if (removeBtn) {
            removeBtn.classList.add('restore');
            removeBtn.title = 'Restore track';
            removeBtn.innerHTML = '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>';
        }
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
 * Clean up track name - remove remastered, feat., etc.
 */
function cleanTrackName(name) {
    if (!name) return '';

    let clean = name;

    // Remove remastered variations
    clean = clean.replace(/\s*[-–—]\s*remaster(ed)?\s*\d*\s*/gi, '');
    clean = clean.replace(/\s*[-–—]\s*\d+\s*remaster(ed)?\s*/gi, '');
    clean = clean.replace(/\(.*?remaster(ed)?.*?\)/gi, '');
    clean = clean.replace(/\[.*?remaster(ed)?.*?\]/gi, '');

    // Remove other common suffixes
    clean = clean.replace(/\s*[-–—]\s*(mono|stereo|deluxe|bonus|extended|anniversary|edition).*$/gi, '');
    clean = clean.replace(/\(.*?(mono|stereo|deluxe|bonus|extended|anniversary|edition).*?\)/gi, '');

    // Remove feat./featuring
    clean = clean.split(/\s+feat\./i)[0];
    clean = clean.split(/\s+featuring\s+/i)[0];
    clean = clean.split(/\s+ft\./i)[0];

    // Remove remaining parentheses/brackets content
    clean = clean.replace(/\(.*?\)/g, '');
    clean = clean.replace(/\[.*?\]/g, '');

    // Clean up extra whitespace and dashes at the end
    clean = clean.replace(/\s*[-–—]\s*$/, '');
    clean = clean.trim();

    return clean;
}

/**
 * Apply all custom text changes and regenerate poster
 */
function applyCustomChanges() {
    // Ensure PosterState is initialized
    if (!window.PosterState) {
        console.error('PosterState not initialized');
        return;
    }

    // Sync all form values to state
    PosterState.syncFromForm();

    // Validate required fields
    if (!PosterState.artist || !PosterState.album) {
        console.error('Missing required artist or album information');
        showErrorFeedback('Missing required information');
        return;
    }

    // Debug log
    console.log('Applying custom changes with state:', PosterState.getState());

    // Show loading state
    showLoadingState();

    // Get full state for API call
    const postData = PosterState.getState();

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

            // Update color palette if new colors were returned
            if (data.colors && typeof updateColorPalette === 'function') {
                updateColorPalette(data.colors);
            }

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

    applyBtn.textContent = 'Applied!';
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

    applyBtn.textContent = 'Error';
    applyBtn.style.background = '#ff4757';
    applyBtn.style.transition = 'all 0.3s ease';

    setTimeout(() => {
        applyBtn.textContent = originalText;
        applyBtn.style.background = '';
    }, 2000);

    console.error(message);
}
