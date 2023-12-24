//java script to ensure that the posters are random on the website
document.addEventListener('DOMContentLoaded', function () {
    const posters = [
    "channel_orange.png",
    "pimp_a_butterfly.png",
    "mbdtf.png",
    "speak_now.png",
    "enema_of_the_state.png",
    "streets_of_bolingbrook.png",
    "new_eyes.png",
    "kick.png",
    "red_moon_in_venus.png",
    "back_in_black.png",
    "an_evening_with_silk_sonic.png",
    "free_your_mind.png",
    "case_study_01.png",
    "han.png",
    "thitvs.png",
    "1988.png",
    "off_the_wall.png",
    "erratic_cinema.png",
    "stick_season.png",
    "aja.png",
    "system_of_a_down.png",
    "blonde.png",
    "minute_by_minute.png",
    "vampires_of_city.png",
    "3_feet_high.png",
    "led_zeppelin_III.png",
    "the_score.png",
    "apolloxxI.png",
    "pink_friday_2.png",
    "oxnard.png",
    "red.png",
    "lover.png",
    "starboy.png",
    "1989.png",
    "innerspeaker.png",
    "make_it_big.png",
    "flower_boy.png",
    "american_teen.png"
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
