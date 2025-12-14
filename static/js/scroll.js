/**
 * Smooth infinite scroll animation for poster galleries
 * Uses CSS transforms for better performance and smoother animation
 */

document.addEventListener('DOMContentLoaded', function () {
    const leftContainer = document.querySelector('.poster-scroll-container[style*="left"]');
    const rightContainer = document.querySelector('.poster-scroll-container[style*="right"]');

    if (!leftContainer || !rightContainer) return;

    // Configuration
    const SCROLL_SPEED = 0.3; // pixels per frame
    const CLONE_BUFFER = 2; // Number of times to clone content for seamless loop

    /**
     * Initialize a scroll container with cloned content and animation
     */
    function initScrollContainer(container, direction = 1) {
        // Wait for posters to be added by random.js
        setTimeout(() => {
            const originalContent = container.innerHTML;
            
            // Clone content for seamless looping
            for (let i = 0; i < CLONE_BUFFER; i++) {
                container.innerHTML += originalContent;
            }

            // Create smooth scroll animation
            let scrollPosition = direction === 1 ? 0 : container.scrollHeight / (CLONE_BUFFER + 1);
            let animationId;
            let isRunning = true;

            function animate() {
                if (!isRunning) return;

                scrollPosition += SCROLL_SPEED * direction;

                // Reset position for seamless loop
                const resetPoint = container.scrollHeight / (CLONE_BUFFER + 1);
                
                if (direction === 1 && scrollPosition >= resetPoint) {
                    scrollPosition = 0;
                } else if (direction === -1 && scrollPosition <= 0) {
                    scrollPosition = resetPoint;
                }

                container.scrollTop = scrollPosition;
                animationId = requestAnimationFrame(animate);
            }

            // Start animation
            animationId = requestAnimationFrame(animate);

            // Pause on hover for better UX
            container.addEventListener('mouseenter', () => {
                isRunning = false;
                cancelAnimationFrame(animationId);
            });

            container.addEventListener('mouseleave', () => {
                isRunning = true;
                animationId = requestAnimationFrame(animate);
            });

            // Cleanup on page unload
            window.addEventListener('beforeunload', () => {
                isRunning = false;
                cancelAnimationFrame(animationId);
            });

        }, 100); // Small delay to ensure random.js has populated the containers
    }

    // Initialize both containers with opposite scroll directions
    initScrollContainer(leftContainer, 1);  // Scroll down
    initScrollContainer(rightContainer, -1); // Scroll up
});