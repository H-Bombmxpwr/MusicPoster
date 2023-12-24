//java script to ensure that the posters are random on the website
document.addEventListener('DOMContentLoaded', function () {
    const posters = [
    "system_of_a_down.png",
    "erratic_cinema.png",
    "flower_boy.png",
    "apolloxxI.png",
    "mbdtf.png",
    "red.png",
    "han.png",
    "1988.png",
    "the_score.png",
    "pink_friday_2.png",
    "off_the_wall.png",
    "led_zeppelin_III.png",
    "pimp_a_butterfly.png",
    "oxnard.png",
    "american_teen.png",
    "minute_by_minute.png",
    "stick_season.png",
    "an_evening_with_silk_sonic.png",
    "back_in_black.png",
    "1989.png",
    "starboy.png",
    "case_study_01.png",
    "enema_of_the_state.png",
    "speak_now.png",
    "streets_of_bolingbrook.png",
    "vampires_of_city.png",
    "aja.png",
    "3_feet_high.png",
    "free_your_mind.png",
    "channel_orange.png",
    "innerspeaker.png",
    "new_eyes.png",
    "blonde.png",
    "make_it_big.png",
    "kick.png",
    "thitvs.png",
    "lover.png"
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
