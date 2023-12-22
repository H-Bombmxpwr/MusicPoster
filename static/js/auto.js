// static/js/script.js

function debounce(func, delay) {
    let inDebounce;
    return function() {
        const context = this;
        const args = arguments;
        clearTimeout(inDebounce);
        inDebounce = setTimeout(() => func.apply(context, args), delay);
    };
}

function fetchSuggestions(inputId, endpoint, suggestionsId) {
    const input = document.getElementById(inputId);
    const suggestions = document.getElementById(suggestionsId);

    input.addEventListener('input', debounce(function() {
        const query = this.value;
        fetch(endpoint + '?q=' + encodeURIComponent(query))
            .then(response => response.json())
            .then(data => {
                suggestions.innerHTML = '';  // Clear existing suggestions
                data.forEach(item => {
                    suggestions.innerHTML += '<option value="' + item + '"></option>';
                });
            });
    }, 1000));
}

// Call fetchSuggestions for artists and albums
fetchSuggestions('artist', '/artist-suggestions', 'artist-suggestions');
fetchSuggestions('album', '/album-suggestions', 'album-suggestions');
