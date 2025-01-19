const mosaicContainer = document.getElementById("mosaic-container");
let isLoading = false; // Prevent multiple API calls

async function fetchMorePosters() {
    if (isLoading) return;
  
    isLoading = true;
  
    try {
      const response = await axios.get("/api/generate-posters");
      const posters = response.data;
  
      if (posters && posters.length > 0) {
        posters.forEach((poster) => {
          const posterElement = document.createElement("div");
          posterElement.className = "poster";
  
          // Verify poster data and append fallback if invalid
          if (poster && poster.startsWith("data:image/")) {
            posterElement.innerHTML = `<img src="${poster}" alt="Generated Poster">`;
          } else {
            posterElement.innerHTML = `<img src="/static/images/fallback.png" alt="Error Loading Poster">`;
            console.error("Invalid poster data:", poster);
          }
  
          mosaicContainer.appendChild(posterElement);
        });
      }
    } catch (error) {
      console.error("Error fetching new posters:", error);
    } finally {
      isLoading = false;
    }
  }
  

// Detect when the user scrolls near the bottom of the page
window.addEventListener("scroll", () => {
  const scrollableHeight = document.documentElement.scrollHeight - window.innerHeight;
  const scrolled = window.scrollY;

  if (scrollableHeight - scrolled < 300) {
    // Trigger fetch if user is near the bottom
    fetchMorePosters();
  }
});
