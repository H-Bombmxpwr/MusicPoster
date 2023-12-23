// JavaScript
document.addEventListener('DOMContentLoaded', function () {
    var scrollContainers = document.querySelectorAll('.poster-scroll-container');

    scrollContainers.forEach(function(container) {
        var items = container.querySelectorAll('.poster-item');
        var scrollHeight = container.scrollHeight;
        var cloneContainer = document.createElement('div');

        // Clone and append items to create an infinite effect
        items.forEach(function(item) {
            var clone = item.cloneNode(true);
            cloneContainer.appendChild(clone);
        });

        // Append the clone container after the original items
        container.appendChild(cloneContainer);

        // Start the scrolling animation
        startScrolling(container, scrollHeight);
    });
});

function startScrolling(container, scrollHeight) {
    var step = 1; // Change step to adjust scroll speed
    function scroll() {
        if (container.scrollTop < scrollHeight * 2 - container.clientHeight) {
            container.scrollTop += step;
        } else {
            // Reset scrollTop position to the start of the cloned items when the end is reached
            container.scrollTop = scrollHeight - container.clientHeight;
        }
        requestAnimationFrame(scroll);
    }
    requestAnimationFrame(scroll);
}