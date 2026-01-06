/**
 * Custom Autocomplete Component
 * Replaces native datalist with a styled dropdown
 * Supports Spotify images for artists and albums
 */

class Autocomplete {
    constructor(inputId, endpoint, options = {}) {
        this.input = document.getElementById(inputId);
        if (!this.input) return;

        this.endpoint = endpoint;
        this.options = {
            minChars: 2,
            debounceMs: 200,
            maxResults: 10,
            dependentInputId: options.dependentInputId || null,
            type: options.type || 'artist', // 'artist' or 'album'
            placeholder: options.placeholder || 'Type to search...',
            ...options
        };

        this.dropdown = null;
        this.items = [];
        this.highlightedIndex = -1;
        this.isOpen = false;
        this.debounceTimer = null;
        this.abortController = null;

        this.init();
    }

    init() {
        // Wrap input in autocomplete container
        this.wrapper = document.createElement('div');
        this.wrapper.className = 'autocomplete-wrapper';
        this.input.parentNode.insertBefore(this.wrapper, this.input);
        this.wrapper.appendChild(this.input);

        // Remove native datalist
        this.input.removeAttribute('list');
        const datalist = document.getElementById(this.input.id + '-suggestions');
        if (datalist) datalist.remove();

        // Create dropdown
        this.dropdown = document.createElement('div');
        this.dropdown.className = 'autocomplete-dropdown';
        this.dropdown.setAttribute('role', 'listbox');
        this.dropdown.id = this.input.id + '-dropdown';
        this.wrapper.appendChild(this.dropdown);

        // Set ARIA attributes
        this.input.setAttribute('role', 'combobox');
        this.input.setAttribute('aria-autocomplete', 'list');
        this.input.setAttribute('aria-controls', this.dropdown.id);
        this.input.setAttribute('aria-expanded', 'false');

        // Bind events
        this.bindEvents();
    }

    bindEvents() {
        // Input events
        this.input.addEventListener('input', (e) => this.onInput(e));
        this.input.addEventListener('focus', (e) => this.onFocus(e));
        this.input.addEventListener('blur', (e) => this.onBlur(e));
        this.input.addEventListener('keydown', (e) => this.onKeydown(e));

        // Click outside to close
        document.addEventListener('click', (e) => {
            if (!this.wrapper.contains(e.target)) {
                this.close();
            }
        });
    }

    onInput(e) {
        const value = e.target.value.trim();

        // Clear previous timer
        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }

        // Cancel previous request
        if (this.abortController) {
            this.abortController.abort();
        }

        if (value.length < this.options.minChars) {
            this.close();
            return;
        }

        // Show loading state
        this.showLoading();

        // Debounce the search
        this.debounceTimer = setTimeout(() => {
            this.search(value);
        }, this.options.debounceMs);
    }

    onFocus(e) {
        if (this.items.length > 0) {
            this.open();
        }
    }

    onBlur(e) {
        // Delay close to allow click on item
        setTimeout(() => {
            if (!this.wrapper.contains(document.activeElement)) {
                this.close();
            }
        }, 200);
    }

    onKeydown(e) {
        if (!this.isOpen) {
            if (e.key === 'ArrowDown' && this.input.value.length >= this.options.minChars) {
                this.search(this.input.value.trim());
            }
            return;
        }

        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.highlight(this.highlightedIndex + 1);
                break;
            case 'ArrowUp':
                e.preventDefault();
                this.highlight(this.highlightedIndex - 1);
                break;
            case 'Enter':
                e.preventDefault();
                if (this.highlightedIndex >= 0) {
                    this.select(this.items[this.highlightedIndex]);
                }
                break;
            case 'Escape':
                this.close();
                break;
            case 'Tab':
                this.close();
                break;
        }
    }

    async search(query) {
        this.abortController = new AbortController();

        try {
            let url = `${this.endpoint}?q=${encodeURIComponent(query)}`;

            // Add dependent input value if applicable
            if (this.options.dependentInputId) {
                const dependentInput = document.getElementById(this.options.dependentInputId);
                if (dependentInput && dependentInput.value.trim()) {
                    url += `&artist=${encodeURIComponent(dependentInput.value.trim())}`;
                }
            }

            const response = await fetch(url, {
                signal: this.abortController.signal
            });

            if (!response.ok) throw new Error('Network error');

            const data = await response.json();
            
            // Handle both old format (array of strings) and new format (array of objects)
            if (Array.isArray(data)) {
                this.items = data.slice(0, this.options.maxResults).map(item => {
                    // If item is already an object, use it directly
                    if (typeof item === 'object' && item !== null) {
                        return item;
                    }
                    // If item is a string (old format), convert to object
                    return { name: item, image: null };
                });
            } else {
                this.items = [];
            }
            
            this.render(query);

        } catch (error) {
            if (error.name !== 'AbortError') {
                console.warn('Autocomplete search failed:', error);
                this.showNoResults();
            }
        }
    }

    render(query) {
        if (this.items.length === 0) {
            this.showNoResults();
            return;
        }

        this.dropdown.innerHTML = this.items.map((item, index) => {
            const name = item.name || item;
            const image = item.image;
            const artist = item.artist; // For albums
            
            // Create image HTML - use Spotify image if available, otherwise fallback icon
            let imageHtml;
            if (image) {
                imageHtml = `<img src="${image}" alt="" loading="lazy" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                             <div class="autocomplete-item-icon-fallback" style="display:none;">${this.getFallbackIcon()}</div>`;
            } else {
                imageHtml = this.getFallbackIcon();
            }
            
            // Create subtitle for albums (show artist name)
            const subtitleHtml = artist ? `<span class="autocomplete-item-subtitle">${this.escapeHtml(artist)}</span>` : '';
            
            return `
                <div class="autocomplete-item" 
                     role="option" 
                     data-index="${index}"
                     aria-selected="${index === this.highlightedIndex}">
                    <div class="autocomplete-item-icon ${image ? 'has-image' : ''}">
                        ${imageHtml}
                    </div>
                    <div class="autocomplete-item-content">
                        <span class="autocomplete-item-text">
                            ${this.highlightMatch(name, query)}
                        </span>
                        ${subtitleHtml}
                    </div>
                </div>
            `;
        }).join('');

        // Add keyboard hint
        this.dropdown.innerHTML += `
            <div class="autocomplete-hint">
                <span><kbd>↑</kbd><kbd>↓</kbd> Navigate</span>
                <span><kbd>Enter</kbd> Select</span>
                <span><kbd>Esc</kbd> Close</span>
            </div>
        `;

        // Bind click events to items
        this.dropdown.querySelectorAll('.autocomplete-item').forEach((el) => {
            el.addEventListener('mousedown', (e) => {
                e.preventDefault();
                const index = parseInt(el.dataset.index);
                this.select(this.items[index]);
            });
            el.addEventListener('mouseenter', () => {
                this.highlight(parseInt(el.dataset.index), false);
            });
        });

        this.highlightedIndex = -1;
        this.open();
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    getFallbackIcon() {
        if (this.options.type === 'album') {
            return `<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 14.5c-2.49 0-4.5-2.01-4.5-4.5S9.51 7.5 12 7.5s4.5 2.01 4.5 4.5-2.01 4.5-4.5 4.5zm0-5.5c-.55 0-1 .45-1 1s.45 1 1 1 1-.45 1-1-.45-1-1-1z"/>
            </svg>`;
        }
        // Default: music/artist icon
        return `<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/>
        </svg>`;
    }

    highlightMatch(text, query) {
        if (!query) return this.escapeHtml(text);
        
        const escapedText = this.escapeHtml(text);
        const regex = new RegExp(`(${this.escapeRegex(query)})`, 'gi');
        return escapedText.replace(regex, '<span class="autocomplete-match">$1</span>');
    }

    escapeRegex(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    highlight(index, scroll = true) {
        // Wrap around
        if (index < 0) index = this.items.length - 1;
        if (index >= this.items.length) index = 0;

        // Remove previous highlight
        const prev = this.dropdown.querySelector('.autocomplete-item.highlighted');
        if (prev) prev.classList.remove('highlighted');

        // Add new highlight
        this.highlightedIndex = index;
        const items = this.dropdown.querySelectorAll('.autocomplete-item');
        if (items[index]) {
            items[index].classList.add('highlighted');
            items[index].setAttribute('aria-selected', 'true');
            
            if (scroll) {
                items[index].scrollIntoView({ block: 'nearest' });
            }
        }
    }

    select(item) {
        // Handle both object format and string format
        const value = typeof item === 'object' ? item.name : item;
        this.input.value = value;
        this.close();
        
        // Trigger input event for any listeners
        this.input.dispatchEvent(new Event('input', { bubbles: true }));
        this.input.dispatchEvent(new Event('change', { bubbles: true }));
        
        // Focus next input or blur
        const form = this.input.closest('form');
        if (form) {
            const inputs = Array.from(form.querySelectorAll('input[type="text"], input[type="color"], button[type="submit"]'));
            const currentIndex = inputs.indexOf(this.input);
            if (currentIndex < inputs.length - 1) {
                inputs[currentIndex + 1].focus();
            }
        }
    }

    showLoading() {
        this.dropdown.innerHTML = `
            <div class="autocomplete-loading">
                <div class="autocomplete-loading-spinner"></div>
                <span>Searching...</span>
            </div>
        `;
        this.open();
    }

    showNoResults() {
        this.dropdown.innerHTML = `
            <div class="autocomplete-no-results">
                <div class="autocomplete-no-results-icon">🔍</div>
                <div>No results found</div>
            </div>
        `;
        this.open();
    }

    open() {
        this.isOpen = true;
        this.dropdown.classList.add('active');
        this.input.setAttribute('aria-expanded', 'true');
    }

    close() {
        this.isOpen = false;
        this.dropdown.classList.remove('active');
        this.input.setAttribute('aria-expanded', 'false');
        this.highlightedIndex = -1;
    }
}

// Initialize autocomplete when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Artist autocomplete
    const artistAutocomplete = new Autocomplete('artist', '/artist-suggestions', {
        type: 'artist',
        placeholder: 'Artist name...'
    });

    // Album autocomplete (with artist dependency)
    const albumAutocomplete = new Autocomplete('album', '/album-suggestions', {
        type: 'album',
        dependentInputId: 'artist',
        placeholder: 'Album name or Spotify link...'
    });
});