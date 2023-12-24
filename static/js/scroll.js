document.addEventListener('DOMContentLoaded', function () {
    const leftContainer = document.querySelector('.poster-scroll-container[style="left: 10px;"]');
    const rightContainer = document.querySelector('.poster-scroll-container[style="right: 10px;"]');

    // Function to clone and append posters for continuous scrolling
    function cloneAndAppendPosters(container) {
        const posters = container.querySelectorAll('.poster-item');
        posters.forEach(poster => {
            const clone = poster.cloneNode(true);
            container.appendChild(clone);
        });
    }

    // Clone and append posters
    cloneAndAppendPosters(leftContainer);
    cloneAndAppendPosters(rightContainer);

    // Function to start scrolling
    function startScrolling(container) {
        let currentScroll = 0;
        let step = 0.05; // Adjust this to control scroll speed

        function scroll() {
            currentScroll += step;
            container.scrollTop = currentScroll;

            // Reset scroll position to start when it reaches the end of the original content
            if (currentScroll >= container.scrollHeight / 2) {
                currentScroll = 0;
                container.scrollTop = 0;
            }

            requestAnimationFrame(scroll);
        }

        requestAnimationFrame(scroll);
    }

    // Start scrolling
    startScrolling(leftContainer);
    startScrolling(rightContainer);
});