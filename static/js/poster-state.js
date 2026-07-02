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

    // Poster style
    style: 'classic',

    // 'album' or 'playlist' — drives the right Spotify lookup + scan code
    spotifyType: 'album',

    // Typography, finish, and canvas shape
    font: 'oswald',
    texture: 'none',
    aspect: 'poster',

    // Drag-layout offsets per element, in base (740-wide) canvas units:
    // { tracks: [dx, dy], banner: [dx, dy], ... }
    offsets: {},

    // Custom text overrides
    customArtist: null,
    customAlbum: null,
    customDate: null,
    customLabel: null,

    // Track customizations
    customTracks: {},
    removedTracks: new Set(),
    noTruncateTracks: new Set(),
    truncatedTracks: new Set(),

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
        this.style = document.getElementById('poster-style')?.value || 'classic';
        this.spotifyType = document.getElementById('spotify-type')?.value || 'album';
        this.font = document.getElementById('poster-font')?.value || 'oswald';
        this.texture = document.getElementById('poster-texture')?.value || 'none';
        this.aspect = document.getElementById('poster-aspect')?.value || 'poster';
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

        // Load truncated tracks data
        const truncatedDataEl = document.getElementById('truncated-tracks-data');
        if (truncatedDataEl) {
            try {
                const truncatedList = JSON.parse(truncatedDataEl.textContent);
                this.truncatedTracks = new Set(truncatedList.map(String));
            } catch (e) {
                this.truncatedTracks = new Set();
            }
        }

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
            style: this.style,
            spotify_type: this.spotifyType,
            font: this.font,
            texture: this.texture,
            aspect: this.aspect,
            offsets: this.offsets,
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
            no_truncate_tracks: Array.from(this.noTruncateTracks),
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

        // Sync typography/finish/shape selectors
        this.font = document.getElementById('poster-font')?.value || this.font;
        this.texture = document.getElementById('poster-texture')?.value || this.texture;
        this.aspect = document.getElementById('poster-aspect')?.value || this.aspect;

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
    },

    /**
     * Check if a track is truncated (needs truncation)
     */
    isTrackTruncated(trackNum) {
        return this.truncatedTracks.has(String(trackNum));
    },

    /**
     * Check if truncation is disabled for a track
     */
    isTrackNoTruncate(trackNum) {
        return this.noTruncateTracks.has(String(trackNum));
    },

    /**
     * Toggle truncation for a track
     */
    setTrackTruncate(trackNum, enabled) {
        const key = String(trackNum);
        if (enabled) {
            this.noTruncateTracks.delete(key);
        } else {
            this.noTruncateTracks.add(key);
        }
    },

    /**
     * Update truncated tracks from backend response
     */
    updateTruncatedTracks(truncatedList) {
        this.truncatedTracks = new Set(truncatedList.map(String));
    },

    /**
     * Deep-copy the editable state for the history stack
     */
    snapshot() {
        return JSON.parse(JSON.stringify({
            backgroundColor: this.backgroundColor,
            textColor: this.textColor,
            tabulated: this.tabulated,
            dotted: this.dotted,
            font: this.font,
            texture: this.texture,
            aspect: this.aspect,
            offsets: this.offsets,
            customArtist: this.customArtist,
            customAlbum: this.customAlbum,
            customDate: this.customDate,
            customLabel: this.customLabel,
            customTracks: this.customTracks,
            customCoverUrl: this.customCoverUrl,
            removedTracks: Array.from(this.removedTracks),
            noTruncateTracks: Array.from(this.noTruncateTracks)
        }));
    },

    /**
     * Restore a history snapshot: set state AND write it back into the form
     * fields, because syncFromForm() re-reads the DOM before every render.
     */
    applySnapshot(s) {
        this.backgroundColor = s.backgroundColor;
        this.textColor = s.textColor;
        this.tabulated = s.tabulated;
        this.dotted = s.dotted;
        this.font = s.font;
        this.texture = s.texture;
        this.aspect = s.aspect;
        this.offsets = JSON.parse(JSON.stringify(s.offsets || {}));
        this.customArtist = s.customArtist;
        this.customAlbum = s.customAlbum;
        this.customDate = s.customDate;
        this.customLabel = s.customLabel;
        this.customTracks = JSON.parse(JSON.stringify(s.customTracks || {}));
        this.customCoverUrl = s.customCoverUrl;
        this.removedTracks = new Set(s.removedTracks || []);
        this.noTruncateTracks = new Set(s.noTruncateTracks || []);

        const setVal = (id, val) => {
            const el = document.getElementById(id);
            if (el) el.value = val == null ? '' : val;
        };
        const setChecked = (id, val) => {
            const el = document.getElementById(id);
            if (el) el.checked = !!val;
        };

        setVal('edit-artist', this.customArtist);
        setVal('edit-album', this.customAlbum);
        setVal('edit-date', this.customDate);
        setVal('edit-label', this.customLabel);
        setVal('edit-cover-url', this.customCoverUrl);
        setVal('current-background-color', this.backgroundColor);
        setVal('current-text-color', this.textColor);
        setVal('poster-font', this.font);
        setVal('poster-texture', this.texture);
        setVal('poster-aspect', this.aspect);
        setChecked('tabulated', this.tabulated);
        setChecked('dotted', this.dotted);

        // Rebuild the track editor (removal state), then apply custom names
        if (typeof populateTrackEditor === 'function') {
            populateTrackEditor();
        }
        for (const [num, val] of Object.entries(this.customTracks)) {
            const input = document.querySelector(`[data-track-num="${num}"]`);
            if (input) input.value = val;
        }
    }
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    PosterState.init();
});

// Export for global use
window.PosterState = PosterState;
