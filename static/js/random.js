//java script to ensure that the posters are random on the website
document.addEventListener('DOMContentLoaded', function () {
    const posters = [
    "sing_the_blues.png",
    "the_score.png",
    "me.png",
    "son_of_a_son_of_a_sailor.png",
    "innerspeaker.png",
    "flirtin_with_disiaster.png",
    "pink_friday_2.png",
    "erratic_cinema.png",
    "vampires_of_city.png",
    "stick_season.png",
    "back_in_black.png",
    "well_done.png",
    "enema_of_the_state.png",
    "testing.png",
    "flower_boy.png",
    "the_woman_in_me.png",
    "melopobia.png",
    "1989.png",
    "cmon.png",
    "make_it_big.png",
    "kick.png",
    "free_your_mind.png",
    "oxnard.png",
    "traffic.png",
    "system_of_a_down.png",
    "case_study_01.png",
    "thee_sacred_souls.png",
    "diver_down.png",
    "cage_the_elephant.png",
    "acid_rap.png",
    "han.png",
    "led_zeppelin_III.png",
    "thitvs.png",
    "channel_orange.png",
    "red.png",
    "little_criminals.png",
    "they_might_be_giants.png",
    "american_teen.png",
    "monsters.png",
    "a_lot_about_livin.png",
    "blonde.png",
    "pinkerton.png",
    "apolloxxI.png",
    "new_eyes.png",
    "gunfighter_ballads.png",
    "mbdtf.png",
    "streets_of_bolingbrook.png",
    "southern_nights.png",
    "human_after_all.png",
    "off_the_wall.png",
    "starboy.png",
    "justice.png",
    "private_space.png",
    "pimp_a_butterfly.png",
    "melophobia2.png",
    "an_evening_with_silk_sonic.png",
    "1988.png",
    "slippery_when_wet.png",
    "minute_by_minute.png",
    "lover.png",
    "uh_huh.png",
    "speak_now.png",
    "yeezus.png",
    "aja.png",
    "red_moon_in_venus.png",
    "astro_lounge.png",
    "once_bitten.png",
    "rubber_soul.png",
    "3_feet_high.png"
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
