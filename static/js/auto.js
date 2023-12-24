function debounce(func, delay) {
    let inDebounce;
    return function() {
        const context = this;
        const args = arguments;
        clearTimeout(inDebounce);
        inDebounce = setTimeout(() => func.apply(context, args), delay);
    };
}

function fetchSuggestions(inputId, endpoint, suggestionsId, dependentInputId = null) {
    const input = document.getElementById(inputId);
    const suggestions = document.getElementById(suggestionsId);

    input.addEventListener('input', debounce(function() {
        let query = endpoint + '?q=' + encodeURIComponent(this.value);

        // If dependent input is provided and it's for album suggestions
        if (dependentInputId && endpoint === '/album-suggestions') {
            const dependentInputValue = document.getElementById(dependentInputId).value;
            if (dependentInputValue) {
                query += '&artist=' + encodeURIComponent(dependentInputValue);
            }
        }

        fetch(query)
            .then(response => response.json())
            .then(data => {
                suggestions.innerHTML = '';  // Clear existing suggestions
                data.forEach(item => {
                    suggestions.innerHTML += '<option value="' + item + '"></option>';
                });
            });
    }, 100));
}

// Call fetchSuggestions for artists and albums
fetchSuggestions('artist', '/artist-suggestions', 'artist-suggestions');
fetchSuggestions('album', '/album-suggestions', 'album-suggestions', 'artist');
