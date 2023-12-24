document.addEventListener('DOMContentLoaded', function () {
    const leftContainer = document.querySelector('.poster-scroll-container[style="left: 10px;"]');
    const rightContainer = document.querySelector('.poster-scroll-container[style="right: 10px;"]');

    // Function to start scrolling
    function startScrolling(container) {
        let scrollHeight = container.scrollHeight;
        let currentScroll = 0;
        let step = 0.2; // Scroll speed

        function scroll() {
            currentScroll += step;
            if (currentScroll >= scrollHeight) {
                // Reset scroll position to start of the cloned posters
                currentScroll = 0;
                container.scrollTop = 0;
            } else {
                container.scrollTop = currentScroll;
            }
            requestAnimationFrame(scroll);
        }

        requestAnimationFrame(scroll);
    }

    // Function to clone and append posters for continuous scrolling
    function cloneAndAppendPosters(container) {
        const posters = container.querySelectorAll('.poster-item');
        posters.forEach(poster => {
            const clone = poster.cloneNode(true);
            container.appendChild(clone);
        });
    }

    // Clone and append posters, then start scrolling
    cloneAndAppendPosters(leftContainer);
    cloneAndAppendPosters(rightContainer);

    startScrolling(leftContainer);
    startScrolling(rightContainer);
});
