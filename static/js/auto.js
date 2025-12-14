/**
 * Autocomplete functionality for artist and album inputs
 * Uses debounced API calls for better performance
 */

function debounce(func, delay) {
    let timeoutId;
    return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
}

function fetchSuggestions(inputId, endpoint, suggestionsId, dependentInputId = null) {
    const input = document.getElementById(inputId);
    const suggestions = document.getElementById(suggestionsId);

    if (!input || !suggestions) return;

    const debouncedFetch = debounce(function(value) {
        if (!value || value.length < 2) {
            suggestions.innerHTML = '';
            return;
        }

        let query = endpoint + '?q=' + encodeURIComponent(value);

        // Add artist filter for album suggestions
        if (dependentInputId && endpoint === '/album-suggestions') {
            const dependentInput = document.getElementById(dependentInputId);
            if (dependentInput && dependentInput.value) {
                query += '&artist=' + encodeURIComponent(dependentInput.value);
            }
        }

        fetch(query)
            .then(response => {
                if (!response.ok) throw new Error('Network response was not ok');
                return response.json();
            })
            .then(data => {
                suggestions.innerHTML = '';
                if (Array.isArray(data)) {
                    data.forEach(item => {
                        const option = document.createElement('option');
                        option.value = item;
                        suggestions.appendChild(option);
                    });
                }
            })
            .catch(error => {
                console.warn('Suggestion fetch failed:', error);
                suggestions.innerHTML = '';
            });
    }, 150);

    input.addEventListener('input', function() {
        debouncedFetch(this.value);
    });
}

// Initialize autocomplete when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    fetchSuggestions('artist', '/artist-suggestions', 'artist-suggestions');
    fetchSuggestions('album', '/album-suggestions', 'album-suggestions', 'artist');
});