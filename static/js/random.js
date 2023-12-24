//java script to ensure that the posters are random on the website
document.addEventListener('DOMContentLoaded', function () {
    const posters = [
    "1988.png",
    "free_your_mind.png",
    "erratic_cinema.png",
    "blonde.png",
    "oxnard.png",
    "back_in_black.png",
    "thitvs.png",
    "innerspeaker.png",
    "apolloxxI.png",
    "streets_of_bolingbrook.png",
    "kick.png",
    "3_feet_high.png",
    "minute_by_minute.png",
    "red_moon_in_venus.png",
    "new_eyes.png",
    "enema_of_the_state.png",
    "the_woman_in_me.png",
    "stick_season.png",
    "han.png",
    "son_of_a_son_of_a_sailor.png",
    "american_teen.png",
    "pimp_a_butterfly.png",
    "lover.png",
    "flower_boy.png",
    "channel_orange.png",
    "starboy.png",
    "mbdtf.png",
    "uh_huh.png",
    "off_the_wall.png",
    "1989.png",
    "red.png",
    "speak_now.png",
    "system_of_a_down.png",
    "a_lot_about_livin.png",
    "pink_friday_2.png",
    "an_evening_with_silk_sonic.png",
    "case_study_01.png",
    "make_it_big.png",
    "southern_nights.png",
    "gunfighter_ballads.png",
    "the_score.png",
    "aja.png",
    "led_zeppelin_III.png",
    "vampires_of_city.png"
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
