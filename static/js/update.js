/**
 * Poster color and style update functionality
 * Handles real-time poster customization via AJAX
 */

function updatePosterColor(color = NaN, isBackground = false, isText = false, tabulated = false, dotted = false) {
    // Get current state
    const artist = document.getElementById('current-artist')?.value;
    const album = document.getElementById('current-album')?.value;
    let backgroundColor = document.getElementById('current-background-color')?.value;
    let textColor = document.getElementById('current-text-color')?.value;

    if (!artist || !album) {
        console.error('Missing artist or album information');
        return;
    }

    // Update colors based on which was changed
    if (isBackground && color) {
        backgroundColor = color;
    }
    if (isText && color) {
        textColor = color;
    }

    // Prepare request data
    const postData = {
        artist: artist,
        album: album,
        background: backgroundColor,
        text: textColor,
        tabulated: tabulated,
        dotted: dotted
    };

    // Show loading state
    const posterImg = document.getElementById('poster-img');
    if (posterImg) {
        posterImg.style.opacity = '0.7';
        posterImg.style.transition = 'opacity 0.2s ease';
    }

    // Send update request
    fetch('/update-poster', {
        method: 'POST',
        body: JSON.stringify(postData),
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
    })
    .then(data => {
        if (posterImg && data.img_data) {
            // Update poster image
            posterImg.src = data.img_data;
            posterImg.style.opacity = '1';

            // Update hidden state
            document.getElementById('current-background-color').value = backgroundColor;
            document.getElementById('current-text-color').value = textColor;

            // Update download link
            const downloadLink = document.getElementById('download-link');
            if (downloadLink) {
                downloadLink.href = data.img_data;
                const formattedAlbumName = album.replace(/\s+/g, '_');
                downloadLink.setAttribute('download', `${formattedAlbumName}.png`);
            }

            // Update hidden form data for submission
            const imgDataInput = document.getElementById('img_data');
            if (imgDataInput) {
                imgDataInput.value = data.img_data;
            }
        }
    })
    .catch(error => {
        console.error('Error updating poster:', error);
        if (posterImg) {
            posterImg.style.opacity = '1';
        }
    });
}

// Initialize download link functionality
document.addEventListener('DOMContentLoaded', function() {
    const downloadLink = document.getElementById('download-link');
    const posterImg = document.getElementById('poster-img');

    if (downloadLink && posterImg) {
        // Ensure download link has correct initial href
        downloadLink.href = posterImg.src;
    }
});