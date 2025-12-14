/**
 * Poster submission functionality
 * Handles submitting user-created posters for review
 */

function submitPoster() {
    const submitButton = document.getElementById('submit-button');
    const successMessage = document.getElementById('success-message');

    // Get form elements
    const posterImg = document.getElementById('poster-img');
    const imgDataInput = document.getElementById('img_data');
    const artistInput = document.querySelector('input[name="artist_name"]');
    const albumInput = document.querySelector('input[name="album_name"]');

    // Validate required elements
    if (!posterImg || !imgDataInput || !artistInput || !albumInput) {
        console.error('Missing required form elements');
        showMessage(successMessage, 'Submission failed: Missing form data.', false);
        return;
    }

    // Ensure latest image data is captured
    imgDataInput.value = posterImg.src;

    // Disable button and show loading state
    if (submitButton) {
        submitButton.disabled = true;
        submitButton.textContent = 'Submitting...';
    }

    // Prepare form data
    const formData = new FormData();
    formData.append('img_data', imgDataInput.value);
    formData.append('artist_name', artistInput.value);
    formData.append('album_name', albumInput.value);

    // Submit poster
    fetch('/submit-poster', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage(successMessage, 'Poster submitted successfully! Thanks for sharing.', true);
            if (submitButton) {
                submitButton.textContent = 'Submitted!';
            }
        } else {
            showMessage(successMessage, 'Upload failed: ' + (data.message || 'Unknown error'), false);
            resetButton(submitButton);
        }
    })
    .catch(error => {
        console.error('Submission error:', error);
        showMessage(successMessage, 'An error occurred while submitting. Please try again.', false);
        resetButton(submitButton);
    });
}

/**
 * Display a success or error message
 */
function showMessage(element, message, isSuccess) {
    if (!element) return;
    
    element.textContent = message;
    element.style.display = 'block';
    element.style.color = isSuccess ? 'var(--success-green, #00d26a)' : 'var(--error-red, #ff4757)';
    element.style.background = isSuccess 
        ? 'rgba(0, 210, 106, 0.1)' 
        : 'rgba(255, 71, 87, 0.1)';
    element.style.border = isSuccess 
        ? '1px solid rgba(0, 210, 106, 0.3)' 
        : '1px solid rgba(255, 71, 87, 0.3)';
}

/**
 * Reset button to default state
 */
function resetButton(button) {
    if (!button) return;
    
    button.disabled = false;
    button.textContent = 'Submit for Review';
}