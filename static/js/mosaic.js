/**
 * Mosaic page functionality
 * Handles infinite scroll loading of dynamically generated posters
 */

const mosaicContainer = document.getElementById('mosaic-container');
let isLoading = false;

/**
 * Fetch and display more posters from the API
 */
async function fetchMorePosters() {
    if (isLoading || !mosaicContainer) return;

    isLoading = true;

    try {
        const response = await axios.get('/api/generate-posters');
        const posters = response.data;

        if (posters && Array.isArray(posters) && posters.length > 0) {
            posters.forEach((poster, index) => {
                const posterElement = document.createElement('div');
                posterElement.className = 'poster';
                posterElement.style.animationDelay = `${index * 0.05}s`;

                if (poster && typeof poster === 'string' && poster.startsWith('data:image/')) {
                    posterElement.innerHTML = `<img src="${poster}" alt="Generated Poster" loading="lazy">`;
                } else {
                    posterElement.innerHTML = `<img src="/static/images/fallback.png" alt="Error Loading Poster">`;
                    console.warn('Invalid poster data received');
                }

                mosaicContainer.appendChild(posterElement);
            });
        }
    } catch (error) {
        console.error('Error fetching posters:', error);
    } finally {
        isLoading = false;
    }
}

//Uncomment to enable infinite scroll for auto-generated posters
window.addEventListener('scroll', () => {
    const scrollableHeight = document.documentElement.scrollHeight - window.innerHeight;
    const scrolled = window.scrollY;

    if (scrollableHeight - scrolled < 300) {
        fetchMorePosters();
    }
});