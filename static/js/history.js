/**
 * Edit history for the poster page.
 *
 * Every successful render pushes a labeled snapshot of PosterState onto a
 * stack. The History panel lists them; clicking an entry (or Ctrl+Z) restores
 * that exact state — colors, text edits, tracklist, layout offsets, font,
 * texture, and shape — and re-renders the poster.
 */

const PosterHistory = {
    stack: [],       // [{ state, label, time }]
    index: -1,       // which entry is "current"
    suppress: false, // true while restoring, so the re-render doesn't push
    MAX: 40,

    ELEMENT_LABELS: {
        cover: 'Cover', artist: 'Artist', album: 'Album', tracks: 'Tracklist',
        date: 'Date', runtime: 'Runtime', label: 'Label',
        banner: 'Spotify Code', squares: 'Colors'
    },

    init() {
        if (!window.PosterState) return;
        // Capture the starting state so there's always something to undo to
        this.push('Original');
        document.addEventListener('keydown', (e) => {
            const typing = /^(input|textarea|select)$/i.test(e.target.tagName);
            if ((e.ctrlKey || e.metaKey) && !e.shiftKey && e.key.toLowerCase() === 'z' && !typing) {
                e.preventDefault();
                this.undo();
            }
        });
    },

    push(label) {
        if (this.suppress) {
            this.suppress = false;
            return;
        }
        const snap = PosterState.snapshot();
        const current = this.stack[this.index];
        if (current && JSON.stringify(current.state) === JSON.stringify(snap)) {
            return; // nothing actually changed
        }
        const entry = {
            state: snap,
            label: label || this.diffLabel(current ? current.state : null, snap),
            time: new Date()
        };
        this.stack.push(entry);
        if (this.stack.length > this.MAX) this.stack.shift();
        this.index = this.stack.length - 1;
        this.render();
    },

    diffLabel(prev, next) {
        if (!prev) return 'Original';
        const changes = [];

        if (prev.backgroundColor !== next.backgroundColor) changes.push(`Background ${next.backgroundColor}`);
        if (prev.textColor !== next.textColor) changes.push(`Text ${next.textColor}`);
        if (prev.font !== next.font) changes.push(`Font: ${next.font}`);
        if (prev.texture !== next.texture) changes.push(`Finish: ${next.texture}`);
        if (prev.aspect !== next.aspect) changes.push(`Shape: ${next.aspect}`);
        if (prev.tabulated !== next.tabulated || prev.dotted !== next.dotted) changes.push('Number format');

        const po = JSON.stringify(prev.offsets || {});
        const no = JSON.stringify(next.offsets || {});
        if (po !== no) {
            if (no === '{}') {
                changes.push('Reset layout');
            } else {
                const moved = Object.keys(next.offsets).find(k =>
                    JSON.stringify((prev.offsets || {})[k]) !== JSON.stringify(next.offsets[k]));
                changes.push(`Moved ${this.ELEMENT_LABELS[moved] || moved || 'element'}`);
            }
        }

        if (prev.customArtist !== next.customArtist) changes.push('Artist text');
        if (prev.customAlbum !== next.customAlbum) changes.push('Album text');
        if (prev.customDate !== next.customDate) changes.push('Date text');
        if (prev.customLabel !== next.customLabel) changes.push('Label text');
        if (prev.customCoverUrl !== next.customCoverUrl) changes.push('Cover image');
        if (JSON.stringify(prev.customTracks) !== JSON.stringify(next.customTracks) ||
            JSON.stringify(prev.removedTracks) !== JSON.stringify(next.removedTracks) ||
            JSON.stringify(prev.noTruncateTracks) !== JSON.stringify(next.noTruncateTracks)) {
            changes.push('Tracklist edit');
        }

        if (changes.length === 0) return 'Edit';
        if (changes.length === 1) return changes[0];
        return `${changes[0]} +${changes.length - 1} more`;
    },

    restore(i) {
        const entry = this.stack[i];
        if (!entry || !window.PosterState) return;
        this.index = i;
        PosterState.applySnapshot(entry.state);
        this.suppress = true; // the render below shouldn't create a new entry
        if (typeof updatePosterColor === 'function') {
            updatePosterColor(null, false, false);
        }
        this.render();
    },

    undo() {
        if (this.index > 0) this.restore(this.index - 1);
    },

    render() {
        const list = document.getElementById('history-list');
        if (!list) return;

        const undoBtn = document.getElementById('undo-btn');
        if (undoBtn) undoBtn.disabled = this.index <= 0;

        // Newest first
        list.innerHTML = this.stack.map((entry, i) => {
            const t = entry.time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
            return `
                <button type="button"
                        class="history-entry ${i === this.index ? 'active' : ''}"
                        data-index="${i}">
                    <span class="history-entry-label">${entry.label}</span>
                    <span class="history-entry-time">${t}</span>
                </button>
            `;
        }).reverse().join('');

        list.querySelectorAll('.history-entry').forEach(el => {
            el.addEventListener('click', () => this.restore(parseInt(el.dataset.index)));
        });
    }
};

// PosterState.init runs on DOMContentLoaded; capture the original state after it
document.addEventListener('DOMContentLoaded', () => setTimeout(() => PosterHistory.init(), 0));
window.PosterHistory = PosterHistory;
