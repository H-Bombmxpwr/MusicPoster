function updatePosterColor(color=NaN, isBackground=false, isText=false, tabulated=false, dotted=false) {
    // Get the current values for artist, album, and current colors from hidden inputs
    const artist = document.getElementById('current-artist').value;
    const album = document.getElementById('current-album').value;
    let backgroundColor = document.getElementById('current-background-color').value;
    let textColor = document.getElementById('current-text-color').value;

    // Determine the new background and text colors
    if (isBackground) {
        backgroundColor = color; // Update background color
    }
    if (isText) {
        textColor = color; // Update text color
    }

    // Prepare the data to send, including the colors
    const postData = {
        artist: artist,
        album: album,
        background: backgroundColor,
        text: textColor,
        tabulated: tabulated,
        dotted: dotted
    };

    // Send the AJAX POST request to the Flask server
    fetch('update-poster', {
        method: 'POST',
        body: JSON.stringify(postData),
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        // Update the poster image with the new image data
        const posterImg = document.getElementById('poster-img');
        const downloadLink = document.getElementById('download-link');
        if (posterImg) {
            posterImg.src = data.img_data;

            // Update the hidden input values for the colors
            document.getElementById('current-background-color').value = backgroundColor;
            document.getElementById('current-text-color').value = textColor;

            // Also update the download link
            downloadLink.href = data.img_data;
            const formattedAlbumName = album.replace(/\s/g, '_');
            downloadLink.setAttribute('download', `${formattedAlbumName}.png`);

            // Update the custom color picker trigger's background color to reflect the change
            if (isBackground) {
                document.querySelector('.custom-color-picker-trigger').style.background = backgroundColor;
            } else {
                document.querySelectorAll('.custom-color-picker-trigger')[1].style.background = textColor;
            }
        }
    })
    .catch(error => {
        console.error('Error updating poster color:', error);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const downloadLink = document.getElementById('download-link');
    downloadLink.addEventListener('click', function(event) {
        // You could also perform any necessary actions here before the download
    });
});
