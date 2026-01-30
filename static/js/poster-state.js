/**
 * Centralized state management for poster customization
 * All changes go through this state to ensure persistence
 */

const PosterState = {
    // Core album info (read-only after init)
    artist: '',
    album: '',
    albumId: '',

    // Customizable fields
    backgroundColor: '#FFFFFF',
    textColor: '#000000',
    tabulated: true,
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
     * Called immediately on page load to capture initial values
     */
    init() {
        this.artist = document.getElementById('current-artist')?.value || '';
        this.album = document.getElementById('current-album')?.value || '';
        this.albumId = document.getElementById('album-id')?.value || '';
        this.backgroundColor = document.getElementById('current-background-color')?.value || '#FFFFFF';
        this.textColor = document.getElementById('current-text-color')?.value || '#000000';
        this.tabulated = document.getElementById('tabulated')?.checked || false;
        this.dotted = document.getElementById('dotted')?.checked || false;

        // Pre-populate custom fields from edit form so state is ready from the start
        const editArtist = document.getElementById('edit-artist');
        const editAlbum = document.getElementById('edit-album');
        const editDate = document.getElementById('edit-date');
        const editLabel = document.getElementById('edit-label');
        const editCoverUrl = document.getElementById('edit-cover-url');

        if (editArtist) this.customArtist = editArtist.value.trim() || null;
        if (editAlbum) this.customAlbum = editAlbum.value.trim() || null;
        if (editDate) this.customDate = editDate.value.trim() || null;
        if (editLabel) this.customLabel = editLabel.value.trim() || null;
        if (editCoverUrl) this.customCoverUrl = editCoverUrl.value.trim() || null;

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
            album_id: this.albumId,
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
     * Empty strings are preserved (sent as '') so the backend can render empty fields
     */
    syncFromForm() {
        // Read current form values
        const artistEl = document.getElementById('edit-artist');
        const albumEl = document.getElementById('edit-album');
        const dateEl = document.getElementById('edit-date');
        const labelEl = document.getElementById('edit-label');
        const coverUrlEl = document.getElementById('edit-cover-url');

        // Use empty string (not null) when field exists but is empty,
        // so the backend knows the user intentionally cleared it
        if (artistEl) this.customArtist = artistEl.value.trim();
        if (albumEl) this.customAlbum = albumEl.value.trim();
        if (dateEl) this.customDate = dateEl.value.trim();
        if (labelEl) this.customLabel = labelEl.value.trim();
        this.customCoverUrl = coverUrlEl ? (coverUrlEl.value.trim() || null) : null;

        // Sync checkbox states
        this.tabulated = document.getElementById('tabulated')?.checked || false;
        this.dotted = document.getElementById('dotted')?.checked || false;

        // Sync custom tracks from track inputs (empty string = hide track text)
        const trackInputs = document.querySelectorAll('[data-track-num]');
        this.customTracks = {};
        trackInputs.forEach(input => {
            const trackNum = input.getAttribute('data-track-num');
            this.customTracks[trackNum] = input.value.trim();
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
