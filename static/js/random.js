//java script to ensure that the posters are random on the website
document.addEventListener('DOMContentLoaded', function () {
    const posters = [
        "3_feet_high.png",
        "american_teen.png",
        "aja.png",
        "an_evening_with_silk_sonic.png",
        "apolloxxI.png",
        "back_in_black.png",
        "blonde.png",
        "case_study_01.png",
        "free_your_mind.png",
        "thitvs.png",
        "han.png",
        "vampires_of_city.png",
        "channel_orange.png",
        "kick.png",
        "mbdtf.png",
        "minute_by_minute.png",
        "off_the_wall.png",
        "oxnard.png",
        "system_of_a_down.png",
        "the_score.png",
        "new_eyes.png",
        "starboy.png"
    ];

    // Function to shuffle an array
    function shuffle(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
        return array;
    }

    // Shuffle the posters array
    const shuffledPosters = shuffle(posters);

    // Function to create poster items
    function createPosterItem(src) {
        const posterItem = document.createElement('div');
        posterItem.className = 'poster-item autoscroll';
        const img = document.createElement('img');
        img.src = `static/posters_resized/${src}`;
        img.alt = src;
        posterItem.appendChild(img);
        return posterItem;
    }

    // Append shuffled images to the scroll containers
    const leftContainer = document.querySelector('.poster-scroll-container[style="left: 10px;"]');
    const rightContainer = document.querySelector('.poster-scroll-container[style="right: 10px;"]');

    shuffledPosters.forEach((posterSrc, index) => {
        const posterItem = createPosterItem(posterSrc);
        if (index % 2 === 0) { // Even index, left side
            leftContainer.appendChild(posterItem);
        } else { // Odd index, right side
            rightContainer.appendChild(posterItem);
        }
    });
});
