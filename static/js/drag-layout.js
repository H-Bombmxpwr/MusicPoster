/**
 * Drag-to-reposition poster elements.
 *
 * The server reports a normalized bounding box (0-1 fractions of the canvas)
 * for every element it drew. When "Move Elements" is on, each box becomes a
 * draggable handle over the preview. Dropping a handle converts the pixel
 * delta into base canvas units (the poster is designed at 740px wide), stores
 * it in PosterState.offsets, and re-renders through the normal update path.
 */

const DragLayout = {
    boxes: {},          // { name: [x, y, w, h] } normalized 0-1
    enabled: false,
    overlay: null,

    BASE_WIDTH: 740,

    LABELS: {
        cover: 'Cover',
        artist: 'Artist',
        album: 'Album',
        tracks: 'Tracklist',
        date: 'Date',
        runtime: 'Runtime',
        label: 'Label',
        banner: 'Spotify Code',
        squares: 'Colors'
    },

    init() {
        const container = document.querySelector('.poster-container');
        const img = document.getElementById('poster-img');
        if (!container || !img) return;

        container.style.position = 'relative';

        this.overlay = document.createElement('div');
        this.overlay.id = 'drag-layout-overlay';
        this.overlay.className = 'drag-layout-overlay';
        container.appendChild(this.overlay);

        // Initial boxes rendered server-side
        const dataEl = document.getElementById('element-boxes-data');
        if (dataEl) {
            try {
                this.boxes = JSON.parse(dataEl.textContent) || {};
            } catch (e) {
                this.boxes = {};
            }
        }

        // Keep handles aligned when the preview resizes
        window.addEventListener('resize', () => this.render());
    },

    setBoxes(boxes) {
        if (boxes && typeof boxes === 'object') {
            this.boxes = boxes;
            this.render();
        }
    },

    setEnabled(on) {
        this.enabled = on;
        const btn = document.getElementById('move-elements-btn');
        if (btn) btn.classList.toggle('active', on);
        const resetBtn = document.getElementById('reset-layout-btn');
        if (resetBtn) resetBtn.style.display = on ? 'flex' : 'none';
        this.render();
    },

    toggle() {
        this.setEnabled(!this.enabled);
    },

    reset() {
        if (!window.PosterState) return;
        PosterState.offsets = {};
        if (typeof updatePosterColor === 'function') {
            updatePosterColor(null, false, false);
        }
    },

    render() {
        if (!this.overlay) return;
        this.overlay.innerHTML = '';
        if (!this.enabled) return;

        const img = document.getElementById('poster-img');
        if (!img || !img.clientWidth) return;

        for (const [name, box] of Object.entries(this.boxes)) {
            const handle = document.createElement('div');
            handle.className = 'drag-handle';
            handle.dataset.element = name;
            handle.style.left = (box[0] * 100) + '%';
            handle.style.top = (box[1] * 100) + '%';
            handle.style.width = (box[2] * 100) + '%';
            handle.style.height = (box[3] * 100) + '%';

            const tag = document.createElement('span');
            tag.className = 'drag-handle-tag';
            tag.textContent = this.LABELS[name] || name;
            handle.appendChild(tag);

            handle.addEventListener('pointerdown', (e) => this._startDrag(e, handle, name));
            this.overlay.appendChild(handle);
        }
    },

    _startDrag(e, handle, name) {
        e.preventDefault();
        const img = document.getElementById('poster-img');
        if (!img) return;

        const startX = e.clientX;
        const startY = e.clientY;
        const startLeft = handle.offsetLeft;
        const startTop = handle.offsetTop;
        handle.classList.add('dragging');
        handle.setPointerCapture(e.pointerId);

        const onMove = (ev) => {
            handle.style.left = (startLeft + ev.clientX - startX) + 'px';
            handle.style.top = (startTop + ev.clientY - startY) + 'px';
        };

        const onUp = (ev) => {
            handle.removeEventListener('pointermove', onMove);
            handle.removeEventListener('pointerup', onUp);
            handle.removeEventListener('pointercancel', onUp);
            handle.classList.remove('dragging');

            const dxPx = ev.clientX - startX;
            const dyPx = ev.clientY - startY;
            if (Math.abs(dxPx) < 2 && Math.abs(dyPx) < 2) return;

            // Preview px → base canvas units (uniform scale: base width is 740)
            const scale = this.BASE_WIDTH / img.clientWidth;
            const prev = (window.PosterState && PosterState.offsets[name]) || [0, 0];
            const next = [
                Math.round(prev[0] + dxPx * scale),
                Math.round(prev[1] + dyPx * scale)
            ];

            if (window.PosterState) {
                PosterState.offsets = Object.assign({}, PosterState.offsets, { [name]: next });
            }
            if (typeof updatePosterColor === 'function') {
                updatePosterColor(null, false, false);
            }
        };

        handle.addEventListener('pointermove', onMove);
        handle.addEventListener('pointerup', onUp);
        handle.addEventListener('pointercancel', onUp);
    }
};

document.addEventListener('DOMContentLoaded', () => DragLayout.init());
window.DragLayout = DragLayout;
