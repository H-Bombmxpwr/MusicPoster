//java script to ensure that the posters are random on the website
document.addEventListener('DOMContentLoaded', function () {
    const posters = [
    "me.png",
    "the_score.png",
    "channel_orange.png",
    "gunfighter_ballads.png",
    "american_teen.png",
    "pink_friday_2.png",
    "traffic.png",
    "monsters.png",
    "flower_boy.png",
    "well_done.png",
    "aja.png",
    "southern_nights.png",
    "melopobia.png",
    "blonde.png",
    "mbdtf.png",
    "lover.png",
    "erratic_cinema.png",
    "3_feet_high.png",
    "back_in_black.png",
    "cmon.png",
    "enema_of_the_state.png",
    "off_the_wall.png",
    "minute_by_minute.png",
    "testing.png",
    "new_eyes.png",
    "kick.png",
    "cage_the_elephant.png",
    "justice.png",
    "private_space.png",
    "they_might_be_giants.png",
    "free_your_mind.png",
    "acid_rap.png",
    "streets_of_bolingbrook.png",
    "red.png",
    "led_zeppelin_III.png",
    "oxnard.png",
    "rubber_soul.png",
    "starboy.png",
    "make_it_big.png",
    "speak_now.png",
    "han.png",
    "vampires_of_city.png",
    "uh_huh.png",
    "thitvs.png",
    "son_of_a_son_of_a_sailor.png",
    "system_of_a_down.png",
    "pimp_a_butterfly.png",
    "apolloxxI.png",
    "red_moon_in_venus.png",
    "the_woman_in_me.png",
    "a_lot_about_livin.png",
    "pinkerton.png",
    "melophobia2.png",
    "1988.png",
    "1989.png",
    "sing_the_blues.png",
    "stick_season.png",
    "astro_lounge.png",
    "little_criminals.png",
    "human_after_all.png",
    "case_study_01.png",
    "innerspeaker.png",
    "thee_sacred_souls.png",
    "an_evening_with_silk_sonic.png"
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
