//java script to ensure that the posters are random on the website
document.addEventListener('DOMContentLoaded', function () {
    const posters = [
    "uh_huh.png",
    "blonde.png",
    "thee_sacred_souls.png",
    "gunfighter_ballads.png",
    "the_score.png",
    "red.png",
    "an_evening_with_silk_sonic.png",
    "han.png",
    "system_of_a_down.png",
    "american_teen.png",
    "son_of_a_son_of_a_sailor.png",
    "3_feet_high.png",
    "monsters.png",
    "traffic.png",
    "a_lot_about_livin.png",
    "off_the_wall.png",
    "led_zeppelin_III.png",
    "mbdtf.png",
    "the_woman_in_me.png",
    "enema_of_the_state.png",
    "stick_season.png",
    "pink_friday_2.png",
    "free_your_mind.png",
    "aja.png",
    "kick.png",
    "make_it_big.png",
    "pimp_a_butterfly.png",
    "case_study_01.png",
    "starboy.png",
    "private_space.png",
    "channel_orange.png",
    "vampires_of_city.png",
    "cmon.png",
    "me.png",
    "back_in_black.png",
    "erratic_cinema.png",
    "streets_of_bolingbrook.png",
    "southern_nights.png",
    "innerspeaker.png",
    "flower_boy.png",
    "apolloxxI.png",
    "oxnard.png",
    "minute_by_minute.png",
    "thitvs.png",
    "red_moon_in_venus.png",
    "new_eyes.png",
    "lover.png",
    "1989.png",
    "1988.png",
    "speak_now.png",
    "sing_the_blues.png"
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
