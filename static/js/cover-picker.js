/**
 * Cover Picker Integration with covers.musichoarders.xyz
 * Uses their remote protocol to allow cover selection within the app
 */

let coverPickerWindow = null;
let coverPickerCallback = null;

/**
 * Open the cover picker - shows instructions first, then opens popup
 */
function openCoverPicker() {
    const artist = document.getElementById('current-artist')?.value || '';
    const album = document.getElementById('current-album')?.value || '';

    if (!artist && !album) {
        alert('Please search for an album first');
        return;
    }

    // Show instructions FIRST, popup opens when user clicks "Got it!"
    showCoverPickerInstructions(artist, album);
}

/**
 * Actually open the external popup window
 */
function launchCoverPickerPopup(artist, album) {
    // Build URL with search parameters
    const baseUrl = 'https://covers.musichoarders.xyz/';
    const params = new URLSearchParams({
    artist: artist,
    album: album,
    country: 'us'
    });

    const url = baseUrl + '?' + params.toString();

    // Calculate popup dimensions and position
    const width = 1200;
    const height = 800;
    const left = (window.screen.width - width) / 2;
    const top = (window.screen.height - height) / 2;

    // Close existing popup if open
    if (coverPickerWindow && !coverPickerWindow.closed) {
        coverPickerWindow.close();
    }

    // Open popup
    coverPickerWindow = window.open(
        url,
        'CoverPicker',
        `width=${width},height=${height},left=${left},top=${top},resizable=yes,scrollbars=yes`
    );

    if (!coverPickerWindow) {
        alert('Please allow popups for this site to use the cover picker');
        return;
    }

    // Show loading state on button
    showCoverPickerLoading();

    // Start polling for popup close
    pollPopupClose();
}

/**
 * Show instructions overlay BEFORE opening popup
 */
function showCoverPickerInstructions(artist, album) {
    // Remove existing if any
    hideCoverPickerInstructions();

    const overlay = document.createElement('div');
    overlay.className = 'cover-instructions-overlay';
    overlay.id = 'cover-instructions-overlay';
    overlay.innerHTML = `
        <div class="cover-instructions-modal">
            <div class="cover-instructions-header">
                <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/>
                </svg>
                <span>How to Select a Cover</span>
            </div>
            <div class="cover-instructions-steps">
                <div class="instruction-step">
                    <div class="step-number">1</div>
                    <div class="step-text">Browse and find a high-resolution cover you like</div>
                </div>
                <div class="instruction-step">
                    <div class="step-number">2</div>
                    <div class="step-text"><strong>Right-click</strong> on the image and select <strong>"Copy image address"</strong> or <strong>"Copy image link"</strong></div>
                </div>
                <div class="instruction-step">
                    <div class="step-number">3</div>
                    <div class="step-text"><strong>Close the popup</strong> and paste the link in the Custom URL field</div>
                </div>
            </div>
            <button class="cover-instructions-btn" id="cover-instructions-continue">
                Got it! Open Cover Search
            </button>
            <button class="cover-instructions-cancel" onclick="hideCoverPickerInstructions()">
                Cancel
            </button>
        </div>
    `;

    document.body.appendChild(overlay);

    // Bind the continue button to open the popup
    document.getElementById('cover-instructions-continue').onclick = function() {
        hideCoverPickerInstructions();
        // Small delay to let the overlay close smoothly
        setTimeout(() => {
            launchCoverPickerPopup(artist, album);
        }, 200);
    };

    // Animate in
    requestAnimationFrame(() => {
        overlay.classList.add('active');
    });
}

/**
 * Hide instructions overlay
 */
function hideCoverPickerInstructions() {
    const overlay = document.getElementById('cover-instructions-overlay');
    if (overlay) {
        overlay.classList.remove('active');
        setTimeout(() => overlay.remove(), 300);
    }
}

/**
 * Handle messages from the cover picker popup
 */
window.addEventListener('message', function(event) {
    // Log all messages for debugging
    console.log('Received postMessage from:', event.origin);
    console.log('Message data:', JSON.stringify(event.data, null, 2));

    // Accept messages from musichoarders.xyz
    if (!event.origin.includes('musichoarders.xyz') && !event.origin.includes('covers.musichoarders')) {
        return;
    }

    const data = event.data;

    if (!data) {
        return;
    }

    // Handle various message formats
    let coverUrl = null;

    if (typeof data === 'string') {
        // Direct URL string
        if (data.startsWith('http')) {
            coverUrl = data;
        }
    } else if (typeof data === 'object') {
        // Try multiple possible property names for the URL
        coverUrl = data.url || data.src || data.image || data.cover || data.href ||
                   data.imageUrl || data.coverUrl || data.link || data.path;

        // Check nested objects
        if (!coverUrl && data.cover && typeof data.cover === 'object') {
            coverUrl = data.cover.url || data.cover.src;
        }
        if (!coverUrl && data.image && typeof data.image === 'object') {
            coverUrl = data.image.url || data.image.src;
        }

        // Handle type-based messages
        if (data.type === 'cover' && data.url) {
            coverUrl = data.url;
        }
        if (data.type === 'pick' || data.type === 'select' || data.type === 'selected') {
            coverUrl = data.url || data.src || data.image;
        }

        // Handle close message
        if (data.type === 'close') {
            hideCoverPickerLoading();
            if (coverPickerWindow && !coverPickerWindow.closed) {
                coverPickerWindow.close();
            }
            return;
        }
    }

    if (coverUrl) {
        console.log('Found cover URL:', coverUrl);
        applyCoverFromPicker(coverUrl);
    }
});

/**
 * Apply the selected cover from the picker
 */
function applyCoverFromPicker(coverUrl) {
    // Update the cover URL input
    const coverInput = document.getElementById('edit-cover-url');
    if (coverInput) {
        coverInput.value = coverUrl;
    }

    // Show the cover input section if hidden
    const customCoverInput = document.getElementById('custom-cover-input');
    if (customCoverInput) {
        customCoverInput.style.display = 'block';
    }

    // Close the popup
    if (coverPickerWindow && !coverPickerWindow.closed) {
        coverPickerWindow.close();
    }

    hideCoverPickerLoading();

    // Show success message
    showCoverAppliedMessage();
}

/**
 * Show loading state while picker is open
 */
function showCoverPickerLoading() {
    const btn = document.querySelector('.hires-cover-btn');
    if (btn) {
        btn.classList.add('loading');
        btn.dataset.originalText = btn.innerHTML;
        btn.innerHTML = `
            <svg class="spin" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 4V2A10 10 0 0 0 2 12h2a8 8 0 0 1 8-8z"/>
            </svg>
            Picker Open...
        `;
    }
}

/**
 * Hide loading state
 */
function hideCoverPickerLoading() {
    const btn = document.querySelector('.hires-cover-btn');
    if (btn && btn.dataset.originalText) {
        btn.classList.remove('loading');
        btn.innerHTML = btn.dataset.originalText;
    }
}

/**
 * Show message when cover is applied
 */
function showCoverAppliedMessage() {
    const section = document.querySelector('.album-cover-section');
    if (!section) return;

    // Remove existing message if any
    const existingMsg = section.querySelector('.cover-applied-msg');
    if (existingMsg) existingMsg.remove();

    const msg = document.createElement('div');
    msg.className = 'cover-applied-msg';
    msg.innerHTML = `
        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
        </svg>
        Cover URL applied! Click "Apply Changes" to update the poster.
    `;
    section.appendChild(msg);

    // Remove message after 5 seconds
    setTimeout(() => {
        msg.remove();
    }, 5000);
}

/**
 * Poll for popup close and prompt for manual URL entry
 */
function pollPopupClose() {
    if (coverPickerWindow && coverPickerWindow.closed) {
        hideCoverPickerLoading();

        // Check if cover was applied automatically
        const coverInput = document.getElementById('edit-cover-url');
        const hasAutoCover = coverInput && coverInput.value && coverInput.value.startsWith('http');

        if (!hasAutoCover) {
            // Prompt user to paste URL manually if auto-detection didn't work
            promptForManualUrl();
        }
        return;
    }

    if (coverPickerWindow && !coverPickerWindow.closed) {
        setTimeout(pollPopupClose, 500);
    }
}

/**
 * Prompt user to paste the cover URL they copied
 */
function promptForManualUrl() {
    // Show the custom cover input
    const customCoverInput = document.getElementById('custom-cover-input');
    if (customCoverInput) {
        customCoverInput.style.display = 'block';
    }

    // Focus the input field
    const coverUrlInput = document.getElementById('edit-cover-url');
    if (coverUrlInput) {
        coverUrlInput.focus();
    }

    // Show a prominent message
    const section = document.querySelector('.album-cover-section');
    if (!section) return;

    // Remove existing message if any
    const existingMsg = section.querySelector('.cover-hint-msg');
    if (existingMsg) existingMsg.remove();

    const msg = document.createElement('div');
    msg.className = 'cover-hint-msg';
    msg.innerHTML = `
        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 3H5a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2V5a2 2 0 00-2-2zm-7 14l-5-5 1.41-1.41L12 14.17l4.59-4.58L18 11l-6 6z"/>
        </svg>
        <span><strong>Paste the image link above</strong> and click <strong>"Apply Changes"</strong> to update your poster.</span>
    `;
    section.appendChild(msg);

    // Remove message after 15 seconds
    setTimeout(() => {
        if (msg.parentNode) {
            msg.remove();
        }
    }, 15000);
}

// Start polling when picker opens
document.addEventListener('DOMContentLoaded', function() {
    // Override the hires-cover-btn click to use the picker
    const hiresBtn = document.querySelector('.hires-cover-btn');
    if (hiresBtn) {
        hiresBtn.addEventListener('click', function(e) {
            e.preventDefault();
            openCoverPicker();
            pollPopupClose();
        });
    }
});
