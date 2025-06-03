function submitPoster() {
    const submitButton = document.getElementById('submit-button');
    const successMessage = document.getElementById('success-message');

    // Ensure elements exist before accessing their values
    const posterImg = document.getElementById('poster-img');
    const imgDataInput = document.getElementById('img_data');
    const artistInput = document.querySelector('input[name="artist_name"]');
    const albumInput = document.querySelector('input[name="album_name"]');

    if (!posterImg || !imgDataInput || !artistInput || !albumInput) {
        console.error("🚨 Error: Missing input fields.");
        successMessage.innerHTML = "❌ Submission failed: Missing form data.";
        successMessage.style.display = "block";
        return;
    }

    // Ensure the latest base64 image is stored in the hidden input
    imgDataInput.value = posterImg.src;

    // Form Data Submission
    const formData = new FormData();
    formData.append('img_data', imgDataInput.value);
    formData.append('artist_name', artistInput.value);
    formData.append('album_name', albumInput.value);

    console.log("📤 Submitting poster with updated image data:", formData);

    fetch("/submit-poster", {
        method: "POST",
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            submitButton.disabled = true;
            successMessage.innerHTML = "✅ Poster successfully submitted!";
            successMessage.style.display = "block";
        } else {
            successMessage.innerHTML = "❌ Upload failed: " + data.message;
            successMessage.style.display = "block";
        }
    })
    .catch(error => {
        console.error("Error:", error);
        successMessage.innerHTML = "❌ An error occurred while submitting.";
        successMessage.style.display = "block";
    });
}

