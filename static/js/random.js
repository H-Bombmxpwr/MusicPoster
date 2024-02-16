//java script to ensure that the posters are random on the website
document.addEventListener('DOMContentLoaded', function () {
    const posters = [
    "1988.png",
    "monsters.png",
    "mbdtf.png",
    "american_teen.png",
    "innerspeaker.png",
    "apolloxxI.png",
    "sing_the_blues.png",
    "channel_orange.png",
    "testing.png",
    "flower_boy.png",
    "aja.png",
    "erratic_cinema.png",
    "enema_of_the_state.png",
    "thee_sacred_souls.png",
    "the_woman_in_me.png",
    "case_study_01.png",
    "free_your_mind.png",
    "me.png",
    "speak_now.png",
    "lover.png",
    "well_done.png",
    "make_it_big.png",
    "an_evening_with_silk_sonic.png",
    "melopobia.png",
    "traffic.png",
    "pink_friday_2.png",
    "starboy.png",
    "a_lot_about_livin.png",
    "new_eyes.png",
    "stick_season.png",
    "han.png",
    "led_zeppelin_III.png",
    "gunfighter_ballads.png",
    "blonde.png",
    "the_score.png",
    "3_feet_high.png",
    "1989.png",
    "son_of_a_son_of_a_sailor.png",
    "southern_nights.png",
    "back_in_black.png",
    "pimp_a_butterfly.png",
    "kick.png",
    "thitvs.png",
    "off_the_wall.png",
    "red.png",
    "cmon.png",
    "minute_by_minute.png",
    "vampires_of_city.png",
    "red_moon_in_venus.png",
    "acid_rap.png",
    "streets_of_bolingbrook.png",
    "system_of_a_down.png",
    "oxnard.png",
    "private_space.png",
    "uh_huh.png"
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
