/**
 * Centralized state management for poster customization
 * All changes go through this state to ensure persistence
 */

const PosterState = {
    // Core album info (read-only after init)
    artist: '',
    album: '',

    // Customizable fields
    backgroundColor: '#FFFFFF',
    textColor: '#000000',
    tabulated: false,
    dotted: false,

    // Custom text overrides
    customArtist: null,
    customAlbum: null,
    customDate: null,
    customLabel: null,

    // Track customizations
    customTracks: {},
    removedTracks: new Set(),

    // Custom cover
    customCoverUrl: null,

    /**
     * Initialize state from DOM elements
     */
    init() {
        this.artist = document.getElementById('current-artist')?.value || '';
        this.album = document.getElementById('current-album')?.value || '';
        this.backgroundColor = document.getElementById('current-background-color')?.value || '#FFFFFF';
        this.textColor = document.getElementById('current-text-color')?.value || '#000000';
        this.tabulated = document.getElementById('tabulated')?.checked || false;
        this.dotted = document.getElementById('dotted')?.checked || false;

        console.log('PosterState initialized:', this.getState());
    },

    /**
     * Update a single field
     */
    set(key, value) {
        if (key in this) {
            this[key] = value;

            // Sync with hidden fields if needed
            if (key === 'backgroundColor') {
                const el = document.getElementById('current-background-color');
                if (el) el.value = value;
            } else if (key === 'textColor') {
                const el = document.getElementById('current-text-color');
                if (el) el.value = value;
            }
        }
    },

    /**
     * Update multiple fields at once
     */
    update(updates) {
        for (const [key, value] of Object.entries(updates)) {
            this.set(key, value);
        }
    },

    /**
     * Get current state as plain object for API calls
     */
    getState() {
        return {
            artist: this.artist,
            album: this.album,
            background: this.backgroundColor,
            text: this.textColor,
            tabulated: this.tabulated,
            dotted: this.dotted,
            custom_artist: this.customArtist,
            custom_album: this.customAlbum,
            custom_date: this.customDate,
            custom_label: this.customLabel,
            custom_tracks: this.customTracks,
            removed_tracks: Array.from(this.removedTracks),
            custom_cover_url: this.customCoverUrl
        };
    },

    /**
     * Sync state from edit form fields
     */
    syncFromForm() {
        // Read current form values
        const customArtist = document.getElementById('edit-artist')?.value.trim();
        const customAlbum = document.getElementById('edit-album')?.value.trim();
        const customDate = document.getElementById('edit-date')?.value.trim();
        const customLabel = document.getElementById('edit-label')?.value.trim();
        const customCoverUrl = document.getElementById('edit-cover-url')?.value.trim();

        // Update state
        this.customArtist = customArtist || null;
        this.customAlbum = customAlbum || null;
        this.customDate = customDate || null;
        this.customLabel = customLabel || null;
        this.customCoverUrl = customCoverUrl || null;

        // Sync checkbox states
        this.tabulated = document.getElementById('tabulated')?.checked || false;
        this.dotted = document.getElementById('dotted')?.checked || false;

        // Sync custom tracks from track inputs
        const trackInputs = document.querySelectorAll('[data-track-num]');
        this.customTracks = {};
        trackInputs.forEach(input => {
            const trackNum = input.getAttribute('data-track-num');
            const trackValue = input.value.trim();
            if (trackValue) {
                this.customTracks[trackNum] = trackValue;
            }
        });
    },

    /**
     * Add a removed track
     */
    removeTrack(trackNum) {
        this.removedTracks.add(String(trackNum));
    },

    /**
     * Restore a removed track
     */
    restoreTrack(trackNum) {
        this.removedTracks.delete(String(trackNum));
    },

    /**
     * Check if a track is removed
     */
    isTrackRemoved(trackNum) {
        return this.removedTracks.has(String(trackNum));
    }
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    PosterState.init();
});

// Export for global use
window.PosterState = PosterState;
